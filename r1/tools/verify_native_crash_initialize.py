#!/usr/bin/env python3
"""Crash initializer and byte-status leaf with explicit provider fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-crash-initialize';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;CTX=0x20007a34;D=0x20010000;TIME=0x20016ac4
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_crash_initialize.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 rea=BASE/'native-crash-initializer-rea.json';ev=json.loads(rea.read_text())['structuredContent'];assert ev['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and ev['normalized_result']['procedure']['body']['total_bytes']==104
 states={};digest=hashlib.sha256();counts=dict(offset=0,timestamp=0,payload=0,copy=0,snapshot=0,crc=0);cases=0
 with tempfile.TemporaryDirectory(prefix='r1-crash-init-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  bindings={'r1_reset_trace_context':CTX,'r1_time_state':TIME,'r1_time_utc_offset_get':0x1100001,'r1_time_backend_timestamp':0x1100011,'r1_crash_record_marker_set':0x1100021,'memcpy':0x1100031,'r1_health_crash_snapshot_builder':0x1100041,'r1_stock_crc16_modbus':0x1100051}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_health_crash_record_initializer',*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   kind={0x8adb4:'offset',0x1100000:'offset',0x8ada4:'timestamp',0x1100010:'timestamp',0x6abe4:'payload',0x1100020:'payload',0x2775c:'copy',0x1100030:'copy',0x5a324:'snapshot',0x1100040:'snapshot',0x5d87c:'crc',0x1100050:'crc'}.get(a)
   if not kind:return
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS];result=0x12345678
   if kind=='offset':
    st['trace'].append([kind]);result=st['offset']
    if st['mode']==1:put(u,CTX+8,D+0x1000)
   elif kind=='timestamp':
    st['trace'].append([kind]);result=0xabcdef12
    if st['mode']==2:u.mem_write(TIME+11,b'\xff');u.mem_write(D+4,b'\x54\xaa')
   elif kind=='payload':
    st['trace'].append([kind,args[0],bytes(u.mem_read(args[0],4)).hex()]);result=0 if st['null'] else D+0x2000
    u.mem_write(args[0],struct.pack('<H',st['length']))
    if st['mode']==3:u.mem_write(D+6,b'\x34\x80');put(u,D+8,0x87654321)
   elif kind=='copy':
    st['trace'].append([kind,args[:3]]);u.mem_write(args[0],bytes(u.mem_read(args[1],args[2])));result=args[0]
   elif kind=='snapshot':
    st['trace'].append([kind,args[:3]]);u.mem_write(args[0],bytes([st['status']])*52)
    if st['mode']==4:put(u,CTX+8,D+0x1000);u.mem_write(D+100,b'\x42')
   else:
    st['trace'].append([kind,args[:2],bytes(u.mem_read(args[0],args[1])).hex()]);result=0xfedc1234
   if not st['side']:counts[kind]+=1
   for reg,value in zip(REGS,[result&0xffffffff,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for null,length,status,offset,mode,seed in itertools.product([0,1],[0,736,895,896,897,65535],[0,1,2,255],[-32768,0,32767],range(5),[0,0xaa]):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*0x3000);u.mem_write(D+0x2000,bytes(range(256))*4);u.mem_write(CTX,struct.pack('<6I',0,0,D,0,0,0));u.mem_write(TIME,bytes(16));u.mem_write(TIME+11,bytes([status]));u.mem_write(SP-1024,bytes([seed])*2048)
    for reg,value in zip(REGS,[0x12345678,0x87654321,0x11223344,0xabcdef01]):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]=dict(side=side,trace=[],null=null,length=length,status=status,offset=offset,mode=mode)
    u.emu_start((syms['r1_health_crash_record_initializer'] if side else 0x5a2b8)|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R3),states[id(u)]['trace'],bytes(u.mem_read(D,0x3000)).hex(),bytes(u.mem_read(CTX,24)).hex(),bytes(u.mem_read(SP-24,24)).hex()])
   assert results[0]==results[1],(null,length,status,offset,mode,seed,results[0][:3],results[1][:3])
   cases+=1;digest.update(json.dumps([null,length,status,offset,mode,seed,results[0]],sort_keys=True).encode())
  for status in range(256):
   for side,u in enumerate(machines):
    u.mem_write(TIME+11,bytes([status]));u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms['r1_time_status_get'] if side else 0x8ad98)|1,0x20000100,count=100);assert u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==SP
 receipt=dict(initializer_comparisons=cases,status_comparisons=256,observation_counts=counts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),rea_sha256=sha(rea),actual_initializer_and_status_bodies=True,other_callees_are_fixtures=True,external_frame24_and_saved_r3_halfword_checked=True,raw_r0_callee_sp_record_ram_checked=True,full_private_frame_history_verified=False,actual_payload_snapshot_crc_composition_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
