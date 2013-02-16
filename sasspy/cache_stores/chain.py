from base import Base

class Chain(Base):
	''' A meta-cache that chains multiple caches together.
		Specifically:

		* All `#store`s are passed to all caches.
		* `#retrieve`s are passed to each cache until one has a hit.
		* When one cache has a hit, the value is `#store`d in all earlier caches.
	'''

	def __init__(self,*caches):
		''' Create a new cache chaingin the given caches '''
		self.caches = caches

	def store(self,key,sha,obj):
		for c in self.caches:
			c.store(key,sha,obj)

	def retrieve(self,key,sha):

		for i,c in enumerate(self.caches):
			obj = c.retrieve(key,sha)
			if obj:
				for cache in self.caches[0:i]:
					cache.store(key,sha,obj)
				return obj

		return None