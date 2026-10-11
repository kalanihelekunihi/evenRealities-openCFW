#!/usr/bin/env python3
"""Compare CASE blocking UART writer at tick/wait child boundaries."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/uart_write_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');p.add_argument('--compose-tick',action='store_true');p.add_argument('--compose-wait',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__uart_write_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'uart_write.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld=H/'uart_write_link.ld';ld.write_text(('' if a.compose_tick or a.compose_wait else 'case_tick_word2 = 0x0010f001; ')+('' if a.compose_wait else 'case_wait_condition = 0x0010f101; ')+'SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
tickobj=(R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__tick_word_provider.c.o') if a.archive_object else H/'tick_word.o'
waitobj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__uart_wait_provider.c.o'
elfpath=H/'uart_write.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),*([str(tickobj)] if a.compose_tick or a.compose_wait else []),*([str(waitobj)] if a.compose_wait else []),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_write_controller_blocking')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
UART=0x20004000;REG=0x20005000;PAY=0x20007000;STOP=0x20000000;SP=0x2000f000
def w(u,x,v):u.mem_write(x,struct.pack('<I',v))
def run(original,state,length,cr1,parity,pointer,fail):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    for x in (0x10f000,0x10f100):u.mem_write(x,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    w(u,0x20000120,0x12345678)
    data=bytes((i*41+length)%256 for i in range(16));u.mem_write(PAY,data)
    w(u,UART,REG);w(u,UART+8,cr1);w(u,UART+16,parity);w(u,UART+0x88,state);w(u,UART+0x90,0xabcdef01)
    w(u,REG+0x28,0xdeadbeef)
    if a.compose_wait:w(u,REG+0x1c,0xc0)
    calls=[];waits=0
    tick=0x08004eac if original else 0x10f000
    wait=0x08008ec4 if original else 0x10f100
    def hook(u,address,size,user):
        nonlocal waits
        if not (a.compose_tick or a.compose_wait) and address==tick:
            calls.append(('tick',));u.reg_write(UC_ARM_REG_R0,0x12345678)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        elif not a.compose_wait and address==wait:
            waits+=1
            r=[u.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            timeout=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0]
            calls.append(('wait',*r,timeout))
            u.reg_write(UC_ARM_REG_R0,1 if waits==fail else 0)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    ptr=0 if pointer=='null' else PAY+(1 if pointer=='odd' else 0)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(UART,ptr,length,0x4567)):u.reg_write(reg,v)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x080066ad if original else entry|1,STOP,count=200000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(UART,0xa0)),
            bytes(u.mem_read(REG,0x40)),bytes(u.mem_read(PAY,16)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0x20,0x21),(0,1,2,3,5),(0,0x1000),(0,1),('aligned','odd','null'),(0,1,2,3,4,6)):
    state,length,cr1,parity,pointer,fail=vals
    if a.compose_wait and (vals[0]!=0x20 or vals[1]==0 or vals[4]!='aligned' or vals[5]!=0):continue
    x=run(True,*vals);y=run(False,*vals)
    assert x==y,(vals,[i for i,(q,z) in enumerate(zip(x,y)) if q!=z],x,y)
    cases.append(vals)
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'boundary':('Stock and source tick/wait execute with ready ISR flags.' if a.compose_wait else 'Stock tick and source tick execute; wait helper intercepted.' if a.compose_tick else 'case_tick_word2 and case_wait_condition intercepted; every wait argument and return branch compared.'),
     'limits':['Synthetic UART handle/peripheral register window.','Wait helper side effects are excluded.','No physical UART timing or delivery claim.']}
(H/('composed_wait_results.json' if a.compose_wait else 'composed_results.json' if a.compose_tick else 'archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
