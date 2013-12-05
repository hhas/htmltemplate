#!/usr/bin/env python3

# Demonstrates how to:
# - generate alternately coloured table rows.


from htmltemplate import Template

#######
# Support

def alternator(*items):
	"""Returns a generator that yields the supplied arguments as a repeating sequence."""
	i = 0
	while 1:
		yield items[i % len(items)]
		i += 1

#######
# Template

template = Template("""<table>
<tr node="rep:row" bgcolor="lime"><td>...</td></tr>
</table>""")


def render_template(node, rows):
	node.row.repeat(render_row, rows, alternator('red', 'green', 'blue'))
	return node.render()

def render_row(node, row, colors):
	node.atts['bgcolor'] = next(colors)

#######
# Test

print(template.render(render_template, range(10)))

