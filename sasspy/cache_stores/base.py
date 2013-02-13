import abc
import pickle
from hashlib import sha1

import utils
import version

class Base(object):
	''' An abstract base class for backends for the Sass cache.
		Any key-value store can act as such a backend;
		it just needs to implement the
		\{#_store} and \{#_retrieve} methods.

		To use a cache store with Sass,
		use the {file:SASS_REFERENCE.md#cache_store-option `cache_store` option}.

		@abstract
	'''

	__metaclass__ = abc.ABCMeta

	def _store(self,key,version,sha,contents):
		''' Store cached contents for later retrieval
			Must be implemented by all CacheStore subclasses

			Note: cache contents contain binary data
		'''

		raise NotImplementedError('%s must implement _store'%self.__class__.__name__)

	def _retrieve(self,key,version,sha):
		''' Retrieved cached contents.
			Must be implemented by all subclasses.

			Note: if the key exists but the sha or version have changed,
			then the key may be deleted by the cache store, if it wants to do so.
		'''

		raise NotImplementedError('%s must implement _retrieve'%self.__class__.__name__)

	def store(self,key,sha,object):
		''' Store a sass.Tree.RootNode '''
		try:
			self._store(key,version.Version,sha,pickle.dump(object))
		except (TypeError,IOError) as e:
			utils.sass_warn("Warning. Error encountered while saving cache %s:%s" % (key,str(e)))

	def retrieve(self,key,sha):
		''' Retrieve a sass.Tree.RootNode '''
		try:
			contents = self._retrieve(key,version.Version,sha)
			return pickle.load(contents) if contents else None
		except (EOFError,TypeError,ValueError,IOError) as e:
			utils.sass_warn("Warning. Error encountered while reading cache %s:%s" % (key,str(e)))

	def key(self,sass_dirname,sass_basename):

		directory = sha1()
		directory.update(sass_dirname)
		filename = "%sc"%sass_basename
		return "%s/%s" %(directory.hexdigest(),filename)