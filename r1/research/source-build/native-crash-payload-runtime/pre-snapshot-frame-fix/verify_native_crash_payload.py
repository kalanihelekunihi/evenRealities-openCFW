#!/usr/bin/env python3
"""Crash graph with actual caches/query/CRC; only clock backend is a fixture."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-crash-payload-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;CTX=0x20007a34;D=0x20010000;TIME=0x20016ac4;PAYLOAD=0x2001e054
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'crash-initialize-source.o';assert sha(obj)==r['graph_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 evidence=BASE/'native-crash-payload/rea-getter.json';n=json.loads(evidence.read_text())['structuredContent']['normalized_result'];assert n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[0x6abe4-0x27000:0x6abf8-0x27000]
 states={};counts=dict(timestamp=0,payload=0,snapshot=0,query=0,crc=0,copy=0);digest=hashlib.sha256();total=0;direct=0
 with tempfile.TemporaryDirectory(prefix='r1-crash-payload-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x20007a34 : { *(.r1.reset.retained.context) } .time_state 0x20016ac4 : { *(.r1.time.state) } .registration 0x20006820 : { *(.r1.time.registration) } .activity 0x200166c4 : { *(.r1.health.cache.activity) } .hr 0x2001654c : { *(.r1.health.cache.hr) } .spo2 0x200165a0 : { *(.r1.health.cache.spo2) } .hrv 0x200169c0 : { *(.r1.health.cache.hrv) } .hourly 0x20016648 (NOLOAD) : { *(.bss.r1.hourly.accumulators) } .payload 0x2001e054 (NOLOAD) : { *(.bss.r1.crash.payload) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_health_crash_record_initializer',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_crash_payload']==PAYLOAD
  hooks={0x6abe4:'payload',0x5a324:'snapshot',0x5ab6c:'query',0x5d87c:'crc',0x2775c:'copy'}
  for name,kind in [('r1_crash_record_marker_set','payload'),('r1_health_crash_snapshot_builder','snapshot'),('r1_hr_hour_query','query'),('r1_stock_crc16_modbus','crc')]:hooks[syms[name]]=kind
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   st=states[id(u)]
   if a==0x1100000:
    assert u.reg_read(UC_ARM_REG_R0)==0;st['trace'].append(['timestamp'])
    if not st['side']:counts['timestamp']+=1
    if st['mode']==1:put(u,CTX+8,D+0x1000);u.mem_write(TIME+8,b'\x34\x12')
    elif st['mode']==2:u.mem_write(TIME+11,b'\x80');u.mem_write(D+4,b'\x54\xaa')
    elif st['mode']==3:u.mem_write(0x2001654c+75,b'\xff');u.mem_write(0x20016648+2,b'\xff\xff')
    for reg,value in zip(REGS,[st['timestamp'],0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   kind=hooks.get(a)
   if not kind:return
   args=[u.reg_read(reg) for reg in REGS]
   if not st['side']:counts[kind]+=1
   if kind=='payload':st['trace'].append([kind,args[0],bytes(u.mem_read(args[0],4)).hex() if args[0] else None])
   elif kind=='snapshot':st['trace'].append([kind,args[:3]])
   elif kind=='query':st['trace'].append([kind,args,bytes(u.mem_read(args[2],4)).hex(),bytes(u.mem_read(args[3],2)).hex()])
   elif kind=='crc':st['trace'].append([kind,args[:2],bytes(u.mem_read(args[0],args[1])).hex()])
   else:st['trace'].append([kind,args[:3]])
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def invoke(u,entry,args):
   for reg,value in zip(REGS,args):u.reg_write(reg,value)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
   u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(entry|1,0x20000100,count=200000)
   assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
   return u.reg_read(UC_ARM_REG_R0)
  for timestamp,offset,status,seed,mode in itertools.product([0,23*3600,0xffffffff,0x80000000,86400],[-32768,-721,-720,-1,0,1,720,721,32767],[0,1,2,255],[0,0xaa,0xff],range(4)):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*0x2000);u.mem_write(0x20016400,bytes([seed])*0x800);u.mem_write(PAYLOAD,bytes([seed])*736);u.mem_write(SP-2048,b'\x96'*4096);u.mem_write(CTX,struct.pack('<6I',0,0,D,0,0,0));u.mem_write(TIME,bytes(16));u.mem_write(TIME+8,struct.pack('<h',offset));u.mem_write(TIME+11,bytes([status]));put(u,0x20006828,0x20018000);put(u,0x20018008,0x1100001)
    hour=((timestamp+max(-720,min(720,offset))*60)&0xffffffff)%86400//3600;u.mem_write(0x20016648,struct.pack('<BBHI',hour,0,seed,0x87654321)*6)
    states[id(u)]=dict(side=side,trace=[],timestamp=timestamp,mode=mode)
    raw=invoke(u,syms['r1_health_crash_record_initializer'] if side else 0x5a2b8,[0x12345678,0x87654321,0x11223344,0xabcdef01])
    results.append([raw,u.reg_read(UC_ARM_REG_R3),states[id(u)]['trace'],bytes(u.mem_read(D,0x2000)).hex(),bytes(u.mem_read(CTX,24)).hex(),bytes(u.mem_read(0x20016400,0x800)).hex(),bytes(u.mem_read(PAYLOAD,736)).hex()])
   assert results[0]==results[1],(timestamp,offset,status,seed,mode,results[0][:3],results[1][:3])
   total+=1;digest.update(json.dumps([timestamp,offset,status,seed,mode,results[0]],sort_keys=True).encode())
  for pointer,seed in itertools.product([0,D,D+1,D+2,PAYLOAD,PAYLOAD+734,SP-24,SP-12],[0,0xaa,0xff]):
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*16);u.mem_write(PAYLOAD,bytes([seed])*736);u.mem_write(SP-128,bytes([seed])*256);states[id(u)]=dict(side=side,trace=[],mode=0,timestamp=0)
    raw=invoke(u,syms['r1_crash_record_marker_set'] if side else 0x6abe4,[pointer,0x12345678,0x87654321,0xabcdef01]);results.append([raw,bytes(u.mem_read(D,16)).hex(),bytes(u.mem_read(PAYLOAD,736)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert results[0]==results[1],(pointer,seed,results);direct+=1
 receipt=dict(initializer_comparisons=total,getter_comparisons=direct,observation_counts=counts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence_sha256=sha(evidence),actual_initializer_snapshot_caches_query_status_offset_crc_and_payload=True,only_timestamp_backend_is_fixture=True,payload_advertises736_and_copy896_gate_unreached=True,raw_r0_restored_r3_callee_sp_record_cache_payload_ram_checked=True,producer_lifecycle_proven=False,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
