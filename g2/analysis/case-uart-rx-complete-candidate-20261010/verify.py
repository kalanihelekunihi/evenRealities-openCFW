#!/usr/bin/env python3
"""Compare stock RX completion parser with source composition and event boundary."""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
H=Path(__file__).resolve().parent;R=H.parents[2]
fw=(R/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(fw).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
src=R/'g2/components/case/source_candidate_20261010/uart_rx_complete_callback.c'
p=argparse.ArgumentParser();p.add_argument('--archive-objects',action='store_true');a=p.parse_args()
names=('frame_callback_offline/frame.c','uart_start_offline/start.c','source_candidate_20261010/uart_read_provider.c',
       'source_candidate_20261010/uart_wait_provider.c','source_candidate_20261010/tick_word_provider.c',
       'source_candidate_20261010/uart_rx_complete_callback.c')
if a.archive_objects:
    B=R/'g2/components/case/source_candidate_20261010/build'
    objects=[B/(name.replace('/','__')+'.o') for name in names]
    archive=json.loads((R/'g2/analysis/case-source-candidate-round2-20261010/receipt.json').read_text())['archive_sha256']
else:
    objects=[];archive=None
    for name in names:
        source=R/'g2/components/case'/name;obj=H/(name.replace('/','__')+'.o')
        subprocess.run(['clang','--target=armv6m-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Og','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
        objects.append(obj)
ld=H/'callback_link.ld';ld.write_text('case_event_post = 0x0010f001; SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }\n')
elfpath=H/'callback.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elfpath)],check=True)
with elfpath.open('rb') as f:
    e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='HAL_UART_RxCpltCallback')
    seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
UART=0x20000e24;REG=0x40013800;FRAME=0x20000974;CTX=0x20000108;STOP=0x20000000
def w(u,x,v):u.mem_write(x,struct.pack('<I',v))
def run(original,count,prefix,ch,state,instance,last):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
    u.mem_map(0x08000000,0x10000);u.mem_write(0x08000000,fw[32:]);u.mem_map(0x100000,0x10000)
    for x,b in seg:u.mem_write(x,bytes(b))
    u.mem_write(0x10f000,b'\x70\x47')
    u.mem_map(0x20000000,0x10000);u.mem_write(0x20000000,b'\xa5'*0x10000)
    u.mem_map(0x40013000,0x1000);u.mem_write(0x40013000,b'\0'*0x1000)
    u.mem_write(FRAME,b'\xa7'*1200);u.mem_write(FRAME,bytes(prefix))
    u.mem_write(CTX,struct.pack('<BBH',ch,last,count));w(u,0x200000f0,0x20006000)
    w(u,UART,instance);w(u,UART+8,0);w(u,UART+16,0);w(u,UART+0x64,0);w(u,UART+0x70,0)
    w(u,UART+0x8c,state);w(u,UART+0x90,0);w(u,0x20000120,0x12345678)
    w(u,REG,0);w(u,REG+4,0);w(u,REG+8,0);w(u,REG+0x1c,0x20);w(u,REG+0x24,0x35)
    calls=[];target=0x0800a888 if original else 0x10f000
    def hook(u,address,size,user):
        if address!=target:return
        calls.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.reg_write(UC_ARM_REG_R0,UART);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,STOP|1)
    u.emu_start(0x08006545 if original else entry|1,STOP,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==STOP,(original,count,prefix,ch,state,hex(instance),hex(u.reg_read(UC_ARM_REG_PC)))
    return (calls,bytes(u.mem_read(0x20000000,0x2000)),bytes(u.mem_read(REG,0x40)),u.reg_read(UC_ARM_REG_PRIMASK))
prefixes=((0x5a,0xa5,0x7f,2,0),(0x5a,0xa5,0xcf,2,0),(ord('D'),ord('E'),0,0,0),
          (ord('d'),ord('f'),0,0,0),(0x5a,0,0xcf,255,255),(0x33,0,0,0,0))
cases=[]
for vals in itertools.product((0,1,2,3,4,5,7,59,1199,1200),prefixes,(0,0x5a,0xa5,0x7f,0xcf,ord('D'),ord('d'),10,255),(0x20,0x22),(0x40013800,0x40004400),(0,0x5a)):
    if vals[0]==4 and vals[1][2]==0xcf and vals[2]>0:continue
    x=run(True,*vals);y=run(False,*vals)
    assert x==y,(vals,[i for i,(q,z) in enumerate(zip(x,y)) if q!=z])
    cases.append(vals)
rec={'status':'PASS','cases':len(cases),'firmware_sha256':hashlib.sha256(fw).hexdigest(),
     'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
     'object_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in objects},'archive_sha256':archive,
     'boundary':'Original/source bulk receive, tick, wait and rearm execute; event post calls intercepted with argument comparison.',
     'limits':['Synthetic coherent frame/UART state; event-group side effects are excluded.','No physical UART, real scheduler, allocation or buffer lifetime proof.']}
(H/('archive_results.json' if a.archive_objects else 'results.json')).write_text(json.dumps(rec,indent=2)+'\n')
print(json.dumps({'status':'PASS','cases':len(cases)}))
