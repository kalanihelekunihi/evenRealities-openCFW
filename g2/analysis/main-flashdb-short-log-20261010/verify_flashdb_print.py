#!/usr/bin/env python3
from pathlib import Path
import hashlib,itertools,json,struct,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

H=Path(__file__).resolve().parent;R=H.parents[2]
src=R/'g2/components/main/flashdb_print_wrapper_candidates_20261010/print_wrapper.c'
blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
cc=subprocess.check_output(['xcrun','--find','clang'],text=True).strip();elf=H/'flashdb-print-wrapper.elf'
cmd=[cc,'--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-Oz','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,g2_flashdb_print','-Wl,--defsym=g2_flashdb_print_sink=0x200742f0','-Wl,--defsym=g2_flashdb_print_buffer=0x2006b930','-Wl,--defsym=g2_flashdb_vformat=0x473037',str(src),'-o',str(elf)]
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
with elf.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='g2_flashdb_print')
 segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
FMT=0x20051000;BUF=0x2006b930;CELL=0x200742f0;SINKA=0x10020000;SINKB=0x10020020;SP=0x200feff0
regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
def run(source,c):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x100000)
 u.mem_write(FMT,b'diagnostic %d %s\0');u.mem_write(BUF,b'\xa5'*32)
 u.mem_write(CELL,struct.pack('<I',(SINKA|1) if c['enabled'] else 0))
 words=c['words'];
 for reg,val in zip(regs,(FMT,*words[:3])):u.reg_write(reg,val)
 u.mem_write(SP,struct.pack('<III',*words[3:6]))
 u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x10000001)
 calls=[]
 def hook(emu,pc,size,data):
  if pc==0x473036:
   args=[emu.reg_read(r) for r in regs[:3]]
   varargs=list(struct.unpack('<IIIIII',emu.mem_read(args[2],24)))
   calls.append(['format',args[0],args[1],varargs])
   emu.mem_write(BUF,b'formatted\0'+b'X'*22)
   if c['switch']:emu.mem_write(CELL,struct.pack('<I',SINKB|1))
   emu.reg_write(UC_ARM_REG_R0,c['result']&0xffffffff)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
  elif pc in (SINKA,SINKB):
   calls.append(['sink',pc,emu.reg_read(UC_ARM_REG_R0)])
   if c['mutate']:emu.mem_write(BUF,b'output\0'+b'Y'*25)
   emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((entry if source else 0x4733ee)|1,0x10000000,count=10000)
 except Exception as exc:raise RuntimeError((source,c,hex(u.reg_read(UC_ARM_REG_PC)),calls)) from exc
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000 and u.reg_read(UC_ARM_REG_SP)==SP
 return dict(ret=u.reg_read(UC_ARM_REG_R0),calls=calls,buffer=bytes(u.mem_read(BUF,32)).hex(),sink=struct.unpack('<I',u.mem_read(CELL,4))[0])
cases=[]
for enabled,switch,mutate,result,seed in itertools.product((False,True),(False,True),(False,True),(0,1,0xffffffff,0x80000000),(0,0x12345678,0xffffffff)):
 words=[(seed+i*0x11111111)&0xffffffff for i in range(6)]
 c=dict(enabled=enabled,switch=switch,mutate=mutate,result=result,words=words)
 a,b=run(False,c),run(True,c)
 if a!=b:raise AssertionError((c,a,b))
 cases.append(c)
receipt=dict(status='PASS',cases=len(cases),stock_body_sha256=hashlib.sha256(blob[0x4733ee-0x437fe0:0x47341a-0x437fe0]).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),compile=cmd,limits='M55 public-entry wrapper only. Shared synthetic vformatter and output sink; no general variadic syntax, output transport, buffer placement, callback lifetime, concurrent state or hardware proof.')
(H/'flashdb-print-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS flashdb print',len(cases))
