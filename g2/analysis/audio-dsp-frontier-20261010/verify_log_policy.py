#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
H=Path(__file__).resolve().parent;R=H.parents[2];im=R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=im.read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
body=blob[0x44a9ae-0x437fe0:0x44a9b4-0x437fe0];assert hashlib.sha256(body).hexdigest()=='527172205113ef50f09d88d57979d81da3197e4ddff0ab0e383699f7462a54a6'
cc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc');elfp=Path('/tmp/audio_log_policy.elf')
flags=['-mcpu=cortex-m55','-mthumb','-O0','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_log_policy','-Wl,--defsym=audio_log_policy_byte=0x20074fa1']
subprocess.run([str(cc),*flags,str(H/'log_policy.c'),'-o',str(elfp)],check=True)
with elfp.open('rb') as f:
 e=ELFFile(f);entry=next(s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols() if s.name=='audio_log_policy');segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
def run(source,value,arg):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob);u.mem_map(0x10000000,0x100000)
 for a,b in segs:u.mem_write(a,b)
 u.mem_map(0x20000000,0x800000);u.mem_write(0x20074fa1,bytes([value]));u.reg_write(UC_ARM_REG_SP,0x207ff000);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_R0,arg)
 u.emu_start((entry if source else 0x44a9ae)|1,0x10000000,count=100)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20074fa0,4)).hex()
rows=[]
for value in range(256):
 for arg in (0,0xffffffff):
  a=run(False,value,arg);b=run(True,value,arg);assert a==b,(value,arg,a,b);rows.append([value,arg,a[0]])
(H/'log-policy-receipt.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'image_sha256':hashlib.sha256(blob).hexdigest(),'body_sha256':hashlib.sha256(body).hexdigest(),'source_sha256':hashlib.sha256((H/'log_policy.c').read_bytes()).hexdigest(),'elf_sha256':hashlib.sha256(elfp.read_bytes()).hexdigest(),'state_address':'0x20074fa1','rows':rows,'limits':'One-byte getter only; RAM byte placement and initialization remain external.'},indent=2)+'\n')
print('PASS',len(rows))
