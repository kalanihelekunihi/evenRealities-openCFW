#!/usr/bin/env python3
"""Actual battery updater/filter/statistics/control composition; ADC registry/delay remain fixtures."""
import hashlib,itertools,json,random,struct,subprocess,tempfile,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-battery-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();D=0x20016b84;B=0x20006890
P={'r1_native_charger_state_get':0x50618,'r1_battery_task_flags_set':0x77240,'r1_native_charger_initialize':0x5079c,'r1_battery_charged_state_refresh':0x3dd0c,'osKernelGetTickCount':0x7d28c,'r1_battery_charging_progress_reset':0x4fe5c,'r1_battery_five_sample_filter_and_conversion':0x91184,'r1_batcfg_word1_signed_get':0x7bb7c,'__aeabi_memclr':0x277aa,'r1_battery_voltage_average':0x3dda0,'r1_battery_stuck_charge_recovery':0x3db70,'r1_battery_discharge_curve':0x50004,'r1_battery_charging_cadence':0x4fe70,'r1_battery_level_average':0x3d834,'r1_battery_diagnostic_cadence_step':0x3d9b8,'r1_battery_low_escalation':0x3d88c,'r1_proto_report_battery_status':0x8345c,'r1_shared_power_client_release':0x50758,'r1_glasses_tag_frame_send':0x913fc}
def main():
 real_control=True;real_statistics=True;providers=dict(P);provider_reports={};executed={'native':{},'source':{}};control_executed={'native':{},'source':{}}
 if real_statistics:
  for name in ('r1_battery_charged_state_refresh','r1_battery_voltage_average','r1_battery_level_average'):del providers[name]
  providers['r1_shared_power_client_acquire']=0x50778
 if real_control:
  for name in ('r1_battery_charging_progress_reset','r1_battery_task_flags_set','r1_shared_power_client_release','r1_shared_power_client_acquire'):del providers[name]
  providers.update(osThreadFlagsSet=0x7d6f4,r1_yhm_register_write_native=0x35760)
 del providers['r1_battery_five_sample_filter_and_conversion']
 providers.update(r1_stock_dispatch_08=0x85d1a,r1_stock_dispatch_0c=0x85cba,r1_stock_dispatch_10=0x85d2c,nrf_delay_ms=0x78550,osDelay=0x7d154)
 vp=OUT/'filter-integration-verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_battery_runtime.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 objects=[obj]
 filter_report=BASE/'native-battery-filter/report.json';fr=json.loads(filter_report.read_text());fo=filter_report.parent/'native_battery_filter.o';assert sha(fo)==fr['units'][0]['object_sha256'];objects.append(fo);provider_reports['native-battery-filter/report.json']=sha(filter_report)
 for path,h in fr['inputs'].items():assert sha(ROOT/path)==h,path
 filter_counts={'native':0,'source':0}
 if real_statistics:
  stats_report=BASE/'native-battery-statistics/report.json';stats=json.loads(stats_report.read_text());stats_object=stats_report.parent/'native_battery_statistics.o';assert sha(stats_object)==stats['units'][0]['object_sha256'];objects.append(stats_object);provider_reports['native-battery-statistics/report.json']=sha(stats_report)
  for path,h in stats['inputs'].items():assert sha(ROOT/path)==h,path
 if real_control:
  control_report=BASE/'native-battery-control/report.json';control=json.loads(control_report.read_text());control_object=control_report.parent/'native_battery_control.o';assert sha(control_object)==control['units'][0]['object_sha256'];objects.append(control_object);provider_reports['native-battery-control/report.json']=sha(control_report)
  for path,h in control['inputs'].items():assert sha(ROOT/path)==h,path
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock';raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x31fd0&length=406']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[0x31fd0-0x27000:0x32166-0x27000];(OUT/'ghidra-memory.json').write_bytes(raw)
 rea=json.loads((OUT/'rea-pseudocode.json').read_text());assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';rng=random.Random(0x31fd0);cases=[];rounding_cases=0
 def fixture(**changes):
  f=dict(state=1,charged=1,flags=(0,0),persist=False,filter=True,mutation=False,average=50,sample=3600,offset=0,tick=0,ring=7,level_ring=7,charge=50,previous=50,voltage=3800,rounding=0)
  f.update(changes);return f
 for state,charged,flags,persist,filtered,mutation,average in itertools.product((0,1,2,0xffffffff),(0,1),((0,0),(1,0),(0,1),(255,255)),(False,True),(False,True),(False,True),(0,1,50,94,95,255)):
  cases.append(fixture(state=state,charged=charged,flags=flags,persist=persist,filter=filtered,mutation=mutation,average=average,sample=rng.choice((0,32767,32768,65535,3600)),offset=rng.choice((0,299,300,(-299)&0xffffffff,(-300)&0xffffffff)),tick=rng.choice((0,1,0xffffffff)),charge=rng.choice((0,1,50,94,95,255)),previous=rng.choice((0,1,50,255))))
 for sample,offset,charged,rounding in itertools.product((0,1,32767,32768,65535,0xffff8000),((-300)&0xffffffff,(-299)&0xffffffff,0,299,300,0x7fffffff,0xffffffff),(0,1),range(4)):
  cases.append(fixture(sample=sample,offset=offset,charged=charged,rounding=rounding));rounding_cases+=1
 for _ in range(1024):cases.append(fixture(state=rng.randrange(3),charged=rng.getrandbits(1),sample=rng.getrandbits(32),offset=rng.getrandbits(32),charge=rng.randrange(256),previous=rng.randrange(256),ring=rng.randrange(16),level_ring=rng.randrange(8),average=rng.choice((0,1,94,95,255,256,0xffffffff)),persist=bool(rng.getrandbits(1)),filter=bool(rng.getrandbits(1)),mutation=bool(rng.getrandbits(1)),flags=(rng.randrange(2),rng.randrange(2)),rounding=rng.randrange(4)))
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(providers)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_battery_device_context='+hex(D),'--defsym=r1_battery_runtime_context='+hex(B),*(['--defsym=r1_battery_thread_handle=0x20006638','--defsym=r1_shared_power_clients=0x20006878'] if real_control else []),*['--defsym='+n+'='+hex(a) for n,a in bindings.items()],*map(str,objects),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in providers.items()};kinds.update({a&~1:n for n,a in bindings.items()})
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
   if a in (0x91184,syms['r1_battery_five_sample_filter_and_conversion']):filter_counts['native' if u is machines[0] else 'source']+=1
   if a in actual_entries:
    counts=executed['native' if u is machines[0] else 'source'];name=actual_entries[a];counts[name]=counts.get(name,0)+1
   if a in control_entries:
    counts=control_executed['native' if u is machines[0] else 'source'];name=control_entries[a];counts[name]=counts.get(name,0)+1
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];event=(n,);value=0
   if n in ('r1_stock_dispatch_08','r1_stock_dispatch_0c'):
    handle=struct.unpack('<I',bytes(u.mem_read(B+16,4)))[0];assert r[0]==handle;event+=(handle,)
   elif n=='r1_stock_dispatch_10':
    handle=struct.unpack('<I',bytes(u.mem_read(B+16,4)))[0];assert r[0]==handle and r[1]==0 and r[3]==1
    before=struct.unpack('<I',bytes(u.mem_read(r[2],4)))[0];assert before&65535==0
    sample=(f['sample']+f['adc_reads']*137)&65535;u.mem_write(r[2],struct.pack('<H',sample));event+=(handle,sample);f['adc_reads']+=1
    if f['mutation']:u.mem_write(B+16,struct.pack('<I',handle+16));u.mem_write(B+1,bytes([f['adc_reads']%2]))
   elif n in ('nrf_delay_ms','osDelay'):
    assert r[0]==2 and n==('osDelay' if bytes(u.mem_read(B+1,1))[0] else 'nrf_delay_ms');event+=(2,)
   elif n=='osThreadFlagsSet':event+=tuple(r[:2]);value=0x80000004
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
    states[id(u)]={**f,'trace':[],'adc_reads':0};u.mem_write(D-8,bytes([0x93])*84);u.mem_write(B-8,bytes([0xa5])*80);u.mem_write(D,bytes([(f['ring']<<4)|13,f['level_ring']]));u.mem_write(D+42,struct.pack('<H',f['voltage']));u.mem_write(D+44,bytes([f['charge'],*f['flags']]));u.mem_write(D+48,bytes([99 if f['persist'] else 0]));u.mem_write(D+49,struct.pack('<H',0x4567 if f['persist'] else 0));u.mem_write(B,bytes([f['previous'],int(f['filter'])]));u.mem_write(B+12,struct.pack('<H',0x2345));u.mem_write(B+14,struct.pack('<H',0x3456));u.mem_write(B+36,struct.pack('<I',123 if f['persist'] else 0));u.mem_write(B+40,struct.pack('<I',0xaabbccdd));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,f['rounding']<<22)
    if real_control:u.mem_write(0x20006638,struct.pack('<I',0x20014418));u.mem_write(0x20006878,struct.pack('<I',index&7))
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms['r1_battery_runtime_update_service']|1) if candidate else 0x31fd1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(D-8,84)),bytes(u.mem_read(B-8,80)),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20006878,4)) if real_control else None))
   assert states[id(machines[0])]['adc_reads']==states[id(machines[1])]['adc_reads']==5
   assert results[0]==results[1],(index,f,[(i,a,b) for i,(a,b) in enumerate(zip(*results)) if a!=b])
 if real_statistics:assert executed['native']==executed['source'] and len(executed['source'])==3 and all(v==len(cases) for v in executed['source'].values()),executed
 if real_control:assert control_executed['native']==control_executed['source'] and len(control_executed['source'])==4 and all(v>0 for v in control_executed['source'].values()),control_executed
 assert filter_counts=={'native':len(cases),'source':len(cases)}
 vp.write_text(json.dumps(dict(executed_filter_entry_counts=filter_counts,comparisons=len(cases),real_statistics=real_statistics,real_control=real_control,executed_control_entry_counts=control_executed,executed_statistics_entry_counts=executed,provider_reports=provider_reports,explicit_numeric_rounding_cases=rounding_cases,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_memory_sha256=sha(OUT/'ghidra-memory.json'),rea_sha256=sha(OUT/'rea-pseudocode.json'),native_entry='0x31fd0',native_size=406,application_linked=False,instruction_identity=False,limitations=['Actual filter, refresh, averages and control execute; ADC registry/delay and remaining hardware/algorithm/reporting endpoints are fixtures; opaque read-word high halves are not compared in this graph, and direct filter verification covers them','Raw device/runtime roots are address bindings, not source-owned initialization','All four FPSCR rounding modes and final FPSCR are compared; physical FPU/concurrency not proven','Packed native-width SRAM views preserve unaligned values; physical interrupt ordering/atomicity/concurrency remain gates','Charged-state refresh consumes five semantic arguments; no decompiler scratch sixth argument']),indent=2)+'\n');print('Battery runtime:',len(cases),'native/source comparisons;',rounding_cases,'explicit numeric/FPSCR cases; real statistics:',real_statistics)
if __name__=='__main__':main()
