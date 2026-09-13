# SPDX-License-Identifier: MIT
"""Byte-exact source admission with independent offset memory checks."""
import json,re,shutil
from build_gx8002_bionic_offsets import build,ROOT,IMAGE,sha,Elf32
from verify_gx8002_logging import check_paths
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();path=ROOT/'build/gx8002-bionic-offsets/offsets.elf';elf=Elf32(path.read_bytes(),str(path));code=decode((path.parent/'offsets.disassembly.txt').read_text());rows=[];cases=0
    for item in evidence['functions']:
        name=item['symbol'];sec=next(s for s in elf.sections if s['name']=='.text.'+name)
        if not item['fits'] or not item['exact_stock_prefix'] or sec['address']!=item['package_offset']+0x101f6a74:raise ValueError('Exact placement')
        for value in (0,1,0xffffffff,0x80000000,0x7f800000,0xff800000,0x7fc12345,0x7f812345,0x43160000):
            m={0x2002e83c+i:(i*37)&255 for i in range(48)};word(m,0x2002e850,value);expected=m.copy();r={f'r{i}':0xabc00000+i for i in range(32)};initial=r.copy();floating=0x12345678;events=[];pc=sec['address']
            for _ in range(12):
                op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
                if op=='rts':break
                if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
                elif op in ('flds','st.w'):
                    reg,base,offset=re.fullmatch(r'((?:fr|r)\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(offset,0)
                    if op=='flds':floating=word(m,address)
                    else:word(m,address,r[reg]);events.append((address,r[reg]))
                else:raise ValueError(('Opcode',op))
                pc+=width
            else:raise ValueError('Execution bound')
            clear=name.endswith('bunkws_offset_clear');getter=name.endswith('bunkws_offset')
            if clear:word(expected,0x2002e858,0);word(expected,0x2002e850,0)
            if m!=expected or floating!=(value if getter else 0x12345678) or events!=([(0x2002e858,0),(0x2002e850,0)] if clear else []):raise ValueError('Memory/float oracle')
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            cases+=1
        rows.append({'symbol':name,'section_name':sec['name'],'compiled_bytes':item['compiled_bytes'],'compiled_sha256':item['compiled_sha256'],'stock_occurrences':[{'symbol':name,'package_offset':item['package_offset'],'bytes':item['stock_envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]})
    if output:output.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,output/'offsets.elf')
    return {'functions':rows,'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Exact compiled stock instruction prefixes and guarded leaf memory oracle. No floating arithmetic; NaN bit patterns transported unchanged. Hardware concurrency unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-bionic-offsets-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
