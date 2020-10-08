# markdown\_link\_attr\_modifier

A [Python-Markdown](https://github.com/Python-Markdown/markdown) extension to modify attributes of all `<a>` tag links. You can add `target="_blank"` attribute, control `opener` and `referrer` policy by adding related attributes, and add any custom attributes.

By default,

```markdown
[abc](https://www.example.com/)
```

will become

```html
<p><a href="https://www.example.com/" referrerpolicy="no-referrer" rel="noopener noreferrer" target="_blank">abc</a></p>
```

with this extension.

Support [Python-Markdown](https://github.com/Python-Markdown/markdown) `3.x`. Tested against Python `3.8.5` + Python-Markdown `3.2.2`, and Python `2.7.17` + Python-Markdown `3.1.1`.

## Install

### Prepare

```bash
python3 -m pip install -U pip wheel setuptools
```

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

s = '[example](https://www.example.com/)'
print(markdown.markdown(s, extensions=['markdown_link_attr_modifier']))

# config
print(markdown.markdown('[local](local.html)', extensions=['markdown_link_attr_modifier'], extension_configs={'markdown_link_attr_modifier': {'external_only': False}}))
```

You can also `import` manually:

```python
import markdown
from markdown_link_attr_modifier import LinkAttrModifierExtension

s = '[example](https://www.example.com/)'
print(markdown.markdown(s, extensions=[LinkAttrModifierExtension()]))

# config
print(markdown.markdown(s, extensions=[LinkAttrModifierExtension(external_only=False)]))
```

For more information, see [Extensions - Python-Markdown documentation](https://python-markdown.github.io/extensions/) and [Using Markdown as a Python Library - Python-Markdown documentation](https://python-markdown.github.io/reference/#extensions).

### CLI

```bash
python3 -m markdown -x markdown_link_attr_modifier input.md > output.html
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
            # config here
        },
    },
    'output_format': 'html5',
}
```

For more information, see [Settings - Pelican Docs](https://docs.getpelican.com/en/stable/settings.html).

## Options

Options about how to match `<a>` links:

- `external_only`: Default is `True`. Only modify external links.

Options about `<a>` tag attributes:

- `new_tab`: Default is `True`. Open in new tab, set `target="_blank"` attribute.
- `security`: Default is `True`. Security, no referrer, no opener.
- `custom_attrs`: Default is `{}`, Custom attributes, dict variable.


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
