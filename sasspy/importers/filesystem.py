import os
import errno

from base import Base
from .. import utils

class Filesystem(Base):

	def __init__(self,root):
		''' Creates a new filesystem importer that imports files relative to a given path. '''
		self.root = os.path.realpath(root)
		self.same_name_warnings = set()

	def find_relative(self,name,base,**options):
		''' see Base.find_relative '''
		return self._find(os.path.dirname(base),name,**options)

	def find(self,name,**options):
		''' see Base.find '''
		return self._find(self.root,name,**options)

	def mtime(self,name,**options):
		''' see Base.mtime '''
		try:
			f,s = utils.destructure(self.find_real_file(self.root,name,**options))
			if f:
				stat = os.stat(f)
				return stat.st_mtime if stat else None
		except Exception as e:
			if e.errcode == errno.ENOENT:
				return None
			else:
				raise

	def key(self,name,**options):
		''' see Base.key '''
		return [self.__class__.__name__ + ":" + os.path.dirname(os.path.realpath(name)), os.path.basename(name)]

	def __str__(self):
		''' see Base.__str__ '''
		return self.root

	def __eql__(self,other):
		return self.root == other.root

	
