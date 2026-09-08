#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify conditional IRQ15 controller reads against decoded stock/source."""
import contextlib,io,json,re,shutil,struct,subprocess
from build_gx8002_flash_interrupt import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths

def execute(code,pc,events):
    r={f'r{i}':0x12340000+i for i in range(32)};initial=r.copy();index=0
    for _ in range(30):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('lsli','andi'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=(a<<b if op=='lsli' else a&b)&0xffffffff
        elif op=='bez':
            if not r[p[0]]:n=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,offset=m.groups();address=r[base]+int(offset,0)
            if index>=len(events) or events[index][0]!=address:raise ValueError('unexpected read')
            r[reg]=events[index][1];index+=1
        elif op=='rts':
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('return mismatch')
            return r['r0']
        else:raise ValueError('unknown interrupt instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    row=evidence['functions'][0]
    if not row['fits']:raise ValueError('interrupt envelope exceeded')
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'flash-interrupt-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15ad4','--stop-address=0x15af4',str(wrapper)],text=True));new=decode((out/'flash-interrupt-linked.disassembly.txt').read_text());cases=0
    for status in [*range(256),*[1<<i for i in range(8,32)],0xffffffff,0x8000000a]:
        for value in (0,0xffffffff,0xa5a5a5a5):
            events=[[0xa2000030,status]]
            if status&2:events.append([0xa2000038,value])
            if status&8:events.append([0xa200003c,value^0xffffffff])
            if execute(old,0x15ad4,events)!=0 or execute(new,0x10023ac0,events)!=0:raise ValueError('interrupt result')
            cases+=1
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'flash-interrupt.elf',output/'flash-interrupt.elf')
    return {'functions':[{'symbol':row['symbol'],'section_name':row['section'],'compiled_bytes':row['compiled_bytes'],'compiled_sha256':row['compiled_sha256'],
      'stock_occurrences':[{'symbol':row['symbol'],'package_offset':row['package_offset'],'bytes':row['stock_envelope_bytes'],'sha256':row['stock_sha256'],'region':'image_a_sram_text'}]}],
      'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,
      'limits':['Ordered register reads qualified; physical IRQ timing and hardware register side effects remain unqualified.']}
if __name__=='__main__':
    (ROOT/'docs/research/gx8002-flash-interrupt-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
