"""Original/native/public callback comparison plus real registration/dispatcher paths."""
from pathlib import Path
import sys,json,hashlib,struct,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];firmware=root/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';raw=firmware.read_bytes()[32:];elf=Path(sys.argv[1]);symbols={};segments=[]
with elf.open('rb') as f:
 e=ELFFile(f)
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':segments.append((s['p_vaddr'],s.data()))
 for s in e.get_section_by_name('.symtab').iter_symbols():symbols[s.name]=s['st_value']
entries=[0xa1c0,symbols['touch_ilo_deep_sleep_callback'],symbols['Cy_SysClk_DeepSleepCallback']]
def guest():
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x3000,0x9000);u.mem_write(0x3300,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x100000,0x10000);u.mem_map(0x40030000,0x1000)
 for a,b in segments:u.mem_write(a,b)
 u.mem_write(0x200004c0,raw[0xb58c-0x3300:0xb58c-0x3300+964]);return u
def call(u,a,args):
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
 u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(a|1,0x20000000,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000000;return u.reg_read(UC_ARM_REG_R0)
def snap(u):return bytes(u.mem_read(0x20000f1c,3))
rows=[]
for mode,params,prevent,measuring in itertools.product([0,1,2,3,4,8,0xffffffff],[0,0x20003000,0xffffffff],[0,1,2,255],[0,1,2,255]):
 vals=[]
 for a in entries:
  u=guest();u.mem_write(0x20000f1c,bytes([77,prevent,measuring]));r=call(u,a,[params,mode]);vals.append((r,snap(u)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='callback',mode=mode,params=hex(params),prevent=prevent,measuring=measuring,result=hex(vals[0][0]),after=list(vals[0][1])))
for prevent,measuring in itertools.product([0,1],[0,1]):
 vals=[]
 for entry in entries:
  u=guest();u.mem_write(0x20000f1c,bytes([0,prevent,measuring]));u.mem_write(0x20000850,struct.pack('<I',entry|1));log=[]
  def hook(u,a,n,data):
   if a==entry&~1:log.append(u.reg_read(UC_ARM_REG_R1))
  u.hook_add(UC_HOOK_CODE,hook)
  assert call(u,0x4634,[])==0
  assert struct.unpack('<I',u.mem_read(0x20000f38,4))[0]==0x20000850
  results=[]
  for m in [1,4,8]:results.append(call(u,0xa444,[1,m]))
  # Descriptor function pointer necessarily differs; compare all other persistent SRAM.
  state=bytearray(u.mem_read(0x20000000,0x2000));state[0x850:0x854]=bytes(4);vals.append((results,log,bytes(state)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='real_registration_dispatch',prevent=prevent,measuring=measuring,result=[hex(x) for x in vals[0][0]],callback_modes=vals[0][1]))
for initial in [0,1]:
 vals=[]
 for entry in entries:
  u=guest();u.mem_write(0x20000f1c,bytes([0,initial,0]));log=[]
  for name,args in [('ready',[0,1]),('start',[]),('cancel',[0,2]),('start',[]),('stop',[]),('after',[0,8])]:
   a=entry if name in ('ready','cancel','after') else (0x9d90 if name=='start' else 0x9ddc);r=call(u,a,args);log.append((name,r if args else None,list(snap(u)),bytes(u.mem_read(0x40030000,0x100)).hex()))
  vals.append(log)
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='cancellation_start_stop_sequence',initial_prevent=initial,trace=vals[0]))
result=dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(firmware.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Synthetic coherent memory and MMIO; direct callback phases and actual original registration/dispatcher instructions, no function-entry stubs.','Only one reset-copied callback registered for dispatcher tests; no whole-startup or complete callback-list proof.','Sequences call phases explicitly; they do not establish hardware sleep/wake delivery or concurrent scheduler behavior.','No EXCO/WCO feature code in selected target device specialization; selected public body/environment, not full SDK build.'])
(D/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',len(rows))
