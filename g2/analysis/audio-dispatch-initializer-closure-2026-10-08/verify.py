from pathlib import Path
import struct,json,hashlib
from unicorn import *
from unicorn.arm_const import *
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];word=lambda a:struct.unpack_from('<I',raw,a-0x438000)[0];record=0x75d3f4;src=record+word(record);encoded=word(record+4);dest=word(record+8);end=src+(encoded>>1);assert encoded&1==0 and dest==0x20000000
out=bytearray();p=src;tokens=0
while p!=end:
 assert p<end
 token=raw[p-0x438000];p+=1;literals=token&3;match=token>>4
 if not literals:literals=raw[p-0x438000]+3;p+=1
 if match==15:match=raw[p-0x438000]+15;p+=1
 for i in range(literals-1):out.append(raw[p-0x438000]);p+=1
 if match:
  offset=raw[p-0x438000];p+=1;high=(token>>2)&3
  if high==3:high=raw[p-0x438000];p+=1
  offset+=high<<8;assert 0<offset<=len(out)
  for i in range(match+2):out.append(out[-offset])
 tokens+=1
assert len(out)==0x4558
u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_write(dest,b'\xa5'*0x4600);u.reg_write(UC_ARM_REG_R0,record);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x43a11f,0x2007f000,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert u.reg_read(UC_ARM_REG_R0)==record+12;assert bytes(u.mem_read(dest,len(out)))==out;assert bytes(u.mem_read(dest+len(out),64))==b'\xa5'*64
from elftools.elf.elffile import ELFFile
elf=Path('/tmp/opencfw-audio-unpack/unpack.elf')
with elf.open('rb') as f:
 e=ELFFile(f);syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
 for seg in e.iter_segments():
  if seg['p_type']=='PT_LOAD':u.mem_write(seg['p_vaddr'],seg.data())
 u.mem_write(dest,b'\xa5'*0x4600);u.reg_write(UC_ARM_REG_R0,src);u.reg_write(UC_ARM_REG_R1,encoded>>1);u.reg_write(UC_ARM_REG_R2,dest);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(syms['audio_startup_unpack']|1,0x2007f000,count=1000000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;assert u.reg_read(UC_ARM_REG_R0)==dest+len(out);assert bytes(u.mem_read(dest,len(out)))==out;assert bytes(u.mem_read(dest+len(out),64))==b'\xa5'*64
rows=[]
for i in range(8):
 off=0x3fbc+i*8;typ,pad,fn=struct.unpack_from('<HHI',out,off);rows.append(dict(slot=i,type=typ,padding=pad,callback=hex(fn)))
(D/'results.json').write_text(json.dumps(dict(status='PASS',comparisons=2,compared_bytes=len(out),tokens=tokens,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),record=hex(record),decoder='0x43a11e',source=hex(src),source_end=hex(end),compressed_bytes=encoded>>1,destination=hex(dest),decoded_sha256=hashlib.sha256(out).hexdigest(),rows=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),limits=['Actual decoder only, not reset runner, all initializer records, later writes or booted runtime.','Full authenticated RAM data record compared to independent Python decoding; no call stubs.']),indent=2)+'\n');print('PASS',len(out),'bytes',rows)
