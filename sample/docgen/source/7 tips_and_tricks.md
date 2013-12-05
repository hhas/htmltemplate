# Tips and tricks #

## Avoid naming conflicts between nodes ##

If two or more nodes have the same name, as long as each has a different parent they will all appear within the template object model independent of one other. For example, the following template defines three different nodes all named 'link':

	<p><a node="con:link">LINK</a></p>

	<ul node="-con:navbar">
		<li node="rep:link"><a node="con:link">LINK</a></li>
	</ul>

While this may result in some confusing-looking controller code, it is a valid HTML template and will parse without problem.

However, if two or more identically named nodes have the same parent then a `ParseError` will occur as sibling nodes can never share the same name. For example, the following template markup will be rejected as it contains three sibling nodes all named 'item':

	<ul>
		<li node="rep:item">ITEM</li>
		<li node="rep:item">ITEM</li>
		<li node="rep:item">ITEM</li>
	</ul>

If the duplicate elements have been included solely for preview purposes, just add Deleted (`del`) directives to each one to prevent them appearing in either the template object model or the rendered output:

	<ul>
		<li node="rep:item">ITEM</li>
		<li node="del:">ITEM</li>
		<li node="del:">ITEM</li>
	</ul>

The following template will also be rejected as it contains two sibling nodes both named 'title':

	<html>
		<head>
			...
			<title node="con:title">TITLE</title>
			
		</head>
		<body>

			<h1 node="con:title">TITLE</title>
			...
		</body>
	</html>

Since the `title` and `h1` elements should both appear in the rendered output, you will have to rename one or both to avoid confusion (remember to update the corresponding controller code as well):


	<html>
		<head>
			...
			<title node="con:title1">TITLE</title>
			
		</head>
		<body>

			<h1 node="con:title2">TITLE</title>
			...
		</body>
	</html>

		
This restriction does not apply to Separators, of course, since a `sep` directive does not create a new node but merely indicates a section of markup that should appear between repeated instances of an existing Repeater node. In fact, a `ParseError` will occur if the Separator's name does _not_ exactly match the name of a preceding Repeater node. For example, this Separator is valid:

	<a node="rep:link">LINK</a> <span node="-sep:link">/</a>
	
but these are not:

	<a node="rep:link1">LINK</a> <span node="-sep:link2">/</a>

	<span node="-sep:link">/</a> <a node="rep:link">LINK</a>



## Modifing part of a node's content ##

There may be times when you want modify only part of an element's content, for example, to replace just the `[NAME]` part of `<title>About [NAME]</title>`. There are a couple of ways to do this.

One solution is to wrap the part of the element's content you want to modify in a `span` element and add a `con` directive to that:

	<title>About <span node="-con:name">[NAME]</span></title>

While this particular template may not be standards-compilant HTML, as long as the `con` directive is prefixed an 'omit tags' modifier (`-con:...`), the `<span>` and `</span>` tags will be omitted when the template is rendered, ensuring valid output.

The other option is to add a `con` directive to the `<title>` element, then modify the node's existing content using (e.g.) Python's standard string substitution mechanism: 

	<title node="con:title">About {name}</title>
    
    node.title.text = node.title.text.format(name=somevalue)

If you need to preserve existing HTML tags within the original and/or new content, you will have to use the `html` property instead of the `text` property, so take care to ensure any new data is properly sanitized before insertion. For example:

	<h1 node="con:title"><em>About</em> {name}</h1>
	
	name = 'Smith & Jones'
    node.content.html = node.content.html.format(name=encodeentity(name))

will ensure any reserved characters (`&`, `<`, `>`, `"`) are properly escaped as HTML entities:

	<h1><em>About</em> Smith &amp; Jones</h1>

htmltemplate's `encodeentity` function is sufficient to replace reserved characters with their HTML entity equivalents, though if your data requires heavier sanitation (e.g. to remove ASCII control characters or to strip `<script>` tags from untrusted HTML strings) you will have to implement this yourself.


##  Modifying vs replacing nodes ##

When setting a node's content, take care to write:

	node.foo.text = somevalue

or:

	node.foo.html = somevalue

These assignments will replace the node's content to a new plain text or HTML string, which is usually what you want.

If you omit the `text`/`html` property name and write the following instead, this does not replace the node's content but instead replaces the node itself:

	node.foo = somevalue

This feature can be useful if you wish to reuse a previously rendered node or replace part of one template's object model with part or all of another (component-based templating). For example, the `docgen.py` script contains two navigation bars at the top and bottom of the page. Rather than render the same information twice, the template's controller function renders the `topnav` node then grafts it over the unrendered `bottomnav` node as well:

	def render_page(node, title, heading, content, navlinks):
		...
		node.topnav.link.repeat(page_navlink, navlinks)
		node.bottomnav = node.topnav

Note that the new value _must_ be a subclass of `Node` (i.e. `Container`, `Repeater`, `Template` or a third-party subclass), otherwise a `TypeError` will be raised. (This helps to catch errors where the `text`/`html` property name is omitted by accident.)


## Customizing the rendering process ##

Copying a `Template` object before manipulating and rendering the copy allows the original object to be reused any number of times. While not essential, this is more efficient than re-compiling the template HTML every time. The simplest way to do this is by passing a callback function as the `Template.render()` method's first argument: the `render` method will automatically copy the original `Template` object and pass it to the controller function to manipulate before rendering the result. 

If greater flexibility is required, each of these steps – copy, manipulate, render – can be performed separately:

1. Create a copy of the original template object:

		node = template.copy()
	
2. Call the controller function, passing it the copied template object and values to insert:

		render_template(node, title, links)

3. Render the copied template object:

		print node.render()

See the `demo1alt_quote.py` and `demo8_multi_step_rendering.py` scripts in the `sample` folder for examples. In particular, the multi-step rendering script demonstrates how splitting these steps can improve efficiency when generating a series of pages that share some common elements such as navigation bars.

