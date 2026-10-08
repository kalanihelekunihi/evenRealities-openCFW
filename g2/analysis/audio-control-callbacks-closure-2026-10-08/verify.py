from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-control/control.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
init=json.loads((D.parent/'audio-dispatch-initializer-closure-2026-10-08/results.json').read_text());table=b''.join(struct.pack('<HHI',r['type'],r['padding'],int(r['callback'],16)) for r in init['rows']);rows=[];P=0x20005000
for typ,role,variant,value,i2s_active,pdm_active,high in itertools.product([0,1],[0,1,2],[0,1],[0,1,2,256,258,0xffffffff],[0,1],[0,1],[0,0x10000]):
 vals=[]
 for entry in [0x53c5ac,sym['audio_control_dispatch_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0xe000e000,0x2000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20003fbc,table);u.mem_write(P,struct.pack('<III',typ|high,1,value));u.mem_write(0x200038f1,bytes([role]));u.mem_write(0x20075019,bytes([variant]));u.mem_write(0x20074fb7,bytes([i2s_active]));u.mem_write(0x20074fba,bytes([pdm_active,pdm_active]));u.mem_write(0x2007502e,b'\xa5');u.mem_write(0x20074a9c,struct.pack('<I',123));u.mem_write(0x20074550,struct.pack('<I',0x20007000));u.mem_write(0x2007454c,struct.pack('<I',0x20007100));boundary=[];nvic=[]
  def code(u,a,size,d):
   if a in [0x57d6b4,0x57d794,0x57b4a8,0x57b770]:boundary.append(hex(a));u.emu_stop()
   if a in [0x57a816,0x449376]:boundary.extend([hex(a),u.reg_read(UC_ARM_REG_R0)]);u.emu_stop()
   if a in [0x4c3138,0x5925b4]:boundary.extend([hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.emu_stop()
   assert a not in [0x43d574,0x43ce9e],'unexpected logging'
  def write(u,access,a,n,v,d):
   if 0xe000e180<=a<0xe000e200:nvic.append([hex(a),n,v])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.reg_write(UC_ARM_REG_R0,P);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=15000);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
  low=value&255;expected_nvic=[['0xe000e184',4,0x1000]] if typ==0 and role!=1 and low==0 and i2s_active else [];assert nvic==expected_nvic
  if typ==0 and role!=1 and low!=2:assert u.mem_read(0x2007502e,1)==bytes([bool(low)]);assert u.mem_read(0x20074a9c,4)==bytes(4)
  vals.append((boundary,nvic,bytes(u.mem_read(0x20074a98,8)),bytes(u.mem_read(0x20074fb7,5)),bytes(u.mem_read(0x2007502e,1))))
 assert vals[0]==vals[1],(typ,role,variant,value,i2s_active,pdm_active,high,vals);rows.append(dict(type=typ,role=role,variant=variant,value=hex(value),initial_i2s=i2s_active,initial_pdm=pdm_active,upper_type_bits=hex(high),boundary=vals[0][0],nvic_writes=vals[0][1]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(blob).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Authentic initial dispatcher table; selected type0/1 and loggerdisabled, constructed role/active flags. No live queue/task scheduling.','DSP/start/special/delay/clock/PDM-clear children stop before entry, not stub returns. Inactive stop branches return for real.','Original NVIC disable and role getter/watchdog-null peer execute; no physical interrupt or DMA completion.']),indent=2)+'\n');print('PASS',len(rows))
