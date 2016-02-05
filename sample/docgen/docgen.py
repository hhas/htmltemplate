#!/usr/bin/env python3

""" docgen -- render Markdown documentation files as HTML

Copyright (C) 2013-2016 HAS

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Requirements:

- markdown2 <https://pypi.python.org/pypi/markdown2/>


Usage:
	
	import docgen
	docgen.renderdocs('/path/to/md-source-dir', '/path/to/html-output-dir', 'author', 'title', 'indextitle', fromyear)
	
	python3  /path/to/docgen.py  /path/to/md-source-dir  /path/to/html-output-dir  author  title  indextitle

"""

from markdown2 import markdown
from htmltemplate import Template

import os, os.path, re, shutil, sys, time


#################################################
# SUPPORT
#################################################

gTemplatesDir = os.path.join(os.path.dirname(__file__), 'templates')

def writefile(dirpath, name, text):
	filepath = os.path.join(dirpath, name)
	with open(filepath, 'w', encoding='utf8') as f:
		f.write(text)
	return filepath

def readfile(dirpath, name):
	with open(os.path.join(dirpath, name), encoding='utf8') as f:
		return f.read()


#################################################
# TEMPLATES
#################################################
# page_template controller

kPageTemplate = Template(readfile(gTemplatesDir, 'page_template.html'))

def page_navlink(node, link):
	title, filename = link
	if title:
		node.atts['href'] = filename
		node.text = title
	else:
		node.omit()

def render_page(node, doctitle, pagetitle, heading, content, navlinks, author, fromyear):
	# set title, h1 and main body content
	node.doctitle.text, node.pagetitle1.text = doctitle.lower(), pagetitle.lower()
	node.pagetitle2.text, node.content.html = heading, content
	# render the top and bottom navigation bars, or remove them if not needed
	if navlinks:
		# render top navbar
		node.topnav.link.repeat(page_navlink, navlinks)
		# the top and bottom navbars are identical, so no need to render the same markup twice; 
		# instead, just graft the topnav node onto bottomnav
		node.bottomnav = node.topnav
	else:
		node.topnav.omit()
		node.bottomnav.omit()
	year = time.localtime().tm_year
	if fromyear and int(fromyear) < year:
		year = '{}-{}'.format(int(fromyear), year)
	node.year.text, node.author.text = year, author


##


kIndexTemplate = Template(readfile(gTemplatesDir, 'toc_template.html'))

def render_link(node, pageinfo):
	node.link.atts['href'], node.link.text = pageinfo[1:3]

def render_toc(node, pageinfos):
	node.chapter.repeat(render_link, pageinfos)
	

#################################################
# MAIN
#################################################


def renderdocs(sourcedir, docdir, doctitle, indextitle, author, fromyear=None):
	# create root folder and copy static files
	if os.path.exists(docdir):
		shutil.rmtree(docdir)
	os.mkdir(docdir)
	shutil.copyfile(os.path.join(gTemplatesDir, 'full.css'), os.path.join(docdir, 'full.css'))
	# get list of numbered chapter .md files from sourcedir, sort, split number prefixes; read content, extracting title and content; build list of [prev,up,next] links
	pageinfos = [(-1, 'index.html', None, None)]
	for name in os.listdir(sourcedir):
		m = re.match(r'^([0-9]+)\s*(.+?)\.md$', name)
		if m:
			seq, fname = m.groups()
			title, content = readfile(sourcedir, name).split('\n', 1)
			pageinfos.append((
					int(seq), # determines page ordering
					'{}.html'.format(fname), # file name
					title.strip(' #'), # title
					markdown(content.strip()) # content
			))
	if len(pageinfos) < 2:
		raise RuntimeError('No source documents found.')
	pageinfos.sort(key=lambda o: o[0])
	for i in range(1, len(pageinfos)):
		_, fname, title, content = pageinfos[i]
		navlinks = [('Prev', pageinfos[i-1][1]), ('TOC', 'index.html')]
		if i+1 < len(pageinfos):
			navlinks.append(('Next', pageinfos[i+1][1]))
		writefile(docdir, fname, 
				kPageTemplate.render(render_page, doctitle, title, title, content, navlinks, author, fromyear))
	contentlist = kIndexTemplate.render(render_toc, pageinfos[1:])
	writefile(docdir, 'index.html', kPageTemplate.render(render_page, doctitle, 
			'TOC', '{} {}'.format(doctitle, indextitle), contentlist, [('Next', pageinfos[1][1])], author, fromyear))


#################################################
# CLI
#################################################


if __name__ == '__main__':
	renderdocs(os.path.expanduser(sys.argv[1]), os.path.expanduser(sys.argv[2]), *sys.argv[3:])

