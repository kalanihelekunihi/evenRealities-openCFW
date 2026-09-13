# SPDX-License-Identifier: MIT
"""Compose initializer writes and configuration on compiled UART defaults."""
import json,struct,subprocess
from itertools import product
from pathlib import Path
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode
from verify_gx8002_uart_initialize import execute as initialize
from execute_gx8002_uart_configure import execute as configure
from verify_gx8002_uart_configure import arithmetic
ROOT=Path(__file__).resolve().parents[1]

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');stock=elf.contents(next(s for s in elf.sections if s['name']=='.data'));assert sha(stock)==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc8ec','--stop-address=0x17574',str(path)],text=True))
    paths={};codes={};reports={}
    for kind,file in (('uart-initialize','initialize.elf'),('uart-configure','configure.elf')):
        # Existing source artifact is read only, so concurrent full build inputs remain unchanged.
        path=ROOT/'build/gx8002-source-candidate'/kind/file
        if not path.exists() and kind=='uart-configure':path=ROOT/'build/gx8002-uart-configure-source/configure.elf'
        e=Elf32(path.read_bytes(),kind);report=json.loads((ROOT/'docs/research'/('gx8002-'+kind+'-source-verification.json')).read_text());s=next(s for s in e.sections if s['name']=='.text');assert sha(e.contents(s))==report['functions'][0]['compiled_sha256']
        paths[kind]=sha(path.read_bytes());codes[kind]=decode(subprocess.check_output([pre,'-d',str(path)],text=True));reports[kind]=report
    path=ROOT/'build/gx8002-board/uart-descriptor.elf';elf=Elf32(path.read_bytes(),'defaults');s=next(s for s in elf.sections if s['name']=='.descriptors');body=elf.contents(s);assert body==stock[0x18aa8:0x18ba8] and s['address']==0x20026a94
    provenance=json.loads((ROOT/'docs/research/gx8002-uart-descriptor-candidate.json').read_text());assert sha(path.read_bytes())==provenance['elf_sha256'];assert sha((ROOT/'components/shared/gx8002/runtime_gx8002_uart_storage.c').read_bytes())==provenance['source_sha256']
    symbols=dict(uint=0x13a5c,divide=0x13894,multiply=0x13694,add=0x13628,fix=0x12ff8,pack=0x13b00,unpack=0x13c90,integer=0x13ab4,core=0x13364,compare=0x139ac,compare_parts=0x13d74,signed=0x139ec,subtract=0x13658,fifo=0xc8ec,irq=0xffe2eac8)
    names=dict(uint='__floatunsidf',divide='__divdf3',multiply='__muldf3',add='__adddf3',fix='__fixunsdfsi',fifo='open_cfw_gx8002_uart_fifo_depth',irq='open_cfw_gx8002_request_irq')
    oldhelpers={symbols[k]:k for k in names};newhelpers={reports['uart-configure']['bindings'][v]:k for k,v in names.items()};numeric=arithmetic(old,symbols);cases=0
    for port,baud,clock in product((0,1),(0,9600,115200),(23999900,24000000,24000100,24000101)):
        base=0x20026a94+128*port;defaults=list(struct.unpack_from('<32I',body,128*port));device=defaults[1];regs={device+i:0 for i in range(0,256,4)};results=[]
        for initcode,entry,helpers,configcode,configentry,confighelpers in ((old,0xcabc,{0xffe2e60c:'gate',0xffe2e79c:'frequency',0xc954:'configure'},old,0xc954,oldhelpers),(codes['uart-initialize'],0x10203530,{0x10025080:'gate',0x10025210:'frequency',0x102033c8:'configure'},codes['uart-configure'],0x102033c8,newhelpers)):
            nested=[]
            def hook(pointer,trace):
                assert pointer==base;d=defaults.copy()
                for event in trace:
                    if event[0]=='write':
                        assert event[1] in (base+12,base+16);d[(event[1]-base)//4]=event[2]
                result=configure(configcode,configentry,d,regs,confighelpers,numeric,16,descriptor_base=base);nested.append(result);return result[0]
            result=initialize(initcode,entry,port,baud,clock,0,helpers,configure_hook=hook)
            assert len(nested)==1 and result[0]==0
            results.append((result,nested[0]))
        assert results[0]==results[1]
        memory=results[0][1][1];remainder=clock%1000000;rounded=clock-remainder if remainder<=100 else clock+1000000-remainder if remainder>=999900 else clock
        assert memory[base+12]==rounded and memory[base+16]==baud
        assert memory[base+28]==8 and memory[base+32]==1 and memory[base+44]==1 and memory[base+48]==16
        if baud:assert memory[base+20]==rounded//(baud*16)
        assert memory[base+104]==memory[base+124]==0xffffffff
        assert memory[device+12]==3
        cases+=1
    return {'cases':cases,'source_artifacts_sha256':paths,'defaults_elf_sha256':sha(path.read_bytes()),'source_admitted':False,'hardware_qualified':False,'limits':['Actual compiled defaults and initializer writes feed decoded configuration, comparing stock/source traces and final state.','Gate/frequency/FIFO/IRQ effects modeled; arithmetic executes decoded stock helper bodies in isolated frames. No physical UART execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-defaults-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print('UART defaults initialization cases:',r['cases'])
