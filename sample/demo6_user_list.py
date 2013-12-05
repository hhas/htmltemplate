#!/usr/bin/env python3

# Demonstrates how to:
# - insert HTML markup as a node's raw (unescaped) content
# - modify part of an existing attribute value (or content) using Python string substitutions
# - compose multiple templates to produce a complete HTML document


from htmltemplate import Template

#######
# PAGE TEMPLATE

pagetpl = Template('''<html>
	<head>
		<title node="con:title1">TITLE</title>
	</head>
	<body>
		<h1 node="con:title2">TITLE</h1>
		<div node="-con:table">...</div>
	</body>
</html>''')

def render_page(node, title, table):
	node.title1.text = node.title2.text = title
	node.table.html = table


#######
# BODY TEMPLATE

tabletpl = Template('''<table cellpadding="3" border="0" cellspacing="1" width="100%">
	<thead>
		<tr>
			<th>ID</th>
			<th>Name</th>
			<th>Email</th>
			<th>Banned</th>
		</tr>
	</thead>
	<tbody>
		<tr node="rep:user">
			<td node="con:id">123</td>
			<td node="con:name">John Doe</td>
			<td><a href="mailto:{}" node="con:email">j.doe@foo.com</a></td>
			<td node="con:banned">&nbsp;</td>
		</tr>
	</tbody>
</table>''')

def render_user(node, user):
	node.id.text = user['id']
	node.name.text = user['name']
	node.email.atts['href'] = node.email.atts['href'].format(user['email'])
	node.email.text = user['email']
	if user['banned']:
		node.banned.text = 'X'

def render_table(node, users):
	node.user.repeat(render_user, users)


#######
# TEST

users = [
	{'id': '1', 'name': 'Jane Brown', 'email': 'j.brown@foo.com', 'banned': False},
	{'id': '2', 'name': 'Sam Jones', 'email': 's.jones@foo.com', 'banned': True},
	{'id': '3', 'name': 'Fred Smith', 'email': 'f.smith@foo.com', 'banned': False},
]

tablehtml = tabletpl.render(render_table, users)
print(pagetpl.render(render_page, 'User List', tablehtml))

