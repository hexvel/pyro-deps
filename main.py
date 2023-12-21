import asyncio
import html
import re

import utils

BOLD_DELIM = "**"
ITALIC_DELIM = "__"
UNDERLINE_DELIM = "--"
STRIKE_DELIM = "~~"
SPOILER_DELIM = "||"
CODE_DELIM = "`"
PRE_DELIM = "```"
QUOTE_DELIM = ">"

MARKDOWN_RE = re.compile(
    r"({d})|\[(.+?)\]\((.+?)\)".format(
        d="|".join(
            [
                "".join(i)
                for i in [
                    [rf"\{j}" for j in i]
                    for i in [
                        PRE_DELIM,
                        CODE_DELIM,
                        STRIKE_DELIM,
                        UNDERLINE_DELIM,
                        ITALIC_DELIM,
                        BOLD_DELIM,
                        SPOILER_DELIM,
                        QUOTE_DELIM,
                    ]
                ]
            ]
        )
    )
)

OPENING_TAG = "<{}>"
CLOSING_TAG = "</{}>"
URL_MARKUP = '<a href="{}">{}</a>'
FIXED_WIDTH_DELIMS = [CODE_DELIM, PRE_DELIM]


class Markdown:
    def __init__(self) -> None:
        self.html = html

    async def parse(self, text: str):
        delims = set()
        is_fixed_width = False

        for i, match in enumerate(re.finditer(MARKDOWN_RE, text)):
            start, _ = match.span()
            delim, text_url, url = match.groups()
            full = match.group(0)

            if delim in FIXED_WIDTH_DELIMS:
                is_fixed_width = not is_fixed_width

            if is_fixed_width and delim not in FIXED_WIDTH_DELIMS:
                continue

            if text_url:
                text = utils.replace_once(
                    text, full, URL_MARKUP.format(url, text_url), start
                )
                continue

            if delim == BOLD_DELIM:
                tag = "b"
            elif delim == ITALIC_DELIM:
                tag = "i"
            elif delim == UNDERLINE_DELIM:
                tag = "u"
            elif delim == STRIKE_DELIM:
                tag = "s"
            elif delim == CODE_DELIM:
                tag = "code"
            elif delim == PRE_DELIM:
                tag = "pre"
            elif delim == SPOILER_DELIM:
                tag = "spoiler"
            elif delim == QUOTE_DELIM:
                tag = "blockqoute"
            else:
                continue

            if delim not in delims:
                delims.add(delim)
                tag = OPENING_TAG.format(tag)
            else:
                delims.remove(delim)
                tag = CLOSING_TAG.format(tag)

            if delim == PRE_DELIM and delim in delims:
                delim_and_language = text[text.find(PRE_DELIM) :].split("\n")[0]
                language = delim_and_language[len(PRE_DELIM) :]
                text = utils.replace_once(
                    text, delim_and_language, f'<pre language="{language}">', start
                )
                continue

            if delim == QUOTE_DELIM and delim in delims:
                lines = text.split("\n")
                formatted_lines = []
                quote_block = False

                for line in lines:
                    if line.startswith(">"):
                        if not quote_block:
                            formatted_lines.append("<blockquote>")
                            quote_block = True
                        formatted_lines.append(line[1:])
                    else:
                        if quote_block:
                            formatted_lines.append("</blockquote>")
                            quote_block = False
                        formatted_lines.append(line)
                if quote_block:
                    formatted_lines.append("</blockquote>")

                return "\n".join(formatted_lines)

            text = utils.replace_once(text, delim, tag, start)
        return text


text = """>test
отступ
>test1 ksdmfkdfmkndfk
>test2 ndfkdjnjkfd
teeeest"""


async def main():
    md = Markdown()
    result = await md.parse(text)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
