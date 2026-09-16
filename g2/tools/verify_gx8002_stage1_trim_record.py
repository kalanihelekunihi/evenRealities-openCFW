# SPDX-License-Identifier: MIT
"""Execute the flash-record validation slices, stopping before trim writes."""
import json,re,random,struct,subprocess
from functools import reduce
from operator import xor
from build_gx8002_stage1_clock_trim import build,ROOT
from verify_gx8002_memcpy_source import decode


def execute(code,start,accept,reject,base_reg,record):
    r={f'r{i}':0 for i in range(32)};r[base_reg]=0x20001000;pc=start;condition=False;reads=[]
    for _ in range(400):
        if pc in (accept,reject):return pc==accept,reads
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bt':
            if condition:nxt=int(p[0],0)
        elif op=='bnezad':
            r[p[0]]-=1
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='xor':r[p[0]]^=r[p[1]]
        elif op in ('ld.w','ld.b','ldbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            dest,base,off=m.groups();offset=r[base]+(int(off,0) if off else 0)-0x20001000;size=4 if op=='ld.w' else 1
            assert 0<=offset<=64-size;reads.append((offset,size));r[dest]=int.from_bytes(record[offset:offset+size],'little')
            if op=='ldbi.b':r[base]+=1
        else:raise AssertionError((pc,op,args))
        pc=nxt
    raise AssertionError('validation bound')


def verify():
    evidence=build();tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x38ed0','--stop-address=0x38ef2',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-stage1-clock-trim/trim.disassembly.txt').read_text())
    rng=random.Random(0x38e48);records=[]
    for _ in range(16):
        data=bytearray(rng.randrange(256) for _ in range(64));struct.pack_into('<I',data,0,0x47525553);data[63]=reduce(xor,data[:63]);records.append(bytes(data))
        for i in range(64):
            changed=data.copy();changed[i]^=1;records.append(bytes(changed))
    for data in records:
        expected=int.from_bytes(data[:4],'little')==0x47525553 and reduce(xor,data[:63])==data[63]
        a=execute(old,0x38ed0,0x38ef2,0x3911e,'r5',data)
        b=execute(new,0x1000056c,0x1000058e,0x10000770,'r4',data)
        assert a==b and a[0]==expected
        assert a[1]==([(0,4)] if int.from_bytes(data[:4],'little')!=0x47525553 else [(0,4)]+[(i,1) for i in range(64)])
    report={'cases':len(records),'build':evidence,'limits':['Only decoded record-validation slices after flash return, with supplied 64-byte record. Entry addresses intentionally pinned to this build; unsupported changes fail closed. Full trim, flash transfer, ABI and hardware execution remain unqualified.']}
    (ROOT/'docs/research/gx8002-stage1-trim-record.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'],'record validation cases passed')
