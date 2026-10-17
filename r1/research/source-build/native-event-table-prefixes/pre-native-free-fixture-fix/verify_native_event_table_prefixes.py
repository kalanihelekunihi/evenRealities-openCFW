#!/usr/bin/env python3
"""Authenticate typed event-table relocations and dispatch through bounded prefixes."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-event-table-prefixes';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;D=0x20010000
def main():
 b=json.loads((OUT/'report.json').read_text());contracts=json.loads((OUT/'prefix-contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';obj=OUT/'native-event-table-prefixes-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 states={};callback_map={w&~1:n for t in contracts['tables'] for w,n in zip(t['words'],t['callbacks']) if w};counts=dict(sensor=0,system=0,storage=0);digest=hashlib.sha256();callbacks=frees=0
 with tempfile.TemporaryDirectory(prefix='r1-event-prefixes-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';text=d/'text.bin';layout=''.join(' .'+t['family']+' '+t['address']+' : { *('+t['section']+') } ' for t in contracts['tables']);ld.write_text('SECTIONS { '+layout+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:w for t in contracts['tables'] for w,n in zip(t['words'],t['callbacks']) if n};subprocess.run(['arm-none-eabi-ld','--gc-sections','-u','r1_native_event_dispatch','-T',str(ld),'--defsym=vPortFree=0x1100001',*[f'--defsym={n}={w}' for n,w in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);symbols={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};relocated={}
  for t in contracts['tables']:
   p=d/(t['family']+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+t['family'],'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();assert data==struct.pack('<'+'I'*len(t['words']),*t['words']);assert symbols['r1_native_event_table_'+t['family']]==int(t['address'],16);relocated[t['family']]=data
  def hook(u,a,size,_):
   st=states[id(u)]
   if a==0x1100000:st['trace'].append(['free',u.reg_read(UC_ARM_REG_R0)])
   elif a in callback_map or a==0x1100100:
    st['trace'].append(['callback',callback_map.get(a,'replacement'),u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.mem_write(D+4,struct.pack('<3I',0xffffffff,0,0xdeadbeef))
   else:return
   for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[0x12345678,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  for t in contracts['tables']:
   for index,length,payload,mutation in itertools.product(range(1,len(t['words'])),[0,4,5,65535],[0,1,D+0x100,0xffffffff],range(3)):
    results=[];event_id=index+1 if t['family']=='sensor' else (0x1000 if t['family']=='system' else 0x2000)+index-1
    for side,u in enumerate(machines):
     for table in contracts['tables']:u.mem_write(int(table['address'],16),relocated[table['family']])
     if mutation:u.mem_write(int(t['address'],16)+index*4,struct.pack('<I',0 if mutation==1 else 0x1100101))
     u.mem_write(D,struct.pack('<4I',0x12345678,event_id|0xabcd0000,length|0xbeef0000,payload));states[id(u)]=dict(trace=[]);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((symbols['r1_native_event_dispatch'] if side else 0x8d888)|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP
     results.append([states[id(u)]['trace'],bytes(u.mem_read(D,16)).hex(),[bytes(u.mem_read(int(table['address'],16),4*len(table['words']))).hex() for table in contracts['tables']]])
    assert results[0]==results[1],(t['family'],index,length,payload,mutation,results)
    expect=t['callbacks'][index] if mutation==0 else None if mutation==1 else 'replacement';trace=results[0][0];assert [x[1:] for x in trace if x[0]=='callback']==([[expect,payload,length]] if expect else []) and [x[1:] for x in trace if x[0]=='free']==([[payload]] if length>4 else [])
    callbacks+=bool(expect);frees+=length>4;counts[t['family']]+=1;digest.update(json.dumps([t['family'],index,length,payload,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations=callbacks,free_observations=frees,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),prefix_contracts_sha256=sha(OUT/'prefix-contracts.json'),relocated_prefix_bytes=sum(len(x) for x in relocated.values()),actual_source_dispatch_and_typed_table_relocations=True,all_observed_prefix_slots_and_writable_rebinding_checked=True,callbacks_and_free_are_fixtures=True,callback_bodies_source_complete=False,full_table_extents_proven=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
