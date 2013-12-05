#!/usr/bin/env python3

# Demonstrates how to:
# - view Template object model's structure for diagnostic purposes
# - insert separators between repeating blocks
# - omit tags from compiled nodes using 'minus tags' modifier (-)
# - use the 'del' directive to delete mock-up content when the template HTML is parsed
#
# Also note how duplicate nodes are automatically omitted from compiled Template.

import urllib.parse

from htmltemplate import Template

#################################################
# TEMPLATE
#################################################

template = Template('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<title node="con:title">Some Title</title>
</head>
<body>
	<!-- side navbar -->
	<ul>
		<li node="rep:sidenavlink"><a href="#" node="con:link">LINK 1</a></li>
		<li node="del:"><a href="#">LINK 2</a></li>
		<li node="del:"><a href="#">LINK 3</a></li>
	</ul>


	<!-- footer navbar -->
	<p>
		<a href="#" node="rep:footernavlink">LINK 1</a>
		<span node="-sep:footernavlink"> | </span>
		<a href="#" node="del:">LINK 2</a>
	</p>
</body>
</html>''')


def render_template(node, title, names):
	node.title.text = title
	node.sidenavlink.repeat(render_sidenavlink, names)
	node.footernavlink.repeat(render_footernavlink, names)
		
def render_sidenavlink(node, name):
	node.link.atts['href'] = '{}.html'.format(urllib.parse.quote(name.lower()))
	node.link.text = name
		
def render_footernavlink(node, name):
	node.atts['href'] = '{}.html'.format(urllib.parse.quote(name.lower()))
	node.text = name



#################################################
# MAIN
#################################################

print('******* TEMPLATE STRUCTURE *******\n')
print(template.structure())
print()
print('******* SAMPLE RENDERED PAGE *******\n')
print(template.render(render_template, 'Fantastic Foo Inc', 
		['Home', 'Products', 'Services', 'About Us', 'Contact Us', 'Help']))
