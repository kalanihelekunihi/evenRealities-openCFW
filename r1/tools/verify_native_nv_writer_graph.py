#!/usr/bin/env python3
"""Actual class serializer/CRC inside update and dirty-scan callers."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-class-writer-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'scan':('r1_native_nv_dirty_scan',0x734e8),'idle':('r1_nv_modules_idle_check',0x73688),'bit':('r1_kv_dev_info_bit2_set',0x73834),'peer':('r1_peer_address_record_write',0x738a8),'command':('r1_protocol_command_000844b0',0x844b0)}
CLASSES=[('devinfo',0x200069a8),('ble_mult',0x200069f4),('health',0x20006a68),('hsync',0x20006a8c),('power',0x20006abc),('serial',0x20006ad8),('r_size',0x20006b6c)]
def main():
 rp=OUT/'caller-graph-report.json';b=json.loads(rp.read_text());obj=OUT/'nv-writer-graph-source.o';assert sha(obj)==b['graph_object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_nv_writer_graph_verification.ld';states={};digest=hashlib.sha256();counts={n:0 for n in ENTRIES};obs=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);sections={}
  for n in ['text','handles','ring','sdk','writer_ring','writer_sdk']+[n for n,a in CLASSES]:
   p=d/(n+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+n,'-O','binary',str(elf),str(p)],check=True);sections[n]=p.read_bytes()
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_nv_handles_begin']==0x20007de8 and syms['r1_nv_handles_end']==0x20007e04 and syms['r1_kv_port']==0x20006974
  cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
  for n,a in CLASSES+[('handles',0x20007de8)]:assert sections[n]==cold[a-0x200064a8:a-0x200064a8+len(sections[n])]
  for n,a in [('ring',0x73580),('sdk',0x735b4),('writer_ring',0x917fc),('writer_sdk',0x91838)]:assert sections[n]==raw[a-0x27000:a-0x27000+len(sections[n])]
  def hook(u,a,size,_):
   st=states[id(u)];source=st['source'];assert not source or not 0x27000<=a<0xc4d08
   kind=({0x20000200:'response',0x20000204:'sdk1',0x20000208:'mode',0x2000020c:'ring',0x20000210:'sdk'} if source else {0x828b4:'response',0x799c8:'sdk1',0x914ec:'mode',0x91638:'ring',0x799d6:'sdk'}).get(a)
   if a in [0x20000214,0x20000218,0x2000021c,0x20000220]:kind={0x20000214:'enter',0x20000218:'leave',0x2000021c:'request',0x20000220:'request2'}[a]
   if a==(syms['r1_store_class_record_write'] if source else 0x91780):
    er=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1]];st['events'].append(['actual_store',er])
   if a==0x20000224:kind='write'
   if not kind:return
   r=[u.reg_read(x) for x in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];ret=st['status'];m=st['mutation']
   if kind=='response':
    st['events'].append(['response',r[0],bytes(u.mem_read(r[1],8)).hex(),r[3]])
    if m==1:u.mem_write(0x20007de8,struct.pack('<I',0x20001000));u.mem_write(0x20003003,b'\x12\x34')
   elif kind=='write':
    assert r[3]==0x20000225;index=r[0]>>8;node=r[1];st['events'].append(['write',r,bytes(u.mem_read(node,r[2])).hex()])
    if m==1 and index==0:u.mem_write(0x20007dec,struct.pack('<I',0x20001000))
    elif m==2:u.mem_write(node+18,bytes(2))
   elif kind=='sdk1':st['events'].append(['sdk1',r[:3]])
   elif kind=='mode':
    ret=st['modes'][st['mi']%len(st['modes'])];st['mi']+=1;st['events'].append(['mode',ret])
    if m==3:u.mem_write(0x20006974,struct.pack('<I',0x20000880))
   elif kind=='ring':
    args=r if r[1]==0x917fc else r+[struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0]];st['events'].append(['ring',args])
   elif kind=='sdk':st['events'].append(['sdk',r])
   elif kind in ['enter','leave']:
    st['events'].append([kind])
    if m==4 and kind=='leave':u.mem_write(0x20007de8,struct.pack('<I',0x20001000))
   else:assert r[:2]==[1,0];st['events'].append([kind,r[:2]])
   u.reg_write(UC_ARM_REG_R0,ret)
   for reg,v in [(UC_ARM_REG_R1,0xabcdef01),(UC_ARM_REG_R2,0x12345678),(UC_ARM_REG_R3,0x89abcdef)]:u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,sections['text']);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  modes=[[0],[1],[2],[4],[7],[0,4,2]];cases=[]
  for kind,dirty,status,mode,m in itertools.product(['scan','idle'],[0,1,2,8,64,127],[0,1,5,0xffffffff],modes,range(5)):cases.append((kind,dirty,status,mode,m,52,0,0,0))
  for value,size,status,mode,m in itertools.product([0,1,2,255,0xffffffff],[0,51,52,53],[0,5],modes[:3],range(5)):cases.append(('bit',0,status,mode,m,size,value,0,0))
  for first,second,size,status,m in itertools.product([0,0x20002001,0x2003efb8+8],[0,0x20002011,0x2003efb8+8],[0,52,53],[0,5],range(5)):cases.append(('peer',0,status,modes[4],m,size,0,first,second))
  for length,handle,size,status,mode,m in itertools.product([0,12,13,24,65535],[0,65535,0x1000ffff],[0,52,53],[0,5],modes[:3],range(5)):cases.append(('command',0,status,mode,m,size,length,handle,0))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for number,(kind,dirty,status,mode,m,size,value,first,second) in enumerate(cases):
   results=[]
   for source,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x40000)
    for n,a in CLASSES:u.mem_write(a,sections[n])
    u.mem_write(0x20007de8,sections['handles']);u.mem_write(0x20001000,sections['devinfo']);u.mem_write(0x200069a8+20,struct.pack('<H',size));u.mem_write(0x20006974,struct.pack('<I',0x20000800))
    for a,request in [(0x20000800,0x2000021d),(0x20000880,0x20000221)]:u.mem_write(a+20,struct.pack('<IIII',0x20000225,request,0x20000215,0x20000219))
    for i,(n,a) in enumerate(CLASSES):u.mem_write(a+18,struct.pack('<H',((1 if dirty&(1<<i) else 0)| (2 if n in ['power','serial','r_size'] else 0))))
    u.mem_write(0x20002000,bytes(range(32)));u.mem_write(0x20003000,bytes(range(32)));u.mem_write(0x20003008,struct.pack('<H',value if kind=='command' else 24));states[id(u)]=dict(source=source,events=[],status=status,modes=mode,mi=0,mutation=m)
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    args=[value,0x11223344,0x55667788,0x99aabbcc] if kind=='bit' else [first,second,0x55667788,0x99aabbcc] if kind=='peer' else [first,0x20003000,0x55667788,0x99aabbcc] if kind=='command' else [0,0x11223344,0x55667788,0x99aabbcc]
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,v)
    u.emu_start((syms[ENTRIES[kind][0]] if source else ENTRIES[kind][1])|1,0x20000100,count=30000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    memory=bytes(u.mem_read(0x20000000,0x3e000))+bytes(u.mem_read(0x2003f000,0x1000));results.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['events'],hashlib.sha256(memory).hexdigest()])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(number=number,case=[kind,dirty,status,mode,m,size,value,first,second],results=results),indent=2)+'\n');raise AssertionError((number,kind,dirty,status,mode,m,size,value,first,second))
   counts[kind]+=1;obs+=len(results[0][1]);digest.update(json.dumps([number,kind,dirty,status,mode,m,size,value,first,second,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observations_per_side=obs,trace_sha256=digest.hexdigest(),source_cold_classes_and_symbolic_table_match=True,actual_record_frames_cached_read_write_musl_fill_copy_dirty_scan_writer_crc=True,only_response_port_write_logging_critical_and_final_request_are_fixtures=True,raw_r0_callee_sp_and_nonstack_ram_checked=True,no_native_candidate_execution=True,driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),application_sha256=sha(app),cross_call_private_stack_history_verified=False,whole_flash_commit_graph_executed=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False)
 (OUT/'caller-graph-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
