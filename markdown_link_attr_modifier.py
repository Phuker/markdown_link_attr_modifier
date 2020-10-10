#!/usr/bin/env python
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

import os
import sys
import logging
import unittest

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor

class LinkAttrModifierTreeprocessor(Treeprocessor):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop('config')
        super(LinkAttrModifierTreeprocessor, self).__init__(*args, **kwargs)
    
    def run(self, root):
        for elem in root.iter('a'):
            href = elem.get('href')
            if href is None:
                return
            
            herf_lower = href.lower()
            match_conditions = [not herf_lower.startswith('#')]

            if self.config.get('external_only')[0]:
                match_conditions.append(herf_lower.startswith('http://') or herf_lower.startswith('https://'))

            if all(match_conditions):
                if self.config.get('new_tab')[0]:
                    elem.set('target', '_blank')

                if self.config.get('security')[0]:
                    elem.set('rel', 'noopener noreferrer')
                    elem.set('referrerpolicy', 'no-referrer')
                
                custom_attrs = self.config.get('custom_attrs')[0]
                for k in custom_attrs:
                    elem.set(k, custom_attrs[k])


class LinkAttrModifierExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            # Options -> how to match <a> links
            'external_only' : [True, 'Only modify external links.'],

            # Options -> attributes
            'new_tab': [True, 'Open in new tab, set target="_blank"'],
            'security': [True, 'Security, no referrer, no opener.'],
            'custom_attrs': [{}, 'Custom attributes, dict.']
        }
        super(LinkAttrModifierExtension, self).__init__(**kwargs)
    
    def extendMarkdown(self, md):
        # priority: Important. Least runs last.
        md.treeprocessors.register(LinkAttrModifierTreeprocessor(md, config=self.config), 'link-mod-phuker', -99999)


def makeExtension(**kwargs):
    return LinkAttrModifierExtension(**kwargs)


class LinkAttrModifierExtensionTests(unittest.TestCase):
    def test_warm_up(self):
        log = logging.getLogger("LinkAttrModifierExtensionTests")
        sys.stderr.write('\n') # break incomplete line output by 'unittest -v'

        s = '''
# hello

[abc](https://www.example.com/)

'''
        log.info('markdown = %s', s)

        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension()])
        log.info('Result HTML = %s', result)
        
        self.assertIn('href="https://www.example.com/"', result)

    def test_local_link(self):
        log = logging.getLogger("LinkAttrModifierExtensionTests")
        sys.stderr.write('\n')

        s = '[abc](local.html)'
        log.info('markdown = %s', s)

        config = {'external_only': True}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertNotIn('target="_blank"', result)

        config = {'external_only': False}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertIn('target="_blank"', result)
    
    def test_external_link(self):
        log = logging.getLogger("LinkAttrModifierExtensionTests")
        sys.stderr.write('\n')

        s = '[example](https://www.example.com/)'
        log.info('markdown = %s', s)

        config = {'new_tab': False}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertNotIn('target="_blank"', result)

        config = {'new_tab': True}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertIn('target="_blank"', result)

        config = {'security': False}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertNotIn('rel="noopener noreferrer"', result)
        self.assertNotIn('referrerpolicy="no-referrer"', result)

        config = {'security': True}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertIn('rel="noopener noreferrer"', result)
        self.assertIn('referrerpolicy="no-referrer"', result)

        config = {'custom_attrs': {'fuck-key': 'fuck-value'}}
        log.info('Config: %r', config)
        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension(**config)])
        log.info('Result HTML = %s', result)
        self.assertIn('fuck-key="fuck-value"', result)
    
    def test_xml_level(self):
        log = logging.getLogger("LinkAttrModifierExtensionTests")
        sys.stderr.write('\n')

        s = '''
- abc
- def
    - [example](https://www.example.com/)
- ghi
'''
        log.info('markdown = %s', s)

        result = markdown.markdown(s, extensions=['extra', LinkAttrModifierExtension()])
        log.info('Result HTML = %s', result)
        
        self.assertIn('href="https://www.example.com/"', result)
        self.assertIn('target="_blank"', result)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]:%(message)s',
        datefmt='%H:%M:%S',
        stream=sys.stderr,
    )
    unittest.main()
