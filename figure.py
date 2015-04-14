import re
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import IMAGE_LINK_RE
from markdown.util import etree

FIGURE_RE = re.compile('|'.join([IMAGE_LINK_RE]))

class FigureProcessor(BlockProcessor):
    ''' Process <figure> elements'''

    def test(self, parent, block):
        return not self.parser.state.isstate('figure') and bool(FIGURE_RE.match(block))

    def run(self, parent, blocks):
        block = blocks.pop(0)
        m = FIGURE_RE.match(block)
        #TODO: Handle image references
        groups = m.groups()
        caption, src = groups[0], groups[-1]
        fig = etree.SubElement(parent, 'figure')
        img = etree.SubElement(fig, 'img')
        img.set('src', src)
        fc = etree.SubElement(fig, 'figcaption')
        fc.text = caption

class FigureExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.parser.blockprocessors.add('figure', FigureProcessor(md.parser), '<code')
