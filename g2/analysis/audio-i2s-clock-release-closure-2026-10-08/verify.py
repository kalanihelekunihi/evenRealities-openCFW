from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-i2s-clock/clock.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def run(native,kind,value,register,member=0,other=0,mask=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0x40004000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(0x40004044,register);w(0x20073344,(member<<value)|(other<<1) if kind=='release' else 0,0);writes=[]
 def hook(u,access,a,size,v,d):writes.append((hex(a),size,v));assert kind!='release' or u.reg_read(UC_ARM_REG_PRIMASK)==1
 u.hook_add(UC_HOOK_MEM_WRITE,hook,begin=0x40004044,end=0x40004047);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 entry=(sym['audio_i2s_power_command'] if native else 0x4d391e) if kind=='power' else (sym['audio_i2s_release_group4'] if native else 0x4c4016)
 u.emu_start(entry|1,0x2007f000,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_PRIMASK)==mask
 expected=(register&~1)|int(bool(value&255)) if kind=='power' else register&~1 if member and not other else register
 assert word(0x40004044)==expected;assert len(writes)==(1 if kind=='power' or member and not other else 0)
 if kind=='release':assert word(0x20073344)==other<<1
 return dict(register=hex(word(0x40004044)),clients=bytes(u.mem_read(0x20073344,8)).hex(),writes=writes,primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for value,register in itertools.product([0,1,2,0x100,0x101,0xffffffff],[0,1,0xa5a5a5a5,0xfffffffe]):
 o=run(False,'power',value,register);n=run(True,'power',value,register);assert o==n;rows.append(dict(kind='power',value=hex(value),initial_register=hex(register),**o))
for value,register,member,other,mask in itertools.product([29,30],[0,1,0xa5a5a5a5,0xfffffffe],[0,1],[0,1],[0,1]):
 o=run(False,'release',value,register,member,other,mask);n=run(True,'release',value,register,member,other,mask);assert o==n;rows.append(dict(kind='release',peripheral=value,initial_register=hex(register),member=member,other=other,initial_primask=mask,**o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Actual clock group4 release/power-command bytes and independent C; original save/disable IRQ peer.','Passive power register fixture; one command write and no status poll in this provider are proven software facts, not completed hardware power/DMA shutdown.','I2S peripheral29/30 group4 only; no other clock groups or changing-source logic.']),indent=2)+'\n');print('PASS',len(rows),'clock release comparisons')
