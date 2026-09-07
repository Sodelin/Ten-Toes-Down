#!/usr/bin/env python3
"""Verify every chapter's complete word sequence survived EPUB conversion."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json
import re

edition = Path(__file__).resolve().parent
tokens = lambda text: re.findall(r"\w+(?:['’]\w+)*", text, flags=re.UNICODE)
chapters_checked = 0
words_checked = 0
with ZipFile(edition / 'book.epub') as archive:
    for book in range(1, 7):
        source = (edition / 'books' / f'book-{book:02}.md').read_text()
        chapters = re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', source, re.M | re.S)
        for chapter, (title, body) in enumerate(chapters, 1):
            filename = f'OEBPS/book-{book}-chapter-{chapter:02}.xhtml'
            tree = ET.fromstring(archive.read(filename))
            rendered = tree.find('{http://www.w3.org/1999/xhtml}body')
            actual = tokens('\n'.join(''.join(child.itertext()) for child in rendered))
            expected = tokens(title + '\n' + body)
            assert actual == expected, f'Complete chapter text differs: {filename}'
            chapters_checked += 1
            words_checked += len(expected)

assert chapters_checked == 130, chapters_checked
result = {'epub_complete_chapter_word_sequences_match': True,
          'chapters_checked': chapters_checked, 'word_tokens_compared': words_checked}
(edition / 'complete-text-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
