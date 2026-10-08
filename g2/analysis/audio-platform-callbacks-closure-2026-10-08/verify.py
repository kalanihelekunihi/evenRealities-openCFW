from pathlib import Path
import struct,json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:]
elf=Path('/tmp/opencfw-audio-platform-callbacks/callbacks.elf');segments=[]
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
def machine():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4);u.mem_map(0x438000,(len(raw)+4095)&~4095);u.mem_write(0x438000,raw);u.mem_map(0x20000000,0x80000);u.mem_map(0x100000,0x10000);u.mem_map(0x40020000,0x2000)
 for a,b in segments:u.mem_write(a,b)
 u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 return u
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def w(u,a,v):u.mem_write(a,struct.pack('<I',v))
# Independent expected registration model, separate from compiled C.
def expected(major,rev,feature):
 major&=255;table=[0]*15
 flags=[int((major==0x22 and rev==2) or (major==0x23 and rev==1)),int((major==0x21 and rev in (2,3)) or (major==0x22 and rev==0)),int(major==0x21 and rev>=3),int((major==0x22 and rev==1) or (major==0x23 and rev==0)),int((major==0x23 and rev>=2) or major>=0x24),0]
 flags[5]=int(flags[0] and not(feature&1))
 if flags[4]:items={0:0x5a4d49,1:0x5a490d,2:0x5a4e0d,7:0x5a4d01,10:0x5a40b7,11:0x5a40cb}
 elif flags[0]:items={0:0x5a1c19,1:0x5a1739,2:0x5a1da5,5:0x5a1bbd,6:0x5a1bcd,7:0x5a1bed,11:0x5a0bcd}
 elif (major==0x21 and rev>=2) or (major==0x22 and rev<2) or (major==0x23 and rev==0):
  items={0:0x5a08e5,1:0x5a0787,2:0x5a0a6d,3:0x5a07e7,4:0x5a07f1,12:0x5a085f,13:0x5a08b7,14:0x5a08cb,6:0x59fd83 if major==0x21 and rev==2 else 0x5a081d,7:0x59fda9 if major==0x21 and rev==2 else 0x5a0843}
 elif major==0x21 and rev==1:items={0:0x5a0019,1:0x59fd37,6:0x59fd83,7:0x59fda9}
 else:items={}
 if major==0x21 and rev<2:items.update({8:0x59fdc3,9:0x59fe5b})
 for i,v in items.items():table[i]=v
 return table,flags
rows=[]
for major,rev,feature,initial in itertools.product([0x20,0x21,0x22,0x23,0x24,0x25,0xdead0021],[0,1,2,3,4,0xffffffff],[0,1],[0,0xa5a5a5a5]):
 table,flags=expected(major,rev,feature);values=[]
 for entry in [0x480434,sym['audio_platform_callbacks_initialize']]:
  u=machine();w(u,0x4002000c,major);w(u,0x200001e8,rev);u.mem_write(0x2007197c,bytes([feature]));u.mem_write(0x2007326c,b'\xa5'*68);u.mem_write(0x20074f60,b'\xa5'*16);w(u,0x40020028,initial);w(u,0x40020060,initial);writes=[];boundary=[]
  def hook(u,a,n,d):
   if a in [0x5a4d48,0x5a1c18,0x5a08e4,0x5a0018]:boundary.append(hex(a));u.emu_stop()
  def write(u,access,a,n,v,d):writes.append([hex(a),n,v])
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write,begin=0x40020028,end=0x40020063);u.emu_start(entry|1,0x2007f000,count=10000)
  assert list(struct.unpack('<15I',u.mem_read(0x20073270,60)))==table
  assert list(u.mem_read(0x20074f64,6))==flags
  assert bytes(u.mem_read(0x2007326c,4))==b'\xa5'*4 and bytes(u.mem_read(0x200732ac,4))==b'\xa5'*4
  assert bytes(u.mem_read(0x20074f60,4))==b'\xa5'*4 and bytes(u.mem_read(0x20074f6a,6))==b'\xa5'*6
  want=[]
  if flags[1] or flags[3] or flags[5]:
   v=initial&~2;want.append(['0x40020028',4,v]);v|=1;want.append(['0x40020028',4,v]);v=initial
   for bit in [0x8000,0x4000,0x2000]:v|=bit;want.append(['0x40020060',4,v])
  assert writes==want,(major,rev,writes,want)
  if table[0]:assert boundary==[hex(table[0]&~1)]
  else:assert not boundary and u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0
  values.append(dict(table=[hex(v) for v in table],flags=flags,mmio_writes=writes,boundary=boundary,return_value=None if boundary else u.reg_read(UC_ARM_REG_R0)))
 assert values[0]==values[1];rows.append(dict(major=hex(major),revision=hex(rev),feature=feature,initial_mmio=hex(initial),**values[0]))
controls=[]
for family,action,metadata,null,enable in itertools.product(['early','middle'],[0,1,2,3,4,5,6,255,256,257,258],[0,1,2,255],[0,1],[0,1]):
 if null and (action&255 in (1,2)):continue
 vals=[]
 for entry in ([0x59fd36,sym['audio_platform_early_control']] if family=='early' else [0x5a0786,sym['audio_platform_middle_control']]):
  u=machine();m=0 if null else 0x20006000;before=bytes([metadata])+b'\xa5'*15;u.mem_write(0x20006000,before);boundary=[]
  def hook(u,a,n,d):
   if a in [0x59fca2,0x59fbac,0x5a0204,0x5a05e0,0x5a0328,0x5a00fc]:boundary.append([hex(a),u.reg_read(UC_ARM_REG_R0)]);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.reg_write(UC_ARM_REG_R0,action);u.reg_write(UC_ARM_REG_R1,enable);u.reg_write(UC_ARM_REG_R2,m);u.emu_start(entry|1,0x2007f000,count=10000)
  normalized=action&255;expected_boundary=None
  if normalized==1:expected_boundary=(0x59fca2 if family=='early' else 0x5a05e0) if not metadata else (0x59fbac if family=='early' else 0x5a0328)
  elif family=='middle' and normalized==2:expected_boundary=0x5a00fc
  elif family=='middle' and normalized==0 and not null and metadata==2:expected_boundary=0x5a0204
  if expected_boundary:
   assert len(boundary)==1 and boundary[0][0]==hex(expected_boundary)
   if normalized==1:assert boundary[0][1]==metadata
   if family=='middle' and normalized==2:assert boundary[0][1]==m
   # Action0's R0 is metadata byte2 in original; C must reproduce it at child boundary.
  else:assert not boundary and u.reg_read(UC_ARM_REG_PC)==0x2007f000 and u.reg_read(UC_ARM_REG_R0)==0
  after=bytes(u.mem_read(0x20006000,16));want=before
  if family=='early' and normalized==2:want=before[:4]+struct.pack('<2I',0xc3888000,0x447a0000)+before[12:]
  assert after==want
  vals.append(dict(boundary=boundary,metadata_after=after.hex(),return_value=None if boundary else u.reg_read(UC_ARM_REG_R0)))
 assert vals[0]==vals[1],(family,action,metadata,null,enable,vals);controls.append(dict(family=family,action=action,metadata_byte=metadata,null_metadata=null,enable=enable,**vals[0]))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows)+len(controls),registration_cases=len(rows),control_cases=len(controls),registration_comparisons=rows,control_comparisons=controls,elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Synthetic major/MMIO and revision/feature RAM; actual stock input producer/reachability not established.','Original table zeroing executes; independent source performs its own zeroing.','Selected registration/control wrappers stop before real initialization/control child first instruction; no fabricated returns.','Ordered passive MMIO writes prove source ordering, not physical effects.']),indent=2)+'\n');print('PASS',len(rows),len(controls),'registration/control comparisons')
