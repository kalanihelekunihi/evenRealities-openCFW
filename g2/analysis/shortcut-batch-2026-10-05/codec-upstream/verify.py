#!/usr/bin/env python3
"""Reproduce raw no-hit and existing controls; deliberately not relocation matching."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
def sha(b): return hashlib.sha256(b).hexdigest()
e=json.loads(Path(__file__).with_name('evidence.json').read_text())
b=(ROOT/e['target']['path']).read_bytes(); c=e['selected_candidate']; o=(ROOT/c['object']).read_bytes()
assert sha(b)==e['target']['sha256'] and sha(o)==c['object_sha256']
assert o[:6]==b'\x7fELF\x01\x01'
h=struct.unpack_from('<16sHHIIIIIHHHHHH',o)
sections=[struct.unpack_from('<IIIIIIIIII',o,h[6]+i*h[11]) for i in range(h[12])]
s=sections[h[13]]; names=o[s[4]:s[4]+s[5]]; found=False
for s in sections:
    name=names[s[0]:].split(b'\0',1)[0].decode()
    if name==c['text_section']:
        raw=o[s[4]:s[4]+s[5]]
        assert sha(raw)==c['text_section_sha256'] and len(raw)==c['text_section_size']
        assert b.find(raw)==-1; found=True
    if name==c['relocation_section']:
        assert s[5]==132 and s[9]==12 and s[5]//s[9]==11
assert found
for r in e['prior_matches_reproduced_but_excluded']:
    off=int(r['payload_offset'],16)
    assert sha(b[off:off+r['size']])==r['sha256']
print('PASS: candidate raw no-hit, 11 relocations, six prior controls; zero new attribution')
