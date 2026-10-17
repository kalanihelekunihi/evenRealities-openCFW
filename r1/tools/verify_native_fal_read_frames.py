#!/usr/bin/env python3
"""Native read/dispatch frames: missing handles/ops, raw registers and request aliases."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-fal-read-frames';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;HANDLE=0x200077c0;REQ=0x2001e56c;DEV=0x20010000;OPS=DEV+64;BUFFER=DEV+128;CALL=0x20001000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 obj=OUT/'native_fal_read_frames.o';stateobj=OUT/'read-state.o';app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';image=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts={'device_read':0,'dispatch':0,'faults':0,'driver_calls':0}
 with tempfile.TemporaryDirectory() as td:
  td=Path(td);ld=td/'layout.ld';ld.write_text('SECTIONS { .read 0x87af8 : { *(.text.r1_native_fal_device_read) } .dispatch 0x85d2c : { *(.text.r1_stock_dispatch_10) } .handle 0x200077c0 (NOLOAD) : { *(.r1.fal.device_handle) } .request 0x2001e56c (NOLOAD) : { *(.r1.fal.read_request) } /DISCARD/ : { *(.ARM.exidx*) } }');elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),str(stateobj),'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacement=[]
  for sec,a,length in [('read',0x87af8,40),('dispatch',0x85d2c,26)]:
   p=td/(sec+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+sec,'-O','binary',str(elf),str(p)],check=True);data=p.read_bytes();assert len(data)==length and data==image[a-0x27000:a-0x27000+length];replacement.append((a,data))
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=[access,address,size,value];return False
  def hook(u,a,size,_):
   if a!=CALL:return
   s=states[id(u)];c=s['case'];r=[u.reg_read(x) for x in REGS];assert r==[DEV,0,REQ,0];words=struct.unpack('<3I',u.mem_read(REQ,12));assert words==(c['destination'],c['offset'],c['length']);s['trace'].append([r,list(words)]);u.mem_write(words[0],bytes(range(min(words[2],8))))
   if c['mutation']&1:u.mem_write(REQ,struct.pack('<3I',0x11223344,0x55667788,0x99aabbcc))
   if c['mutation']&2:u.mem_write(HANDLE,struct.pack('<I',0))
   for reg,value in zip(REGS,[c['result'],0xaabbccdd,0x12345678,0xfedcba98]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,image);u.mem_map(0x20000000,0x40000)
   if side:
    for a,data in replacement:u.mem_write(a,data)
   u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  cases=[dict(entry=entry,mode=mode,offset=offset,length=length,result=result,mutation=mutation,destination=destination) for entry,mode,offset,length,result,mutation,destination in itertools.product(['device_read','dispatch'],range(4),[0,1,0x80000000,0xffffffff],[0,1,32,0xffffffff],[0,1,0x80000000,0xffffffff],range(4),[BUFFER,REQ,REQ+4])]
  for c in cases:
   results=[]
   for u in machines:
    u.mem_write(DEV,b'\x96'*256);u.mem_write(DEV+4,struct.pack('<I',0x20100000 if c['mode']==1 else OPS));u.mem_write(OPS+16,struct.pack('<I',CALL+1 if c['mode']==3 else 0));u.mem_write(HANDLE,struct.pack('<I',DEV if c['mode'] else 0));u.mem_write(REQ,struct.pack('<3I',c['destination'],c['offset'],c['length']));u.mem_write(SP-128,b'\x96'*256)
    args=[c['offset'],c['destination'],c['length'],0xabcdef01] if c['entry']=='device_read' else [DEV if c['mode'] else 0,0,REQ,0]
    for r,v in zip(REGS,args):u.reg_write(r,v)
    for i,r in enumerate(SAVED):u.reg_write(r,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);s=dict(case=c,trace=[],fault=None);states[id(u)]=s
    try:u.emu_start(0x87af9 if c['entry']=='device_read' else 0x85d2d,0x20000100,count=1000)
    except UcError:assert s['fault']
    assert bool(s['fault'])==(c['mode']==1)
    if not s['fault']:
     expected=c['length'] if c['entry']=='device_read' else c['result'] if c['mode']==3 else 2 if c['mode']==2 else 1;assert u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(r) for r in SAVED]==[0x12340000+i for i in range(8)]
    assert len(s['trace'])==int(c['mode']==3);results.append([[u.reg_read(r) for r in REGS],u.reg_read(UC_ARM_REG_SP),s['fault'],s['trace'],bytes(u.mem_read(DEV,256)).hex(),bytes(u.mem_read(REQ,12)).hex(),bytes(u.mem_read(HANDLE,4)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1],c;counts[c['entry']]+=1;counts['faults']+=int(c['mode']==1);counts['driver_calls']+=int(c['mode']==3);digest.update(json.dumps([c,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=len(cases),counts=counts,trace_sha256=digest.hexdigest(),object_sha256=sha(obj),read_state_object_sha256=sha(stateobj),driver_sha256=sha(Path(__file__)),report_sha256=sha(OUT/'report.json'),application_sha256=sha(app),actual_read_and_registry_dispatch_execute=True,driver_callback_is_fixture=True,request_alias_and_mutation_and_missing_paths_checked=True,ignored_driver_result_and_saved_length_oracle=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'direct-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
