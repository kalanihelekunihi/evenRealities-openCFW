from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-i2s-stop/stop.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
H=0x20006000;RET=0x2007f000;TABLE=0x20073324

def run(native,module,valid,enabled,active,divider,bit12,clockbit,other,source,kind='stop'):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0x40208000,0x2000);u.mem_map(0x40020000,0x1000);u.mem_map(0x40004000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 peripheral=29+module;control=0x40208100+module*0x1000;aux=0x40208054+module*0x1000
 initial_control=0x80000001|(bit12<<12)|(divider<<4)|0x20000;initial_aux=0x12345679
 w(H,(0x01125125 if valid else 0x12345678)|(enabled<<25),module);w(H+0x5c,source);u.mem_write(H+0x60,bytes([active]));w(control,initial_control);w(aux,initial_aux);w(0x400204e8,(2<<5)|(2<<7))
 w(TABLE+4*8,(clockbit<<peripheral)|(other<<1),0);writes=[];cuts=[];calls=[]
 def code(u,a,n,d):
  if a in [0x4c4530,0x58fdbc,0x58fd1c]:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)))
  if a==0x4d391e:cuts.append((hex(a),u.reg_read(UC_ARM_REG_R0)));u.emu_stop()
 def write(u,access,a,size,v,d):writes.append((hex(a),size,v))
 def invalid(u,access,a,size,v,d):
  print(('unmapped',hex(u.reg_read(UC_ARM_REG_PC)),hex(a),module,valid,enabled,active,divider,bit12,clockbit,other,source,kind));return False
 u.hook_add(UC_HOOK_MEM_INVALID,invalid);u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40208000,end=0x40209fff)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,RET|1);u.reg_write(UC_ARM_REG_R0,module if kind=='reconfigure' else H)
 if kind=='reconfigure':u.reg_write(UC_ARM_REG_R1,0x217);entry=sym['audio_i2s_reconfigure_217_matching_source'] if native else 0x58fdbc
 else:entry=sym['audio_i2s_dma_stop_selected'] if native else 0x590c62
 u.emu_start(entry|1,RET,count=100000);assert cuts or u.reg_read(UC_ARM_REG_PC)==RET,(hex(u.reg_read(UC_ARM_REG_PC)),kind)
 if kind=='stop':
  if not valid:assert not writes and not cuts and u.reg_read(UC_ARM_REG_R0)==2
  elif not enabled:assert not writes and not cuts and u.reg_read(UC_ARM_REG_R0)==0
  elif clockbit and not other:assert cuts==[('0x4d391e',0)] and not writes and word(H)&0x02000000
  else:
   assert not cuts and u.reg_read(UC_ARM_REG_R0)==0 and not word(H)&0x02000000
   if active:assert word(control)==(initial_control&~(1|0x1000|0x70000|0x1f0))|0x40000|(23<<4);assert word(aux)==initial_aux&~1
   else:assert not writes
 else:
  expected=(initial_control&~(0x70000|0x1f0))|0x40000|(23<<4);assert word(control)==expected and word(aux)==initial_aux&~1
 return (None if cuts or kind=='reconfigure' else u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(H,100)),bytes(u.mem_read(TABLE,56)),word(control),word(aux),writes,cuts,u.reg_read(UC_ARM_REG_PRIMASK),calls if kind=='stop' else [])
rows=[]
cases=[(*c,'stop') for c in itertools.product([0,1],[0,1],[0,1],[0,1],[7,23],[0,1],[0,1],[0,1],[0,0x200,0x208,0x20f,0x217])]
# 1280 cases; invalid/inactive dimensions intentionally retain no-write expectations.
for module,valid,enabled,active,divider,bit12,clockbit,other,source,kind in cases:
 o=run(False,module,valid,enabled,active,divider,bit12,clockbit,other,source,kind);n=run(True,module,valid,enabled,active,divider,bit12,clockbit,other,source,kind);assert o==n,(module,valid,enabled,active,divider,bit12,clockbit,other,source,o,n)
 rows.append(dict(module=module,valid=valid,enabled=enabled,active=active,divider=divider,bit12=bit12,clockbit=clockbit,other_clock_client=other,source_config=hex(source),return_value=o[0],mmio_writes=o[5],boundary=o[6],calls=o[8]))
helper=[]
for module,divider,bit12 in itertools.product([0,1],[0,7,23,31],[0,1]):
 o=run(False,module,1,1,1,divider,bit12,0,1,0,'reconfigure');n=run(True,module,1,1,1,divider,bit12,0,1,0,'reconfigure');assert o==n,(module,divider,bit12,o,n);helper.append(dict(module=module,divider=divider,bit12=bit12,mmio_writes=o[5]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(helper),stop_comparisons=rows,reconfigure_comparisons=helper,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Passive MMIO register fixtures; no DMA engine, interrupt delivery, clock stability or physical completion modeled.','Original full selected stop and clock source/reconfigure peers; independent stop uses those common peers, separate matching-source reconfigure C uses own stores.','Last-client clock release stops before 0x4D391E first instruction; enabled marker retained at this boundary.','Only module0/1, mapped nonnull handle, matching source2 config217 branches; no changing-source complex provider branches.']),indent=2)+'\n');print('PASS',len(rows)+len(helper),'I2S stop/config comparisons')
