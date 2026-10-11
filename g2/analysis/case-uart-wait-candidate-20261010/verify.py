#!/usr/bin/env python3
"""Compare CASE UART wait, including timeout and error cleanup branches."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/uart_wait_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__uart_wait_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'wait.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld=H/'wait_link.ld';ld.write_text('case_tick_word2 = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elfpath=H/'wait.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_wait_condition')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
UART=0x20004000;REG=0x20005000;STOP=0x20000000;SP=0x2000f000
def w(u,x,v):u.mem_write(x,struct.pack('<I',v))
def run(original,flag,expected,isr,cr1,cr3,timeout,start,elapsed,primask):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_write(0x10f000,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    w(u,UART,REG);w(u,UART+0x84,0x12345678);w(u,UART+0x88,0x21);w(u,UART+0x8c,0x22);w(u,UART+0x90,0x11223344)
    w(u,REG,cr1);w(u,REG+8,cr3);w(u,REG+28,isr);w(u,REG+32,0xabcdef00)
    calls=[];target=0x08004eac if original else 0x10f000
    def hook(u,address,size,user):
        if address!=target:return
        calls.append('tick')
        # On a non-expired ordinary wait, peripheral status changes after one tick.
        if elapsed<=timeout and timeout!=0 and not (cr1&4 and isr&0x800):
            current=struct.unpack('<I',u.mem_read(REG+28,4))[0]
            w(u,REG+28,current ^ flag)
        u.reg_write(UC_ARM_REG_R0,(start+elapsed)&0xffffffff)
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(UART,flag,expected,start)):u.reg_write(reg,v)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,STOP|1)
    w(u,SP,timeout);u.reg_write(UC_ARM_REG_PRIMASK,primask)
    u.emu_start(0x08008ec5 if original else entry|1,STOP,count=20000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return (u.reg_read(UC_ARM_REG_R0),calls,bytes(u.mem_read(UART,0xa0)),bytes(u.mem_read(REG,0x40)),u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for vals in itertools.product((0x40,0x80),(0,1),(0,0x40,0x80,0x800,0x880),(0,4,0x1a4),(0,1),(0,1,5,0xffffffff),(0,0xfffffff0),(1,2,7),(0,1)):
    flag,expected,isr,cr1,cr3,timeout,start,elapsed,primask=vals
    observed=int((flag & ~isr)==0)
    if timeout==0xffffffff and observed==expected:continue
    x=run(True,*vals);y=run(False,*vals)
    assert x==y,(vals,[i for i,(q,z) in enumerate(zip(x,y)) if q!=z],x,y)
    cases.append(vals)
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'boundary':'Tick getter return and scripted peripheral ISR evolution; all UART/peripheral bytes and PRIMASK compared.',
     'limits':['Synthetic UART/peripheral state; hardware register side effects not modeled.','Infinite wait with unchanged status is excluded.','No physical UART timing or delivery proof.']}
(H/('archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
