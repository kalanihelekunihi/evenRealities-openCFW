#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/bootloader/source_candidate_20261010/queue_create_static.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'queue-create-static-candidate.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,opencfw_bl_kernel_queue_create_static','-Wl,--defsym=opencfw_boot_kernel_queue_reset=0x419be9','-Wl,--defsym=opencfw_bl_mask_interrupts=0x41b2f9',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='opencfw_bl_kernel_queue_create_static')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
CB=0x20020000;STORAGE=0x20021000;SP=0x2003eff0;RET=0x10000000
regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x410000,((len(blob)+4095)//4096)*4096);u.mem_write(0x410000,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x40000);u.mem_write(CB,b'\xa5'*96)
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,RET|1)
 for r,v in zip(regs,(c['count'],c['item'],c['storage'],c['cb'])):u.reg_write(r,v)
 u.mem_write(SP,struct.pack('<I',c['type']))
 calls=[];stop=[]
 def hook(emu,pc,size,data):
  if pc==0x419be8:
   calls.append(['reset',emu.reg_read(UC_ARM_REG_R0),emu.reg_read(UC_ARM_REG_R1)])
   emu.mem_write(CB+8,struct.pack('<I',0x12345678))
   emu.reg_write(UC_ARM_REG_R0,1);emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc==0x41b2f8:
   calls.append(['assert']);stop.append('assert');emu.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x419c9c)|1,RET,count=10000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 if not stop:assert u.reg_read(UC_ARM_REG_PC)==RET and u.reg_read(UC_ARM_REG_SP)==SP
 return dict(outcome=stop[0] if stop else 'return',ret=u.reg_read(UC_ARM_REG_R0) if not stop else None,calls=calls,cb=bytes(u.mem_read(CB,96)).hex())
cases=[]
for count,item,storage,cb,type_ in itertools.product((0,1,3,0xffffffff),(0,1,16),(0,STORAGE),(0,CB),(0,2,3,255,256)):
 c=dict(count=count,item=item,storage=storage,cb=cb,type=type_)
 a,b=run(False,c),run(True,c)
 if a!=b:raise AssertionError((c,a,b))
 cases.append(c)
receipt=dict(status='PASS',cases=len(cases),stock_constructor_sha256=hashlib.sha256(blob[0x419c9c-0x410000:0x419d08-0x410000]).hexdigest(),stock_initializer_sha256=hashlib.sha256(blob[0x419d68-0x410000:0x419d8a-0x410000]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='Cortex-M4 scalar original/source oracle. Queue reset is a shared synthetic lower callback; separately selected source reset exists. Invalid inputs stop at original/source assertion mask entry; no claimed execution of nonreturning fault loop. Cortex-M55 archive compile independent; no scheduler or hardware behavior.')
(H/'queue-create-static-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS queue create static',len(cases))
