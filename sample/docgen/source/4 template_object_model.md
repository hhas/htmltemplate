# Understanding the template object model #

## About the TOM ##

htmltemplate's  template object model ('TOM') is similar in concept to the Document Object Model found in web browsers, in that both parse an HTML document into a hierarchical tree structure which can then be manipulated via a programmatic API. However, while the DOM implements a large, complex API allowing general manipulation of every element in the document, the TOM provides a very small, simple, callback-based API for performing templating-specific operations on selected elements only.

A template object model is constructed from three classes: `Template`, `Container` and `Repeater`. The `Template` object is the template object model's root node, representing the complete HTML document. Each Container and Repeater node describes an element within the template HTML whose content and/or attributes can be dynamically manipulated by Python code. 

Each Container node has a one-to-one relationship with its parent node, i.e. it will appear only once in a rendered document. Each Repeater node has a one-to-many relationship with its parent, i.e. it will appear zero or more times in the output. The Template node can contain any number of Container and/or Repeater sub-nodes, each of which may contain its own sub-nodes, and so on. 


## The `Template` node ##

As well as representing the template object model's root, the `Template` class is also responsible for parsing an HTML template whenever its `__init__` method is called. For example, [Tutorial 1](tutorial_1.html) used the following code to create a template object model from an HTML template string:

	template = Template("""
	<html>
		<head>
			<title node="con:title">TITLE</title>
		</head>
		<body>
			<ul>
				<li node="rep:item">
					<a href="#" node="con:link">LINK</a>
				</li>
			</ul>
		</body>
	</html>
	""")

Each time the template parser encounters a special 'node' attribute containing a `con` or `rep` directive, it creates the corresponding `Container` or `Repeater` object at the appropriate point in the template object model.

Once the template HTML is successfully parsed, the resulting `Template` object can be used to generate any number of HTML documents. The simplest way to generate an HTML document is by calling `Template.render()`, passing a callback function as its first argument, followed by any data the function might need such as the values to be inserted:

	title = "Site Map"
	links = [('index.html', 'Home'), ('products/index.html', 'Products'), ('about.html', 'About')]

	template.render(render_template, title, links)

This 'controller' function should contain the code responsible for manipulating the Template node's immediate sub-nodes – inserting content, setting tag attributes, deleting unwanted nodes, and so on. For example, the following `render_template` function sets the content of the Container sub-node named `title` and tells the Repeater sub-node named `item` to render copies of itself using the given list:

	def render_template(node, pagetitle, linkinfos):
		node.title.text = pagetitle
		node.item.repeat(render_item, linkinfos)

Before calling the controller function, the `render` method first creates a full copy of the original template object model, and it is this copy which is passed to the function to manipulate. Since the original `Template` object is not modified, it can be reused as many times you like without the need to re-parse it each time.

Once the controller function has finished its work, the `render` method converts the modified object model back to HTML and returns the result.

(Note that while this all-in-one approach is the easiest way to generate documents, htmltemplate also allows you to perform each step separately should you need to customize the copy, manipulate, and/or render operations. See the 'Fine-tuning the rendering process' section in the Notes chapter for details.)


## `Container` nodes ##

A Container node represents a modifiable HTML element that will normally appear once in the finished page, e.g.:

	<title node="con:title">TITLE</title>

The HTML element may be empty (e.g. `<br/>`) in which case it has no content and only its tag attributes are modifiable, or non-empty (e.g. `<p>...</p>`) in which case it may contain either modifiable content (plain text/markup) or other Container and/or Repeater nodes.

Container nodes can be manipulated in various ways:

* If the node contains one or more subnodes, these will appear as properties. For example, the above example defines a node named 'title' at the top level of the template which will appear as the `Template.title` property.
* If the node contains plain text and/or static markup only, this can be retrieved or replaced using the node's `text` and `html` properties. For example, the following line replaces the 'title' node's original content with new text:

		node.title.text = pagetitle
	
* The node's tag attributes can be accessed via its `atts` property, which contains a dict-like `Attributes` object. For example, following line sets the 'link' node's `href` attribute:

		node.link.atts['href'] = url

* If the node is no longer required, calling its `omit` method will prevent it appearing in the rendered output. If only the node's content is required, calling the node's `omittags` method will prevent its tags appearing in the rendered output.

See the [Class definitions](class_definitions.html) chapter for a full list of available properties and methods.



## `Repeater` nodes ##

A Repeater node is similar to a Container node, except that it can appear any number of times in the finished page:

	<li node="rep:item">...</li>

Repeater objects support all of the properties and methods provided by Container nodes, plus two additional methods, `repeat` and `add`. Unlike a Container node, which appears by default in the rendered output, a Repeater node will not appear at all unless its `add` or `repeat` method is called. 

The `add` method works a lot like the main `render` method in that its first argument is a 'controller' callback function that is responsible for manipulating a copy of the original node: inserting content, modifying tag attributes, manipulating its sub-nodes, and so on. Any values to be used by the callback function can be passed as additional arguments. Unlike `render`, however, the `add` method does not return the rendered HTML but instead stores it within the original Repeater node. Each time `add` is called, another copy of the Repeater node is copied, manipulated, rendered and stored. For example, [Tutorial 1](tutorial_1.html)'s main `render_template` controller function could be implemented like so:

	def render_template(node, pagetitle, linkinfos):
		node.title.text = pagetitle
		for linkinfo in linkinfos:
			node.item.add(render_item, linkinfo)

While the `add` method provides flexibility, the `repeat` method supports a more streamlined approach in the most common use case: iterating over a single list. As with `add`, the `repeat` method's first argument is a controller function. This should be followed by a second argument, which is the list to iterate over. Any subsequent arguments will be forwarded to the callback function as before. Thus the above `render_template` function can be more concisely written as:

	def render_template(node, pagetitle, linkinfos):
		node.title.text = pagetitle
		node.item.repeat(render_item, linkinfos)

The `repeat` method will iterate over the given list, cloning the original Repeater node and passing the copy to the controller function to manipulate, once for each item in the list. If a particular iteration is not needed, the controller function can call the cloned node's `omit` method before it returns. The parent controller function can also call the original Repeater node's `omit` method to omit _all_ iterations. The following example demonstrates how to do both:
	
	<ul>
		<li node="rep:item">ITEM</li>
	</ul>

	def render_item(node, value):
		if value:
			node.text = value
		else:
			node.omit() # omit just this instance of the 'item' node
	
	def render_template(node, values, isvisible):
		if isvisible:
			node.item.repeat(render_item, values)
		else:
			node.item.omit() # omit all instances of the 'item' node


## Notes ##

Like the `Template` class, `Container` and `Repeater` classes also support a `render` method that renders either a copy or the original depending on whether or not a controller function is passed as an argument. While not often needed, this can be useful if you need to render just that portion of the template.

Nodes support a number of introspection-related features:

* Each node provides read-only `nodetype` and `nodename` properties containing the directive type and node name specified in the original HTML template.
* Each node implements a `structure` method which returns a string describing the template object model's hierarchy for debugging purposes.
* All nodes implement the standard `__iter__` method, allowing their subnodes to be recursively iterated over for (e.g.) introspection purposes.
* Container and Repeater nodes also implement the standard `__len__` method which indicates how many times the node will appear in the rendered output.



