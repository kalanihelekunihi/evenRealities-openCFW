#!/usr/bin/env python3
"""Normalize addresses, relocations, and branch destinations; retain opcode/register/dataflow shape."""
import re, sys
src, dst = sys.argv[1:3]
lines=[]
pat=re.compile(r'^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2,8}\s+)+)\s*([.A-Za-z][.A-Za-z0-9]*)\s*(.*)$')
for raw in open(src, encoding='utf-8', errors='replace'):
    m=pat.match(raw)
    if not m: continue
    mnemonic=m.group(3).lower()
    operands=m.group(4).strip().lower()
    if mnemonic.startswith('r_arm_'): continue
    operands=re.sub(r'\s*;.*$', '', operands)
    operands=re.sub(r'<[^>]*>', '<symbol>', operands)
    operands=re.sub(r'\b0x[0-9a-f]+\b', '0ximm', operands)
    if mnemonic in ('bl','blx'):
        operands='<call>'
    elif mnemonic == 'b' or (mnemonic.startswith('b') and mnemonic not in ('bic','bics','bkpt')):
        operands='<branch>'
    elif mnemonic in ('cbz','cbnz'):
        reg=operands.split(',',1)[0]
        operands=reg+',<branch>'
    if mnemonic in ('movw','movt'):
        operands=re.sub(r'#(?:0x)?[0-9a-f]+', '#reloc', operands)
    if mnemonic.startswith('ldr') and '[pc,' in operands:
        operands=re.sub(r'#(?:0x)?[0-9a-f]+', '#pcrel', operands)
    if mnemonic in ('.word','.short'):
        operands='<literal>'
    operands=re.sub(r'\s+', ' ', operands)
    operands=re.sub(r'\s*,\s*', ',', operands)
    lines.append(mnemonic + ((' ' + operands) if operands else ''))
open(dst,'w',encoding='utf-8').write('\n'.join(lines)+'\n')
