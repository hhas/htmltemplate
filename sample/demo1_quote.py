#!/usr/bin/env python3

# Demonstrates how to:
# - automatically copy the original Template object, preserving the original for reuse
# - set HTML elements' contents
# - render the template.


from htmltemplate import Template

#################################################
# TEMPLATE
#################################################

# compile the template
template = Template('''<html>
    <head>
        <title node="con:pagetitle">Page Title</title>
    </head>
    <body>
        <h1 node="con:h1title">Page Title </h1>
        <p node="con:quote">Some Text</p>
    </body>
</html>''')

# define the template's controller
def render_template(node, title, quote):
	# 'node' is a copy of the original Template object
	node.pagetitle.text = node.h1title.text = title # set page title and h1 content
	node.quote.text = quote # set quote text

#################################################
# MAIN
#################################################

title, quote = 'Quote of the Day', '"God does not play dice." Albert Einstein'

# render the template
print(template.render(render_template, title, quote))
