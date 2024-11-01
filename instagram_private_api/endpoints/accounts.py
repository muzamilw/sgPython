import json

from ..compat import (
    compat_urllib_request, compat_urllib_error,
    compat_http_client, compat_urllib_parse
)
from ..errors import (
    ErrorHandler, ClientError, ClientLoginError, ClientConnectionError
)
from ..http import MultipartFormDataEncoder
from ..compatpatch import ClientCompatPatch
from socket import timeout, error as SocketError
from ssl import SSLError


from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem
from kivy.app import App

try:
    ConnectionError = ConnectionError       # pylint: disable=redefined-builtin
except NameError:  # Python 2:
    class ConnectionError(Exception):
        pass

class IgLoginValidationDlgContent(BoxLayout):
    pass

class AccountsEndpointsMixin(object):
    """For endpoints in ``/accounts/``."""

    headers = None
    Login_alert_dialog = None
    dlgContent = None
    checkpoint_url = None
    IsChallenged = False
    IsChallengedResolved = False
    
    

    def login(self):
       
        """Login."""

        print('overrided login()')

        prelogin_params = self._call_api(
            'si/fetch_headers/',
            params='',
            query={'challenge_type': 'signup', 'guid': self.generate_uuid(True)},
            return_response=True)

        login_params = {
            'device_id': self.device_id,
            'guid': self.uuid,
            'adid': self.ad_id,
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'username': self.username,
            'password': self.password,
            'login_attempt_count': '0',
        }

        try:
            """
            login_response = self._call_api(
            'accounts/login/', params=login_params, return_response=True)
            """

            url = 'https://i.instagram.com/api/v1/accounts/login/'
            params = login_params

            headers = self.default_headers
            headers['Content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            
            json_params = json.dumps(params, separators=(',', ':'))
            hash_sig = self._generate_signature(json_params)
            post_params = {
                'ig_sig_key_version': self.key_version,
                'signed_body': hash_sig + '.' + json_params
            }

            data = compat_urllib_parse.urlencode(post_params).encode('ascii')
            req = compat_urllib_request.Request(url, data, headers=headers)

            self.IsChallenged = False
            try:
                response = self.opener.open(req, timeout=self.timeout)
            except compat_urllib_error.HTTPError as e:
                
                response_text = json.loads(e.read().decode('utf8'))
                checkpoint_url = response_text.get('challenge').get('url')
                print('login failed, challenge received')
                self.IsChallenged = True
                self.login_challenge(checkpoint_url, headers)
            if self.on_login and self.IsChallenged == False:
                on_login_callback = self.on_login
                on_login_callback(self)
        except Exception as e:
            print('unhandled exception', e)

    

    def continue_ig_validation(self, code):
        print('clicked')
        app = App.get_running_app()
        #self.Logout_alert_dialog.dismiss()
        
        if code != "":
            try:
                
                print('processing code')
                code_data = {'security_code': code}
                data = compat_urllib_parse.urlencode(code_data).encode('ascii')

                req = compat_urllib_request.Request(self.checkpoint_url, data, headers=self.headers)
                response = self.opener.open(req, timeout=self.timeout)

                if response.info().get('Content-Encoding') == 'gzip':
                    buf = BytesIO(response.read())
                    res = gzip.GzipFile(fileobj=buf).read().decode('utf8')
                else:
                    res = response.read().decode('utf8')

                print(res)
                self.IsChallengedResolved = True
                if self.on_login:
                    on_login_callback = self.on_login
                    on_login_callback(self)

            except compat_urllib_error.HTTPError as e:
                print('unhandled exception', e)
        else:
            print('no code entered')

    def dismiss_callback(self, *args):
        self.Login_alert_dialog.dismiss(force=True)
        print('canceling')

    def login_challenge(self, checkpoint_url, headers):
        
        try:
            print('redirecting to ..', checkpoint_url)
            headers['X-CSRFToken'] = self.csrftoken
            headers['Referer'] = checkpoint_url
            
            mode = 1#int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
            challenge_data = {'choice': mode}
            data = compat_urllib_parse.urlencode(challenge_data).encode('ascii')
            
            req = compat_urllib_request.Request(checkpoint_url, data, headers=headers)
            response = self.opener.open(req, timeout=self.timeout)

            self.checkpoint_url = checkpoint_url
            self.headers = headers

            on_validation_required_callback = self.on_validation_required
            on_validation_required_callback(self)

        except compat_urllib_error.HTTPError as e:
            print('unhandled exception', e)


    

    def current_user(self):
        """Get current user info"""
        params = self.authenticated_params
        res = self._call_api('accounts/current_user/', params=params, query={'edit': 'true'})
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def edit_profile(self, first_name, biography, external_url, email, phone_number, gender):
        """
        Edit profile

        :param first_name:
        :param biography:
        :param external_url:
        :param email: Required.
        :param phone_number:
        :param gender: male: 1, female: 2, unspecified: 3
        :return:
        """
        if int(gender) not in [1, 2, 3]:
            raise ValueError('Invalid gender: {0:d}'.format(int(gender)))
        if not email:
            raise ValueError('Email is required.')

        params = {
            'username': self.authenticated_user_name,
            'gender': int(gender),
            'phone_number': phone_number or '',
            'first_name': first_name or '',
            'biography': biography or '',
            'external_url': external_url or '',
            'email': email,
        }
        params.update(self.authenticated_params)
        res = self._call_api('accounts/edit_profile/', params=params)
        if self.auto_patch:
            ClientCompatPatch.user(res.get('user'))
        return res

    def remove_profile_picture(self):
        """Remove profile picture"""
        res = self._call_api(
            'accounts/remove_profile_picture/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def change_profile_picture(self, photo_data):
        """
        Change profile picture

        :param photo_data: byte string of image
        :return:
        """
        endpoint = 'accounts/change_profile_picture/'
        json_params = json.dumps(self.authenticated_params)
        hash_sig = self._generate_signature(json_params)
        fields = [
            ('ig_sig_key_version', self.key_version),
            ('signed_body', hash_sig + '.' + json_params)
        ]
        files = [
            ('profile_pic', 'profile_pic', 'application/octet-stream', photo_data)
        ]

        content_type, body = MultipartFormDataEncoder().encode(fields, files)

        headers = self.default_headers
        headers['Content-Type'] = content_type
        headers['Content-Length'] = len(body)

        endpoint_url = '{0}{1}'.format(self.api_url.format(version='v1'), endpoint)
        req = compat_urllib_request.Request(endpoint_url, body, headers=headers)
        try:
            self.logger.debug('POST {0!s}'.format(endpoint_url))
            response = self.opener.open(req, timeout=self.timeout)
        except compat_urllib_error.HTTPError as e:
            error_response = self._read_response(e)
            self.logger.debug('RESPONSE: {0:d} {1!s}'.format(e.code, error_response))
            ErrorHandler.process(e, error_response)
        except (SSLError, timeout, SocketError,
                compat_urllib_error.URLError,   # URLError is base of HTTPError
                compat_http_client.HTTPException) as connection_error:
            raise ClientConnectionError('{} {}'.format(
                connection_error.__class__.__name__, str(connection_error)))

        post_response = self._read_response(response)
        self.logger.debug('RESPONSE: {0:d} {1!s}'.format(response.code, post_response))
        json_response = json.loads(post_response)

        if self.auto_patch:
            ClientCompatPatch.user(json_response['user'], drop_incompat_keys=self.drop_incompat_keys)

        return json_response

    def set_account_private(self):
        """Make account private"""
        res = self._call_api('accounts/set_private/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def set_account_public(self):
        """Make account public"""""
        res = self._call_api('accounts/set_public/', params=self.authenticated_params)
        if self.auto_patch:
            ClientCompatPatch.list_user(res['user'], drop_incompat_keys=self.drop_incompat_keys)
        return res

    def logout(self):
        """Logout user"""
        params = {
            'phone_id': self.phone_id,
            '_csrftoken': self.csrftoken,
            'guid': self.uuid,
            'device_id': self.device_id,
            '_uuid': self.uuid
        }
        return self._call_api('accounts/logout/', params=params, unsigned=True)

    def presence_status(self):
        """Get presence status setting"""
        json_params = json.dumps({}, separators=(',', ':'))
        query = {
            'ig_sig_key_version': self.key_version,
            'signed_body': self._generate_signature(json_params) + '.' + json_params
        }
        return self._call_api('accounts/get_presence_disabled/', query=query)

    def set_presence_status(self, disabled):
        """
        Set presence status setting

        :param disabled: True if disabling, else False
        """
        params = {
            'disabled': '1' if disabled else '0'
        }
        params.update(self.authenticated_params)
        return self._call_api('accounts/set_presence_disabled/', params=params)

    def enable_presence_status(self):
        """Enable presence status setting"""
        return self.set_presence_status(False)

    def disable_presence_status(self):
        """Disable presence status setting"""
        return self.set_presence_status(True)
