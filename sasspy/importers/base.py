import ..utils

class Base(object):
	''' The abstract base class for Sass importers.
		All importers should inherit from this.

		At the most basic level, an importer is given a string
		and must return a {Sass::Engine} containing some Sass code.
		This string can be interpreted however the importer wants;
		however, subclasses are encouraged to use the URI format
		for pathnames.
		
		Importers that have some notion of "relative imports"
		should take a single load path in their constructor,
		and interpret paths as relative to that.
		They should also implement the \{#find\_relative} method.
		
		Importers should be serializable via `Marshal.dump`.
		In addition to the standard `_dump` and `_load` methods,
		importers can define `_before_dump`, `_after_dump`, `_around_dump`,
		and `_after_load` methods as per {Sass::Util#dump} and {Sass::Util#load}.
	'''

	def find_relative(self,uri,base,**options):
		''' Find a Sass file relative to another file.
			Importers without a notion of "relative paths"
			should just return nil here.
			
			If the importer does have a notion of "relative paths",
			it should ignore its load path during this method.
			
			See \{#find} for important information on how this method should behave.
			
			The `:filename` option passed to the returned {Sass::Engine}
			should be of a format that could be passed to \{#find}.
		'''
		utils.abstract(self)

	def find(self,uri,**options):
		''' Find a Sass file, if it exists.
			
			This is the primary entry point of the Importer.
			It corresponds directly to an `@import` statement in Sass.
			It should do three basic things:
			
				* Determine if the URI is in this importer's format.
					If not, return nil.
				* Determine if the file indicated by the URI actually exists and is readable.
					If not, return nil.
				* Read the file and place the contents in a {Sass::Engine}.
					Return that engine.

			If this importer's format allows for file extensions,
			it should treat them the same way as the default {Filesystem} importer.
			If the URI explicitly has a `.sass` or `.scss` filename,
			the importer should look for that exact file
			and import it as the syntax indicated.
			If it doesn't exist, the importer should return nil.
			
			If the URI doesn't have either of these extensions,
			the importer should look for files with the extensions.
			If no such files exist, it should return nil.
			
			The {Sass::Engine} to be returned should be passed `options`,
			with a few modifications. `:syntax` should be set appropriately,
			`:filename` should be set to `uri`,
			and `:importer` should be set to this importer.
		'''
		utils.abstract(self)

	def mtime(self,uri,**options):
		''' Returns the time the given Sass file was last modified.
			
			If the given file has been deleted or the time can't be accessed
			for some other reason, this should return nil.
		'''
		utils.abstract(self)

	def key(self,uri,**options):
		''' Get the cache key pair for the given Sass URI.
			The URI need not be checked for validity.
			
			The only strict requirement is that the returned pair of strings
			uniquely identify the file at the given URI.
			However, the first component generally corresponds roughly to the directory,
			and the second to the basename, of the URI.
			
			Note that keys must be unique *across importers*.
			Thus it's probably a good idea to include the importer name
			at the beginning of the first component.
		'''
		utils.abstract(self)

	def __str__(self):
		''' A string representation of the importer.
			Should be overridden by subclasses.

			This is used to help debugging,
			and should usually just show the load path encapsulated by this importer.
		'''
		utils.abstract(self)