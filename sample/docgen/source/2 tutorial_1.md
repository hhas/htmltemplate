# Tutorial 1: Generating a simple links page #

## About this tutorial ##

This tutorial shows how to create a simple links page that'll look something like this:

	  Site Map
	
	  • Home
	  • Products
	  • About
	

## 1. Define the static HTML document ##

Here is a simple, static HTML document:

	<html>
		<head>
			<title>TITLE</title>
		</head>
		<body>
			<ul>
				<li>
					<a href="#">LINK</a>
				</li>
			</ul>
		</body>
	</html>

The document contains two elements, `title` and `a`, whose content and/or attributes need to be modified, plus a third element, `li`, which needs to be repeated over a list of links.


## 2. Add compiler directives to the HTML ##

The `title`, `li`, and `a` elements need to be declared as dynamic nodes within the template object model. This is done by adding a custom `node` attribute to each element's opening tag. Each `node` attribute contains a simple `TYPE:NAME` directive that indicates how htmltemplate should parse it:

* An element that appears once should contain a Container (`con:NAME`) directive.
* An element that appears any number of times should contain a Repeater (`rep:NAME`) directive. 
* The `NAME` portion of the directive should be a valid Python identifier. This will be used to identify the node within its parent.

To declare the `title` element as a dynamic Container node named `title`, add a `node="con:title"` attribute to its tag. Similarly, to declare the `li` element as a dynamic Repeater node, add a `node="rep:item"` attribute. Declaring the `a` element as a Container node named `link` is left as an exercise.

Once the compiler directives have been added, the HTML document should look like this:

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


## 3. Create the template object model ##

Compiling the template is simple. Just create a new `Template` instance, passing it the HTML string:

	from htmltemplate import Template
	
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

htmltemplate will compile this HTML to the following template object model:

	template
	 |
	 |- con:title
	 |
	 |- rep:item
	 |   |
	 |   |- con:link


## 4. Check the template object model ##

The structure of the template object model can be checked during development and debugging by calling the `Template` object's `structure` method and printing its output:

	print(template.structure())

In this case, the `structure` method should return the following:

	tem:
		con:title
		rep:item
			con:link

Once the template's object model is confirmed correct, the `print` command can be removed or commented out.


## 4. Define the template controller functions ##

Both the Template and Repeater (`rep:item`) nodes require callback functions to control their rendering.

The main `render_template` callback function inserts text into the `title` element and generates a list of `li` items:

	def render_template(node, pagetitle, linkinfos):
		node.title.text = pagetitle
		node.item.repeat(render_item, linkinfos)

This function takes a _copy_ of the `Template` object as its first argument, followed by two user-supplied arguments containing the data to be inserted into the template:

	pagetitle : string -- the page title
	linkinfos : list of tuple -- a list of form [(URI, name),...]


The `repeat` method call in the `render_template` function takes a second callback function, `render_item`, to control the rendering of each `li` list item and its `a` element:

	def render_item(node, linkinfo):
		url, name = linkinfo
		node.link.atts['href'] = url
		node.link.text = name


## 5. Render the template ##

To render a page, call the `Template` object's `render` method, passing it the `render_template` callback function along with any data to be passed as additional arguments to `render_template`:

	title = "Site Map"
	links = [('index.html', 'Home'), 
	         ('products/index.html', 'Products'), 
	         ('about.html', 'About')]
	
	template.render(render_template, title, links)

When called with a controller callback function as its first argument, the `render` method automatically creates a _copy_ of the original `Template` object and all of its sub-nodes, then passes it to the callback function for manipulation. Once the callback function returns, the `render` method converts the modified template object model to HTML and returns the result.

Here's the result:

	<html>
		<head>
			<title>Site Map</title>
		</head>
		<body>
			<ul>
				<li>
					<a href="index.html">Home</a>
				</li>
	<li>
					<a href="products/index.html">Products</a>
				</li>
	<li>
					<a href="about.html">About</a>
				</li>
			</ul>
		</body>
	</html>

