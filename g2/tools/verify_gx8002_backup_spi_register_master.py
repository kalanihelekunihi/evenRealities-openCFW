#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded SPI list insertion and first flash binding against independent model."""
import json,re,shutil,struct,subprocess
from itertools import product
from build_gx8002_backup_spi_register_master import ROOT,IMAGE,build,sha,IMAGE_SHA,Elf32
from model_gx8002_backup_spi_register_master import Case,Model,expected,MASK
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
OFFSET=0x40b58
ADDRESS=0x10008218


def execute(code,pc,case):
    m=Model(case);r={f'r{i}':(case.seed^i*0x1020304)&MASK for i in range(32)}
    r['r0']=case.master;initial=r.copy();condition=False
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('ld.w','ld.b','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('SPI memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
            if op=='st.w':m.write(address,r[reg])
            else:r[reg]=m.read_byte(address) if op=='ld.b' else m.read(address)
        elif op in ('cmpne','cmphs'):
            condition=r[p[0]]!=r[p[1]] if op=='cmpne' else r[p[0]]>=r[p[1]]
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):nxt=int(args,0)
        elif op in ('bez','blz'):
            if r[p[0]]==0 if op=='bez' else bool(r[p[0]]&0x80000000):nxt=int(p[1],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SPI leaf ABI')
            return m.trace,m.words,r['r0']
        else:raise ValueError('SPI unknown instruction '+op)
        pc=nxt
    raise ValueError('SPI execution bound')


def programs():
    out=ROOT/'build/gx8002-backup-spi-register-master';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    path=out/'spi-register-master-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(path)],check=True)
    data=bytearray(path.read_bytes());struct.pack_into('<I',data,36,0x21006009);path.write_bytes(data)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x40b58','--stop-address=0x40bbc',str(path)],text=True))
    elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    return old,decode((out/'spi-register-master-candidate.disassembly.txt').read_text())


def verify(prefix=None,sdk=None,output=None):
    evidence=build();old,new=programs();cases=0
    lists=((),((0,0),),((1,0),(0,0)),((0,255),(0,1),(0,0)),((0,0),(0,0)),tuple((i%3,i*31) for i in range(8)))
    for bus,selects,old_count,flashes,seed in product((0,1,2,0x7fffffff,0x80000000,MASK),(0,1,2,255,256,MASK),range(4),lists,(0,MASK,0x12345678)):
        case=Case(bus=bus,selects=selects,old_count=old_count,flashes=flashes,seed=seed);wanted=expected(case)
        if execute(old,OFFSET,case)!=wanted or execute(new,ADDRESS,case)!=wanted:raise ValueError('SPI registration mismatch')
        cases+=1
    case=Case(master=0)
    if execute(old,OFFSET,case)!=expected(case) or execute(new,ADDRESS,case)!=expected(case):raise ValueError('SPI null rejection')
    cases+=1
    if not evidence['fits']:raise ValueError('SPI envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':100,'sha256':evidence['stock_sha256'],'region':'image_b_sram_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/spi-register-master-candidate.elf',output/'spi-register-master.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'model_sha256':sha((ROOT/'tools/model_gx8002_backup_spi_register_master.py').read_bytes()),'source_admitted':False,'hardware_qualified':False,
            'limits':['Ordered word/byte reads, insertion writes, first eligible binding and leaf ABI on bounded valid lists. Invalid pointers, repeated registration, malformed/concurrent lists excluded.']}


if __name__=='__main__':
    (ROOT/'docs/research/gx8002-backup-spi-register-master-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
