#!/usr/bin/env python3
"""Check both native snapshot ranges with explicit health-cache fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-crash-snapshot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;D=0x20010000;A=D+0x1000;H=D+0x2000;O=D+0x3000;V=D+0x4000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_crash_snapshot.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 rea=OUT/'rea-snapshot.json';ev=json.loads(rea.read_text())['structuredContent'];body=ev['normalized_result']['procedure']['body'];assert body['non_contiguous'] and body['total_bytes']==350 and body['ranges']==[dict(start='0x3f47c',end='0x3f52f'),dict(start='0x5a324',end='0x5a3cd')]
 states={};counts=dict(clear=0,activity=0,hr=0,spo2=0,hrv=0,query=0);digest=hashlib.sha256();total=0
 with tempfile.TemporaryDirectory(prefix='r1-crash-snapshot-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  names=['__aeabi_memclr','r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_spo2_daily_cache_accessor','r1_hrv_daily_cache_accessor','r1_hr_hour_query'];bindings={name:0x1100001+i*16 for i,name in enumerate(names)}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_health_crash_snapshot_builder',*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  kinds=['clear','activity','hr','spo2','hrv','query'];hooks=dict(zip([0x277aa,0x5a9f0,0x5ace0,0x5baec,0x5af18,0x5ab6c],kinds));hooks.update({0x1100000+i*16:k for i,k in enumerate(kinds)})
  def hook(u,a,size,_):
   kind=hooks.get(a)
   if not kind:return
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS];result=0
   if kind=='clear':st['trace'].append([kind,args[:2]]);u.mem_write(args[0],bytes(args[1]))
   elif kind=='query':
    st['trace'].append([kind,args,bytes(u.mem_read(args[2],4)).hex(),bytes(u.mem_read(args[3],2)).hex()]);u.mem_write(args[2],struct.pack('<I',0x87654321));u.mem_write(args[3],b'\x23\xf1')
    if st['mode']==1:u.mem_write(D+45,b'\x80');u.mem_write(O+75,b'\xff');u.mem_write(V+147,b'\xff\xff')
    result=0xdeadbeef
   else:
    index=kinds.index(kind)-1;result=([A,H,O,V][index] if st['mask']&(1<<index) else 0)
    if kind=='activity' and result and st['mode']==2:result=D
    st['trace'].append([kind,result])
   if not st['side']:counts[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  timestamps=[hour*3600 for hour in range(24)]+[0xffffffff,0x80000000,86400]
  for timestamp,offset,mask,mode,seed in itertools.product(timestamps,[-32768,-721,-720,-1,0,1,720,721,32767],range(16),range(3),[0,0xaa]):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*256);u.mem_write(SP-1024,bytes([seed])*2048)
    for address in [A,H,O,V]:u.mem_write(address,bytes(((i*73+seed)&255) for i in range(1024)))
    u.mem_write(H+75,bytes([seed]));u.mem_write(O+75,bytes([seed]));u.mem_write(V+147,struct.pack('<H',seed))
    for reg,value in zip(REGS,[D,timestamp,offset&0xffffffff,0xabcdef01]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]=dict(side=side,trace=[],mask=mask,mode=mode)
    u.emu_start((syms['r1_health_crash_snapshot_builder'] if side else 0x5a324)|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(D,256)).hex(),*[bytes(u.mem_read(address,1024)).hex() for address in [A,H,O,V]]])
   assert results[0]==results[1],(timestamp,offset,mask,mode,seed,results[0][:3],results[1][:3])
   total+=1;digest.update(json.dumps([timestamp,offset,mask,mode,seed,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=total,observation_counts=counts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),rea_sha256=sha(rea),actual_both_snapshot_ranges=True,providers_and_clear_are_fixtures=True,declared_query_outputs_and_native_pointer_offsets_checked=True,raw_r0_callee_sp_record_and_cache_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,actual_health_provider_composition_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
