# SPDX-License-Identifier: MIT
"""Stateful token sequence oracle for decoded stock and reconstructed C."""
import json,subprocess
from itertools import product
from build_gx8002_strtok import build,ROOT
from execute_gx8002_strtok import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify(backup=False):
    candidate=build(backup=backup);p=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    from build_gx8002_backup_cfft import IMAGE,IMAGE_SHA,sha,Elf32
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=Elf32(p.read_bytes(),'stock');assert wrapper.contents(next(s for s in wrapper.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x49c14' if backup else '--start-address=0x12ee8','--stop-address=0x49c84' if backup else '--stop-address=0x12f58',str(p)],text=True))
    new=decode((ROOT/('build/gx8002-backup-strtok/candidate.disassembly.txt' if backup else 'build/gx8002-strtok/candidate.disassembly.txt')).read_text());cases=0
    for data,delimiters,saved_seed in product((b'',b'a',b'0.0.2.3',b'..a..b.',b'aaa',b'a,b.c',b'\x80a\xffb'),(b'',b'.',b'a',b',.',b'\x80\xff'),(0,1,0xffffffff,0x20050003)):
        initial={0x20050000+i:v for i,v in enumerate(data+b'\0')};initial.update({0x20051000+i:v for i,v in enumerate(delimiters+b'\0')});initial.update({(0x2002d3e0 if backup else 0x2002e934)+i:(saved_seed>>(8*i))&255 for i in range(4)})
        expected=initial.copy(); states=[initial.copy(),initial.copy()];cursor=0x20050000
        for call in range(len(data)+3):
            if cursor:
                while expected[cursor] and expected[cursor] in delimiters:cursor+=1
                token=cursor if expected[cursor] else 0
                if token:
                    while expected[cursor] and expected[cursor] not in delimiters:cursor+=1
                    if expected[cursor]:expected[cursor]=0;cursor+=1
                    else:cursor=0
                else:cursor=0
            else:token=0
            word(expected,0x2002d3e0 if backup else 0x2002e934,cursor)
            def helper(*args):raise ValueError('Unexpected helper')
            for index,(code,entry) in enumerate(((old,0x49c14 if backup else 0x12ee8),(new,0x49c14-0x3b940+0x10003000 if backup else 0x1020995c))):
                ret,states[index],events=execute(code,entry,[0 if call else 0x20050000,0x20051000],states[index],helper)
                assert ret==('return',token) and states[index]==expected,(data,delimiters,call,ret,token)
            cases+=1
    return {'candidate':candidate,'calls':cases,'source_admitted':False,'limits':['Sequential token/state oracle and integer ABI pass; nested application execution unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-strtok-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['calls'])
