"""Three-way actual instructions, independent C and selected pinned public C."""
from pathlib import Path
import sys,json,itertools,struct,hashlib
D=Path(__file__).resolve().parent
# Reuse sealed ELF loader/guest/call helpers without running its test loops.
helper=D.parent/'touch-ilo-pm-closure-2026-10-08/verify.py';text=helper.read_text().split('rows=[]')[0];text=text.replace("entries=[0xa1c0,symbols['touch_ilo_deep_sleep_callback'],symbols['Cy_SysClk_DeepSleepCallback']]","entries=[]");text=text.replace('UC_MODE_THUMB,UC_HOOK','UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK').replace('UC_ARCH_ARM,UC_MODE_THUMB);','UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);');ns={'__file__':str(helper)};exec(text,ns);guest=ns['guest'];call=ns['call'];symbols=ns['symbols'];firmware=ns['firmware'];elf=ns['elf'];rows=[]
register=[0xa3b0,symbols['touch_pm_register'],symbols['Cy_SysPm_RegisterCallback']];execute=[0xa444,symbols['touch_pm_execute'],symbols['Cy_SysPm_ExecuteCallback']];probe=symbols['touch_pm_probe']|1
addresses=[0x20002000+32*i for i in range(4)]
def seed(u,t,orders,skips=(0,0,0,0),ready=(0,0,0,0),other=(0,0,0,0)):
 for i,a in enumerate(addresses):
  p=0x20002400+16*i;c=0x20002500+16*i
  u.mem_write(a,struct.pack('<IB3xIIIIB3x',probe,t,skips[i],p,0,0,orders[i]));u.mem_write(p,struct.pack('<II',0x40030000+i,c));u.mem_write(c,struct.pack('<III',i,ready[i],other[i]))
def memory(u):return bytes(u.mem_read(0x20000000,0x4000))
def trace(u):
 n=struct.unpack('<I',u.mem_read(0x20003000,4))[0];return [struct.unpack('<III',u.mem_read(0x20003004+12*i,12)) for i in range(n)]
for orders,order,t in itertools.product([(0,1,2,3),(3,2,1,0),(5,5,5,5),(255,0,128,128)],list(itertools.permutations(range(4))),[0,1]):
 vals=[]
 for m in range(3):
  u=guest();seed(u,t,orders);returns=[call(u,register[m],[addresses[i]]) for i in order];returns += [call(u,register[m],[addresses[order[0]]]),call(u,register[m],[addresses[order[-1]]])];assert returns==[1,1,1,1,0,0]
  linked=[];a=struct.unpack('<I',u.mem_read(0x20000f34+4*t,4))[0]
  while a:
   assert a not in linked;linked.append(a);a=struct.unpack('<I',u.mem_read(a+20,4))[0]
  expected=sorted(order,key=lambda i:orders[i]);assert linked==[addresses[i] for i in expected];vals.append((returns,memory(u)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='registration_permutation',type=t,orders=orders,registration_order=order,duplicates_rejected=True))
for invalid in ['null','params','callback']:
 vals=[]
 for m in range(3):
  u=guest();seed(u,1,(0,1,2,3));arg=addresses[0]
  if invalid=='null':arg=0
  else:u.mem_write(arg+(12 if invalid=='params' else 0),bytes(4))
  before=memory(u);r=call(u,register[m],[arg]);assert r==0 and memory(u)==before;vals.append((r,memory(u)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='invalid_registration',invalid=invalid))
for t,skip,fail,nonfailure in itertools.product([0,1],[0,1,2,4,8,15],[-1,0,1,2,3],[0,0x420001]):
 vals=[];ready=[nonfailure]*4
 if fail>=0:ready[fail]=0x4200ff
 for m in range(3):
  u=guest();seed(u,t,(0,1,2,3),skips=(skip,0,skip,0),ready=ready,other=(0x420001,0,0x4200ff,0));assert all(call(u,register[m],[a])==1 for a in addresses);r=call(u,execute[m],[t,1]);last_mode=2 if r==0x4200ff else 8
  results=[r]
  if last_mode==8:results.append(call(u,execute[m],[t,4]))
  results.append(call(u,execute[m],[t,last_mode]));vals.append((results,trace(u),memory(u)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='dispatch_sequence',type=t,skip_even=skip,requested_fail_id=fail,other_ready_status=hex(nonfailure),phases=[1,2] if last_mode==2 else [1,4,8],returns=[hex(r) for r in vals[0][0]],callback_trace=vals[0][1]))
for t,mode in itertools.product([0,1],[1,2,4]):
 vals=[]
 for m in range(3):
  u=guest();r=call(u,execute[m],[t,mode]);assert r==0;vals.append((r,memory(u)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='empty_supported_list',type=t,mode=mode))
# Demonstrate the single shared LAST across types under explicit synthetic interleaving.
vals=[]
for m in range(3):
 u=guest();seed(u,0,(0,1,2,3));assert call(u,register[m],[addresses[0]])==1;assert call(u,register[m],[addresses[1]])==1
 u.mem_write(addresses[2]+4,bytes([1]));u.mem_write(addresses[3]+4,bytes([1]));assert call(u,register[m],[addresses[2]])==1;assert call(u,register[m],[addresses[3]])==1
 call(u,execute[m],[0,1]);call(u,execute[m],[1,1]);call(u,execute[m],[0,2]);log=trace(u);assert [x[0] for x in log]==[0,1,2,3,2];vals.append((log,memory(u)))
assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='synthetic_cross_type_last_interleave',callback_trace=vals[0][0],limit='Not an observed application interleaving; caller serialization remains required.'))
# Installed clock callback through full wrapper, ending before physical sleep.
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_PRIMASK
clock=[0xa1c0,symbols['touch_ilo_deep_sleep_callback'],symbols['Cy_SysClk_DeepSleepCallback']]
sleep=[0xa58c,symbols['touch_pm_deep_sleep'],symbols['Cy_SysPm_CpuEnterDeepSleep']]
for measuring,prevent,primask,key,scr in itertools.product([0,1],[0,1],[0,1],[0,1,0x8000,0xffff],[0,0xffffffff]):
 vals=[]
 for m in range(3):
  u=guest();u.mem_map(0x0ffff000,0x1000);u.mem_map(0xe000e000,0x1000);u.mem_write(0x0ffff152,struct.pack('<H',key));u.mem_write(0xe000ed10,struct.pack('<I',scr));u.mem_write(0x20000f1c,bytes([77,prevent,measuring]));u.mem_write(0x20000850,struct.pack('<I',clock[m]|1));assert call(u,register[m],[0x20000850])==1
  state={'wfi':False,'phases':[]}
  def stop(u,a,n,data):
   if a==clock[m]&~1:state['phases'].append(u.reg_read(ns['UC_ARM_REG_R1']))
   if bytes(u.mem_read(a,2))==bytes.fromhex('30bf'):state['wfi']=True;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,stop);u.reg_write(UC_ARM_REG_PRIMASK,primask);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20000001);u.emu_start(sleep[m]|1,0x20000000,count=10000)
  assert state['wfi']==(not measuring)
  if measuring:
   assert u.reg_read(UC_ARM_REG_PC)==0x20000000 and u.reg_read(UC_ARM_REG_R0)==0x4200ff;assert state['phases']==[1]
  else:
   assert state['phases']==[1,4] and u.reg_read(UC_ARM_REG_PRIMASK)==1;assert struct.unpack('<I',u.mem_read(0x40030004,4))[0]==key;assert struct.unpack('<I',u.mem_read(0xe000ed10,4))[0]==scr|4
  ram=bytearray(memory(u));ram[0x850:0x854]=bytes(4);vals.append((state,bytes(ram),bytes(u.mem_read(0x40030000,0x100)),bytes(u.mem_read(0xe000ed00,0x100)),u.reg_read(UC_ARM_REG_PRIMASK),None if state['wfi'] else u.reg_read(UC_ARM_REG_R0)))
 assert vals[0]==vals[1]==vals[2];rows.append(dict(kind='installed_clock_sleep_pre_wfi',measuring=measuring,initial_prevent=prevent,initial_primask=primask,sflash_key_input=key,scr_input=hex(scr),stopped_at_wfi=vals[0][0]['wfi'],callback_phases=vals[0][0]['phases'],primask_at_boundary=vals[0][4]))

(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),comparisons=rows,firmware_sha256=hashlib.sha256(firmware.read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Compiled synthetic callbacks, no function-entry stubs; coherent constructed lists and valid supported types0/1 modes1/2/4/8 only.','Callback probe statuses and ordering are supplied inputs, not physical or concurrent firmware traces.','Installed clock full wrapper tests stop before WFI; wake/after-transition hardware delivery not simulated.', 'Mode8 on empty list and invalid type/mode assertion paths excluded from supported comparison contract.','Selected verbatim public bodies use explicit ARM32 layout/status/global environment, not full SDK build or byte-equality proof.']),indent=2)+'\n');print('PASS',len(rows))
