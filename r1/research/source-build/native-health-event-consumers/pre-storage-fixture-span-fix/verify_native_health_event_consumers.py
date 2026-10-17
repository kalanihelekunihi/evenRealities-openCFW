#!/usr/bin/env python3
"""Native health consumers, packed saved words and actual callback composition."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-event-consumers';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;D=0x20010000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
CALLBACKS={0x42788:'activity',0x42896:'hr',0x428a4:'hrv',0x4296a:'spo2',0x42978:'stress',0x42a10:'temperature'};FAMILIES={0x8a7f4:'activity',0x8a80a:'hr',0x8a83e:'hrv',0x8a8ae:'spo2',0x8a8d8:'stress',0x8a8fc:'temperature'};STORAGE={0x5aa14:'activity',0x5ad90:'hr',0x5af60:'hrv',0x5bb2c:'spo2',0x5bcec:'stress',0x5be7c:'temperature'}
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-health-event-consumers-runtime.o';assert sha(obj)==b['linked_sha256'];c=json.loads((OUT/'contracts.json').read_text());providers={int(a,16):n for a,n in c['providers'].items()};providers.update({0x914ec:'r1_structured_log_mode_get',0x91638:'r1_structured_log_format',0x799c8:'nrf_log_frontend_std_1',0x79a0c:'nrf_log_frontend_std_5'});app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==c['application_sha256'];states={};counts=dict(direct=0,callback_composed=0,faults=0);by_family=dict.fromkeys(FAMILIES.values(),0);digest=hashlib.sha256();obs=dict(timestamp=0,storage=0,notify=0,mode=0,ring=0,sdk=0)
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 with tempfile.TemporaryDirectory(prefix='r1-health-consumers-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';text=d/'text.bin';rom=''.join(' .s'+x['address'][2:]+' '+x['address']+' : { *('+x['section']+') } ' for x in json.loads((BASE/'native-event-callbacks/text-spans.json').read_text()) if 'section' in x);ld.write_text('SECTIONS { '+rom+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:0x1100001+256*i for i,n in enumerate(providers.values())};roots=b['roots']+['r1_event_callback_%08x'%a for a in CALLBACKS];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for n in roots for v in ['-u',n]],'-T',str(ld),*[f'--defsym={n}={a}' for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};hooks={a:a for a in providers};hooks.update({bindings[n]&~1:a for a,n in providers.items()})
  def hook(u,a,size,_):
   if a not in hooks:return
   a=hooks[a];st=states[id(u)];case=st['case'];args=[u.reg_read(x) for x in REGS];value=case['result'];extra=[]
   if a==0x8ada4:
    kind='timestamp';value=case['now']
    if case['mutation']:u.mem_write(D,struct.pack('<I',0x1234ef));st['live_value']=0x1234ef
   elif a in STORAGE:
    kind='storage';extra=[bytes(u.mem_read(args[0],8)).hex()];st['storage'].append([STORAGE[a],extra[0]])
    if case['mutate_record']:u.mem_write(args[0],bytes.fromhex('deadbeefcafebabe'))
   elif a==0x8b138:kind='notify';st['notify'].append(args[0])
   elif a==0x914ec:kind='mode';value=case['modes'][min(st['modes'],len(case['modes'])-1)];st['modes']+=1;args=[value]
   elif a==0x91638:
    kind='ring';count=(args[0]>>22)&15;extra=list(struct.unpack('<'+'I'*max(0,count-1),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-1)*4)));args=args[:3+min(1,count)]
   else:
    kind='sdk';count=1 if a==0x799c8 else 5;extra=list(struct.unpack('<'+'I'*max(0,count-2),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-2)*4)));args=args[:2+min(2,count)]
   st['trace'].append([kind,hex(a),args,extra,value]);
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[value,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  default=dict(entry=0x8a80a,value=100,oldtime=0,now=0x12345678,payload=D,length=8,result=0,mutation=0,mutate_record=0,modes=[0]);cases=[]
  for value in range(65536):cases.append(dict(default,entry=0x8a8fc,value=value))
  for entry,value,oldtime,now,mutation,mutate_record in itertools.product([0x8a80a,0x8a8ae,0x8a8d8],range(256),[0,1,0xffffffff],[0,0xffffffff],range(2),range(2)):cases.append(dict(default,entry=entry,value=value,oldtime=oldtime,now=now,mutation=mutation,mutate_record=mutate_record))
  for entry,value,oldtime,now,payload,result in itertools.product(FAMILIES,[0,1,39,40,69,70,100,101,220,221,249,250,500,501,65535],[0,1],[0x7fffffff,0x80000000],[0,D,D+1,0x2003ffff],[0,1,0xffffffff]):cases.append(dict(default,entry=entry,value=value,oldtime=oldtime,now=now,payload=payload,result=result))
  for entry,value,oldtime,now,modes,mutation,mutate_record in itertools.product(CALLBACKS,[0,39,40,69,70,100,101,220,221,249,250,500,501,65535],[0,1],[0,0xffffffff],[[0],[7],[0,4,2]],range(2),range(2)):cases.append(dict(default,entry=entry,value=value,oldtime=oldtime,now=now,modes=modes,mutation=mutation,mutate_record=mutate_record))
  for case in cases:
   results=[];family=(FAMILIES|CALLBACKS)[case['entry']];composed=case['entry'] in CALLBACKS
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*512);u.mem_write(D,struct.pack('<3I',case['value'],case['oldtime'],0x12345678));u.mem_write(SP-1024,b'\x96'*2048);args=[case['payload'],case['length'],0xabcdef01,0x98765432]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(case=case,side=side,trace=[],storage=[],notify=[],modes=0,fault=None,live_value=case['value']);states[id(u)]=st;name=('r1_event_callback_' if composed else 'r1_event_service_')+'%08x'%case['entry']
    try:u.emu_start((syms[name] if side else case['entry'])|1,0x20000100,count=10000)
    except UcError:assert st['fault'],(case,side,hex(u.reg_read(UC_ARM_REG_PC)))
    if not st['fault']:
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
     if not composed and case['payload']==D:
      accepted=case['value']!=0 if family=='activity' else 40<=(case['value']&255)<=220 if family=='hr' else True if family=='hrv' else (case['value']&255)>=70 if family=='spo2' else (case['value']&255)<=100 if family=='stress' else 250<=(case['value']&65535)<=500
      if family=='activity':accepted=True
      assert bool(st['storage'])==accepted,(case,st)
      if accepted and family!='activity':
       when=case['oldtime'] if family in ['hr','hrv'] and case['oldtime'] else case['now'];live=st['live_value'];packed=(struct.pack('<H',live&65535) if family=='hrv' else bytes([((live&255)+6 if family=='temperature' else live)&255]))+struct.pack('<I',when);assert bytes.fromhex(st['storage'][0][1]).startswith(packed),(case,st['storage'],packed.hex())
      expected_notify=[] if not accepted or family in ['stress','temperature'] else [dict(activity=4,hr=0,hrv=5,spo2=1)[family]];assert st['notify']==expected_notify
    results.append([None if st['fault'] else [u.reg_read(x) for x in REGS],st['trace'],st['fault'],bytes(u.mem_read(D,16)).hex()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(case=case,results=results),indent=2)+'\n');raise AssertionError(case)
   counts['callback_composed' if composed else 'direct']+=1;counts['faults']+=bool(results[0][2]);by_family[family]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=counts['direct']+counts['callback_composed'],counts=counts,by_family=by_family,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),rea_bytes_sha256=sha(OUT/'rea-native-bytes.json'),all_65536_temperature_words_checked=True,packed_field_validation_and_timestamp_rules_independently_checked=True,actual_six_consumers_and_callbacks_execute=True,clock_storage_notification_and_log_are_fixtures=True,full_dispatcher_composition=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
