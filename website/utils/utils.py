# from markdown import markdown
# from markdown.extensions.fenced_code import FencedCodeExtension
# from markdown.extensions.codehilite import CodeHiliteExtension
# from markdown.extensions.toc import TocExtension
# from markdown.extensions.sane_lists import SaneListExtension


# def parseMD(md_str):
#     return markdown(
#         md_str,
#         extensions=[
#             FencedCodeExtension(),
#             CodeHiliteExtension(),
#             TocExtension(),
#             SaneListExtension(),
#         ],
#     )

import re
from markdown import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.sane_lists import SaneListExtension


def parseMD(md_str):
    escape_backslashes = lambda match: match.group(0).replace("\\", "\\\\")
    md_str = re.sub(r"\$\$(.*?)\$\$", escape_backslashes, md_str, flags=re.DOTALL)
    md_str = re.sub(r"\$(.*?)\$", escape_backslashes, md_str)

    return markdown(
        md_str,
        extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(),
            TocExtension(),
            SaneListExtension(),
        ],
    )
