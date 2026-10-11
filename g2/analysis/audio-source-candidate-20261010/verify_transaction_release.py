#!/usr/bin/env python3
"""Compare complete transaction-release body with file-heap free as lower ABI."""
import hashlib,itertools,json,struct,subprocess
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
from elftools.elf.elffile import ELFFile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest()
assert sha=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
source=ROOT/'g2/components/audio/source_candidate_20261010/transaction_release_provider.c';elfpath=Path('/tmp/audio_transaction_release_m4.elf')
gcc=Path('/tmp/opencfw-arm-gnu/arm-gnu-toolchain-13.3.rel1-darwin-arm64-arm-none-eabi/bin/arm-none-eabi-gcc')
flags=['-mcpu=cortex-m4','-mthumb','-Og','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x10001000','-Wl,-e,audio_release_transaction','-Wl,--defsym=audio_file_heap_free=0x474d17']
subprocess.run([str(gcc),*flags,str(source),'-o',str(elfpath)],check=True)
with elfpath.open('rb') as stream:
 e=ELFFile(stream);sym={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()};segments=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
def run(pointer,packet,length,alignment,pattern,compiled):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x437000,((len(blob)+0xfe0+0xfff)//0x1000)*0x1000);u.mem_write(0x437fe0,blob)
 u.mem_map(0x10000000,0x40000)
 for address,data in segments:u.mem_write(address,data)
 u.mem_map(0x20000000,0x20000)
 desc=0x20008000+alignment
 raw=bytearray(((i*pattern+0x35)&255) for i in range(26));raw[14:18]=struct.pack('<I',packet);raw[18:20]=struct.pack('<H',length)
 u.mem_write(desc,bytes(raw));u.reg_write(UC_ARM_REG_SP,0x2001ff00);u.reg_write(UC_ARM_REG_LR,0x10000001);u.reg_write(UC_ARM_REG_R0,desc if pointer else 0)
 calls=[];writes=[]
 def hook(emu,pc,size,data):
  if pc==0x474d16:
   calls.append(emu.reg_read(UC_ARM_REG_R0));emu.reg_write(UC_ARM_REG_PC,emu.reg_read(UC_ARM_REG_LR))
 def write(emu,access,address,size,value,data):
  if 0x20008000<=address<0x20008100:writes.append([address-desc,size,value])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write)
 u.emu_start((sym['audio_release_transaction'] if compiled else 0x57c640)|1,0x10000000,count=5000)
 assert u.reg_read(UC_ARM_REG_PC)==0x10000000
 return {'descriptor':u.mem_read(desc,26).hex(),'calls':calls,'writes':writes,'sp':u.reg_read(UC_ARM_REG_SP)}
rows=[]
for pointer,packet,length,alignment,pattern in itertools.product((0,1),(0,0x20010000,0xffffffff),(0,1,0xffff),(0,1,2,3),(1,7)):
 original=run(pointer,packet,length,alignment,pattern,False);new=run(pointer,packet,length,alignment,pattern,True)
 assert original==new,(pointer,hex(packet),length,alignment,pattern,original,new)
 rows.append({'pointer':pointer,'packet':hex(packet),'length':length,'alignment':alignment,'pattern':pattern,'observed':original})
receipt={'status':'PASS','cases':len(rows),'original_entry':'0x57c640','original_body_sha256':hashlib.sha256(blob[0x57c640-0x437fe0:0x57c664-0x437fe0]).hexdigest(),'image_sha256':sha,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'comparison_elf_sha256':hashlib.sha256(elfpath.read_bytes()).hexdigest(),'compiler_sha256':hashlib.sha256(gcc.read_bytes()).hexdigest(),'flags':flags,'rows':rows,'limits':'File-heap free intercepted at its public ABI; actual free/mutex/pool and faults not executed. Descriptor bytes, ordered writes, call arguments, SP compared.'}
(HERE/'transaction-release-execution.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS',len(rows))
