#!/usr/bin/env python3
"""Native battery updater control/data/float contract; lower providers remain explicit fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-context-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84;B=0x20006890
P={'r1_native_charger_state_get':0x50618,'r1_battery_task_flags_set':0x77240,'r1_native_charger_initialize':0x5079c,'r1_battery_charged_state_refresh':0x3dd0c,'osKernelGetTickCount':0x7d28c,'r1_battery_charging_progress_reset':0x4fe5c,'r1_battery_five_sample_filter_and_conversion':0x91184,'r1_batcfg_word1_signed_get':0x7bb7c,'__aeabi_memclr':0x277aa,'r1_battery_voltage_average':0x3dda0,'r1_battery_stuck_charge_recovery':0x3db70,'r1_battery_discharge_curve':0x50004,'r1_battery_charging_cadence':0x4fe70,'r1_battery_level_average':0x3d834,'r1_battery_diagnostic_cadence_step':0x3d9b8,'r1_battery_low_escalation':0x3d88c,'r1_proto_report_battery_status':0x8345c,'r1_shared_power_client_release':0x50758,'r1_glasses_tag_frame_send':0x913fc}
def main():
 real_control=True;real_statistics=True;providers=dict(P);provider_reports={};executed={'native':{},'source':{}};control_executed={'native':{},'source':{}}
 for name in ('r1_battery_charged_state_refresh','r1_battery_voltage_average','r1_battery_level_average','r1_battery_charging_progress_reset','r1_battery_task_flags_set','r1_shared_power_client_release'):del providers[name]
 providers.update(osThreadFlagsSet=0x7d6f4,r1_yhm_register_write_native=0x35760)
 vp=OUT/'verification.json';rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'battery-control-context-source.o';assert sha(obj)==r['control_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 objects=[obj];app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 rng=random.Random(0x31fd0);cases=[];rounding_cases=0;digest=hashlib.sha256();layout=ROOT/'r1/source-config/runtime/native_battery_context_verification.ld'
 def fixture(**changes):
  f=dict(state=1,charged=1,flags=(0,0),persist=False,filter=True,mutation=False,average=50,sample=3600,offset=0,tick=0,ring=7,level_ring=7,charge=50,previous=50,voltage=3800,rounding=0)
  f.update(changes);return f
 for state,charged,flags,persist,filtered,mutation,average in itertools.product((0,1,2,0xffffffff),(0,1),((0,0),(1,0),(0,1),(255,255)),(False,True),(False,True),(False,True),(0,1,50,94,95,255)):
  cases.append(fixture(state=state,charged=charged,flags=flags,persist=persist,filter=filtered,mutation=mutation,average=average,sample=rng.choice((0,32767,32768,65535,3600)),offset=rng.choice((0,299,300,(-299)&0xffffffff,(-300)&0xffffffff)),tick=rng.choice((0,1,0xffffffff)),charge=rng.choice((0,1,50,94,95,255)),previous=rng.choice((0,1,50,255))))
 for sample,offset,charged,rounding in itertools.product((0,1,32767,32768,65535,0xffff8000),((-300)&0xffffffff,(-299)&0xffffffff,0,299,300,0x7fffffff,0xffffffff),(0,1),range(4)):
  cases.append(fixture(sample=sample,offset=offset,charged=charged,rounding=rounding));rounding_cases+=1
 for _ in range(1024):cases.append(fixture(state=rng.randrange(3),charged=rng.getrandbits(1),sample=rng.getrandbits(32),offset=rng.getrandbits(32),charge=rng.randrange(256),previous=rng.randrange(256),ring=rng.randrange(16),level_ring=rng.randrange(8),average=rng.choice((0,1,94,95,255,256,0xffffffff)),persist=bool(rng.getrandbits(1)),filter=bool(rng.getrandbits(1)),mutation=bool(rng.getrandbits(1)),flags=(rng.randrange(2),rng.randrange(2)),rounding=rng.randrange(4)))
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(providers)}
  subprocess.run(['arm-none-eabi-ld','-T',str(layout),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  assert syms['r1_battery_device_context']==D and syms['r1_battery_runtime_context']==B and syms['r1_device_state_byte_2c']==D+44 and syms['r1_device_state_byte_2d']==D+45 and syms['r1_vbat_adc_device']==B+16
  cold={}
  for name,address in [('device',D),('runtime',B),('thread',0x20006638),('lowthread',0x20006548),('power',0x20006878)]:
   p=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(p)],check=True);cold[address]=p.read_bytes()
  observed=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for address,data in cold.items():
   if address<0x20007e04:assert data==observed[address-0x200064a8:address-0x200064a8+len(data)]
   else:assert data==bytes(len(data)) and address>=0x20007e04 and address+len(data)<=0x2003beb8
  for state,rounding,mutation in itertools.product([0,1,2],range(4),[False,True]):cases.append(fixture(state=state,rounding=rounding,mutation=mutation,cold=True))
  image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in providers.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);u.mem_map(0xe000e000,4096);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);machines.append(u)
  actual_entries={}
  if real_statistics:
   for name,native in [('r1_battery_charged_state_refresh',0x3dd0c),('r1_battery_voltage_average',0x3dda0),('r1_battery_level_average',0x3d834)]:
    actual_entries[native]=name;actual_entries[syms[name]&~1]=name
  control_entries={}
  if real_control:
   for name,native in [('r1_battery_charging_progress_reset',0x4fe5c),('r1_battery_task_flags_set',0x77240),('r1_shared_power_client_acquire',0x50778),('r1_shared_power_client_release',0x50758)]:
    control_entries[native]=name;control_entries[syms[name]&~1]=name
  def hook(u,a,size,_):
   if u is machines[1] and 0x27000<=a<0xc4d08:raise AssertionError(("native candidate execution",hex(a)))
   if a in actual_entries:
    counts=executed['native' if u is machines[0] else 'source'];name=actual_entries[a];counts[name]=counts.get(name,0)+1
   if a in control_entries:
    counts=control_executed['native' if u is machines[0] else 'source'];name=control_entries[a];counts[name]=counts.get(name,0)+1
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n=='osThreadFlagsSet':event+=tuple(r[:2]);value=0x80000004
   elif n=='r1_yhm_register_write_native':
    assert r[:2]==[2,1];command=bytes(u.mem_read(r[2],1));assert command in (b'\xa8',b'\x28');event+=(r[0],r[1],command.hex());value=0xffffffff
    if f['mutation']:u.mem_write(0x20006878,struct.pack('<I',0x80))
   elif n=='r1_native_charger_state_get':value=f['state']
   elif n=='r1_battery_task_flags_set':event+=(r[0],)
   elif n=='r1_shared_power_client_acquire':event+=(r[0],);assert r[0]==0
   elif n=='r1_battery_charged_state_refresh':
    extra=struct.unpack('<I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),4)))[0];event+=(*r,extra);assert tuple(r[1:])+ (extra,)==(B+36,B+12,B+40,B+14);value=f['charged']
   elif n=='osKernelGetTickCount':value=f['tick']
   elif n=='r1_battery_five_sample_filter_and_conversion':value=f['sample']
   elif n=='r1_batcfg_word1_signed_get':value=f['offset']
   elif n=='__aeabi_memclr':
    event+=tuple(r[:2]);assert r[0]==D+2 and r[1]==16;u.mem_write(D+2,bytes(16))
    if f['mutation']:u.mem_write(D,b'\xa5')
   elif n=='r1_battery_voltage_average':
    if f['mutation']:u.mem_write(D+42,struct.pack('<H',0x1234))
   elif n=='r1_battery_stuck_charge_recovery':
    event+=tuple(r[:2]);assert r[1]==B+36
    if f['mutation']:u.mem_write(B+36,struct.pack('<I',0x12345678))
   elif n=='r1_battery_discharge_curve':event+=tuple(r[:2]);value=33
   elif n=='r1_battery_charging_cadence':
    assert r[:2]==[struct.unpack('<H',bytes(u.mem_read(D+42,2)))[0],struct.unpack('<I',bytes(u.mem_read(B+36,4)))[0]];event+=tuple(r[:2]);value=77
   elif n=='r1_battery_level_average':value=f['average']
   elif n=='r1_battery_diagnostic_cadence_step':event+=(*r,*struct.unpack('<2I',bytes(u.mem_read(u.reg_read(UC_ARM_REG_SP),8))))
   elif n=='r1_battery_low_escalation':
    if f['mutation']:u.mem_write(D+44,b'\x00')
   elif n in ('r1_proto_report_battery_status','r1_glasses_tag_frame_send'):
    event+=tuple(r[:2])
    if f['mutation']:u.mem_write(D+44,b'\xff')
   elif n=='r1_shared_power_client_release':
    event+=(r[0],)
    if f['mutation']:u.mem_write(D+44,b'\x5a')
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,f in enumerate(cases):
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={**f,'trace':[]};u.mem_write(D-8,bytes([0x93])*84);u.mem_write(B-8,bytes([0xa5])*80);u.mem_write(D,bytes([(f['ring']<<4)|13,f['level_ring']]));u.mem_write(D+42,struct.pack('<H',f['voltage']));u.mem_write(D+44,bytes([f['charge'],*f['flags']]));u.mem_write(D+48,bytes([99 if f['persist'] else 0]));u.mem_write(D+49,struct.pack('<H',0x4567 if f['persist'] else 0));u.mem_write(B,bytes([f['previous'],int(f['filter'])]));u.mem_write(B+12,struct.pack('<H',0x2345));u.mem_write(B+14,struct.pack('<H',0x3456));u.mem_write(B+36,struct.pack('<I',123 if f['persist'] else 0));u.mem_write(B+40,struct.pack('<I',0xaabbccdd));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,f['rounding']<<22)
    if real_control:u.mem_write(0x20006638,struct.pack('<I',0x20014418));u.mem_write(0x20006878,struct.pack('<I',index&7))
    if f.get('cold'):
     for address,data in cold.items():u.mem_write(address,data)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_runtime_update_service']|1) if candidate else 0x31fd1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(D-8,84)),bytes(u.mem_read(B-8,80)),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20006878,4)) if real_control else None))
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(repr((index,f,results)));raise AssertionError((index,f))
   digest.update(repr((index,f,results[0])).encode())
 if real_statistics:assert executed['native']==executed['source'] and len(executed['source'])==3 and all(v==len(cases) for v in executed['source'].values()),executed
 if real_control:assert control_executed['native']==control_executed['source'] and len(control_executed['source'])==4 and all(v>0 for v in control_executed['source'].values()),control_executed
 receipt=dict(comparisons=len(cases),cold_context_cases=24,real_statistics=True,real_control=True,executed_control_entry_counts=control_executed,executed_statistics_entry_counts=executed,explicit_numeric_rounding_cases=rounding_cases,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),layout_sha256=sha(layout),application_sha256=sha(app),source_owned_cold_contexts_match=True,existing_status_and_adc_aliases_preserved=True,no_native_candidate_execution=True,full_raw_abi_verified=False,whole_battery_hardware_graph_executed=False,instruction_identity=False,whole_image_complete=False,limitations=['Updater/statistics/control source execute; other lower algorithm/hardware/reporting providers remain fixtures','Alias and cold-byte evidence do not establish concurrency or hardware behavior','All four FPSCR modes/final FPSCR compared; private frame and complete raw ABI remain gates'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
