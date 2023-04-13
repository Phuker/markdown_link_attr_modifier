#!/usr/bin/env python3
# encoding: utf-8

"""
Python markdown extension to modify attributes of all <a> links

Author: https://github.com/Phuker

Referenced & related:

https://stackoverflow.com/questions/4425198/
https://stackoverflow.com/questions/46525733/

https://github.com/danasilver/markdown-newtab

https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
https://developer.mozilla.org/en-US/docs/Web/HTML/Link_types
https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a
https://mathiasbynens.github.io/rel-noopener/

https://python-markdown.github.io/extensions/api/
https://docs.python.org/3/library/xml.etree.elementtree.html
"""

import sys
import logging
import unittest

import markdown


logger = logging.getLogger(__name__)


# https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel
def link_add_rel_attr(elem, append_values):
    old_str = elem.get('rel')
    if old_str is None:
        old_list = []
    else:
        old_str = old_str.strip()
        if len(old_str) == 0:
            old_list = []
        else:
            old_list = old_str.split()
    
    append_list = append_values.split()
    new_list = []

    for x in old_list:
        if x not in new_list:
            new_list.append(x)
    
    for x in append_list:
        if x not in new_list:
            new_list.append(x)
    
    elem.set('rel', ' '.join(new_list))


class LinkAttrModifierTreeprocessor(markdown.treeprocessors.Treeprocessor):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config')
        super(LinkAttrModifierTreeprocessor, self).__init__(*args, **kwargs)
    
    def run(self, root):
        config_new_tab = self.config.get('new_tab')[0]
        config_no_referrer = self.config.get('no_referrer')[0]
        config_auto_title = self.config.get('auto_title')[0]
        config_custom_attrs = self.config.get('custom_attrs')[0]

        for elem in root.iter('a'):
            link_url = elem.get('href')
            if link_url is None:
                link_url = ''
            
            link_url_lower = link_url.lower()
            link_url_is_external = link_url_lower.startswith('http://') or link_url_lower.startswith('https://')
            link_has_attr_title = 'title' in elem.keys()
            link_text = ''.join(elem.itertext())

            condition_good_url = all([
                len(link_url) > 0,
                not link_url_lower.startswith('#'),
                not link_url_lower.startswith('javascript:'),
                not link_url_lower.startswith('mailto:'),

                # <someone@example.com> ==> <a href="&#109;&#97;&#105;&#108; ...
                # see:
                # class AutomailInlineProcessor in
                # https://github.com/Python-Markdown/markdown/blob/master/markdown/inlinepatterns.py
                # util.AMP_SUBSTITUTE in
                # https://github.com/Python-Markdown/markdown/blob/master/markdown/util.py
                not link_url_lower.startswith('\x02amp\x03#109;\x02amp\x03#97;\x02amp\x03#105;\x02amp\x03#108;\x02amp\x03#116;\x02amp\x03#111;\x02amp\x03#58;'),
            ])

            condition_new_tab = condition_good_url and (config_new_tab == 'on' or (config_new_tab == 'external_only' and link_url_is_external))
            if condition_new_tab:
                elem.set('target', '_blank')
                link_add_rel_attr(elem, 'noopener')

            condition_no_referrer = condition_good_url and (config_no_referrer == 'on' or (config_no_referrer == 'external_only' and link_url_is_external))
            if condition_no_referrer:
                link_add_rel_attr(elem, 'noreferrer')
                elem.set('referrerpolicy', 'no-referrer')
            
            condition_auto_title = config_auto_title == 'on' and (not link_has_attr_title)
            if condition_auto_title:
                elem.set('title', link_text)

            for k in config_custom_attrs:
                elem.set(k, config_custom_attrs[k])


class LinkAttrModifierExtension(markdown.extensions.Extension):
    def __init__(self, **kwargs):
        # can not use mixed type value, e.g. (True, 'string_value', False),
        # or ValueError: Cannot parse bool value: 'external_only'
        # https://github.com/Python-Markdown/markdown/blob/master/markdown/extensions/__init__.py
        # https://github.com/Python-Markdown/markdown/blob/master/markdown/util.py
        valid_values = {
            'new_tab': ('on', 'external_only', 'off'),
            'no_referrer': ('on', 'external_only', 'off'),
            'auto_title': ('on', 'off'),
        }

        # Default value: DO NOT do anything
        self.config = {
            'new_tab': ['off', f'Open in new tab, set target="_blank" and rel="noopener" attributes. Valid values: {valid_values["new_tab"]!r}'],
            'no_referrer': ['off', f'No referrer. Valid values: {valid_values["no_referrer"]!r}'],
            'auto_title': ['off', f'Auto add title attribute. Valid values: {valid_values["auto_title"]!r}'],
            'custom_attrs': [{}, 'Custom attributes. Valid value is a dict.']
        }
        super(LinkAttrModifierExtension, self).__init__(**kwargs)

        for k in valid_values:
            v = self.getConfig(k)
            if v not in valid_values[k]:
                raise ValueError(f'Invalid config {k!r} value: {v!r}, valid values: {valid_values[k]!r}')

    def extendMarkdown(self, md):
        # priority: Important. Least runs last.
        md.treeprocessors.register(LinkAttrModifierTreeprocessor(md, config=self.config), 'link-mod-phuker', -99999)


def makeExtension(**kwargs):
    return LinkAttrModifierExtension(**kwargs)


def print_help():
    print('Configuration:', file=sys.stderr)
    config_info = LinkAttrModifierExtension().getConfigInfo()
    key_max_length = 0
    for k, _ in config_info:
        if len(k) > key_max_length:
            key_max_length = len(k)
    
    for k, v in config_info:
        gap = ' ' * (key_max_length + 4 - len(k))
        print(f'{k}{gap}{v}', file=sys.stderr)

    print('', file=sys.stderr)


class LinkAttrModifierExtensionTests(unittest.TestCase):
    def setUp(self):
        # break incomplete line output by 'unittest -v'
        print('', file=sys.stderr)
        print('\x1b[1;36m= = = = = = = = = = = = = = = = \x1b[0m', file=sys.stderr)
    
    def md2html(self, s, config):
        logger.info('Markdown:\n%s', s)
        logger.info('Config: %r', config)

        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        logger.info('Result HTML:\n%s', result)
        print('\x1b[36m--------\x1b[0m', file=sys.stderr)

        return result

    
    def test_warm_up(self):
        s = '''
# hello

[abc](https://www.example.com/)

<https://www.example.org/>

[abc][link1]

[link1]: https://example.com/
'''

        config = {}
        result = self.md2html(s, config)
        self.assertIn('href="https://www.example.com/"', result)
        self.assertIn('href="https://www.example.org/"', result)
        self.assertIn('href="https://example.com/"', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'external_only',
            'auto_title': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('href="https://www.example.com/"', result)
        self.assertIn('href="https://www.example.org/"', result)
        self.assertIn('href="https://example.com/"', result)

    def test_skip_link(self):
        # not work:
        # <javascript:alert(0);> ==> <javascript:alert(0);>
        # <#test-1> ==> <p>&lt;#test-1&gt;</p>
        s = '''
[alert0](javascript:alert(1);)

[test-2](#test-3)

<test4@example.com>

[test5](mailto:test6@example.com)
'''

        config = {
            'new_tab': 'on',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('<a href="javascript:alert(1);">alert0</a>', result)
        self.assertIn('<a href="#test-3">test-2</a>', result)
        self.assertIn('<a href="&#109;&#97;&#105;&#108;&#116;&#111;&#58;&#116;&#101;&#115;&#116;&#52;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;">&#116;&#101;&#115;&#116;&#52;&#64;&#101;&#120;&#97;&#109;&#112;&#108;&#101;&#46;&#99;&#111;&#109;</a>', result)
        self.assertIn('<a href="mailto:test6@example.com">test5</a>', result)

    def test_local_link(self):
        s = '[abc](local.html)'

        config = {
            'new_tab': 'off',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertNotIn('rel=', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertNotIn('rel=', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener"', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'off',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertNotIn('rel=', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertNotIn('rel=', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener"', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'off',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertIn('rel="noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertIn('rel="noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)
    
    def test_external_link(self):
        s = '[example](https://www.example.com/)'

        config = {
            'new_tab': 'off',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertNotIn('rel=', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener"', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'off',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener"', result)
        self.assertNotIn('referrerpolicy=', result)

        config = {
            'new_tab': 'off',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertIn('rel="noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'external_only',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'off',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertNotIn('target=', result)
        self.assertIn('rel="noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'external_only',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('target="_blank"', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)
    
    def test_rel(self):
        s = "[example](https://www.example.com/){: rel='nofollow noreferrer'}"
        config = {
            'new_tab': 'on',
            'no_referrer': 'on',
        }
        result = self.md2html(s, config)
        self.assertIn('rel="nofollow noreferrer noopener"', result)

    def test_custom_attrs(self):
        s = '[example](https://www.example.com/)'

        config = {'custom_attrs': {'fuck-key': 'fuck-value'}}
        result = self.md2html(s, config)
        self.assertIn('fuck-key="fuck-value"', result)

        config = {'custom_attrs': {'href': 'fuck-value'}}
        result = self.md2html(s, config)
        self.assertIn('href="fuck-value"', result)

        config = {
            'new_tab': 'on',
            'no_referrer': 'on',
            'custom_attrs': {
                'target': 'fuck-target',
                'rel': 'fuck-rel',
            },
        }
        result = self.md2html(s, config)
        self.assertIn('target="fuck-target"', result)
        self.assertIn('rel="fuck-rel"', result)
    
    def test_auto_title(self):
        s = '[1 > 0](local.html)'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="1 &gt; 0"', result)

        s = '[1 > 0](local.html "0 < 1")'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="0 &lt; 1"', result)

        s = '<https://example.com/>'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="https://example.com/"', result)

        s = '[header1](#h1)'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="header1"', result)

        s = '[12![34](56.png)789](local.html)'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="12789"', result)

        s = '[a **b** `c` d](https://example.com/)'
        config = {'auto_title': 'on'}
        result = self.md2html(s, config)
        self.assertIn('title="a b c d"', result)

    def test_xml_level(self):
        s = '''
- abc
- def
    - [example](https://www.example.com/)
- ghi
'''
        config = {'new_tab': 'on'}
        result = self.md2html(s, config)
        self.assertIn('href="https://www.example.com/"', result)
        self.assertIn('target="_blank"', result)
    
    def test_config(self):
        s = '[example](https://www.example.com/)'

        config = {'new_tab': 'xxxyyy'}
        with self.assertRaises(ValueError) as e:
            _ = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        
        logger.info('Error: %r', e.exception)

        config = {'xxxyyy': 'xxxyyy'}
        with self.assertRaises(KeyError) as e:
            _ = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        
        logger.info('Error: %r', e.exception)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]:%(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr,
    )

    print_help()

    print('Tests:', file=sys.stderr)
    unittest.main()
