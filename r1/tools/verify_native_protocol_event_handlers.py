#!/usr/bin/env python3
"""Event leaf contracts, raw stack records, supplemental target and boundary faults."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-event-handlers';I=0x20010000;SP=0x2003f000;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());unit=r['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';rows=list(csv.DictReader(ledger.open()));activity_row=next(row for row in rows if row['image']=='application' and row['entry']=='0x00082c10');assert activity_row['size']=='52' and not any(row['image']=='application' and row['entry']=='0x00084cc0' for row in rows);evidence={}
 for address,size in [(0x84cc0,24),(0x82c10,52)]:
  p=OUT/('rea-'+format(address,'x')+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-'+format(address,'x')+'-body.json')).read_bytes());j=json.loads(p.read_text());assert j['error']['code']=='invalid_request';evidence[p.name]=sha(p)
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(size)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+size];p=OUT/('ghidra-'+format(address,'x')+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address=0x9a588&length=8']);assert bytes(json.loads(raw)['data'])==struct.pack('<HHI',1,0,0x84cc1);p=OUT/'ghidra-special-registration.json';p.write_bytes(raw);evidence[p.name]=sha(p)
 attribution={'native_entry':'0x84cc0','native_end':'0x84cd7','native_body_bytes':24,'symbol':'r1_protocol_command_00084cc0','locked_ownership_row':False,'registration_address':'0x9a588','registration_key':1,'registration_pointer':'0x84cc1','attribution':'Registered Thumb target, exact Ghidra-MCP bytes and complete native branch/return execution; no locked ledger mutation','source':'r1/components/board/native_protocol_event_handlers.c','unresolved_gates':['Full event provider composition, canonical startup/device/imageidentity']};p=OUT/'target-attribution.json';p.write_text(json.dumps(attribution,indent=2)+'\n')
 machines=[];states={};counts={'special':0,'activity':0};events={'special':0,'activity':0};faults={};trace_hash=hashlib.sha256()
 with tempfile.TemporaryDirectory() as temporary:
  d=Path(temporary);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_event_publish=0x1100001',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def invalid(u,access,address,size,value,_):states[id(u)]['fault']=(access,address,size);return False
  def hook(u,address,size,_):
   f=states[id(u)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs[3]==f['original3'];data=None
   if f['kind']=='special':
    assert regs[:3]==[15,(f['packet']+12)&0xffffffff,9] and u.reg_read(UC_ARM_REG_SP)==SP and u.reg_read(UC_ARM_REG_LR)==0x20000101
    if f['packet']==I:data=bytes(u.mem_read(regs[1],9))
   else:
    assert regs[:3]==[14,SP-16,8];data=bytes(u.mem_read(SP-16,8));assert data==f['record'],(f,data,f['record'])
   f['trace'].append((regs,data.hex() if data is not None else None))
   if f['mutation'] and data is not None:u.mem_write(regs[1],bytes(byte^0xa5 for byte in data))
   for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(f['raw'],0x11111111,0x22222222,0x33333333)):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.mem_map(0xfffff000,4096);machines.append(u);u.hook_add(UC_HOOK_MEM_INVALID,invalid)
   for address in (0x8d8fc,0x1100000):u.hook_add(UC_HOOK_CODE,hook,begin=address,end=address)
   if len(machines)==2:
    def reject(u,address,size,_):
     if address!=0x8d8fc:raise AssertionError(('source executed native',hex(address)))
    u.hook_add(UC_HOOK_CODE,reject,begin=0x20000,end=0xe0000)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  special=(('special',I,length,0,0,(length*997)&0xffffffff,length^0xdeadbeef,length&1,0xffffffff if length&1 else 0) for length in range(65536))
  edges=(('special',packet,length,0,0,seed,seed^0xffffffff,mutation,raw) for packet,length,seed,mutation,raw in itertools.product((0xfffffff4,0xfffffff3),(0,12,13,65535),(0,0xffffffff),(0,1),(0,7,0xffffffff)))
  activity=(('activity',I,0,flags,sequence,seed,seed^0xdeadbeef,mutation,raw) for flags,sequence,seed,mutation,raw in itertools.product(range(256),(0,1,255,256,65535),(0,0x12345678,0xffffffff),(0,1),(0,7,0xffffffff)))
  all_sequences=(('activity',I,0,0,sequence,(sequence*37)&0xffffffff,(sequence*71)&0xffffffff,sequence&1,0x80000007) for sequence in range(65536))
  aliases=(('activity',packet,0,0,sequence,seed,seed^0xdeadbeef,mutation,raw) for packet,sequence,seed,mutation,raw in itertools.product((SP-21,SP-19,SP-16,SP-15,SP-12,SP-8,SP-4),(0,65535),(0,0x12345678,0xffffffff),(0,1),(0,0xffffffff)))
  nulls=[('special',0,0,0,0,0,0,0,0),('activity',0,0,0,0,0,0,0,0)]
  for index,(kind,packet,length,flags,sequence,original2,original3,mutation,raw) in enumerate(itertools.chain(special,edges,activity,all_sequences,aliases,nulls)):
   results=[];handle=(index*997)&0xffffffff
   for candidate,u in enumerate(machines):
    u.mem_write(I,bytes(range(64)));u.mem_write(I+3,struct.pack('<H',sequence));u.mem_write(I+5,bytes([flags]));u.mem_write(I+8,struct.pack('<H',length));u.mem_write(SP-96,b'\x96'*160);u.mem_write(SP-16,struct.pack('<4I',original2,original3,0x12345600,0x20000101));u.mem_write(0xffffffe0,b'\x5a'*32)
    if packet>=0xfffff000:u.mem_write(packet+8,struct.pack('<H',length))
    expected_event=False;record=None
    if kind=='special' and packet:expected_event=bool(((length-12)&65535) and ((packet+12)&0xffffffff))
    elif kind=='activity' and packet:
     initial_flags=bytes(u.mem_read(packet+5,1))[0];expected_event=not(initial_flags&3)
     if expected_event:
      frame=bytearray(u.mem_read(SP-16,16));frame[0:2]=b'\x04\0'
      if SP-16<=packet+3 and packet+5<=SP:seq=bytes(frame[packet+3-(SP-16):packet+5-(SP-16)])
      else:seq=bytes(u.mem_read(packet+3,2))
      frame[2:4]=seq;record=bytes(frame[:8])
    states[id(u)]={'kind':kind,'packet':packet,'original3':original3,'mutation':mutation,'raw':raw,'trace':[],'fault':None,'record':record};u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(handle,packet,original2,original3)):u.reg_write(reg,value)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    entry=syms['r1_protocol_command_00084cc0' if kind=='special' else 'r1_activity_refresh_handler'] if candidate else 0x84cc0 if kind=='special' else 0x82c10
    try:u.emu_start(entry|1,0x20000100,count=1000)
    except UcError:assert not packet and states[id(u)]['fault']
    f=states[id(u)]
    if f['fault']:results.append(('fault',f['fault']));continue
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];assert len(f['trace'])==int(expected_event);regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if kind=='special':expected=[raw,0x11111111,0x22222222,0x33333333] if expected_event else [(length-12)&65535,packet if length==12 else 0,original2,original3]
    elif expected_event:
     final_record=bytes(byte^0xa5 for byte in record) if mutation else record;expected=[raw,0x11111111,*struct.unpack('<2I',final_record)]
    else:expected=[initial_flags if initial_flags&2 else 0,packet,original2,original3]
    assert regs==expected,(index,kind,packet,candidate,regs,expected);results.append((regs,f['trace'],bytes(u.mem_read(I,64)),bytes(u.mem_read(SP-16,16)) if kind=='activity' else None,bytes(u.mem_read(0xffffffe0,32))))
   assert results[0]==results[1],(index,kind,packet,length,flags,sequence,original2,original3,mutation,raw,results);counts[kind]+=1
   if results[0][0]=='fault':faults[kind]=results[0][1]
   else:events[kind]+=expected_event
   trace_hash.update(json.dumps((kind,packet,length,flags,sequence,original2,original3,mutation,raw,results[0]),default=lambda value:value.hex()).encode())
 vp.write_text(json.dumps(dict(comparisons=sum(counts.values()),counts=counts,event_calls_per_side=events,fault_boundaries=faults,all_special_length_halfwords=True,all_activity_sequence_halfwords=True,all_activity_flag_bytes=True,full_r0_r1_r2_r3=True,activity_native_frame16=True,activity_incoming_r3_word_preserved=True,special_tail_stack_and_lr=True,wrapped_payload_pointer_zero_checked=True,record_mutation_and_header_aliases=True,trace_sha256=trace_hash.hexdigest(),target_attribution_sha256=sha(OUT/'target-attribution.json'),activity_ownership_row=activity_row,ownership_sha256=sha(ledger),rea_boundary_available=False,evidence=evidence,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,application_linked=False,instruction_identity=False,limitations=['Special24-byte body is a supplemental registered target without a locked ownership row; original ledger unchanged','Event publisher is an explicit boundary fixture; actual queue/delivery and uninitialized downstream event record remain gated','Activity Cworker uses extra private callstack; its bytes outside the native16-byte saved frame are not compared, including packet aliases there; event writes beyond the passed8-byte record remain gated','Null header and wrapped payload boundary faults modeled; no physical exception/interrupt/concurrency proof','Other compiler/LTO, canonical fullstartup and instruction/wholeimage identity remain gated']),indent=2)+'\n');print('Protocol event leaves:',counts,events,faults)
if __name__=='__main__':main()
