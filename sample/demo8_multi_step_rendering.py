#!/usr/bin/env python3

# Demonstrates how to assemble completed pages in multiple steps based on a single master template. This is a useful performance optimisation when some parts of your template will contain the same data across many pages. Rather than re-insert that common data every time you create a new page, you insert it only once.
#
# In this example, a static website is logically divided into two sections, 'Products' and 'Support', each of which contains several pages. Each section has navlinks that are identical across all pages within that section. To reduce rendering time when generating the site, the navlinks need only be rendered once per section rather than for every single page. Per-section templates are created by copying the master template and partly populating it. Individual pages for a section are created by copying the section template and filling in the remaining areas.
#

from htmltemplate import Template

#################################################
# TEMPLATE
#################################################

# Compile the master template:
# - each page title consists of a section name and a page name
# - each site section has a common navbar
# - each page has unique content

template = Template("""
<html>
	<head>
		<title><span node="-con:sectiontitle">SECTION</span> : <span node="-con:pagetitle">PAGE</span></title>
	</head>
	<body>
	<!-- section navbar -->
	<ul>
		<li node="rep:navbaritem"><a href="" node="con:link">LINK</a></li>
	</ul>
		<h1 node="con:pageheading">PAGE</h1>
		<!-- page content -->
		<div node="-con:bodyhtml">BODY</div>
	</body>
</html>
""")



def render_navbaritem(node, link):
	node.link.atts['href'] = link
	node.link.text = link

# Function to create semi-rendered templates for each section:

def createsectiontemplate(sectiontitle, links):
	node = template.copy()
	node.sectiontitle.text = sectiontitle # set the part of the title common to all pages in a section
	node.navbaritem.repeat(render_navbaritem, links) # render the navlinks common to all pages in a section
	return node


# Function to render a finished page from a semi-rendered section template:

def renderpage(sectiontemplate, pagetitle, bodyhtml):
	node = sectiontemplate.copy()
	node.pagetitle.text = pagetitle # set the part of the title unique to this page
	node.pageheading.text = pagetitle # set the h1 heading unique to this page
	node.bodyhtml.html = bodyhtml # set the content unique to this page
	return node.render()


#################################################
# MAIN
#################################################


sections = [
	{
		'title': 'Products', 
		'pages': [
			('Widgets', '<div[Product info for widgets ...]</div>'),
			('Geegaws', '<div>[Product info for geegaws ...]</div>'),
			('McGuffins', '<div>[Product info for McGuffins ...]</div>'),
		]
	},
	{
		'title': 'Support',
		'pages': [
			('FAQ', '<p>Common questions [...]</p>'), 
			('Contact', '<p>How to reach us [...]</p>')
		]
	}
]


for section in sections:
	# Get a partially-rendered template for each section. Each contains a standard title and navbar for that section:
	navlinks = ['{}.html'.format(pagetitle) for pagetitle, bodyhtml in section['pages']]
	sectiontemplate = createsectiontemplate(section['title'], navlinks)
	
	# Render the pages for this section:
	print('------- {} PAGES -------'.format(section['title'].upper()))
	for pagetitle, bodyhtml in section['pages']:
		print(renderpage(sectiontemplate, pagetitle, bodyhtml))

