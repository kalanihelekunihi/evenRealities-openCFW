from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import *
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;R=D.parents[2];blob=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863';raw=blob[32:];receipt=json.loads((D/'reproduction-receipt.json').read_text());elf=Path(receipt['elf']);assert hashlib.sha256(elf.read_bytes()).hexdigest()==receipt['elf_sha256']
with elf.open('rb') as f:
 e=ELFFile(f);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
Q=0x20006000;MSG=0x20006100;THREAD=0x20007200;CONTROL=0x20003f98;log_address=struct.unpack_from('<I',raw,0x43d13c-0x438000)[0];rows=[]
def run(native,kind,argument,queue,enabled=0,counter=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 def invoke(at,args=(),stack=()):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
  if stack:w(0x2007e000,*stack)
  u.emu_start(at|1,0x2007f000,count=100000)
 w(0x20074a30,0);w(0x20074a3c,1);invoke(0x441696,[1,12,Q+80,0],[Q]);assert u.reg_read(UC_ARM_REG_PC)==0x2007f000
 if queue=='full':w(MSG,99,88,77);invoke(0x4417ee,[Q,MSG,0,0]);assert u.reg_read(UC_ARM_REG_R0)==1
 w(CONTROL+8,THREAD,Q if queue!='null' else 0);u.mem_write(log_address,b'\0');u.mem_write(0x2007502e,bytes([enabled]));w(0x20074a9c,counter)
 trace=[];boundary=[]
 def hook(u,a,n,d):
  if a==0x53c638:trace.append({'call':'audio_submit','message':list(struct.unpack('<III',u.mem_read(u.reg_read(UC_ARM_REG_R0),12)))})
  if a==0x43d0ce:
   assert bytes(u.mem_read(log_address,1))==b'\0';trace.append({'call':'log_mask'})
  if a==0x449abe:trace.append({'call':'message_queue_put','queue':u.reg_read(UC_ARM_REG_R0),'priority':u.reg_read(UC_ARM_REG_R2),'timeout_ticks':u.reg_read(UC_ARM_REG_R3)})
  if a==0x449238:
   boundary.append({'kind':'before_thread_flags_set','thread':u.reg_read(UC_ARM_REG_R0),'flags':u.reg_read(UC_ARM_REG_R1)});u.emu_stop();return
  assert a not in [0x4420bc,0x43d574,0x43ce9e],'unexpected scheduler/log branch'
 u.hook_add(UC_HOOK_CODE,hook)
 original={'tick':0x53c2a4,'emit_type0':0x53ca10,'type6':0x53c92e};names={'tick':'audio_watchdog_tick','emit_type0':'audio_watchdog_emit_type0','type6':'audio_watchdog_type6_log_disabled'}
 invoke(sym[names[kind]] if native else original[kind],[argument]);assert boundary or u.reg_read(UC_ARM_REG_PC)==0x2007f000
 posts=[x['message'] for x in trace if x['call']=='audio_submit'];expected=[6,0,0] if kind=='tick' else [0,1,argument&255] if kind=='emit_type0' else [0,1,2] if enabled and counter<20 else None
 assert posts==([expected] if expected else [])
 assert word(0x20074a9c)==(0 if kind=='type6' and enabled else counter)
 assert bool(boundary)==bool(expected and queue=='empty')
 assert word(Q+56)==(1 if queue=='full' or expected and queue=='empty' else 0)
 return {'trace':trace,'boundary':boundary,'counter_after':word(0x20074a9c),'queue_count':word(Q+56),'queue_payload':bytes(u.mem_read(Q+80,12)).hex(),'queue_digest':hashlib.sha256(bytes(u.mem_read(Q,92))).hexdigest(),'basepri':u.reg_read(UC_ARM_REG_BASEPRI)}
cases=[]
for argument,queue in itertools.product([0,1,0xcafebabe,0xffffffff],['null','empty','full']):cases.append(dict(kind='tick',argument=argument,queue=queue))
for argument,queue in itertools.product([0,1,2,255,256,258,0xffffffff],['null','empty','full']):cases.append(dict(kind='emit_type0',argument=argument,queue=queue))
for argument,queue,enabled,counter in itertools.product([0,0xcafebabe],['null','empty','full'],[0,1,255],[0,19,20,21,0xffffffff]):cases.append(dict(kind='type6',argument=argument,queue=queue,enabled=enabled,counter=counter))
for c in cases:
 o=run(False,**c);n=run(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
(D/'results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'logging_mask_address':hex(log_address),'comparisons':rows,'limits':['Callback and emitter complete; type6 handler selects logging-disabled contract only.','Actual publisher/CMSIS queue wrapper/queue copy execute; success stops before thread flag set rather than fabricating a resumed task.','No callback argument memory read, real time cadence, live timer/delete interleaving or hardware fault inference.']},indent=2)+'\n');print('PASS',len(rows),'watchdog callback/message comparisons')
