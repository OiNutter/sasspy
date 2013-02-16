import os
import errno
import regex as re

import utils
from base import Base

class Filesystem(Base):
	''' A backend for the Sass cache using the filesystem '''

	def __init__(self,cache_location):
		self.cache_location = cache_location

	def _retrieve(self,key,version,sha):
		''' See Base._retrieve '''

		keypath = self.path_to(key)
		if not os.access(keypath,os.R_OK):
			return

		try:
			with open(keypath,'rb') as f:
				if f.readline().strip() == version and f.readline().strip() == sha:
					return f.read()

			os.unlink(key)
			return None
		except (TypeError,EOFError,ValueError) as e:
			utils.sass_warn('Warning. Error encountered while reading cache %s: %s' % (keypath,str(e)))

	def _store(self,key,version,sha,contents):
		''' See Base._store '''

		keypath = self.path_to(key)

		try:
			if not os.path.exists(os.path.dirname(keypath)):
				os.makedirs(os.path.dirname(keypath))

		except Exception as e:
			if e.errcode != errno.EACCES:
				raise

	def path_to(self,key):
		''' Returns the path to a file for the given key '''

		def replace(match):
			return ord(match.group(0))

		key = re.sub(r'''[<>:\|?*%]''',replace,key)
		return os.path.join(self.cache_location,key)
