from distutils.core import setup

setup(name = 'htmltemplate',
	version = '2.2.1',
	description = 'A simple, powerful [X]HTML templating library for Python 3',
	long_description = "htmltemplate converts [X]HTML documents into simple template object models easily manipulated using ordinary Python code. It is powerful, flexible, and easy to use.",
	author = 'HAS',
	author_email = 'hhas@users.sourceforge.net',
	url='https://github.com/hhas/htmltemplate',
	py_modules = ['htmltemplate'],
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
	]
)
