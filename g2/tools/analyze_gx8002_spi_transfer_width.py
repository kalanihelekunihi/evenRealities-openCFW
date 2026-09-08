#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exhaustive decoded width selection; analysis only, no firmware emission."""
import json
import subprocess
from analyze_gx8002_dw_spi_quick_transfer import analyze, ROOT
from verify_gx8002_memcpy_source import decode

BASE = 0x10206204


def decoded_width(code, bits):
    r = {'r2':0,'r21':8,'r22':1,'r23':32}
    pc = BASE+0x8c
    condition = False
    width = None
    final_bits = bits
    for _ in range(20):
        if pc == BASE+0xa4:
            return final_bits,width
        op,args,size = code[pc]
        p = [s.strip() for s in args.split(',')]
        nxt = pc+size
        if op=='ld.b' and args=='r2, (r1, 0xd)':
            r['r2'] = bits
        elif op=='bez':
            if r[p[0]]==0:
                nxt=int(p[1],0)
        elif op=='addi':
            r[p[0]]+=int(p[1],0)
        elif op=='andi':
            r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmpnei':
            condition=r[p[0]]!=int(p[1],0)
        elif op=='incf':
            if not condition:
                r[p[0]]=r[p[1]]+int(p[2],0)
        elif op=='lsri':
            r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='st.b' and args.endswith('(r4, 0x28)'):
            width=r[p[0]]&255
        elif op=='st.b' and args.endswith('(r1, 0xd)'):
            final_bits=r[p[0]]&255
        elif op=='br':
            nxt=int(args,0)
        else:
            raise ValueError('Unexpected width instruction '+op+' '+args)
        pc=nxt
    raise ValueError('Width step bound')


def verify():
    attribution=analyze()
    path=ROOT/'build/gx8002-board/dw-spi-quick-transfer-oracle.elf'
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(path)],text=True))
    rows=[]
    for bits in range(256):
        actual=decoded_width(code,bits)
        # Independently expressed eight-bit rounded bit-count arithmetic.
        width=1 if bits==0 else ((bits+7)//8)%32
        if width==3:
            width=4
        wanted=(bits or 8,width)
        if actual!=wanted:
            raise ValueError('Width mismatch '+str(bits))
        rows.append({'input_bits':bits,'stored_bits':actual[0],'element_bytes':actual[1]})
    return {'attribution':attribution,'decoded_cases':256,'mapping':rows,
            'zero_width_inputs':[r['input_bits'] for r in rows if r['element_bytes']==0],
            'source_admitted':False,
            'limits':['Width selection only; no complete transfer or hardware proof. Widths other than 1, 2 and 4 have no matching data-access branch; zero width reaches later division.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-spi-transfer-width.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Verified',report['decoded_cases'],'width inputs; zero widths:',report['zero_width_inputs'])
