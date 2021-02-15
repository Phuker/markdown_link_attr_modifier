# markdown\_link\_attr\_modifier

A [Python-Markdown](https://github.com/Python-Markdown/markdown) extension to modify attributes of `<a>` link tags. With this extension, you can:

- Open links in new tab by adding `target="_blank"` attribute (along with `rel="noopener"` attribute for [security reasons](https://mathiasbynens.github.io/rel-noopener/))
- Do not send `Referer` (sic) request header by setting related attributes for [privacy and security reasons](https://developer.mozilla.org/en-US/docs/Web/Security/Referer_header:_privacy_and_security_concerns)
- Auto add [`title` attribute](https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/title)
- Add/overwrite any custom attributes

For instance, this markdown code

```markdown
[abc](https://example.com/)
```

could become

```html
<p><a href="https://example.com/" referrerpolicy="no-referrer" rel="noopener noreferrer" target="_blank" title="abc">abc</a></p>
```

with this extension.

Support [Python-Markdown](https://github.com/Python-Markdown/markdown) `3.x`. Tested against Python `3.9.1` + Python-Markdown `3.3.3`. Not support Python < `3.6` (including `2.7.x`) anymore since version `0.2.0`.

## Install

Before you start, check and upgrade your `pip` installation.

```bash
python3 -m pip install -U pip wheel setuptools
```

You can install this package with any of the methods below.

### Install from PyPI

```bash
python3 -m pip install -U markdown-link-attr-modifier
```

### Install from source code manually

First, clone/download this repo, and then:

```bash
make PYTHON=python3
```

`make` command required.

If you do NOT have `make` command:

```bash
python3 ./setup.py bdist_wheel
cd dist/

# For Windows CMD, press TAB just before press ENTER
python3 -m pip install *.whl

python3 -m pip show markdown_link_attr_modifier
```

## Usage

```python
import markdown

s = '[example](https://example.com/)'
extensions = ['markdown_link_attr_modifier', ]
extension_configs = {
    'markdown_link_attr_modifier': {
        'new_tab': 'on',
        'no_referrer': 'external_only',
        'auto_title': 'on',
    },
}

print(markdown.markdown(s, extensions=extensions, extension_configs=extension_configs))
```

Output:

```html
<p><a href="https://example.com/" referrerpolicy="no-referrer" rel="noopener noreferrer" target="_blank" title="example">example</a></p>
```

You can also `import` manually:

```python
import markdown
from markdown_link_attr_modifier import LinkAttrModifierExtension

s = '[example](https://example.com/)'

# without config
print(markdown.markdown(s, extensions=[LinkAttrModifierExtension()]))

# with config
print(markdown.markdown(s, extensions=[LinkAttrModifierExtension(new_tab='on', no_referrer='external_only')]))
```

Output:

```html
<p><a href="https://example.com/">example</a></p>
<p><a href="https://example.com/" referrerpolicy="no-referrer" rel="noopener noreferrer" target="_blank">example</a></p>
```

For more information, see [Extensions - Python-Markdown documentation](https://python-markdown.github.io/extensions/) and [Using Markdown as a Python Library - Python-Markdown documentation](https://python-markdown.github.io/reference/#extensions).

### CLI

```bash
python3 -m markdown -x markdown_link_attr_modifier input.md > output.html
python3 -m markdown -x markdown_link_attr_modifier -c config.json input.md > output.html
```

For more information, see [Using Python-Markdown on the Command Line - Python-Markdown documentation](https://python-markdown.github.io/cli/).

### Pelican

[Pelican](https://blog.getpelican.com/) is a static site generator.

Edit `pelicanconf.py`, `MARKDOWN` dict variable. Example:

```python
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.codehilite': {
            'css_class': 'highlight',
            'linenums': False,
            'guess_lang': False,
        },
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.toc': {},
        
        'markdown_link_attr_modifier': {
            'new_tab': 'on',
            'no_referrer': 'external_only',
            'auto_title': 'on',
        },
    },
    'output_format': 'html5',
}
```

For more information, see [Settings - Pelican Docs](https://docs.getpelican.com/en/stable/settings.html).

## Options

By default, this extension does NOT do anything. Configuration items:

- `new_tab`: Open links in new tab, set `target="_blank"` and `rel="noopener"` attributes. Default value: `'off'`. Valid values: `('on', 'external_only', 'off')`
- `no_referrer`: No referrer. Default value: `'off'`. Valid values: `('on', 'external_only', 'off')`
- `auto_title`: Auto add title attribute. Default value: `'off'`. Valid values: `('on', 'off')`
- `custom_attrs`: Custom attributes. Default value: `{}`. Valid value is a `dict`.

Values about how to match `<a>` links:

- `on`: Modify all valid links.
- `external_only`: Only modify external valid links.
- `off`: Do not modify any link.

FYI:

- [MDN: Referer header: privacy and security concerns](https://developer.mozilla.org/en-US/docs/Web/Security/Referer_header:_privacy_and_security_concerns)
- [About `rel=noopener`](https://mathiasbynens.github.io/rel-noopener/)

## Tests

Test installed module:

```bash
python3 -m markdown_link_attr_modifier -v
```

Test module in this repo without install:

```bash
make test
```

## License

This repo is licensed under the **GNU General Public License v3.0**
