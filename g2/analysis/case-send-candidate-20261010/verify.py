#!/usr/bin/env python3
"""Compare CASE framed send at its three lower provider boundaries."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/send_provider.c'
p=argparse.ArgumentParser();p.add_argument('--archive-object',action='store_true');a=p.parse_args()
if a.archive_object:
    obj=R/'g2/components/case/source_candidate_20261010/build/source_candidate_20261010__send_provider.c.o'
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    obj=H/'send.o';archive=None
    subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og',
                    '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
ld=H/'send_link.ld';ld.write_text('case_write_controller_blocking = 0x0010f001; g2_log_printf = 0x0010f101; log_hex_buffer = 0x0010f201; SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elfpath=H/'send.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='case_send')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
PAY=0x20007000;STOP=0x20000000
def cstr(u,x):
    b=bytearray()
    for i in range(80):
        q=u.mem_read(x+i,1)[0]
        if q==0:return bytes(b)
        b.append(q)
    raise AssertionError('unterminated format')
def run(original,payload,flags):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:])
    u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    for x in (0x10f000,0x10f100,0x10f200):u.mem_write(x,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\0'*0x10000)
    u.mem_write(PAY,payload)
    u.mem_write(0x20000895,bytes([flags[0]]));u.mem_write(0x200000bf,bytes([flags[1]]))
    calls=[]
    addresses={0x080066ac:'uart',0x08009170:'log',0x080067c8:'hex'} if original else {0x10f000:'uart',0x10f100:'log',0x10f200:'hex'}
    def hook(u,address,size,user):
        kind=addresses.get(address)
        if not kind:return
        r=[u.reg_read(i) for i in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        if kind=='uart':calls.append((kind,r[0],u.mem_read(r[1],1)[0],r[2],r[3]))
        elif kind=='log':calls.append((kind,cstr(u,r[0]),r[1]))
        else:calls.append((kind,bytes(u.mem_read(r[0],r[1])),r[1]))
        u.reg_write(UC_ARM_REG_R0,0)
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_R0,PAY);u.reg_write(UC_ARM_REG_R1,len(payload))
    u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x0800680d if original else entry|1,STOP,count=500000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP
    return calls,bytes(u.mem_read(PAY,len(payload))),u.reg_read(UC_ARM_REG_PRIMASK)
cases=[]
for length,flags in itertools.product((0,1,2,5,16,255,256),itertools.product((0,1),(0,1))):
    payload=bytes((i*37+length)%256 for i in range(length));x=run(True,payload,flags);y=run(False,payload,flags)
    assert x==y,(length,flags,x,y)
    cases.append((length,flags))
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),
     'archive_sha256':archive,'lengths':[0,1,2,5,16,255,256],'flags':[[0,0],[0,1],[1,0],[1,1]],
     'boundary':'UART single-byte calls, logger format/argument, hex buffer pointer contents and length.',
     'limits':['Lower UART/logger providers are intercepted, not source-defined here.','Payload length limited to tested 0..256; uint16 loop behavior above 65535 is outside valid contract.','No physical UART or delivery proof.']}
(H/('archive_results.json' if a.archive_object else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
