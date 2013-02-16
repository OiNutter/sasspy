import copy

from base import Base

class Memory(Base):

	def _dump(self,depth):
		return ""

	def __init__(self):
		self.contents = {}

	def retrieve(self,key,sha):
		if self.contents.has_key(key):
			if self.contents[key]['sha']==sha:
				obj = self.contents[key]['obj']
				return copy.deepcopy(obj)
		
		return None

	def store(self,key,sha,obj):
		self.contents[key] = {
			"sha":sha,
			"obj":obj
		}

	def reset(self):
		self.contents = {}
