from markdown import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension


def parseMD(md_str):
    return markdown(
        md_str,
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(),
            TocExtension(),
            SaneListExtension(),
        ],
    )
