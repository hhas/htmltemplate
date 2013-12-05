#!/usr/bin/env python3

# Demonstrates how to:
# - generate multiple table rows
# - assign strings to tag attributes

from htmltemplate import Template

#################################################
# TEMPLATE
#################################################


template = Template('''<html>
	<head>
		<title node="con:title">TITLE</title>
	</head>
	<body>
	
		<table>
			<tr node="rep:client">
				<td node="con:name">Surname, Firstname</td>
				<td><a node="con:email" href="mailto:client@email.com">client@email.com</a></td>
			</tr>
		</table>
	
	</body>
</html>''')

def render_template(node, title, clients):
	node.title.text = title
	node.client.repeat(render_client, clients)

def render_client(node, client):
	node.name.text = client.surname + ', ' + client.firstname
	node.email.atts['href'] = 'mailto:' + client.email
	node.email.text = client.email


#################################################
# MAIN
#################################################

class Client:
	def __init__(self, surname, firstname, email):
		self.surname, self.firstname, self.email = surname, firstname, email

title = 'Foo Co.'
clients = [Client('Smith', 'K', 'ks@foo.com'), Client('Jones', 'T', 'tj@bar.org')]

print(template.render(render_template, title, clients))
