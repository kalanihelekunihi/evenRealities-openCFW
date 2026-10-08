from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-timer-aux/aux.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
B=0x20006800;rows=[];cases=[(p,r) for p,r in itertools.product([1,7,8,15,16,44,680,1024],[0,8,16,24])]+[(p,None) for p in [0,0x7fffffef,0x7ffffff0,0x80000000,0xfffffff0,0xffffffff]]
for payload,remainder in cases:
 extra=16-(payload&7);adjusted=0 if payload==0 or payload>0xffffffff-extra else payload+extra;wanted=0 if adjusted&0x80000000 else adjusted;size=wanted+remainder if remainder is not None else 64;END=B+size
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(0x20074a3c,1);w(0x20074a30,0);w(0x20074158,B,0);w(B,END,size);w(END,0,0);w(0x2007465c,END);w(0x20074660,size);w(0x20074664,size);cuts=[];seen=[]
 def code(u,a,n,d):
  if a==0x45614c:seen.append(u.reg_read(UC_ARM_REG_R4))
  if a==0x46d85e:cuts.append(hex(a));u.emu_stop()
  assert a!=0x4420bc,'unexpected yield'
 u.hook_add(UC_HOOK_CODE,code);u.reg_write(UC_ARM_REG_R0,payload);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(0x456111,0x2007f000,count=100000);assert seen==[adjusted]
 if remainder is not None:
  assert not cuts and u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==B+8;allocated=wanted if remainder>16 else size;assert word(B+4)==allocated|0x80000000;assert word(0x20074660)==size-allocated
 else:assert cuts==['0x46d85e'];allocated=None
 u.reg_write(UC_ARM_REG_R0,payload);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(sym['audio_heap_minimum_block']|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==wanted
 rows.append(dict(payload=hex(payload),remainder=remainder,adjusted=adjusted,minimum_accepted=wanted,allocated_block=allocated,original_failure_entry=cuts))
(D/'allocator-size-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Independent minimum-size helper versus real allocator adjusted R4/header outcomes; not independent full allocator.','Boundary cases stop before original malloc-failure hook; no NULL-return or failed-hook body simulated.','Accepted arithmetic bound is not physical heap capacity. Real allocator takes whole block when remainder<=16.']),indent=2)+'\n');print('PASS',len(rows),'allocator size cases')
