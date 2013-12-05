#!/usr/bin/env python3

# Demonstrates how to recursively render nested data using a single HTML list element.

from htmltemplate import Template

#################################################
# TEMPLATE
#################################################

template = Template("""
<html>

	<ul node="con:list">

<li node="rep:item">...</li>

	</ul>

</html>
""")


def render_item(node, dataitem):
	if isinstance(dataitem, list):
		# recursively render sub-list using original con:list node
		listnode = template.list.copy()
		listnode.item.repeat(render_item, dataitem)
		node.html = listnode.render()
	else:
		node.text = str(dataitem)

def render_template(node, datalist):
	node.list.item.repeat(render_item, datalist)

#################################################
# MAIN
#################################################

data = [
	'A1', 
	'A2', 
	[
		'b1', 
		'b2', 
		'b3', 
		[
			'c1', 
			'c2', 
			'c3',
		],
		'b4',
		[
			'c5', 
			'c6', 
		],
	],
	'A3', 
	'A4',
]

print(template.render(render_template, data))

