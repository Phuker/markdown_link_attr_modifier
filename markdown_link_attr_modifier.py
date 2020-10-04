#!/usr/bin/env python
# encoding: utf-8

"""
Python markdown extension to modify attributes of all <a> links

Author: https://github.com/Phuker

Referenced & related:
https://github.com/danasilver/markdown-newtab
https://stackoverflow.com/questions/4425198/
https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
https://python-markdown.github.io/extensions/api/
https://docs.python.org/3/library/xml.etree.elementtree.html
"""

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
                    elem.set('rel', 'noopener norefferrer')
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

