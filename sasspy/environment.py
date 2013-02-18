class Environment(object):
	''' The lexical environment for SassScript.
  		This keeps track of variable, mixin, and function definitions.
 		
 		A new environment is created for each level of Sass nesting.
		This allows variables to be lexically scoped.
		The new environment refers to the environment in the upper scope,
		so it has access to variables defined in enclosing scopes,
		but new variables are defined locally.
		
		Environment also keeps track of the {Engine} options
		so that they can be made available to {Sass::Script::Functions}.
	'''

	def __init__(self,parent=None,**options):
		self.caller = None
		self.content = None
		self.parent = parent
		self.options = options if self.options else parent.options if parent and parent.options else {}

	def caller(self):
		''' The environment of the caller of this environment's mixin or function '''
		return self.caller if self.caller else self.parent.caller if self.parent and self.parent.caller else None

	def content(self):
		''' The content passed to this environment. This is naturally only set
			for mixin body environments with content passed in
		'''
		return self.content if self.content else self.parent.content if self.parent and self.parent.content else None