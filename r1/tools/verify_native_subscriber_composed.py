#!/usr/bin/env python3
"""Source registration -> multicast through actual local sync wrappers/config."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-registration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;ROOTS=0x20015708;MUTEX=0x20006794;PAY=0x20030000;CB=0x20001000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];states={}
def word(u,a):return int.from_bytes(u.mem_read(a,4),'little')
def main():
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();digest=hashlib.sha256();counts=dict(workflows=0,registrations=0,multicasts=0,inline_callbacks=0,publishes=0);proof=[]
 objects=[OUT/'native_subscriber_registration.o',BASE/'native-event-multicast/native_event_multicast.o',BASE/'native-subscriber-sync/native_subscriber_sync.o'];bodies=[]
 for stage in ['native-subscriber-registration','native-event-multicast','native-subscriber-sync']:bodies+=json.loads((BASE/stage/'contracts.json').read_text())['bodies']
 with tempfile.TemporaryDirectory() as tmp:
  td=Path(tmp);ld=td/'proof.ld';ld.write_text('SECTIONS {'+''.join(' .b%d %s : { *(.text.%s) }'%(i,x['address'],x['symbol']) for i,x in enumerate(bodies))+' .routes 0x99ba8 : { *(.r1.subscriber.routes) } .attr 0x99bb8 : { *(.r1.subscriber.attr) } .name 0xbf784 : { *(.r1.subscriber.name) } .mutex 0x20006794 : { *(.r1.subscriber.mutex) } .roots 0x20015708 : { *(.r1.subscriber.roots) } .control 0x2001571c : { *(.r1.subscriber.control) } /DISCARD/ : { *(.ARM.exidx*) } }\n'+''.join('%s = 0x%x;\n'%(n,a) for n,a in {'pvPortMalloc':0x855a1,'vPortFree':0x95d49,'memmove':0x2775d,'r1_event_publish':0x8d8fd,'osMutexNew':0x7d4d7,'osMutexAcquire':0x7d489,'osMutexRelease':0x7d537,'xTaskGetCurrentTaskHandle':0x9879d,'r1_event_sensor':0x2000668c,'r1_event_system':0x20006608}.items()));elf=td/'proof.elf';subprocess.run(['arm-none-eabi-ld','-T',str(ld),*[str(x) for x in objects],'-o',str(elf)],check=True,stderr=subprocess.PIPE);replacements=[]
  for sec,a,n in [*[(f'.b{i}',int(x['address'],16),x['source_span_bytes']) for i,x in enumerate(bodies)],('.routes',0x99ba8,16),('.attr',0x99bb8,16),('.name',0xbf784,12)]:
   f=td/(sec[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',sec,'-O','binary',str(elf),str(f)],check=True);d=f.read_bytes();assert len(d)==n and d==raw[a-0x27000:a-0x27000+n];replacements.append((a,d));proof.append(dict(address=hex(a),size=n,sha256=hashlib.sha256(d).hexdigest()))
  fixture_addresses=[0x855a0,0x95d48,0x2775c,0x8d8fc,0x7d4d6,0x7d488,0x7d536,0x9879c,CB,CB+16,CB+32]
  def hook(u,a,size,_):
   if a not in fixture_addresses:return
   s=states[id(u)];r=[u.reg_read(x) for x in REGS];ret=0x98765432;s['trace'].append([a,r])
   if a==0x855a0:ret=s['next'];s['next']+=(r[0]+7)&~7;s['allocations'].append([ret,r[0]])
   elif a==0x2775c:u.mem_write(r[0],bytes(u.mem_read(r[1],r[2])) if r[2] else b'');ret=r[0]
   elif a==0x7d4d6:assert r[0]==0x99bb8;ret=0x20002000
   elif a in [0x7d488,0x7d536]:assert r[0]==0x20002000;ret=s['status']
   elif a==0x9879c:ret=s['thread']
   elif a==0x8d8fc:s['published'].append([r[:3],bytes(u.mem_read(r[1],r[2])).hex()]);ret=s['status'];counts['publishes']+=1
   elif a in [CB,CB+16,CB+32]:s['inline'].append([a,r[0],r[1]]);ret=1;counts['inline_callbacks']+=1
   elif a==0x95d48:s['frees'].append(r[0])
   for reg,val in zip(REGS,[ret,0xa1a1a1a1,0xb2b2b2b2,0xc3c3c3c3]):u.reg_write(reg,val)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x100000);u.mem_write(0x27000,raw);u.mem_map(0x20000000,0x40000)
   if side:
    for a,d in replacements:u.mem_write(a,d)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  for roles,length,current,status,idx in itertools.product(itertools.product(range(3),repeat=3),[0,1,4,5,12],[0x11111111,0x22222222,0x33333333],[0,1,0xffffffff],[0,4]):
   expected_contexts=[0x20006694 if r==0 else 0x20006610 if r==1 else 0x20011000 for r in roles];context_threads={0x20006694:0x11111111,0x20006610:0x22222222,0x20011000:0x33333333};payload=bytes(range(length));outputs=[]
   for u in machines:
    u.mem_write(ROOTS,bytes(100));u.mem_write(MUTEX,bytes(4));u.mem_write(0x20006694,struct.pack('<I',0x11111111));u.mem_write(0x20006610,struct.pack('<I',0x22222222));u.mem_write(0x20011000,struct.pack('<I',0x33333333));u.mem_write(0x20018000,b'\x96'*512);u.mem_write(PAY,payload or b'\0');s=dict(next=0x20018000,trace=[],published=[],inline=[],frees=[],allocations=[],thread=current,status=status);states[id(u)]=s
    def call(a,args,expected):
     u.mem_write(SP-128,b'\x96'*256)
     for reg,val in zip(REGS,args+[0x87654321]):u.reg_write(reg,val)
     u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start(a|1,0x20000100,count=2000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_R0)==expected
    for i,context in enumerate(expected_contexts):call(0x8af8c,[idx,CB+i*16+1,0 if context==0x20006694 else context],1)
    call(0x8af8c,[idx,CB+1,0x20011000],0)
    header=word(u,ROOTS+idx*4);assert header==0x20018000 and word(u,header)==0x20018010 and word(u,header+4)==0x20018030
    for i,context in enumerate(expected_contexts):assert bytes(u.mem_read(0x20018010+i*16,12))==struct.pack('<3I',CB+i*16+1,context,0x20018010+(i+1)*16 if i<2 else 0)
    call(0x8b028,[idx,PAY,length],1)
    assert s['inline']==[[CB+i*16,PAY,cx] for i,cx in enumerate(expected_contexts) if context_threads[cx]==current]
    routes=[]
    for cx in expected_contexts:
     if context_threads[cx]!=current and cx in [0x20006694,0x20006610]:
      channel=2 if cx==0x20006694 else 0x1000
      if channel not in routes:routes.append(channel)
    assert [x[0][0] for x in s['published']]==routes
    for args,packet in s['published']:
     data=bytes.fromhex(packet);assert args[1:]==[0x20018040,length+8] and data[:6]==struct.pack('<IH',0x20018010,length) and data[6:6+length]==payload and data[6+length:]==b'\x96'*2
    assert s['frees']==[0x20018040] and s['allocations']==[[0x20018000,12],[0x20018010,12],[0x20018020,12],[0x20018030,12],[0x20018040,length+8]]
    assert bytes(u.mem_read(header+8,4))==(payload+bytes(4-length) if length<=4 else b'\0'*4)
    outputs.append([s['trace'],s['published'],s['inline'],bytes(u.mem_read(0x20018000,128)).hex(),bytes(u.mem_read(ROOTS,100)).hex(),bytes(u.mem_read(SP-128,256)).hex()])
   assert outputs[0]==outputs[1];counts['workflows']+=1;counts['registrations']+=4;counts['multicasts']+=1;digest.update(json.dumps([roles,length,current,status,idx,outputs[0]],sort_keys=True).encode())
 v=dict(comparisons=counts['workflows'],counts=counts,trace_sha256=digest.hexdigest(),exact_spans=proof,exact_rom_bytes=sum(x['size'] for x in proof),object_sha256s={str(p.relative_to(ROOT)):sha(p) for p in objects},report_sha256=sha(OUT/'report.json'),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),actual_registration_multicast_and_sync_execute=True,heap_memmove_cmsis_publish_and_task_providers_are_fixtures=True,independent_list_and_route_oracle=True,full_private_history_or_raw_abi_verified=False,whole_image_complete=False,hardware_write_executed=False);(OUT/'composed-verification.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
