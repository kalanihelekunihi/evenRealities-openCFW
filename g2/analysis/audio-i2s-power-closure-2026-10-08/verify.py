from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];elf=Path('/tmp/opencfw-audio-i2s-power/power.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
H=0x20006000;OFFSETS=[0x48,0x40,0x44,0x54,0x100,0x4c,0x10,0x30,0x300,0x200,0x60,0x64]
def run(native,module,valid,marker,active,mode,backup,powered,allowed,status_busy=False,clock_config=0x217):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0x40208000,0x2000);u.mem_map(0x40020000,0x2000);u.mem_map(0x40004000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(H,0x01125125 if valid else 0x12345678,module);u.mem_write(H+8,bytes([marker]));w(H+12,*[0x10000000+i for i in range(12)]);w(H+0x5c,clock_config);u.mem_write(H+0x60,bytes([active]))
 base=0x40208000+module*0x1000
 for i,o in enumerate(OFFSETS):w(base+o,0x20000000+i)
 w(base+0x100,0x20000000|(7<<4)|0x1001);w(0x400204e8,(2<<5)|(2<<7));w(0x4002100c,(0x40 if module==0 else 0x80) if powered else 0);w(0x40021010,0xc0 if status_busy else 0);u.mem_write(0x20004536,bytes([allowed]));calls=[];cuts=[];writes=[]
 def hook(u,a,n,d):
  if a in [0x47f5b8,0x47f7ae,0x58fdbc,0x4c44bc,0x4c4530,0x480312]:calls.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a in [0x58fdbc,0x4c44bc,0x4c4530,0x480312] else None))
  if a==0x4807a0:cuts.append((hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1) if a==0x480312 else None));u.emu_stop()
 def write(u,access,a,size,v,d):writes.append((hex(a),size,v))
 def invalid(u,access,a,size,v,d):print('unmapped',hex(u.reg_read(UC_ARM_REG_PC)),hex(a));return False
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
 for a,z in [(0x40208000,0x40209fff),(0x40020000,0x40021fff),(0x40004000,0x40004fff)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=z)
 u.reg_write(UC_ARM_REG_R0,H);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,backup);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start((sym['audio_i2s_power_selected'] if native else 0x590648)|1,0x2007f000,count=200000);assert cuts or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 rv=None if cuts else u.reg_read(UC_ARM_REG_R0)
 if not valid:assert rv==2 and not calls and not writes
 elif mode&255 not in [0,1,2]:assert rv==6 and not calls and not writes
 elif mode&255==0 and backup and not marker:assert rv==7 and not calls and not writes
 elif mode&255 in [1,2] and not backup and not powered:assert rv==0 and not writes
 return dict(return_value=rv,boundary=cuts,calls=calls,writes=writes,handle=bytes(u.mem_read(H,100)).hex(),clock_state=bytes(u.mem_read(0x20073324,56)).hex(),power_commands=hex(word(0x4002100c)),primask=u.reg_read(UC_ARM_REG_PRIMASK))
rows=[]
for module,valid,marker,active,mode,backup,powered,allowed in itertools.product([0,1],[0,1],[0,1],[0,1],[0,1,2,3,256,257],[0,1],[0,1],[0,1]):
 o=run(False,module,valid,marker,active,mode,backup,powered,allowed);n=run(True,module,valid,marker,active,mode,backup,powered,allowed);assert o==n,(module,valid,marker,active,mode,backup,powered,allowed,o,n);rows.append(dict(module=module,valid=valid,marker=marker,active=active,mode=mode,backup=backup,powered=powered,clock_allowed=allowed,**o))
for module,mode,backup in itertools.product([0,1],[0,1,2],[0,1]):
 o=run(False,module,1,1,1,mode,backup,1 if mode else 0,1,True);n=run(True,module,1,1,1,mode,backup,1 if mode else 0,1,True);assert o==n;rows.append(dict(module=module,mode=mode,backup=backup,status_busy=True,**o))
for module,mode,powered,allowed in itertools.product([0,1],[0,1,2],[0,1],[0,1]):
 o=run(False,module,1,1,1,mode,1,powered,allowed,False,0x208);n=run(True,module,1,1,1,mode,1,powered,allowed,False,0x208);assert o==n;rows.append(dict(module=module,mode=mode,backup=1,powered=powered,clock_allowed=allowed,clock_config='0x208',**o))
# Uninitialize is independent of peripheral providers and safely checks NULL before dereference.
uninit=[]
for module,valid,flags,null in itertools.product([0,1],[0,1],[0,0x02000000,0x04000000,0xfe000000],[0,1]):
 vals=[]
 for entry in [0x5900ce,sym['audio_i2s_uninitialize_selected']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  header=(0x01125125 if valid else 0x12345678)|flags;before=struct.pack('<3I',header,module,0xa5a5a5a5);u.mem_write(H,before);u.reg_write(UC_ARM_REG_R0,0 if null else H);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000;success=valid and not null;assert u.reg_read(UC_ARM_REG_R0)==(0 if success else 2);after=bytes(u.mem_read(H,12));assert after==(struct.pack('<3I',header&0xfe000000,0,0xa5a5a5a5) if success else before);vals.append(after)
 assert vals[0]==vals[1];uninit.append(dict(module=module,valid=valid,flags=hex(flags),null=null,after=vals[0].hex()))
dispatch=[]
for action,enable,callback in itertools.product([0,4,256,260],[0,1,256,257],[0,0x53c2a5]):
 vals=[]
 for entry in [0x480312,sym['audio_power_control_dispatch']]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20073274,struct.pack('<I',callback));u.mem_write(H,struct.pack('<I',0xc0));boundary=[]
  def hook(u,a,n,d):
   if a==0x53c2a4:boundary.append([hex(a),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)]);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,action);u.reg_write(UC_ARM_REG_R1,enable);u.reg_write(UC_ARM_REG_R2,H);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.emu_start(entry|1,0x2007f000,count=10000)
  if callback:assert boundary==[['0x53c2a4',action&255,enable&255,H]]
  else:assert u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0
  assert bytes(u.mem_read(H,4))==struct.pack('<I',0xc0);vals.append((boundary,None if callback else u.reg_read(UC_ARM_REG_R0)))
 assert vals[0]==vals[1];dispatch.append(dict(action=action,enable=enable,callback=hex(callback),boundary=vals[0][0],return_value=vals[0][1]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(uninit)+len(dispatch),control_dispatch_comparisons=dispatch,power_comparisons=rows,uninitialize_comparisons=uninit,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Complete original/independent power control and uninitialize selected paths, common real peripheral/clock providers; no result stubs.','Passive synthetic MMIO, absent registered callbacks, source217/208 matching source2; no physical power/DMA completion.','Retry delay0x4807A0 stops before first instruction; actual NULL control-callback branch executes, configured callback cases stop before user child first instruction.','Clock allowed flag and snapshot fields are explicit fixtures; actual system initializer reachability is not demonstrated.']),indent=2)+'\n');print('PASS',len(rows)+len(uninit)+len(dispatch),'power/uninitialize/control comparisons')
