import copy
import traceback

class SyntaxError(Exception):

	def __init__(self,msg,**attrs):
		self.message = msg
		self.sass_backtrace = []
		self.add_backtrace(attrs)

	def sass_filename(self):
		''' The name of the file in which the exception was raised.
			This could be None if no filename is available
		'''
		return self.sass_backtrace[0]['filename'] if self.sass_backtrace and self.sass_backtrace[0].has_key('filename') else None

	def sass_mixin(self):
		''' The name of the mixin in which the error occurred.
			This could be `nil` if the error occurred outside a mixin.
		'''
		return self.sass_backtrace[0]['mixin'] if self.sass_backtrace and self.sass_backtrace[0].has_key('mixin') else None

	def sass_line(self):
		''' The line of the Sass template on which the error occurred.
		'''
		return self.sass_backtrace[0]['line'] if self.sass_backtrace and self.sass_backtrace[0].has_key('line') else 0

	def add_backtrace(self,attrs):
		''' Adds an entry to the exception's Sass backtrace '''
		self.sass_backtrace.append(dict(((k,v) for k,v in attrs.iteritems() if v is not None)))

	def modify_backtrace(self,attrs):
		attrs = dict((k,v) for k,v in attrs.iteritems() if v is not None)

		backtrace = copy.deepcopy(self.sass_backtrace)

		backtrace.reverse()

		for entry in backtrace:
			entry = attrs.update(entry)
			attrs = dict((k,v) for k,v in attrs.iteritems() if not entry.has_key(k))
			if not attrs:
				break

		backtrace.reverse()
		self.sass_backtrace = backtrace

	def __str__(self):
		return self.message

	def backtrace(self):
		''' Returns the standard exception backtrace including the Sass backtrace '''

		if not traceback.extract_stack():
			return None

		all_empty = True
		for h in self.sass_backtrace:
			if h:
				all_empty = False
				break

		if all_empty:
			return traceback.extract_stack()

		backtrace = []
		for h in self.sass_backtrace:
			backtrace.append('%s:%d%s' % (
					h['filename'] if h.has_key('filename') else '(sass)', 
					h['line'] if h.has_key('line') else 0,
					"in %s"% h['mixin'] if h.has_key('mixin') else ''
				))

		return backtrace + traceback.extract_stack()


