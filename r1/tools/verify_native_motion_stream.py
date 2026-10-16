#!/usr/bin/env python3
"""Motion selection and sample adapter; sensor/probe/NV/clock ports are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-motion-stream-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;SEL=0x200076ac;BYPASS=0x20006c35;HANDLE=0x20007dfc;TICK=0x2001a2b4;D=0x20010000;TABLE=D+0x1000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'motion-stream-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence={p.name:sha(p) for p in (BASE/'native-motion-stream').glob('rea-*.json')}
 for p in (BASE/'native-motion-stream').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[a-0x27000:a-0x27000+n['returned_bytes']]
 counts={k:0 for k in ['initialize','entry','interrupt','fifo','close','bypass','calibration','batch']};observations=dict(probe=0,open=0,interrupt=0,fifo=0,nv=0,policy=0,tick=0);states={};digest=hashlib.sha256()
 with tempfile.TemporaryDirectory(prefix='r1-motion-stream-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .selected 0x200076ac : { *(.r1.motion.selected) } .bypass 0x20006c35 : { *(.r1.motion.calib.bypass) } .handles 0x20007de8 : { *(.r1.nv.handles) } .tick_getter 0x2001a2b4 (NOLOAD) : { *(.bss.r1.stream.tick_getter) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  bindings={'r1_kv_class_read':0x1100001,'r1_motion_probe_and_select_provider':0x1100011,'osKernelGetTickCount':0x1100021};roots=['r1_motion_selected_provider_initialize','r1_motion_initialize_entry','r1_native_motion_interrupt','r1_motion_selected_fifo_read','r1_motion_stream_close_boundary','r1_motion_calibration_bypassed','r1_motion_calibration_read','r1_motion_thirty_sample_batch_producer']
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[arg for name in roots for arg in ['-u',name]],'-T',str(ld),'-e',roots[0],*[f'--defsym={name}={value}' for name,value in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_device_info_kv_handle']==HANDLE
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS]
   if a in [0x72b90,syms['r1_motion_calibration_bypassed']]:
    if st['kind']=='batch':
     i=st['policy_calls'];st['policy_calls']+=1;value=0 if st['policy']==0 else 255 if st['policy']==1 else i&1
     u.mem_write(BYPASS,bytes([value]));st['trace'].append(['policy',i,value])
     if st['policy']==3:u.mem_write(SP-24,struct.pack('<3H',i,65535-i,0x8000+i))
     if not st['side']:observations['policy']+=1
    return
   if a in [0x73930,0x1100000]:
    kind='nv';st['trace'].append([kind,args[:3]]);assert args[2]==124
    record=bytearray(b'\x55'*124);record[68:74]=struct.pack('<3H',*st['offsets'])
    if st['read_mode']==0:u.mem_write(args[1],bytes(record))
    elif st['read_mode']==1:u.mem_write(args[1],bytes(record[:70]))
    result=0 if st['read_mode']==0 else 0x12345678
    if st['mutation']:put(u,HANDLE,0)
   elif a in [0x50208,0x1100010]:kind='probe';st['trace'].append([kind,args]);put(u,SEL,TABLE+32 if st['probe'] else 0);result=0x12345678
   elif a==0x1100020:
    kind='tick';st['trace'].append([kind]);result=0x89abcdef
    if st['mutation'] and st['kind']=='batch':u.mem_write(st['destination']+180,b'\xff\xff')
   elif a in [0x1100100,0x1100200]:kind='open';st['trace'].append([kind,args]);result=st['returned']
   elif a in [0x1100130,0x1100230]:kind='interrupt';st['trace'].append([kind,args]);result=st['returned']
   elif a in [0x1100120,0x1100220]:
    kind='fifo';st['trace'].append([kind,args]);result=st['returned']
    if args[0]:u.mem_write(args[0],struct.pack('<3H',0xfff0,0x7fff,0x8001)*32)
    if st['mutation']:put(u,SEL,0)
   else:return
   if not st['side']:observations[kind]+=1
   for reg,value in zip(REGS,[result&0xffffffff,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  entries=dict(zip(counts,zip([0x50270,0x6f400,0x50294,0x502ac,0x6f300,0x72b90,0x7b9c8,0x6f4a0],roots)));saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  defaults=dict(selected=1,mask=7,probe=0,returned=30,seed=0,mutation=0,read_mode=0,offsets=(1,2,3),policy=0,destination=D,length=188,handle=D+0x3000)
  cases=[]
  for kind,selected,mask,probe,returned,seed,mutation in itertools.product(['initialize','entry','interrupt','fifo'],range(3),range(8),range(2),[0,1,30,0xffffffff],[0,0xaa],range(2)):cases.append(dict(defaults,kind=kind,selected=selected,mask=mask,probe=probe,returned=returned,seed=seed,mutation=mutation))
  for value in range(256):cases.append(dict(defaults,kind='bypass',value=value))
  for value in [0,1,30,0x12345678,0xffffffff]:cases.append(dict(defaults,kind='close',returned=value))
  offsets=[(0,0,0),(65535,65535,65535),(65535,65535,1),(1,32768,65534),(0x1234,0xabcd,0x7fff)]
  for read_mode,offset,destination,handle,seed in itertools.product(range(3),offsets,[D,D+1,D+2],[0,D+0x3000],[0,0xaa]):cases.append(dict(defaults,kind='calibration',read_mode=read_mode,offsets=offset,destination=destination,handle=handle,seed=seed))
  for returned,read_mode,offset,policy,seed,destination in itertools.product([0xffffffff,0x80000000,0,1,2,29,30,31,32,65536,65537,0x7fff0000],range(3),offsets,range(4),[0,0xaa],[D,D+1]):cases.append(dict(defaults,kind='batch',returned=returned,read_mode=read_mode,offsets=offset,policy=policy,seed=seed,destination=destination,mutation=seed!=0))
  for selected,mask,destination,length in itertools.product([0,1],[0,7],[0,D],[0,187,188,65724]):cases.append(dict(defaults,kind='batch',selected=selected,mask=mask,destination=destination,length=length))
  for case in cases:
   kind=case['kind'];results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([case['seed']])*0x4000);u.mem_write(SP-2048,bytes([0x96 if case['seed'] else 0])*4096);put(u,SEL,0 if not case['selected'] else TABLE if case['selected']==1 else TABLE+32);u.mem_write(BYPASS,bytes([case.get('value',0)]));put(u,HANDLE,case['handle']);put(u,TICK,0x1100021)
    for i in range(2):u.mem_write(TABLE+i*32,struct.pack('<4I',(0x1100101+i*256) if case['mask']&1 else 0,0,(0x1100121+i*256) if case['mask']&2 else 0,(0x1100131+i*256) if case['mask']&4 else 0))
    args=[case['destination'],case['length'],0x12345678,0xabcdef01]
    if kind=='fifo':args[1]=case['returned']
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);st=dict(case,side=side,trace=[],policy_calls=0);states[id(u)]=st
    u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=200000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),[u.reg_read(reg) for reg in [UC_ARM_REG_R2,UC_ARM_REG_R3]] if kind=='batch' else None,st['trace'],bytes(u.mem_read(D,512)).hex(),bytes(u.mem_read(SEL,4)).hex(),bytes(u.mem_read(BYPASS,1)).hex(),bytes(u.mem_read(HANDLE,4)).hex()])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,actual_eight_entries_batch_adjustment_and_shared_tick_selector=True,only_selected_sensor_probe_nv_read_clock_are_fixtures=True,raw_r0_batch_restored_r2_r3_callee_sp_and_ram_checked=True,exact_nv_scratch_and_offset_api_pointer_coordinates_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_nv_clock_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
