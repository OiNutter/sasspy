from base import Base

class Null(Base):

	def __init__(self):
		self.keys = {}

	def _retrieve(self,key,version,sha):
		return None

	def _store(self,key,version,sha,contents):
		self.keys[key] = True

	def was_set(self,key):
		return self.keys.get(key,False)
