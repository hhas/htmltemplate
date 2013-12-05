# Tutorial 2: Repeating groups of nodes #

## About this tutorial ##

When designing an HTML template, you'll sometimes need to insert additional HTML elements (typically `div` or `span`) to allow you to define template nodes in the proper locations. For example, given the data:

	sections = [('title 1', 'description 1'), 
	            ('title 2', 'description 2'), 
	            ('title 3', 'description 3')]

to generate a page like the following, you need to repeat the `h2` and `p` elements for each tuple in the list:

	<h2>title 1</h2>
	<p>description 1</p>

	<h2>title 2</h2>
	<p>description 2</p>

	<h2>title 3</h2>
	<p>description 3</p>

A common mistake for beginners is to write:

	<h2 node="rep:title">section title</h2>
	<p node="rep:desc">section description</p>

but this template generates the following output, which is not what you want:

	<h2>title 1</h2>
	<h2>title 2</h2>
	<h2>title 3</h2>
	<p>description 1</p>
	<p>description 2</p>
	<p>description 3</p>

The solution is to group the `h2` and `p` elements within a single Repeater node and repeat that.


## 1. Group the elements ##

Wrap the related `h2` and `p` elements in a generic `div` element:

	<div>
		<h2>section title</h2>
		<p>section description</p>
	</div>


## 2. Add a Repeater directive ##

Mark the `div` element as a Repeater (`rep`) node named `section` and the `h2` and `p` elements as Container (`con`) nodes:

	<div node="rep:section">
		<h2 node="con:title">section title</h2>
		<p node="con:desc">section description</p>
	</div>

Now wrap this HTML as a Python string and compile it into a `Template` object.


## 3. Implement the controller callback functions ##

Define a callback function named `render_section` that controls how the section information is inserted into the `rep:section` node's `con:title` and `con:desc` sub-nodes. This function should take a copy of the Repeater node as its first parameter and a `(title,description)` tuple as its second:

	def render_section(node, section):
		node.title.text, node.desc.text = section

Define a `render_template` function that takes a copy of the `Template` object as its first parameter and a list of `(title,description)` tuples as its second. It should then call the `rep:section` node's `repeat` method, passing it the `render_section` function and the list of section information tuples:
	
	def render_template(node, sections):
		node.section.repeat(render_section, sections)

Now add the code to call the `Template` object's `render` method, passing the `render_template` function and section data list as arguments, and print the result.


## 4. Render the template ##

Here is the completed tutorial script:

	from htmltemplate import Template

	template  = Template("""
	<div node="rep:section">
		<h2 node="con:title">section title</h2>
		<p node="con:desc">section description</p>
	</div>
	""")

	def render_section(node, section):
		node.title.text, node.desc.text = section
	
	def render_template(node, sections):
		node.section.repeat(render_section, sections)


	sections = [('title 1', 'description 1'), 
	            ('title 2', 'description 2'), 
	            ('title 3', 'description 3')]
	print(template.render(render_template, sections))


When rendered, this template will generate the following HTML:

	<div>
		<h2>title 1</h2>
		<p>description 1</p>
	</div>
	<div>
		<h2>title 2</h2>
		<p>description 2</p>
	</div>
	<div>
		<h2>title 3</h2>
		<p>description 3</p>
	<div>


## 5. Tidy the output ##

If the `<div>` and `</div>` tags serve no purpose in the rendered page, you can omit them by prefixing the `rep:section` directive with an 'omit tags' modifier (`-`):

	<div node="-rep:section">

Here's how the generated HTML now looks:

	
		<h2>title 1</h2>
		<p>description 1</p>
	

		<h2>title 2</h2>
		<p>description 2</p>
	

		<h2>title 3</h2>
		<p>description 3</p>
