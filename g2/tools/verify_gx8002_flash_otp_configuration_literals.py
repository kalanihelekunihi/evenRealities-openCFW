# SPDX-License-Identifier: MIT
"""Check linked OTP literal loads against actual section bytes and boundaries."""
import json,re,struct
from verify_gx8002_flash_otp_configuration_api import verify as qualify
from build_gx8002_flash_otp_configuration_candidate import ROOT,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def inspect(text,address,data):
    code=decode(text);loads=[]
    for line in text.splitlines():
        if not re.search(r'\blrw\s',line):continue
        match=re.search(r'^([0-9a-f]+):\s+[0-9a-f]+\s+lrw\s+r\d+,\s+(0x[0-9a-f]+)\s+//\s+([0-9a-f]+)',line)
        if not match:raise ValueError('Unrecognized literal disassembly')
        pc,value,cell=(int(v,16) for v in match.groups())
        if not (address<=pc<address+len(data) and address<=cell<=address+len(data)-4 and cell%4==0):raise ValueError('Literal outside own section')
        if struct.unpack_from('<I',data,cell-address)[0]!=value:raise ValueError('Literal contents mismatch')
        loads.append({'instruction':pc,'cell':cell,'value':value})
    if len(loads)!=3 or {r['cell'] for r in loads}!={0x10025d6c,0x10025d70}:raise ValueError('Unexpected literal layout')
    # Verify every decoded local branch stays in instructions before the pool.
    for pc,(op,args,width) in code.items():
        if op in ('br','bez','bnez','bhsz'):
            target=int(args.split(',')[-1].strip(),0)
            if not address<=target<0x10025d6c or target not in code:raise ValueError('Local branch leaves code')
    return loads


def verify():
    evidence=qualify();path=ROOT/'build/gx8002-board/flash-otp-configuration-candidate.elf';elf=Elf32(path.read_bytes(),str(path));section=next(s for s in elf.sections if s['name']=='.text');data=elf.contents(section)
    text=(path.with_suffix('.disassembly.txt')).read_text();loads=inspect(text,section['address'],data)
    rejected=0
    for cell in (0x10025d6c,0x10025d70):
        damaged=bytearray(data);damaged[cell-section['address']]^=1
        try:inspect(text,section['address'],damaged)
        except ValueError:rejected+=1
        else:raise AssertionError('Corrupt literal accepted')
    try:inspect(text.replace('// 10025d70','// 10025d84'),section['address'],data)
    except ValueError:rejected+=1
    else:raise AssertionError('External literal accepted')
    assert rejected==3
    return {'evidence':evidence,'literal_loads':loads,'negative_checks':rejected,'elf_sha256':sha(path.read_bytes()),'source_admitted':False,'limits':['All three disassembled literal loads resolve to two checked words contained within the 112-byte source section. Disassembler decoding trusted; three corrupted/out-of-envelope cases rejected. Candidate remains unregistered; retained hybrid OTP path still needs replacement.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-flash-otp-configuration-literals.json').write_text(json.dumps(r,indent=2)+'\n');print(len(r['literal_loads']))
