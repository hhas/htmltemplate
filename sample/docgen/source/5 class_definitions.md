# Class definitions #

## Overview ##

htmltemplate defines the following class hierarchy:

	Node
	 |
	 |- Container
	 |   |
	 |   |- Repeater
	 |
	 |- Template
	
	Attributes
	
	ParseError

These classes are documented below.


## `Node` ##

This abstract base class is subclassed by the `Template`, `Container` and `Repeater` classes from which the template object model is constructed. Each node in the object model contains zero or more named properties corresponding to the node directives declared in the original HTML template.

	Node -- Abstract base class
	
		nodetype : str (r/o) -- the node's type ('con', 'rep' or 'tem')

		nodename : str (r/o) -- the node's name

		«NAME» : Node -- a sub-node, as declared by a compiler directive in the 
						 template HTML, where «NAME» is the sub-node's name. 
						 A node may contain zero or more Container and/or
						 Repeater sub-nodes.
		
		__iter__() -- can be used to iterate over a node's sub-nodes (e.g. for
		              introspection purposes) [1]
			Result : generator
		
		structure() -- output the hierarchical structure of this node and
					   its sub-nodes for diagnostic purposes
			Result : str

		copy() -- duplicate this node (including any sub-nodes)
			Result : Node -- a new Container/Repeater/Template object

		render(fn, *args, **kwargs) -- render this node as HTML
			fn : function | None -- the controller function responsible for
									inserting content into the node [2]
			*args : any -- extra values to pass to the controller function
			**kwargs : any -- extra values to pass to the controller function
			Result : str -- the generated HTML


`[1]` See the `demo7_simple_interpolation.py` script in the `sample` folder for a demonstration of use.


`[2]` The `render` method's first argument is normally a controller function that takes the following arguments:

    node : Node -- a copy of this node to manipulate
    *args : any -- extra  values that were passed to the 'render' method
    **kwargs : any -- extra  values that were passed to the 'render' method

If given, the `render` method will pass a _copy_ of the node to the function to manipulate, then render it as an HTML string. Otherwise, if `None`, the `render` method will render the original node as HTML.



## `Container` ##

`Container` objects represent HTML elements whose content can be manipulated by controller code. A Container node is rendered once, unless its `omit` method is called, in which case it won't appear at all. The HTML template can declare a Container node using the `con` directive (e.g. `<h1 node="con:title">`).

	Container(Node) -- A mutable HTML element ('con')
    
        atts : Attributes -- a dict-like object representing the element's 
                             tag attributes

        text : str -- the element's content as plain text. HTML entities are
                      automatically encoded/decoded. [1][2]

        html : str -- the element's content as raw HTML. Unlike the `text`
                      property, HTML entities are not encoded/decoded 
                      automatically. [1][3]

        __len__() -- returns 0 if this node is omitted, else 1
            Result : int

        omit() -- don't render this node

        omittags() -- don't render this node's tags, only its content

`[1]` If the node is derived from an empty HTML element (e.g. `<hr node="..."/>`), setting its `text` or `html` property has no effect. If the node is derived from an non-empty HTML element (e.g. `<p node="...">...</p>`), setting these properties replaces any existing content with the given text or HTML (if the node contains any sub-nodes, these will be deleted). Note that non-string values will be automatically cast to `str`.

`[2]` By default, HTML entities are encoded using the `htmltemplate` module's `encodeentity` function which encodes the `&`, `<`, `>` and `"` characters only, unless an alternate encoder function was specified in `Template.__init__()`.

`[3]` The `html` property should only be used when getting/setting the node's content as raw HTML markup, otherwise the `text` property should be used. When setting the `html` property, it is the user's responsibility to sanitize the new content as appropriate (escaping reserved `&`, `<`, `>`, `"` characters, stripping inappropriate tags, checking for malicious code, etc.) to ensure injection attacks, malform HTML output, etc. are avoided.


## `Repeater` ##

`Repeater` objects are containers that can appear any number of times in the rendered output. The HTML template can declare a Repeater node using the `rep` directive (e.g. `node="rep:list_item"`).

	Repeater(Container) -- A mutable, repeatable HTML element ('rep')
    
        __len__() -- the number of times this node has already been repeated
                     (omitted instances are ignored)
            Result : int

        add(fn, *args, **kwargs) -- render a copy of this node
		    fn : function -- the controller function responsible for inserting
			                 content into the node [1]
			*args : any -- extra values to pass to the controller function
			**kwargs : any -- extra values to pass to the controller function

        repeat(fn, sequence, *args, **kwargs) -- render a copy of this node for 
                                                 each item in the given list
		    fn : function -- the controller function responsible for inserting
			                 content into a copy of this node [2]
            sequence : any -- a list, generator, or other iterable collection
			*args : any -- extra values to pass to the controller function
			**kwargs : any -- extra values to pass to the controller function


`[1]` The `add` method's first argument is a controller function that accepts the following arguments:

    node : Repeater -- a copy of this node to manipulate
    *args : any -- extra  values that were passed to the 'add' method
    **kwargs : any -- extra  values that were passed to the 'add' method


`[2]` The `repeat` method's first argument is a controller function that accepts the following arguments:

    node : Repeater -- a copy of this node to manipulate
    item : any -- an item from the sequence being iterated
    *args : any -- extra  values that were passed to the 'repeat' method
    **kwargs : any -- extra  values that were passed to the 'repeat' method


## `Template` ##

The `Template` object is the top-level node in a template object model. This represents the complete HTML template document and can contain any number of `Container` and/or `Repeater` sub-nodes.

	Template(Node) -- The top-level template node ('tem')
    
        __init__(html, isxhtml=True, attribute='node', encodefn=encodeentity)
            html : str -- the HTML template
            isxhtml : bool -- if True, trailing slash will be preserved in 
                              empty tags (e.g. '<br />'); if False, it will 
                              be removed (e.g. '<br>')
            attribute : str -- the name of the attribute used to hold
                               compiler directives
            encodefn : function -- the function used to encode HTML entities 
                                   when setting sub-nodes' text content and 
                                   attribute values [1]


`[1]` The default `encodeentity` function is suitable for use in generating UTF8-encoded HTML documents. If generating HTML documents in other encodings (e.g. ISO-8859-1), client should pass a suitable encoder function that takes a string as input and returns a string with reserved and unsupported characters encoded as HTML entities. Note that this function *must* at the very least encode the reserved `&`, `<` and `"` characters, otherwise the generated HTML will be susceptible to injection attacks and almost certainly malformed or invalid.


## `Attributes` ##

`Attributes` instances are used by `Container` and `Repeater` objects to represent their tag attributes. The `Attributes` class defines a simple dict-like interface that supports getting, setting and deleting attributes by name. For example, to set the `href` attribute of an `<a>` tag:

	node.atts["href"] = "foo.html"
	
Note that any HTML entities in the attribute's value will be encoded/decoded automatically.


	Attributes -- A dict-like object containing an HTML tag's attributes
		
		__getitem__(name) -- get an attribute
			name : str -- the attribute's name
			Result : str | None -- the attribute's value, if it has one
	
		__setitem__(name, value) -- set an attribute
			name : str -- the attribute's name [1]
			value : str | None -- the attribute's value, if it has one [2][3]
	
		__delitem__(name) -- delete an attribute
			name : str -- the attribute's name
	
		keys() -- get all attribute names
			Result : generator

		values() -- get all attribute values
			Result : generator

		items() -- get all attributes as (name,value) tuples
			Result : generator



`[1]` The attribute's name must match the pattern `^[a-zA-Z_][-.:a-zA-Z_0-9]*$`. While this does not detect all invalid attribute names, it will prevent obviously incorrect or possibly malicious strings being inserted.

`[2]` Any reserved characters in the attribute's new value will be automatically encoded as HTML entities. (By default, this is performed by the `htmltemplate` module's `encodeentity` function which encodes the `&`, `<`, `>` and `"` characters only, unless an alternate encoder function was specified in `Template.__init__()`.) The user is responsible for performing any additional escaping/encoding that attribute values might require; for example, to URL-encode strings before inserting them into `src` and `href` attributes.

`[3]` If the attribute's value is `None`, only the attribute's name is inserted into the tag, allowing the miminized form of Boolean attributes – for example, `<option selected>` instead of `<option selected="selected">` – to be used if required for (e.g.) compatibility with older browsers.


## `ParseError` ##

In the event that `Template.__init__()` is unable to parse the supplied HTML template string (e.g. due to malformed markup), a `ParseError` exception will be raised.

	ParseError(Exception) -- A template parsing error


