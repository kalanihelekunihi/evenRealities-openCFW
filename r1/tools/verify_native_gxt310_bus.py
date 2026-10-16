#!/usr/bin/env python3
"""Native I2C2 cache/locking/request layout, store order and persistent NULL writes."""
import hashlib,itertools,json,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-bus';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ENTRIES={'cache':('r1_i2c2_handle_cache',0x50f08),'acquire':('r1_gxt310_bus_acquire',0x50f28),'release':('r1_gxt310_bus_release',0x50efc),'read':('r1_gxt310_transfer_read_native',0x50f34),'write':('r1_gxt310_transfer_write_native',0x50f5c),'read_thunk':('r1_gxt310_register_read_native',0x6f640),'write_thunk':('r1_gxt310_register_write_native',0x6f644)}
CALLS=[('r1_stock_registry_find',0x85ce0),('r1_stock_dispatch_08',0x85d1a),('r1_stock_dispatch_0c',0x85cba),('r1_stock_dispatch_10',0x85d2c),('r1_stock_dispatch_14',0x85da8)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_gxt310_bus.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';analysis=BASE/'i2c5/stock-analysis-exec.elf';layout=ROOT/'r1/source-config/runtime/native_gxt310_bus_verification.ld';states={};counts={k:0 for k in ENTRIES};counts['persistent_sequence']=0;callbacks=0;digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_gxt310_i2c2_state']==0x200076f8 and syms['r1_gxt310_i2c2_name']==0x50f20
  native={a:i for i,(_,a) in enumerate(CALLS)};compiled={syms[n]&~1:i for i,(n,_) in enumerate(CALLS)};decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if m:decoded[int(m[1],16)]=(m[2],m[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11,sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR)
  def fixture_write(u,st,address,width,value):
   value&=(1<<(width*8))-1;u.mem_write(address,value.to_bytes(width,'little'));st['writes'].append(['fixture',address,width,value])
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is not None:
    args=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];before=bytes(u.mem_read(0x200076f8,24))
    if index==0:assert args[0]==0x50f20 and bytes(u.mem_read(args[0],6))==b'i2c_2\0';used=[args[0]]
    elif index in [1,2]:assert args[0]==struct.unpack_from('<I',before)[0];used=args[:1]
    else:assert args==[struct.unpack_from('<I',before)[0],0,0x200076fc,0];used=args
    st['events'].append([index,used,before.hex()]);fixture_write(u,st,0x20006000,4,(st['call_index']+1)*0x10203+index)
    if st['mutation']:
     fixture_write(u,st,0x200076f8,4,0x20003100+st['call_index']*4);fixture_write(u,st,0x2000770e,2,0xa55a)
    if index==3:
     pointer=struct.unpack_from('<I',before,16)[0]
     if 0x20001000<=pointer<0x20001010:fixture_write(u,st,pointer,2,0x0050)
    for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):u.reg_write(reg,(0xabcdef01+i*0x11111111)&0xffffffff)
    u.reg_write(UC_ARM_REG_R0,st['status']);st['call_index']+=1;u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   assert not st['source'] or not 0x27000<=address<0xc4d08
   mnemonic,operands=decoded.get(address,('',''))
   if not mnemonic.startswith('str') or '[' not in operands:return
   names,mem=operands.split('[',1);names=[x.strip() for x in names.rstrip(', ').split(',')];terms=mem.split(']',1)[0].split(',');base=terms[0].strip()
   if base=='sp':return
   target=u.reg_read(registers[base])
   if len(terms)>1:target+=int(terms[1].strip()[1:],0) if terms[1].strip().startswith('#') else u.reg_read(registers[terms[1].strip()])
   target&=0xffffffff
   if not 0x20000000<=target<0x2003e000:return
   width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
   for i,name in enumerate(names):st['writes'].append(['body',target+i*width,width,u.reg_read(registers[name])&((1<<(width*8))-1)])
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];values=[0,1,0x90,0x94,0xffff,0xffffffff];lengths=[0,1,2,0xffff,0x10000,0xffffffff];pointers=[0,0x20001000,0x20001001,0xffffffff];statuses=[0,1,4,0x80000000,0xffffffff];cases=[]
  for kind,args,status,fill,mutation in itertools.product(['read','write','read_thunk','write_thunk'],itertools.product(values,values,pointers,lengths),statuses,[0,0x96],[0,1]):cases.append((kind,[(kind,args)],0x20003000,status,fill,mutation))
  for kind,handle,status,fill,mutation in itertools.product(['cache','acquire','release'],[0,0x20003000,0xffffffff],statuses,[0,0x96],[0,1]):cases.append((kind,[(kind,(0,0,0,0)),(kind,(0,0,0,0))],handle,status,fill,mutation))
  for handle,status,fill,mutation in itertools.product([0,0x20003000],statuses,[0,0x96],[0,1]):
   steps=[('cache',(0,0,0,0)),('acquire',(0,0,0,0)),('write',(0x90,1,0x20001000,2)),('write_thunk',(0x94,3,0,1)),('read',(0x90,3,0,2)),('read_thunk',(0x94,3,0x20001001,2)),('release',(0,0,0,0))];cases.append(('persistent_sequence',steps,handle,status,fill,mutation))
  for kind,steps,handle,status,fill,mutation in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,bytes([fill])*0x3e000);u.mem_write(0x200076f8,struct.pack('<I',handle));u.mem_write(0x20007700,struct.pack('<I',0x20002000));initial=bytearray(u.mem_read(0x20000000,0x3e000));st=dict(source=candidate,status=status,mutation=mutation,events=[],writes=[],call_index=0);states[id(u)]=st;returns=[]
    for entry,args in steps:
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     for value,reg in zip(args,[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]):u.reg_write(reg,value)
     u.emu_start((syms[ENTRIES[entry][0]] if candidate else ENTRIES[entry][1])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];returns.append(u.reg_read(UC_ARM_REG_R0))
     if entry in ['read','write','read_thunk','write_thunk']:assert returns[-1]==int(status==0)
    for _,address,width,value in st['writes']:initial[address-0x20000000:address-0x20000000+width]=value.to_bytes(width,'little')
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,('store reconciliation',kind,candidate)
    results.append([st['events'],st['writes'],returns,hashlib.sha256(actual).hexdigest()])
   if results[0]!=results[1]:
    fail=dict(kind=kind,steps=steps,handle=handle,status=status,fill=fill,mutation=mutation,results=results);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError({k:v for k,v in fail.items() if k!='results'})
   counts[kind]+=1;callbacks+=len(results[0][0]);digest.update(json.dumps([kind,steps,handle,status,fill,mutation,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=callbacks,trace_sha256=digest.hexdigest(),all_seven_source_entries_executed=True,request_field_widths_and_store_order_checked=True,read_pointer_unconditionally_replaced=True,null_write_pointer_preserves_prior_record_pointer=True,zero_dispatch_status_returns_one=True,cache_retries_and_cached_handle_reuse=True,callback_mutated_handle_and_padding=True,persistent_multi_call_record_sequences=True,raw_r0_callee_integer_stack_full_observed_nonstack_ram_and_callback_args_checked=True,executed_store_observer_with_full_ram_reconciliation=True,registry_dispatch_and_lookup_are_named_fixtures=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,source_state_bytes=24,source_name_bytes=8,whole_startup_graph_executed=False,physical_bus_verified=False,instruction_identity=False,full_raw_abi_verified=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Registry/dispatch providers are fixtures in these body tests; physical I2C and complete startup execution are unproven.','Both native and source use the same verification state addresses; final source state/link ownership and full raw private ABI remain open.','Cold source initialization is authenticated separately from arbitrary-state behavior fixtures; no executable blob fallback is used.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
