import winreg

def getusers(self) -> Optional[str]:
        if is_windows():

            try:
                for h_root in (winreg.HKEY_CURRENT_USER):
                    with winreg.OpenKey(h_root, r"Software\SocialPlannerPro") as h_apps:
                        for idx in range(winreg.QueryInfoKey(h_apps)[0]):
                            try:
                                with winreg.OpenKeyEx(h_apps, winreg.EnumKey(h_apps, idx)) as h_app_info:
                                    def get_value(key):
                                        return winreg.QueryValueEx(h_app_info, key)[0]

                                   

                            except (WindowsError, KeyError, ValueError):
                                continue

            except (WindowsError, KeyError, ValueError):
                logging.exception("Failed to get client install location")
                return None
        else:
            return None 