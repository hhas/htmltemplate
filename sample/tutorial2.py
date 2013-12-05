#!/usr/bin/env python3

from htmltemplate import Template


# Define and compile the template:

template  = Template("""
<div node="rep:section">
	<h2 node="con:title">section title</h2>
	<p node="con:desc">section description</p>
</div>
""")


# Define functions to control template rendering:

def render_section(node, section):
	node.title.text, node.desc.text = section

def render_template(node, sections):
	node.section.repeat(render_section, sections)


# Render the template:

sections = [('title 1', 'description 1'), ('title 2', 'description 2'), ('title 3', 'description 3')]
print(template.render(render_template, sections))

