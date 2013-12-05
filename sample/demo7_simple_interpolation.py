#!/usr/bin/env python3

# Demonstrates how to interpolate dict-based data into template nodes by automatically matching node names to dictionary keys.
#
# - the dict's 'foo' and 'baz' items are automatically inserted into the 'foo' and 'baz' sub-nodes
# - the sub-node named 'bar' is automatically deleted as there's no item named 'bar' in the dict
# - the dict's 'fub' item is ignored as there's no sub-node named 'fub'

from htmltemplate import Template

template = Template('''
<tag1 node="con:foo">???</tag1>
<tag2 node="con:bar">???</tag2>
<tag3 node="con:baz">???</tag3>
''')


def interpolate(node, data):
	""" Inserts content from the given data dict into a node's sub-nodes.
		
		node : Node -- a Container/Repeater node containing one or more simple Container sub-nodes
		data : dict -- keys should match sub-node names; values should be strings
	"""
	for subnode in node:
		if subnode.nodename in data:
			subnode.text = data[subnode.nodename]
		else:
			subnode.omit()


data = {'foo':'Bob', 'baz':'Jane', 'fub':'Sam'}

node = template.copy()
interpolate(node, data)
print(node.render())

# Result:
# <tag1>Bob</tag1>
# 
# <tag3>Jane</tag3>

