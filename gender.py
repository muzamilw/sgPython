import json
from unidecode import unidecode
from string import ascii_lowercase
import os
import re
from collections import defaultdict

from typing import NamedTuple

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# when the ASCII flag is used, \w is [a-zA-Z0-9_]
email_exp = re.compile(r'^[a-z]+[\w\.\-]+[a-z0-9]+\@{1}[a-z0-9]+[\w\.]+[a-z]$', flags=re.ASCII)

sal = {"common":{"m":["mr","sir","mister"],"f":["mrs","ms","miss"],"u":["dr","doctor","prof","professor"]},"uncommon":{"m":["hr","herr","dhr","senor","admiral","ambassador","baron","capt","col","commander","congressman","count","consul","datuk","dato","dean","governor","rabbi","reverend","senator","sergeant","sheikh","sultan","viscount","esq","brother","father","major","lieutenant","don","prince"],"f":["frau","fr","fraulein","senora","sra","barones","dra","madame","mme","mademoiselle","mlle","mevrouw","mw","viscountess","dame","princess","lady"],"u":["md","hon"]}}
#json.load(open(os.path.join(os.path.dirname(__file__),'data/data_salutations_.json')))
saluts = json.loads(json.dumps(sal))



#json.load(open(os.path.join(os.path.dirname(__file__), 'data/data_names_.json')))

#lnames = [l.strip() for l in open(resource_path(os.path.join('gender','data','data_last_names_.txt'))) if l.strip()] #[l.strip() for l in open(os.path.join(os.path.dirname(__file__), 'data/data_last_names_.txt')) if l.strip()]

lnames = ""

hypocs = json.loads(json.dumps(hp))

fnames = json.loads(json.dumps(fna))
#json.load(open(os.path.join(os.path.dirname(__file__), 'data/data_hypocorisms_.json')))
gramms = json.loads(json.dumps(gm))
#json.load(open(os.path.join(os.path.dirname(__file__),'data/data_grammgender_.json')))

class Person(NamedTuple):

	title: str
	first_name: str
	last_name: str
	email: str
	gender: str

	@classmethod
	def from_string(cls, st):

		title = None
		first_name = None
		last_name = None
		email = None
		gender = None

		st_ = str(st).lower().strip()

		for _ in st_.split():
			try:
				email = re.search(email_exp, _).group(0)
			except:
				pass

		if email:
			st_ = ''.join(st_.split(email)[:-1])

		st_ = re.sub(r'\s+', ' ', re.sub(r'[^' + ascii_lowercase + r']', ' ', st_)).strip()
		
		# try to find salutation
		def find_title(s):

			possible_titles = set()

			for type_ in 'common uncommon'.split():
				for g in saluts[type_]:
					tt_ = set(saluts[type_][g]) & set(s.split())
					if tt_:
						possible_titles |= tt_

			return possible_titles

		titles = find_title(st_)
		
		# now to the first name; assume that first name is more likely to stand before the last name
		fnms = []
		for _ in st_.split():
			if _ in fnames:
				if fnames[_] in 'm f'.split():
					first_name = _
					break
				else:
					# it's a unisex name, add to candidates
					fnms.append(_)

		# some names can be like titles, e.g. Dean
		names_like_titles = set(fnms) & titles

		if names_like_titles:
			# priority to names
			title = (titles - names_like_titles).pop()
			first_name = names_like_titles.pop()
			st_ = ' '.join([_ for _ in st_.split() if _ != title])

		if (not first_name) and fnms:
			first_name = fnms[0]
		elif (not first_name):
			for _ in st_.split():
				if _ in hypocs:
					first_name = _
					break

		if first_name:
			st_ = ' '.join([_ for _ in st_.split() if _ != first_name]).strip()

		# what's the last name then? assume it's more likely to come last
		if st_:
			wrds = st_.split()
			known_lnames = set(lnames) & set(wrds)
			if len(known_lnames) == 1:
				last_name = known_lnames.pop()
			elif len(wrds) == 1:
				last_name = wrds[-1]
			elif wrds[-2] not in 'al el de los la van dos del di der ter'.split():
				last_name = wrds[-1]
			else:
				last_name = ' '.join(wrds[-2:])

		return cls(title=title, first_name=first_name,  last_name=last_name, email=email, gender=gender)

class GenderDetector:

	def __init__(self):

		self.GENDS = 'm f'.split()

	def _from_title(self, title):

		for g in self.GENDS:
			if {title} & set(saluts['common'][g] + saluts['uncommon'][g]):
				return g

	def _from_first_name(self, first_name):

		if (first_name in fnames) and (fnames[first_name] in self.GENDS):
			return fnames[first_name]

		if first_name in hypocs:
			gnds = {fnames[nm] for nm in (set(hypocs[first_name]) & set(fnames))}
			return 'm' if {'m'} == gnds else 'f' if {'f'} == gnds else None

	def _from_email(self, email):

		if not email:
			return None

		_email = re.split(r'[\s\-\.\_]', email.split('@')[0])

		# keep potential genders based in first names in here
		first_name_cands = set()
		# grammatical gender words found in email address 