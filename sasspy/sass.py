import os

import utils
from engine import Engine

class Sass(object):

	_load_paths = None

	@property
	def load_paths(self):
		''' The global load paths for Sass files. This is meant for plugins and
  			libraries to register the paths to their Sass stylesheets to that they may
  			be `@imported`. This load path is used by every instance of [sass.Engine].
  			They are lower-precedence than any load paths passed in via the
  			{file:SASS_REFERENCE.md#load_paths-option `:load_paths` option}.
  			
  			If the `SASS_PATH` environment variable is set,
  			the initial value of `load_paths` will be initialized based on that.
  			The variable should be a colon-separated list of path names
  			(semicolon-separated on Windows).
  
  			Note that files on the global load path are never compiled to CSS
  			themselves, even if they aren't partials. They exist only to be imported.
  
  			@example
  			   Sass.load_paths().append(os.path.dirname(__file__ + '/sass'))
  			@return [list<str, sass.importers.Base>]
  		'''
		if not self._load_paths:
			self._load_paths = os.getenv('SASS_PATH','').split(';' if utils.is_windows() else ':')

		return self._load_paths

	def compile(self,contents,**options):
		''' Compile a Sass or SCSS string to CSS.
 			Defaults to SCSS.
  
  			@param contents [str] The contents of the Sass file.
  			@param **options options keyword arguments;
  			   see {file:SASS_REFERENCE.md#sass_options the Sass options documentation}
  			@raise [sass.SyntaxError] if there's an error in the document
  			@raise [Encoding::UndefinedConversionError] if the source encoding
  			   cannot be converted to UTF-8
  			@raise [ArgumentError] if the document uses an unknown encoding with `@charset`
  		'''
		if not options.has_key('syntax'):
			options['syntax'] = 'scss'

		return Engine(contents,**options).to_css()

	def compile_file(self,filename,*args,**options):
		''' Compile a file on disk to CSS. '''

		css_filename = args.pop(0)
		result = Engine.for_file(filename,**options).render()
		if css_filename:
			if not options.has_key('css_filename'):
				options['css_filename'] = css_filename
			with open(css_filename,'w') as f:
				f.write(result)
			return None
		else:
			return result
