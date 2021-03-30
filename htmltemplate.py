""" htmltemplate -- A simple, powerful HTML templating system for Python 3.

Copyright (C) 2007-2021 HAS

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""

# TO DO: from usability POV, it'd probably be better to treat sibling nodes with identical names as a single group node whose tags are all rendered using the same content; and require the use of 'del' directives to eliminate cosmetic placeholders

# TO DO: there is a Python gotcha when grafting nodes, e.g.:
#
#		subnode = node.subnode = sometemplate.somenode
#      subnode.repeat(...)
#
# The RH assignment doesn't return the value of node.subnode, which is actually a copy of somenode (RichContent.__setattr__ automatically copies on assignment to prevent the original being modified), but here the code also binds the original to a local var for 'convenience', so ends up modifying the original instead of the copy now bound to node; the result is that the new content is added to the original node so does not appear in the rendered output, but will appear in all future renderings (with additional copies of the data appended to the original somenode each time the above code runs, as `repeat` is additive, leading to many accidental duplications appearing in the rendered result). There isn't a way around this (even if Python assignment operations were standard right-associative operator expressions, which they're not, the RH assignment would still return the original somenode unless __setattr__ was able to return its own result for subsequent assignments to use, which Python doesn't support). Probably the only solution is to add a note to documentation so unwary users know not to fall into this gotcha, i.e. use:
#
#		node.subnode = sometemplate.somenode
#		node.subnode.repeat(...)
#
# or:
#
#		node.subnode = sometemplate.somenode
#		subnode = node.subnode
#      subnode.repeat(...)
#


import html, html.parser, keyword, re

__all__ = ['ParseError', 'Node', 'Template', 'encodeentity', 'decodeentity']


#####################################################################
# SUPPORT
#####################################################################


def _renderatts(atts):
	""" Used by Parser and Node classes to render tag attributes.
	
		atts : list of (str, str | None) -- zero or more key-value pairs (note: string values must be HTML-encoded)
		Result : str
	"""
	return ''.join(((' ' + name) if value is None else ' {}="{}"'.format(name, value)) for name, value in atts)

##

def encodeentity(s):
	""" Default encoder for HTML entities: replaces &, <, > and " characters only. """
	return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

decodeentity = html.unescape


#####################################################################
# TEMPLATE PARSER
#####################################################################


class ParseError(Exception):
	""" A template parsing error. """
	pass


class ElementCollector:
	""" Used by Parser to assemble individual HTML elements. """

	def __init__(self, *args):
		self.nodetype, self.nodename, self.tagname, self.atts, self.isempty, self.omittags, self.shoulddelete = args
		self.content = ['']
		self.elementnames = {}
		self.__depth = 1
	
	def incdepth(self):
		self.__depth += 1
		
	def decdepth(self):
		self.__depth -= 1
		
	def iscomplete(self):
		return self.__depth < 1
		
	def addtext(self, txt):
		self.content[-1] += txt
		
	def addelement(self, node, nodetype, nodename):
		self.content.extend([node, ''])
		self.elementnames[nodename] = nodetype


class Parser(html.parser.HTMLParser):
	""" Parses an HTML document, converting elements tagged with special 'node' attributes (e.g. node="con:foo") to template nodes. Called by Template.__init__(). 
	"""

	__specialattvaluepattern = re.compile('(-)?(con|rep|sep|del):(.*)')
	__validnodenamepattern = re.compile('[a-zA-Z][_a-zA-Z0-9]*')
	
	# List of words already used as property and method names, so cannot be used as template node names as well:
	__invalidnodenames = set(keyword.kwlist).union({'nodetype', 'nodename', 
			'text', 'html', 'atts', 'omittags', 'omit', 'add', 'repeat', 'copy', 'render', 'structure', 'separator'})
	
	##
	
	def __init__(self, attribute, encode, isxhtml):
		html.parser.HTMLParser.__init__(self)
		self.__specialattributename = attribute
		self._encode = encode
		self.__outputstack = [ElementCollector('tem', '', None, None, False, False, False)]
		self.__emptytagclose = ' />' if isxhtml else '>'
		self.__emptytagformat = '<{}{{}} />' if isxhtml else '<{}{{}}>'
	
	def __isspecialtag(self, atts, specialattname):
		for name, value in atts:
			if name == specialattname:
				value = self.__specialattvaluepattern.match(value)
				if value:
					atts = dict(atts)
					del atts[specialattname]
					omittags, nodetype, nodename = value.groups()
					return True, nodetype, nodename, omittags, atts
		return False, '', '', False, _renderatts(atts)
	
	def __starttag(self, tagname, atts, isempty):
		node = self.__outputstack[-1]
		if node.shoulddelete:
			isspecial = 0
		else:
			isspecial, nodetype, nodename, omittags, atts = self.__isspecialtag(atts, self. __specialattributename)
		if isspecial:
			if nodetype != 'del' and \
					(not self.__validnodenamepattern.match(nodename) or nodename in self.__invalidnodenames):
				raise ParseError("Invalid node name: {!r}".format(nodename))
			if nodename in node.elementnames and nodetype != 'sep':
				raise ParseError("Duplicate node name: {!r}.".format(nodename))
			self.__outputstack.append(
					ElementCollector(nodetype, nodename, tagname, atts, isempty, omittags, nodetype == 'del'))
		else:
			if node.tagname == tagname:
				node.incdepth()
			if not node.shoulddelete:
				node.addtext('<' + tagname + atts + (self.__emptytagclose if isempty else '>'))
	
	def __hascompletedelement(self, element, parent):
		content = [] if element.isempty else element.content
		if element.nodetype in ['con', 'rep']:
			node = _kNodeClasses[element.nodetype][min(len(content), 2)](
					element.nodename, element.tagname, element.atts, content, self.__emptytagformat, self._encode)
			if element.omittags:
				node.omittags()
			parent.addelement(node, element.nodetype, element.nodename)
		else: # element.nodetype == 'sep'
			# Add this separator to its repeater
			for node in parent.content[1::2]:
				if node._nodename == element.nodename:
					if node._nodetype != 'rep':
						raise ParseError("Can't process separator node 'sep:{}': repeater node 'rep:{}' wasn't found. Found node '{}:{}' instead.".format(element.nodename, element.nodename, element.nodetype, element.nodename))
					if element.omittags:
						node._sep = content[0] if content else ''
					elif content:
						node._sep = '<{}{}>{}</{}>'.format(
								element.tagname, _renderatts(element.atts), content[0], element.tagname)
					else:
						node._sep = '<{}{}{}'.format(element.tagname, _renderatts(element.atts), self.__emptytagclose)
					return
			raise ParseError(
					"Can't process separator node 'sep:{}' in node '{}:{}': repeater node 'rep:{}' wasn't found." 
					.format(element.nodename, parent.nodetype, parent.nodename, element.nodename))
	
	def __endtag(self, tagname, isempty):
		node = self.__outputstack[-1]
		if node.tagname == tagname:
			node.decdepth()
		if node.iscomplete():
			self.__outputstack.pop()
			if not node.shoulddelete:
				parent = self.__outputstack[-1]
				self.__hascompletedelement(node, parent)
		elif not isempty:
			node.addtext('</{}>'.format(tagname))

	def __addtext(self, txt):
		self.__outputstack[-1].addtext(txt)
	
	##
	
	def unescape(self, s):
		# Override HTMLParser.unescape() to prevent HTML entities in attributes being decoded during parsing; Attributes instances will encode/decode attribute entities as and when needed.
		return s
	
	# event handlers

	def handle_startendtag(self, tagname, atts):
		self.__starttag(tagname, atts, True)
		self.__endtag(tagname, True)

	def handle_starttag(self, tagname, atts):
		self.__starttag(tagname, atts, False)

	def handle_endtag(self, tagname):
		self.__endtag(tagname, False)

	def handle_charref(self, txt):
		self.__addtext('&#{};'.format(txt))

	def handle_entityref(self, txt):
		self.__addtext('&{};'.format(txt))

	def handle_data(self, txt):
		self.__addtext(txt)

	def handle_comment(self, txt):
		self.__addtext('<!--{}-->'.format(txt))

	def handle_decl(self, txt):
		self.__addtext('<!{}>'.format(txt))

	def handle_pi(self, txt):
		self.__addtext('<?{}?>'.format(txt))
	
	##
	
	def result(self):
		element = self.__outputstack.pop()
		if element.nodetype != 'tem':
			raise ParseError("Can't compile template: node '{}:{}' is not correctly closed."
					.format(element.nodetype, element.nodename))
		return element.content


#####################################################################
# OBJECT MODEL CLASSES
#####################################################################


class CloneNode:
	""" Used to clone existing nodes; cheaper and more precise than using Python's standard copy/deepcopy functions. """
	
	def __init__(self, node):
		self.__dict__ = node.__dict__.copy()
		self.__class__ = node.__class__


#####################################################################
# Abstract base classes


class Node:
	""" Abstract base class for all template nodes.
	
		Notes:
		
		- If implementing custom node classes, these must also inherit from Node otherwise RichContent.__setattr__ will raise a TypeError when the user tries to replace an existing node with the custom one.
	"""
	
	nodetype = property(lambda self:self._nodetype, doc="str -- The node's type (e.g. 'con').")
	nodename = property(lambda self:self._nodename, doc="str -- The node's name.")
	
	def __init__(self, nodename, encode):
		self._nodename, self._encode = nodename, encode
	
	def __repr__(self):
		return '<{} {}:{}>'.format(self.__class__.__name__, self._nodetype, self._nodename)
	
	def structure(self):
		""" Render the template's structure for diagnostic use.
		
			Result : str
		"""
		out = []
		def walk(node, indent, out):
			out.append(indent + node.nodetype + ':' + node.nodename)
			for subnode in node:
				walk(subnode, '\t' + indent, out)
		walk(self, '',out)
		return '\n'.join(out)
	
	def render(self, fn=None, *args, **kwargs):
		""" Render this node as text.
			
			fn : function | None -- if given, the node is copied and passed to the function to manipulate before being rendered; if None, the current node is rendered as-is
			*args : any -- any additional arguments to pass to the function (e.g. the data to insert)
			**kwargs : any -- any additional arguments to pass to the function
			Result : str -- the generated HTML
		"""
		if fn:
			self = self.copy()
			fn(self, *args, **kwargs)
		collector = []
		self._render(collector)
		return ''.join(collector)


class Container(Node):
	""" A Container node has a one-to-one relationship with the node that contains it. """
	
	_nodetype = 'con'
	
	def __init__(self, nodename, tagname, atts, emptytagformat, encode):
		Node.__init__(self, nodename, encode)
		self._atts = dict(atts) # Note: on cloning node, shallow copy this dict.
		if isinstance(self, NullContent):
			self.__starttag = emptytagformat.format(tagname)
			self.__endtag = ''
		else:
			self.__starttag = '<{}{{}}>'.format(tagname)
			self.__endtag = '</{}>'.format(tagname)
		self.__omittags = False
		self._omit = False
	
	def __len__(self):
		return int(not self._omit)
	
	def copy(self):
		""" Make a full copy of this node.
			
			Result : Container
		"""
		newnode = CloneNode(self) # performance optimisation
		newnode._atts = self._atts.copy()
		return newnode
	
	def _rendernode(self, collector):
		if self.__omittags:
			self._rendercontent(collector)
		else:
			collector.append(self.__starttag.format(_renderatts(self._atts.items())))
			self._rendercontent(collector)
			collector.append(self.__endtag)

	def _render(self, collector):
		if not self._omit:
			self._rendernode(collector)
	
	def __attsget(self):
		return Attributes(self._atts, self._encode)
	
	def __attsset(self, value):
		self._atts = {}
		atts = Attributes(self._atts, self._encode)
		for k, v in value.items():
			atts[k] = v
	
	atts = property(__attsget, __attsset, doc="Attributes -- the element's tag attributes")
	
	def omittags(self):
		"""Don't render this element's tag(s)."""
		self.__omittags = True
	
	def omit(self):
		"""Don't render this element."""
		self._omit = True


class Repeater(Container):
	"""A Repeater node has a one-to-many relationship with the node that
	   contains it.
	"""
	
	_nodetype = 'rep'
	
	def _setsep(self, s): self._sep = str(s)
	separator = property(lambda self: self._sep, _setsep)
	
	def __init__(self, nodename, tagname, atts, emptytagformat, encode):
		self._sep = '\n'
		self.__renderedcontent = [] # On cloning, shallow-copy this list.
		Container.__init__(self, nodename, tagname, atts,  emptytagformat, encode)
		
	_fastclone = Container.copy
	
	def __len__(self):
		return len(self.__renderedcontent) / 2
	
	def copy(self):
		""" Make a full copy of this node.
			
			Result : Repeater
		"""
		newnode = Container.copy(self)
		newnode.__renderedcontent = self.__renderedcontent[:]
		return newnode
	
	def _render(self, collector):
		if not self._omit:
			collector.extend(self.__renderedcontent[1:])
	
	def add(self, fn, *args, **kwargs):
		"""Render an instance of this node."""
		newnode = self._fastclone()
		fn(newnode, *args, **kwargs)
		if not newnode._omit:
			self.__renderedcontent.append(newnode._sep)
			newnode._rendernode(self.__renderedcontent)

	def repeat(self, fn, list, *args, **kwargs):
		"""Render an instance of this node for each item in list."""
		for item in list:
			self.add(fn, item, *args, **kwargs)


#######
# 'Mixin' classes used to manage nodes' content


class Content:
	""" Abstract base class. """
	
	def __iter__(self):
		def makegen():
			raise StopIteration
			yield None
		return makegen()


##

class NullContent(Content):
	""" Represents an empty HTML element's non-existent content. """
	
	def _rendercontent(self, collector):
		pass


class PlainContent(Content):
	""" Represents a non-empty HTML element's content where it contains plain text/markup only. """
	
	def __init__(self, content):
		self._html = content
		
	def _rendercontent(self, collector):
		# Called by Node classes to add HTML element's content.
		collector.append(self._html)
	
	def __settext(self, txt): 
		self._html = self._encode(str(txt))
	text = property(lambda self: decodeentity(self._html), __settext, 
			doc="str -- The element's content as plain text; HTML entities are automatically encoded/decoded.")
	
	
	def __sethtml(self, txt): 
		self._html = str(txt)
	html = property(lambda self: self._html, __sethtml, doc="str -- The element's content as raw HTML. Use with care.")

class RichContent(Content):
	""" Represents a non-empty HTML element's content where it contains other Container/Repeater nodes. """
	
	__nodesdict = {} # this declaration avoids infinite recursion between __setattr__ and __getattr__ during __init__
	
	def __init__(self, content):
		Content.__init__(self)
		self.__nodesdict = dict([(node._nodename, node) for node in content[1::2]]) # On cloning, replace with a new dict built from cloned self.__nodeslist.
		self.__nodeslist = content # On cloning, shallow copy this list then clone and replace each node in the list.
		
	def __iter__(self):
		def makegen():
			for i in range(1, len(self.__nodeslist), 2):
				yield self.__nodeslist[i]
			raise StopIteration
		return makegen()

	def _initrichclone(self, node):
		D = node.__nodesdict = {}
		L = node.__nodeslist = self.__nodeslist[:]
		for i in range(1, len(L), 2):
			D[L[i]._nodename] = L[i] = L[i].copy()
		return node
	
	def _rendercontent(self, collector):
		L = self.__nodeslist
		collector.append(L[0])
		for i in range(1, len(L), 2):
			L[i]._render(collector)
			collector.append(L[i + 1])
	
	def __getattr__(self, name):
		try:
			return self.__nodesdict[name]
		except KeyError as e: # Note: attempting to get 'text' or 'html' property will also raise error
			raise AttributeError("{}:{} node has no attribute {!r}.".format(self.nodetype, self.nodename, name)) from e
	
	def __setattr__(self, name, value):
		""" Replace a sub-node, or replace node's content. """
		if name in self.__nodesdict:
			if not isinstance(value, Node):
				# check user hasn't accidentally written 'node.foo="TEXT"' instead of 'node.foo.text="TEXT"'
				raise TypeError("Can't replace node '{}:{}': value isn't a Node object.".format(
						self.__nodesdict[name]._nodename, self.__nodesdict[name]._nodename))
			value = value.copy() 
			value._nodename = name
			idx = self.__nodeslist.index(self.__nodesdict[name])
			self.__nodesdict[name] = self.__nodeslist[idx] = value
		elif name == 'text':
			self.__nodeslist = [self._encode(str(value))]
			self.__nodesdict = {}
		elif name == 'html':
			self.__nodeslist = [str(value)]
			self.__nodesdict = {}
		else:
			self.__dict__[name] = value


#####################################################################
# Concrete classes
#
# The following classes are instantiated by Parser.__hascompletedelement(), which returns the appropriate node type for a given element according to its directive type ('con' or 'rep') and contents (empty, plain text/static markup only, or sub-nodes). Note that the user documentation glosses over these details for simplicity by omitting any mention of 'mixin' classes and pretending the class hierarchy is strictly single inheritance (Node<-Container<-Repeater). Only advanced users who wish to define their own custom node classes need know the full details.

class EmptyContainer(NullContent, Container):
	""" A single node with no content, e.g. <br node="con:foo" /> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		NullContent.__init__(self)
		Container.__init__(self, nodename, tagname, atts, emptytagformat, encode)


class PlainContainer(PlainContent, Container):
	""" A single node without sub-nodes, e.g. <p node="con:foo">Hello, <b>World</b>!<p> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		PlainContent.__init__(self, content[0])
		Container.__init__(self, nodename, tagname, atts, emptytagformat, encode)


class RichContainer(RichContent, Container):
	""" A single node with sub-nodes, e.g. <p node="con:foo">Hello, <b node="con:bar">NAME</b>!<p> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		RichContent.__init__(self, content)
		Container.__init__(self, nodename, tagname, atts, emptytagformat, encode)
		
	def copy(self):
		return self._initrichclone(Container.copy(self))

##

class EmptyRepeater(NullContent, Repeater):
	""" A repeatable node with no content, e.g. <br node="rep:foo" /> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		NullContent.__init__(self)
		Repeater.__init__(self, nodename, tagname, atts, emptytagformat, encode)


class PlainRepeater(PlainContent, Repeater):
	""" A repeatable node without sub-nodes, e.g. <p node="rep:foo">Hello, <b>World</b>!<p> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		PlainContent.__init__(self, content[0])
		Repeater.__init__(self, nodename, tagname, atts, emptytagformat, encode)


class RichRepeater(RichContent, Repeater):
	""" A repeatable node with sub-nodes, e.g. <p node="con:foo">Hello, <b node="con:bar">NAME</b>!<p> """
	
	def __init__(self, nodename, tagname, atts, content, emptytagformat, encode):
		RichContent.__init__(self, content)
		Repeater.__init__(self, nodename, tagname, atts, emptytagformat, encode)
		
	def copy(self):
		return self._initrichclone(Repeater.copy(self))
		
	def _fastclone(self): # performance optimisation
		return self._initrichclone(Repeater._fastclone(self))

##

_kNodeClasses = {
		'con': [EmptyContainer, PlainContainer, RichContainer],
		'rep': [EmptyRepeater, PlainRepeater, RichRepeater]}


#######


class Attributes:
	"""Public facade for modifying a node's tag attributes."""
	
	__attnamepattern = re.compile('^[a-zA-Z_][-.:a-zA-Z_0-9]*$')
	
	def __init__(self, atts, encode):
		self.__atts, self._encode = atts, encode
	
	def __getitem__(self, name):
		return decodeentity(self.__atts[name])
		
	def __setitem__(self, name, val):
		try:
			# Note: the next line will fail if the name is not a string; this will be caught and reported below.
			if not self.__attnamepattern.match(name): 
				raise ValueError("Bad attribute name.")
			if isinstance(val, str):
				val = self._encode(val)
			elif val is not None:
				raise TypeError("Bad attribute value (not a string or None): {!r}".format(val))
			self.__atts[name] = val
		except Exception as e:
			msg = str(e) if isinstance(name, str) else "Bad attribute name (not a string)."
			raise e.__class__("Can't set tag attribute {!r}: {}".format(name, msg)) from e
		
	def __delitem__(self, name):
		del self.__atts[name]
	
	def __repr__(self):
		return '<Attributes [{}]>'.format(_renderatts(self.__atts.items())[1:])
	
	def keys(self):
		return self.__atts.keys()
	
	def values(self):
		return [decodeentity(v) for v in self.__atts.values()]
	
	def items(self):
		return [(k, decodeentity(v)) for v in self.__atts.items()]
	
	def __len__(self):
		return len(self.__atts)


#####################################################################
# MAIN
#####################################################################


class Template(RichContent, Node):
	""" An HTML template object model. """
	
	_nodetype = 'tem'
	
	def __init__(self, html, isxhtml=True, attribute='node', encodefn=encodeentity):
		"""
			html : str -- the template HTML
			isxhtml : bool -- if True, trailing slash will be preserved in empty tags (e.g. '<br />'); if False, it will be removed (e.g. '<br>')
			attribute : str -- name of the tag attribute used to hold compiler directives
			encodefn : function -- the function used to encode HTML entities; if omitted, the &, <, > and " characters will be encoded by default
			
			Notes:
			
			- The default encodeentity function is suitable for use in generating UTF8-encoded HTML documents. If generating HTML documents in other encodings (e.g. ISO-8859-1), client should pass a suitable encoder function that takes a string as input and returns a string with reserved and unsupported characters encoded as HTML entities.
			
			Caution:
			
			- If a custom encodeentity function is used, it must always encode the reserved &, < and " characters, otherwise the generated HTML will be malformed.
		"""
		parser = Parser(attribute, encodefn, isxhtml)
		parser.feed(html)
		parser.close()
		Node.__init__(self, '', encodefn)
		RichContent.__init__(self, parser.result())
	
	# Allow Template nodes to replace Container/Repeater nodes
	_render = RichContent._rendercontent
	
	def copy(self):
		""" Make a full copy of this node. 
			
			Result : Template
		"""
		return self._initrichclone(CloneNode(self)) # performance optimisation

