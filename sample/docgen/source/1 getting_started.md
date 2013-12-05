# Getting started #

## About htmltemplate ##

htmltemplate converts [X]HTML documents into simple template object models easily manipulated using ordinary Python code. It is powerful, flexible, and easy to use.

Some advantages:

* **Total separation of markup and code.** HTML templates can be edited using your favourite HTML editor and previewed in web browsers. Controller code can be written and maintained with your favourite Python editor. Special tag attributes indicate which HTML elements should be converted into nodes within the object model. Absolutely no code is kept in the HTML markup, not even presentation logic.
* **Simple, practical interface.** htmltemplate's compact yet capable API is designed for simplicity and ease of use, yet without compromising power and flexibility. The entire interface comprises of one module, six classes, and fewer than two dozen properties and methods. An elegant callback-driven interaction model takes care of details, simplifying user code.
* **Supports component-based construction.** Rendered pages can be constructed from a single large template or composed from several smaller ones. Template object models can be combined and remixed at will. Generated content can be reused whole or in-part.
* **Doesn't get in your face.** Lightweight design, strictly KISS. No boilerplate code required. Strong emphasis on ease of use.
* **Free and open source.** htmltemplate is distributed under the MIT Licence, allowing its use in both open and closed-source projects.

htmltemplate supports Python 3.1 and later.


## Installing via `pip` ##

To download and install htmltemplate using [`pip`](https://pypi.python.org/pypi/pip):

	sudo pip-3.3 install htmltemplate

 This will download the latest version of htmltemplate from the Python Package Index and install it. (Amend the Python version number as needed.)

Full documentation and example scripts can be found in the source release – see below.


## Installing from source ##

Download the latest `.tar.gz` [source release](https://pypi.python.org/pypi/htmltemplate/) from the Python Package Index and follow the instructions in its `README` file.
