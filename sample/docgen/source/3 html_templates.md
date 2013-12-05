# Defining HTML templates #

## Template structure ##

An HTML template is usually a complete HTML/XHTML document, though it may also be a fragment of one – htmltemplate doesn't require the document be complete, or even have a single root element.

To create a Template object model, selected HTML elements must be annotated with _compiler directives_ – special tag attributes that indicate how the object model is to be constructed. By default, the special attribute is named 'node', though a different name may be specified via `Template.__init__()` if needed. Here are some examples:

	<h1 node="con:title">Welcome</h1>
	
	<img node="con:photo" src="" />
	
	<a node="rep:link" href="#">LINK</a>
	
	<span node="-sep:link"> | </span>
	
	<div node="del:"> ... </div>

One restriction does apply when authoring templates: all HTML elements must be correctly closed according to XHTML rules: elements containing content must have both opening and closing tags, and empty tags must include a trailing slash. For example, this markup is acceptable:

	<p>Hello World</p>
	
	<hr />

but this is not:

	<p>Hello World
	
	<hr>

Since the htmltemplate parser already requires templates to be partially XHTML compatible, it is often convenient to develop templates using full XHTML markup and generate valid XHTML documents as output; therefore, htmltemplate preserves empty tags' trailing slashes by default. However, if you do not intend to produce XML-compatible documents, the `Template.__init__()` method's `isxhtml` argument can be used to omit trailing slashes from the final output instead.


## Compiler directives ##

htmltemplate defines four types of compiler directive:

* `con` -- defines a **Container** node that can appear only once at the given location
* `rep` -- defines a **Repeater** node that can appear any number of times
* `sep` -- defines a **Separator** string to be inserted between each iteration of a Repeater object of the same name
* `del` -- indicates a section of dummy markup to **Delete** so that it never appears in generated output.

and its values are typically of form "FOO:BAR", where FOO is a three-letter code indicating the type of directive and BAR is the name of the node to create. For example, `con:title` directs the parser to create a Container node named 'title', while `rep:link` will produce a Repeater node named 'link'.

Directives and node names are both case-sensitive. Each node name must be a valid Python identifier with two additional restrictions: 1. it cannot begin with an underscore, and 2. it cannot match the name of any property or method defined by the [`Container`, `Repeater` and `Template` classes](class_definitions.html).

Directives also supports an 'omit tags' modifier, '-',. When prepended to a directive, e.g. "-con:foo", the minus tags modifier indicates that the HTML element's tags should be omitted in the compiled node/separator string. Use this modifier when adding an arbitrary HTML element (typically `<div>` or `<span>`) to an HTML template purely to construct a node or separator string to prevent the rendered page being cluttered with the leftover tags.

Only the (`con`) and Repeater (`rep`) directives actually describe nodes within the template object mode; these will be discussed in the [next chapter](template_object_model.html). The two remaining directives, Separator and Delete, only affect how the template HTML is parsed, so are described below.

### Using Separator directives ###

The Separator (`sep`) directive indicates a section of markup that should appear between multiple instances of a Repeater node. The default separator for all Repeater nodes is a single linefeed (`"\n"`) character; for example:

	<ul>
		<li node="rep:item">...</li>
	</ul>

will render as:

	<ul>
		<li>ITEM 1</li>
	<li>ITEM 2</li>
	<li>ITEM 3</li>
	<ul>

If a particular Repeater node requires a different separator, this can be defined by adding a `sep` directive to a second element that appears after the Repeater element. For example to insert a `<br />` tag between each instance of a Repeater node named 'foo':

	<br node="sep:foo" />

Note that the Separator element must appear _after_ the Repeater element to which it applies and its name must match the Repeater's name exactly. 

If the Separator element's tags are not required in the final output, just prefix the `sep` directive with an 'omit tags' modifier (`-`) and only the element's content will be used as the separator string:

	<p><span node="-rep:item">...</span> <span node="-sep:link">, </span></p>

will render as:

	<p>ITEM 1, ITEM 2, ITEM 3, ITEM 4</p>

### Using Delete directives ###

The Delete (`del`) directive is used to strip any dummy markup that a template designer has added to the template purely for preview purposes and which should never appear in any rendered output. For example, the following template defines a `table` element whose rows and cells will be dynamically created:

	<table>
		<tr node="rep:row">
			<td node="rep:cell">1</td>
		</tr>
	</table>

While this template is perfectly functional, previewing it in a web browser won't provide a realistic impression of the final output. One way to create a more convincing preview is to insert dummy HTML elements into the template, adding a `del` directive to each one to ensure it will never appear in any rendered output:

	<table>
		<tr node="rep:row">
			<td node="rep:cell">1</td>
			<td node="del:">2</td>
			<td node="del:">3</td>
		</tr>
		<tr node="del:">
			<td>4</td>
			<td>5</td>
			<td>6</td>
		</tr>
	</table>

Deleted elements do not need to be named (for obvious reasons), so their special attributes are normally just written as `node="del:"`.


## Notes ##

The parser will automatically remove the special attribute from any element it converts into a template node. Tag attributes whose name is the same as that used for special attributes but whose value isn't a valid directive are left as-is. For example, should you use an existing HTML attribute such as `id` as your special attribute name, `id="con:foo"` will be recognized as a valid directive and omitted from the output while `id="some-anchor"` will be recognized as non-special and left as-is.

