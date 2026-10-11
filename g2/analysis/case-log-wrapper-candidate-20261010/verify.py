#!/usr/bin/env python3
"""Compare stock and source log wrapper/byte callback at lower boundaries."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/log_wrapper_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__log_wrapper_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'wrapper.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld=H/'wrapper_link.ld';ld.write_text('case_vformat = 0x0010f001; case_write_controller_blocking = 0x0010f101; SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elfpath=H/'wrapper.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
STOP=0x20000000;FMT=0x20007000
def cstr(u,x):
    out=bytearray()
    for i in range(80):
        b=u.mem_read(x+i,1)[0]
        if not b:return bytes(out)
        out.append(b)
    raise AssertionError('unterminated format')
def setup():
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    for x in (0x10f000,0x10f100):u.mem_write(x,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    return u
def wrapper(original,fmt,words):
    u=setup();u.mem_write(FMT,fmt+b'\0');u.mem_write(0x2000f000,struct.pack('<II',*words[3:]))
    calls=[];target=0x08009210 if original else 0x10f000
    def hook(u,address,size,user):
        if address!=target:return
        r=[u.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        args=struct.unpack('<IIIII',u.mem_read(r[1],20))
        expected_cb=0x0800a381 if original else syms['case_log_output_char']|1
        assert r[3]==expected_cb,(hex(r[3]),hex(expected_cb))
        calls.append((cstr(u,r[0]),args,r[2],bool(r[3])))
        u.reg_write(UC_ARM_REG_R0,0x1234);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(FMT,*words[:3])):u.reg_write(reg,value)
    u.emu_start(0x08009171 if original else syms['g2_log_printf']|1,STOP,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK)
def callback(original,ch,context):
    u=setup();calls=[];target=0x080066ac if original else 0x10f100
    def hook(u,address,size,user):
        if address!=target:return
        r=[u.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        calls.append((r[0],u.mem_read(r[1],1)[0],r[2],r[3]))
        u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_R0,ch);u.reg_write(UC_ARM_REG_R1,context)
    u.emu_start(0x0800a381 if original else syms['case_log_output_char']|1,STOP,count=50000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return calls,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK)
cases=0
for fmt,words in itertools.product((b'',b'%02x ',b'%s %08x %u',b'plain'),
                                    ((0,0,0,0,0),(1,2,3,4,5),(0x12345678,0xabcdef01,0xffffffff,0xdeadbeef,0xfacecafe))):
    x=wrapper(True,fmt,words);y=wrapper(False,fmt,words)
    assert x==y,(fmt,words,x,y);cases+=1
for ch,context in itertools.product((0,1,0x41,0xff,0x12345678),(0,0x200001a0,0xabcdef01)):
    x=callback(True,ch,context);y=callback(False,ch,context)
    assert x==y,(ch,context,x,y);cases+=1
rec={'status':'PASS','cases':cases,'wrapper_cases':12,'output_callback_cases':15,
     'firmware_sha256':hashlib.sha256(fw).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
     'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'archive_sha256':archive,
     'boundary':'Variadic word stream and formatter context/callback; UART output byte arguments and return.',
     'limits':['case_vformat and case_write_controller_blocking are lower imports.','No formatter or physical UART output claim.']}
(H/('archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':cases}))
