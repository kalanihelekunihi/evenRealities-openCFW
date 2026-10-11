#!/usr/bin/env python3
"""Compare stock and source hex dump at the printf child boundary."""
from pathlib import Path
import argparse,hashlib,itertools,json,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/hex_log_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__hex_log_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'hex.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld=H/'hex_link.ld';ld.write_text('g2_log_printf = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elfpath=H/'hex.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='log_hex_buffer')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
PAY=0x20007000;FLAG=0x200000bf;STOP=0x20000000
def cstr(u,x):
    out=bytearray()
    for i in range(20):
        b=u.mem_read(x+i,1)[0]
        if b==0:return bytes(out)
        out.append(b)
    raise AssertionError('unterminated format')
def run(original,payload,disabled,toggle_after):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_write(0x10f000,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    u.mem_write(PAY,payload);u.mem_write(FLAG,bytes([disabled]))
    calls=[];target=0x08009170 if original else 0x10f000
    def hook(u,address,size,user):
        if address!=target:return
        fmt=cstr(u,u.reg_read(UC_ARM_REG_R0));arg=u.reg_read(UC_ARM_REG_R1)
        calls.append((fmt,arg if fmt==b'%02x ' else None))
        if toggle_after is not None and len(calls)==toggle_after:u.mem_write(FLAG,b'\1')
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_R0,PAY);u.reg_write(UC_ARM_REG_R1,len(payload))
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x080067c9 if original else entry|1,STOP,count=500000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return calls,u.mem_read(FLAG,1)[0],bytes(u.mem_read(PAY,len(payload))),u.reg_read(UC_ARM_REG_PRIMASK)
cases=[]
for length,disabled,toggle in itertools.product((0,1,2,5,16,255,256),(0,1),(None,1,2)):
    payload=bytes((i*17+length)%256 for i in range(length))
    x=run(True,payload,disabled,toggle);y=run(False,payload,disabled,toggle)
    assert x==y,(length,disabled,toggle,x,y)
    cases.append((length,disabled,toggle))
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'boundary':'Printf format string and byte argument; dynamic disable flag after child calls.',
     'limits':['Printf is intercepted, not source-defined here.','Only readable buffers with length <=65535 are valid.','No physical logger output claim.']}
(H/('archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
