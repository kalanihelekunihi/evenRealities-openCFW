#!/usr/bin/env python3
"""Raw-seeded serial getter/report and response helpers versus authenticated native."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-serial';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003f000
ENTRIES={'ack':('r1_protocol_ack_header_send',0x82b54),'inverse':('r1_protocol_send_flag_inv',0x82b96),'checked':('r1_protocol_send_checked',0x84c5e),'read':('r1_native_product_serial_read',0x7ba78),'serial':('r1_device_serial_handler',0x83db0)}
def main():
 rp=BASE/'native-protocol-serial-runtime/report.json';r=json.loads(rp.read_text());obj=rp.parent/'protocol-serial-source.o';assert sha(obj)==r['serial_object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_protocol_serial_verification.ld';states={};digest=hashlib.sha256();counts={k:0 for k in ENTRIES};observations=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_device_info_kv_handle']==0x20007dfc and syms['r1_serial_record_class']==0x20006ad8
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for section,offset,n in [('.class',0x630,148),('.handle',0x1954,4)]:
   p=d/(section[1:]+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(p)],check=True);assert p.read_bytes()==cold[offset:offset+n]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   if a==(syms['r1_native_memory_move'] if source else 0x2775c):
    dest=u.reg_read(UC_ARM_REG_R0);src=u.reg_read(UC_ARM_REG_R1);n=u.reg_read(UC_ARM_REG_R2);assert n==15;st['events'].append(['move',dest,src,n,bytes(u.mem_read(src,n)).hex()]);return
   if a==(syms['memset'] if source else 0x2779c):
    dest=u.reg_read(UC_ARM_REG_R0);n=u.reg_read(UC_ARM_REG_R2 if source else UC_ARM_REG_R1);value=u.reg_read(UC_ARM_REG_R1 if source else UC_ARM_REG_R2);assert n==15 and value==255;st['events'].append(['fill',dest,n,value]);return
   if a==(0x20000200 if source else 0x73930):
    handle=u.reg_read(UC_ARM_REG_R0);record=u.reg_read(UC_ARM_REG_R1);assert u.reg_read(UC_ARM_REG_R2)==124 and record==st['record'];st['events'].append(['kv',handle,record,bytes(u.mem_read(record,124)).hex(),bytes(u.mem_read(st['destination'],16)).hex()]);u.mem_write(record,st['record_data'][:st['prefix']])
    if st['mutation']==1:u.mem_write(0x20007dfc,struct.pack('<I',0xabcdef01));u.mem_write(st['packet']+3,b'\x34\x12')
    elif st['mutation']==2:u.mem_write(st['destination'],b'\xa5'*16)
    u.reg_write(UC_ARM_REG_R0,st['status']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   if a==(0x20000204 if source else 0x828b4):
    handle=u.reg_read(UC_ARM_REG_R0);header=u.reg_read(UC_ARM_REG_R1);payload=u.reg_read(UC_ARM_REG_R2);length=u.reg_read(UC_ARM_REG_R3);assert length<=32;st['events'].append(['response',handle,bytes(u.mem_read(header,8)).hex(),payload,length,bytes(u.mem_read(payload,length)).hex() if length else ''])
    if st['mutation']==2:u.mem_write(header,b'\xff'*8)
    if st['kind'] in ['ack','inverse','checked']:
     u.reg_write(UC_ARM_REG_R1,0x87654321);u.reg_write(UC_ARM_REG_R2,0xabcdef01);u.reg_write(UC_ARM_REG_R3,0x12345678)
    u.reg_write(UC_ARM_REG_R0,st['status']);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  rng=random.Random(0x83db0);cases=[]
  for kind,flag,pattern in itertools.product(['ack','inverse','checked'],range(256),range(8)):cases.append(dict(kind=kind,flag=flag,pattern=pattern,poison=0x96,sentinel=0,prefix=124,destmode=0,lenmode=0,mutation=pattern%3))
  for poison,sentinel,prefix,destmode,lenmode,mutation in itertools.product([0,255,0x96,0xa5],[0,1,255],[0,1,31,32,45,46,61,62,123,124],range(6),range(5),range(3)):cases.append(dict(kind='read',flag=0,pattern=destmode,poison=poison,sentinel=sentinel,prefix=prefix,destmode=destmode,lenmode=lenmode,mutation=mutation))
  for poison,sentinel,prefix,pattern,mutation in itertools.product([0,255,0x96,0xa5],[0,1,255],[0,1,31,32,45,46,61,62,123,124],range(5),range(3)):cases.append(dict(kind='serial',flag=0,pattern=pattern,poison=poison,sentinel=sentinel,prefix=prefix,destmode=0,lenmode=0,mutation=mutation))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def execute(u,source,case,number,initialize=True):
   kind=case['kind'];pattern=case['pattern'];flag=case['flag'];record=SP-(176 if kind=='serial' else 136);destination=SP-32 if kind=='serial' else [0x20003000,0x20003001,record+30,record+31,record+32,record+61][case['destmode']];length_ptr=[0,0x20004000,destination,destination+14,record+61][case['lenmode']];packet=0x20005000+(number&1);handle=[0,1,0xffff,0x1000ffff,0xffffffff][pattern%5];command=[0,1,65535,0xffffffff,0x12345678,0x101,0x10,0x501][pattern];version=(flag*0x01010101)^(0xabcdef00 if pattern&2 else 0);flags=(flag*0x01010101)^(0xabcdef00 if pattern&4 else 0);sequence=[0,1,65535,65536,0xffffffff,0x12345678,0x80000000,0x11223344][pattern];status=[0,1,0xffffffff,0x80000000][(number+flag)%4];payload=0 if pattern==0 else 0x20006000;size=[0,1,15,16,32,0,15,32][pattern];data=bytearray((i*17+number)%256 for i in range(124));data[31:46]=b'R1-SERIAL-12345';data[61]=case['sentinel']
   if initialize:
    u.mem_write(0x20000000,bytes([case['poison']])*0x40000);u.mem_write(0x20007dfc,struct.pack('<I',0 if number&1 else 0x20002000));pkt=bytearray(range(32));pkt[3:5]=struct.pack('<H',sequence&65535);u.mem_write(packet,bytes(pkt));u.mem_write(0x20006000,bytes(range(32)))
   st=dict(kind=kind,source=source,events=[],record=record,destination=destination,packet=packet,record_data=bytes(data),prefix=case['prefix'],mutation=case['mutation'],status=status);states[id(u)]=st
   u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
   for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
   if kind in ['ack','inverse']:
    args=[handle,command,version,flags];stack=[sequence,payload,size]
   elif kind=='checked':args=[handle,command,flags,sequence];stack=[payload,size]
   elif kind=='read':args=[destination,length_ptr,0x55667788,0x99aabbcc];stack=[]
   else:args=[handle,packet,0x55667788,0x99aabbcc];stack=[]
   for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
   if stack:u.mem_write(SP,struct.pack('<'+'I'*len(stack),*stack))
   u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
   memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));return [[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]] if kind in ['ack','inverse','checked'] else u.reg_read(UC_ARM_REG_R0),st['events'],hashlib.sha256(memory).hexdigest()]
  for number,case in enumerate(cases):
   results=[execute(u,source,case,number) for source,u in enumerate(machines)]
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=case,results=results),indent=2)+'\n');raise AssertionError((number,case))
   counts[case['kind']]+=1;observations+=len(results[0][1]);digest.update(json.dumps([number,case,results[0]],sort_keys=True).encode())
  # A separate bounded history probe retains each machine's actual private stack.
  history=[]
  for poison in [0,255,0x96,0xa5]:
   case=dict(kind='serial',flag=0,pattern=1,poison=poison,sentinel=0,prefix=0,destmode=0,lenmode=0,mutation=0);steps=[]
   for step in range(2):steps.append([execute(u,source,case,1,initialize=step==0) for source,u in enumerate(machines)])
   history.append(dict(poison=poison,first_match=steps[0][0]==steps[0][1],second_match=steps[1][0]==steps[1][1],steps=steps))
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=observations,trace_sha256=digest.hexdigest(),actual_source_memory_move_and_fill=True,source_cold_class148_and_symbolic_handle4_match=True,actual_source_header_and_checked_helpers=True,header_checked_r0_through_r3_with_lower_register_clobbers_checked=True,raw_record_and_serial_output_pointer_identity_checked=True,failed_partial_reads_preserve_external_raw_record=True,only_kv_read_and_lower_response_are_fixtures=True,raw_r0_callee_sp_and_observed_nonstack_ram_checked=True,private_header_pointers_not_compared=True,candidate_native_execution_forbidden=True,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),whole_kv_transport_graph_executed=False,physical_serial_or_delivery_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');(OUT/'history-probe.json').write_text(json.dumps(dict(driver_sha256=sha(Path(__file__)),runtime_report_sha256=sha(rp),object_sha256=sha(obj),probes=history,private_stack_history_matches_all=all(x['second_match'] for x in history),whole_image_complete=False),indent=2)+'\n');print(json.dumps(receipt));print('History probe second-call matches:',[x['second_match'] for x in history])
if __name__=='__main__':main()
