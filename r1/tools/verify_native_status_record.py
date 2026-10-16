#!/usr/bin/env python3
"""Native status packing/ring and real state getters; remaining provider gates explicit."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-status-record';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'r1_status_record_ring_publish':(0x5e118,170),'r1_device_state_byte_2d_get':(0x91264,8),'r1_peer_channel_count':(0x4cb08,26),'r1_charge_state_byte_get':(0x91270,28)}
A={'r1_status_read_index':0x20006938,'r1_status_write_index':0x20006939,'r1_status_dropped':0x2000693c,'r1_status_records':0x20019bc8,'r1_device_state_byte_2c':0x20016bb0,'r1_device_state_byte_2d':0x20016bb1,'r1_connection_field8':0x200064ba,'r1_connection_field10':0x200064bc}
P={'r1_advertising_configuration_byte_get':0x7ba24,'r1_battery_runtime_update_service':0x31fd0,'r1_structured_log_local_timestamp':0x8ad40,'vPortEnterCritical':0x95cf4,'vPortExitCritical':0x95d24,'r1_event_publish':0x8d8fc}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_status_record.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};socket='/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock'
 for n,(a,z) in ENTRIES.items():
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket',socket,f'http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x{a:x}&length={z}']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[a-0x27000:a-0x27000+z];p=OUT/('ghidra-'+n+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 counts={n:0 for n in ENTRIES};drops=0;events=0;rng=random.Random(0x5e118)
 with tempfile.TemporaryDirectory() as directory:
  d=Path(directory);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';bindings={n:0x1100001+i*16 for i,n in enumerate(P)};ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),*['--defsym='+n+'='+hex(a) for n,a in {**bindings,**A}.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};image=binary.read_bytes();assert len(image)<0x10000;machines=[];states={};kinds={a:n for n,a in P.items()};kinds.update({a&~1:n for n,a in bindings.items()})
  for _ in (0,1):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,image);u.mem_map(0x1100000,0x1000);u.mem_map(0x20000000,0x40000);machines.append(u)
  def hook(u,a,size,_):
   if a not in kinds:return
   f=states[id(u)];n=kinds[a];value=0;event=(n,)
   if n=='r1_advertising_configuration_byte_get':value=f['configuration']
   elif n=='r1_battery_runtime_update_service':u.mem_write(0x20016bb0,bytes([f['updated']]))
   elif n=='r1_structured_log_local_timestamp':
    value=0x89abcdef
    if f['mutation']==1:u.mem_write(0x20006938,b'\x05\x0f')
   elif n=='vPortEnterCritical':
    if f['mutation']==2:u.mem_write(0x20006938,b'\x00\x0f')
   elif n=='r1_event_publish':
    event=(n,*[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]);assert event[1:]==(0x2003,0,0);value=0x12345678
   f['trace'].append(event);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for u in machines:u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def case(name,args=(),device=0,charge=0,configuration=0,updated=0,peers=(0xffff,0xffff),read=0,write=0,dropped=0,mutation=0):
   nonlocal drops,events
   results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]={'trace':[],'configuration':configuration,'updated':updated,'mutation':mutation};u.mem_write(0x20006938,bytes([read,write,0xa5,0x5a])+struct.pack('<H',dropped)+b'\x96\x69');u.mem_write(0x20019bc0,bytes([0x93])*144);u.mem_write(0x20016bb0,bytes([charge,device]));u.mem_write(0x200064ba,struct.pack('<2H',*peers));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,value)
    u.emu_start((syms[name]|1) if candidate else ENTRIES[name][0]|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    results.append((None if name=='r1_status_record_ring_publish' else u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(0x20006938,8)),bytes(u.mem_read(0x20019bc0,144)),bytes(u.mem_read(0x20016bb0,2)),bytes(u.mem_read(0x200064ba,4))))
   assert results[0]==results[1],(name,args,device,charge,configuration,updated,peers,read,write,dropped,mutation,results);counts[name]+=1
   if name=='r1_status_record_ring_publish':
    events+=1;drops+=struct.unpack('<H',results[0][2][4:6])[0]!=dropped
    assert results[0][2][2:4]==b'\xa5\x5a' and results[0][2][6:8]==b'\x96\x69'
  for args,device,peer_count,charge in itertools.product(itertools.product((0,3,64,0xffffffff),repeat=4),(0,1,2,3,255),(0,1,2),(0,1,127,255)):
   case('r1_status_record_ring_publish',args,device,charge,configuration=0x55 if device&1 else 0,updated=charge,peers=((0,0xffff) if peer_count==1 else (0,1) if peer_count==2 else (0xffff,0xffff)),write=rng.randrange(16),read=rng.randrange(16),dropped=rng.choice((0,0xfffe,0xffff)))
  for read,write,dropped,mutation in itertools.product(range(16),range(16),(0,0xfffe,0xffff),(0,1,2)):case('r1_status_record_ring_publish',(0xffffffff,0xffffffff,0xffffffff,0xffffffff),255,255,peers=(0,1),read=read,write=write,dropped=dropped,mutation=mutation)
  for device in range(256):case('r1_device_state_byte_2d_get',device=device)
  for peers in itertools.product((0,1,0xfffe,0xffff),repeat=2):case('r1_peer_channel_count',peers=peers)
  for charge,configuration,updated in itertools.product(range(256),(0,0x55,0xffffff55,0xffffffff),(0,85,255)):case('r1_charge_state_byte_get',charge=charge,configuration=configuration,updated=updated)
 rea={p.name:sha(p) for p in OUT.glob('rea-*.json')}
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,drop_counter_updates=drops,drain_event_calls=events,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),ghidra_evidence=evidence,rea_evidence=rea,entries=ENTRIES,data_anchors=A,application_linked=False,instruction_identity=False,limitations=['Configuration accessor, battery updater, timestamp, critical boundaries and event publish are fixtures','Real peer/device/charge getters execute in publisher cases','16-byte state/record boundary sentinels authenticate write width; valid write indices0..15 only','Ring/device-state initialization and actual lower-provider/canonical graph remain gates','Native counter is16-bit despite decompiler32-bit spelling; adjacent bytes remain unchanged']),indent=2)+'\n');print('Status publisher/getters:',counts,'drops',drops,'drain events',events)
if __name__=='__main__':main()
