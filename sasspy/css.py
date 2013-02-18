import copy

from errors import SyntaxError
import utils
import scss
import tree
import selector

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
				self.parse_selectors(child)
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
		children = []
		for child in root.children:
			if not isinstance(child,tree.RuleNode) and not child.parsed_rules.members.size > 1:
				if isinstance(child,tree.DirectiveNode):
					child = self.expand_commas(child)
				
				children.append(child)
				continue

			members = []
			for seq in child.parsed_rules.members:
				node = tree.RuleNode([])
				node.parsed_rules = self.make_cseq(seq)
				node.children = child.children
				node.append(members)
			children.append(members)

		root.children = utils.flatten(children)
		return root

	def nest_seqs(self,root):
		''' Make rules use nesting so that

				foo
					color: green
				foo bar
					color: red
				foo baz
					color: blue

			becomes

				foo
					color: green
					bar
						color: red
					baz
						color: blue
		'''

		current_rule = None

		children = []
		for child in root.children:
			if not isinstance(child,tree.RuleNode):
				if isinstance(child,tree.DirectiveNode):
					child = self.nest_seqs(child)
				
				children.append(child)
				continue

			seq = self.first_seq(child)
			seq.members[:] = [m for m in seq.members if m != "\n"]
			first, rest = seq.members[0],seq.members[1:]

			if not current_rule or self.first_sseq(current_rule) != first:
				current_rule = tree.RuleNode([])
				current_rule.parsed_rules = self.make_seq(first)

			if rest:
				child.parsed_rules = self.make_seq(*rest)
				current_rule += child
			else:
				current_rule.children += child.children

			children.append(current_rule)

			root.children[:] = [c for c in children if c is not None]
			root.children = list(set(root.children))

			for v in root.children:
				self.nest_seqs(v)

			return root

	def parent_ref_rules(self,root):
		''' Make rules use parent refs so that

				foo
					color: green
				foo.bar
					color: blue

			becomes

				foo
					color: green
					&.bar
						color: blue
		'''

		current_rule = None
		
		children = []
		for child in root.children:
			if not isinstance(child,tree.RuleNode):
				if isinstance(child,tree.DirectiveNode):
					child = self.parent_ref_rules(child)

				children.append(child)
				continue

			sseq = self.first_sseq(child)
			if not isinstance(sseq,selector.SimpleSequence):
				children.append(child)
				continue

			firsts,rest = [sseq.members[0]],sseq.members[1:]
			if isinstance(firsts[0],selector.Parent):
				firsts.append(rest.pop(0))

			last_simple_subject = rest == [] and sseq.is_subject()
			if not current_rule or self.first_sseq(current_rule).members != firsts or (not not self.first_sseq(current_rule).is_subject()) != (not not last_simple_subject):
				current_rule = tree.RuleNode([])
				current_rule.parsed_rules = self.make_sseq(last_simple_subject, *firsts)

			if rest:
				rest.insert(0,selector.Parent())
				child.parsed_rules = self.make_sseq(sseq.is_subject(),*rest)
				current_rule += child
			else:
				current_rule.children += child.children

			children.append(current_rule)

		root.children[:] = [c for c in children if c is not None]
		root.children = list(set(root.children))

		for v in root.children:
			self.parent_ref_rules(v)

		return root

	def flatten_rules(self,root):
		''' Flatten rules so that

				foo
					bar
						color: red

			becomes

				foo bar
					color: red

			and

				foo
					&.bar
						color: blue

			becomes

				foo.bar
					color: blue

		'''

		for child in root.children:

			if isinstance(child,tree.RuleNode):
				child = self.flatten_rule(child)
			elif isinstance(child,tree.DirectiveNode):
				child = self.flatten_rules(child)

		return root

	def flatten_rule(self,rule):
		''' Flattens a single rule '''

		while len(rule.children) == 1 and isinstance(rule.children[0],tree.RuleNode):
			child = rule.children[0]

			if isinstance(self.first_simple_sel(child),selector.Parent):
				rule.parsed_rules = child.parsed_rules.resolve_parent_refs(rule.parsed_rules)
			else:
				rule.parsed_rules = self.make_seq(*(self.first_seq(rule).members + self.first_seq(child).members))

			rule.children = child.children

		return self.flatten_rules(rule)

	def bubble_subject(self,root):

		for child in root.children:
			if isinstance(child,tree.RuleNode) or isinstance(child,tree.DirectiveNode):
				self.bubble_subject(child)

				if not isinstance(child,tree.RuleNode):
					continue

				match = True
				for c in child.children:
					if not isinstance(c,tree.RuleNode):
						continue

					if not (isinstance(self.first_simple_sel(c),selector.Parent) and self.first_sseq(c).is_subject()):
						match = False

				if not match:
					continue

				self.first_sseq(child).subject = True
				for c in child.children:
					self.first_sseq(c).subject = False


	def fold_commas(self,root):
		''' Transform

				foo
					bar
						color: blue
					baz
						color: blue

			into

				foo
					bar, baz
						color:blue

		'''

		prev_rule = None

		children = []
		for child in root.children:
			if not isinstance(child,tree.RuleNode):
				if isinstance(child,tree.DirectiveNode):
					child = self.fold_commas(child)

				children.append(child)
				continue

			if prev_rule and prev_rule.children == child.children:
				prev_rule.parsed_rules.members += self.first_seq(child)
				continue

			child = self.fold_commas(child)
			prev_rule = child
			children.append(child)

		root.children[:] = [c for c in children if c is not None]

		return root

	def dump_selectors(self,root):
		''' Dump all the parsed <tree.RuleNode> selectors to strings '''

		for child in root.children:
			if isinstance(child, tree.DirectiveNode):
				child = self.dump_selectors(child)
				continue

			if not isinstance(child,tree.RuleNode):
				continue

			child.rule = [str(child.parsed_rules)[1:-1]]
			child = self.dump_selectors(child)

		return root

	def make_cseq(self,*seqs):
		''' Create a <selector.CommaSequence> '''
		return selector.CommaSequence(seqs)

	def make_seq(self,*sseqs):
		''' Create a <selector.CommaSequence> containing only a single <selector.Sequence> '''
		return self.make_cseq(selector.Sequence(sseqs))

	def make_sseq(self,subject,*sseqs):
		''' Create a <selector.CommaSequence> containing only a single
			<selector.Sequence> which in turn only contains a single 
			<selector.SimpleSequence>
		'''
		return self.make_seq(selector.SimpleSequence(sseqs,subject))

	def first_seq(self,rule):
		''' Return the first <selector.Sequence> in a <tree.RuleNode> '''
		return rule.parsed_rules.members[0] if rule.parsed_rules.members else None

	def first_sseq(self,rule):
		'''Return the first <selector.SimpleSequence> in a <tree.RuleNode> '''
		seq = self.first_seq(rule)
		return seq.members[0] if seq.members else None

	def first_simple_self(self,rule):
		''' Return the first <selector.Simple> in a <tree.RuleNode>
			unless the rule begins with a combinator
		'''
		sseq = self.first_sseq(rule)
		if isinstance(sseq,selector.SimpleSequence):
			return sseq.members[0] if sseq.members else None
		
		return None