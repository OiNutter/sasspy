import copy

from errors import SyntaxError
import utils
import scss
import tree

class CSS(object):

	def __init__(self,template,**options):
		if isinstance(template,file):
			template = template.read()

		self.options = copy.deepcopy(options)
		self.template = template

	def render(self,fmt = 'sass'):
		''' Converts the CSS template into Sass or SCSS code '''
		
		try:
			self.check_encoding()
			return getattr(self.build_tree,'to_%s'%fmt,lambda :'')(**self.options).strip() + "\n"
		except SyntaxError as err:
			err.modify_backtrace(filename=self.options['filename'] if self.options.has_key('filename') else '(css)')
			raise err

	def source_encoding(self):
		''' Returns the original encoding of the document '''

		self.check_encoding()
		return self.original_encoding

	def check_encoding(self):
		if self.checked_encoding:
			return

		self.checked_encoding = True
		def do(msg,line):
			raise SyntaxError(msg,line=line)

		self.template,self.original_encoding = utils.check_sass_encoding(self.template,callback=do)

	def build_tree(self):
		''' Parses the CSS tempalte and applies various transformations '''
		root = scss.Parser(self.template,self.options['filename'] if self.options.has_key('filename') else None).parse()

		root = self.parse_selectors(root)
		root = self.expand_commas(root)
		root = self.nest_seqs(root)
		root = self.parent_ref_rules(root)
		root = self.flatten_rules(root)
		root = self.bubble_subject(root)
		root = self.fold_commas(root)
		root = self.dump_selectors(root)
		return root

	def parse_selectors(self,root):

		for child in root.children:

			if isinstance(child,tree.DirectiveNode):
				continue

			if not isinstance(child,tree.RuleNode):
				continue

			parser = scss.CssParser(child.rule.first,child.filename,child.line)
			child.parsed_rules = parser.parse_selector()

		return root

	def expand_commas(self,root):
		''' Transform

				foo, bar, baz
					color: blue

			into

				foo
					color: blue
				bar
					color: blue
				baz
					color: blue

		'''
		


