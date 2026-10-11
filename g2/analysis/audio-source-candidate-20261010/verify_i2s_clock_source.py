#!/usr/bin/env python3
"""Compare complete 0x58fd1c selector against source across all branch classes."""
import hashlib, itertools, json, struct, subprocess
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
from elftools.elf.elffile import ELFFile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
image=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';blob=image.read_bytes();sha=hashlib.sha256(blob).hexdigest()
assert sha=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
source=ROOT/'g2/components/audio/source_candidate_20261010/i2s_clock_source_provider.c'
obj=Path('/tmp/g2-i2s-clock-source-m4.o');elf_path=Path('/tmp/g2-i2s-clock-source-m4.elf')
flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-c']
subprocess.run(['clang',*flags,str(source),'-o',str(obj)],check=True)
subprocess.run(['/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc','-mcpu=cortex-m4','-mthumb','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_i2s_clock_source',str(obj),'-o',str(elf_path)],check=True)
with elf_path.open('rb') as stream:
 e=ELFFile(stream);sym={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()};segments=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
assert sym['audio_i2s_clock_source']==sym['audio_power_clock_source']
def run(value,mmio,compiled):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x40000)
 for addr,data in segments:u.mem_write(addr,data)
 u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_write(0x40004048,struct.pack('<I',mmio))
 u.reg_write(UC_ARM_REG_SP,0x2000ff00);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_R0,value)
 reads=[];writes=[]
 def read(emu,access,address,size,val,data):
  if address>=0x40000000:reads.append([address,size])
 def write(emu,access,address,size,val,data):writes.append([address,size,val])
 u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((sym['audio_i2s_clock_source'] if compiled else 0x58fd1c)|1,0x10000000,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return dict(result=u.reg_read(UC_ARM_REG_R0),sp=u.reg_read(UC_ARM_REG_SP),reads=reads,writes=writes,mmio=u.mem_read(0x40004048,4).hex())
# Original condition boundaries, wraparound values, random representatives.
values=sorted(set([0,1,0xff,0x100,0x101,0x1ff,*range(0x1fd,0x22d),0x101ff,*range(0x10200,0x10206),0xffffffff,0xfffffffe,0x80000000,0x12345678]))
rows=[]
for value,mmio in itertools.product(values,[0,1,0x3fffffff,0x40000000,0x80000000,0xffffffff]):
 original=run(value,mmio,False);new=run(value,mmio,True);assert original==new,(hex(value),hex(mmio),original,new)
 rows.append({'input':hex(value),'mmio':hex(mmio),**original})
receipt={'status':'PASS','cases':len(rows),'image_sha256':sha,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'comparison_object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest(),'comparison_elf_sha256':hashlib.sha256(elf_path.read_bytes()).hexdigest(),'original_entry':'0x58fd1c','original_body_sha256':hashlib.sha256(blob[0x58fd1c-0x437fe0:0x58fd7e-0x437fe0]).hexdigest(),'literal_address':'0x590810','literal_value':'0x40004048','flags':flags,'rows':rows,'limits':'Synthetic MMIO word; exact branch/return/MMIO read behavior of isolated source, not hardware clock ownership.'}
(HERE/'i2s-clock-source-execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',len(rows))
