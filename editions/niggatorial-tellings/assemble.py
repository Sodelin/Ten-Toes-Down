#!/usr/bin/env python3
"""Assemble this edition from its six complete, separately readable books."""
from pathlib import Path
import re

edition = Path(__file__).resolve().parent
expected = [17, 20, 24, 22, 23, 24]
books = []
for number, count in enumerate(expected, 1):
    path = edition / 'books' / f'book-{number:02}.md'
    text = path.read_text(encoding='utf-8').strip()
    chapters = re.findall(r'^## (\d+)\. ', text, re.M)
    assert list(map(int, chapters)) == list(range(1, count + 1)), path
    books.append(text)

front = '''# TEN TOES DOWN

# The Niggatorial Tellings

Written by ChatGPT for Nolan, following Nolan's creative direction.

Complete six-book revised edition · September 2026

'''
(edition / 'manuscript.md').write_text(front + '\n\n'.join(books) + '\n', encoding='utf-8')
print(edition / 'manuscript.md')
