#!/usr/bin/env python3

from htmltemplate import Template


# Define the template:

html = """
<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
		<ul>
			<li node="rep:item">
				<a href="" node="con:link">LINK</a>
			</li>
		</ul>
	</body>
</html>
"""


# Compile the template:

template = Template(html)
# print(template.structure())


# Define functions to control template rendering:

def render_template(node, pagetitle, linkinfos):
	"""Renders the template.
		node : Template -- the top-level Template node
		pagetitle : string -- the page title
		linkinfos : list of tuple -- a list of form [(URI, name),...]
	"""
	node.title.text = pagetitle
	node.item.repeat(render_item, linkinfos)


def render_item(node, linkinfo):
	"""Callback function used by render().
		node : Repeater -- the copy of the rep:item node to manipulate
		linkinfo : tuple of string -- a tuple of form: (URI, name)
	"""
	url, name = linkinfo
	node.link.atts['href'] = url
	node.link.text = name


# Render the template:

title = "Site Map"
links = [('index.html', 'Home'), ('products/index.html', 'Products'), ('about.html', 'About')]
print(template.render(render_template, title, links))

