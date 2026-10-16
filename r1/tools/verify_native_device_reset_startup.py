#!/usr/bin/env python3
"""Native device/reset dispatch and state effects with typed leaf fixtures."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-reset-startup';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PROVIDERS=[('r1_device_preinitialize_3510c',0x3510c,0),('r1_gxt310_self_check',0x50ecc,0),('r1_reset_reason_decode_and_report',0x8198c,1),('r1_stock_dispatch_08',0x85d1a,1),('r1_stock_dispatch_20',0x85d46,3),('r1_structured_log_mode_get',0x914ec,0),('r1_structured_log_format',0x91638,3),('nrf_log_frontend_std_0',0x799c0,2),('nrf_log_frontend_std_1',0x799c8,3)]
TARGETS={'module':('r1_device_module_init',0x5c4c8),'tail':('r1_device_hardware_check_tail',0x4e914),'rtc':('r1_rtc_open_enable',0x4e9ec),'thunk':('r1_device_init_thunk_4e9e8',0x4e9e8),'reset':('r1_reset_reason_nordic_adapter',0x77e98),'noop':('r1_native_rtc_startup_tick_noop',0x4ea10)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_device_reset_startup.o';assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_device_reset_startup_verification.ld';region_file=ROOT/'r1/source-config/startup/device-reset-data-regions.json';regions=json.loads(region_file.read_text());states={};digest=hashlib.sha256();counts=dict.fromkeys(TARGETS,0);calls_total=0;raw_module_r0_equal=True
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_rtc_startup_tick_noop']==0x4ea10;overlays=[]
  for name,a,n in regions:
   q=d/f'{name}.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.device.startup.'+name,'-O','binary',str(elf),str(q)],check=True);data=q.read_bytes();assert len(data)==n and data==app.read_bytes()[a-0x27000:a-0x27000+n];overlays.append((a,data))
  analysis=BASE/'i2c5/stock-analysis-exec.elf';assert sha(analysis)=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8';decoded={}
  for image in [analysis,elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    match=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if match:decoded[int(match[1],16)]=(match[2],match[3].split('@')[0].strip())
  regs={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};regs.update(sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR,ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11)
  native={a:(name,n) for name,a,n in PROVIDERS};compiled={syms[name]&~1:(name,n) for name,_,n in PROVIDERS}
  def hook(u,address,size,_):
   st=states[id(u)];selected=(compiled if st['source'] else native).get(address)
   if selected:
    name,n=selected;args=[u.reg_read(regs[f'r{i}']) for i in range(n)]
    if name=='r1_structured_log_format' and args[0]==0x0c400000:args.append(u.reg_read(UC_ARM_REG_R3))
    st['calls'].append([name,args]);result=0x55aa55aa
    if name=='r1_structured_log_mode_get':
     assert st['mode_index']<6;result=st['modes'][st['mode_index']];st['mode_index']+=1
     if st['mutate_reset']:u.mem_write(0x40000400,struct.pack('<I',st['reset_raw']^0xffffffff))
    elif name=='r1_stock_dispatch_08':u.mem_write(0x20007690,struct.pack('<I',st['second_handle']));result=st['open_status']
    elif name=='r1_stock_dispatch_20':result=st['bind_status']
    elif name=='r1_gxt310_self_check':u.mem_write(0x20007684,struct.pack('<I',st['mutated_state']));result=st['check_status']
    elif name=='r1_reset_reason_decode_and_report':result=st['decoded']
    u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   assert not st['source'] or not 0x27000<=address<0xc4d08 or 0x4ea10<=address<0x4ea12,('source executed unowned native code',hex(address))
   mnemonic,operands=decoded.get(address,('',''))
   if not mnemonic.startswith('str'):return
   names,mem=operands.split('[',1);terms=mem.split(']',1)[0].split(',');base=terms[0].strip()
   if base=='sp':return
   target=u.reg_read(regs[base]);
   if len(terms)>1:target+=int(terms[1].strip()[1:],0)
   target&=0xffffffff;width=1 if mnemonic.startswith('strb') else 2 if mnemonic.startswith('strh') else 4
   if target in [0x20007684,0x200064a8,0x40000400]:st['writes'].append([target,width,u.reg_read(regs[names.strip().rstrip(',')])&((1<<(8*width))-1)])
   else:assert target>=0x2003e000,('unexpected nonstack store',hex(address),hex(target))
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_map(0x40000000,0x1000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
   if source:
    for address,data in overlays:u.mem_write(address,data)
  rng=random.Random(0x5c4c8);queues=[tuple([m]*6) for m in range(8)]+[tuple(t+t) for t in itertools.product(range(8),repeat=3)]+[tuple(rng.randrange(8) for _ in range(6)) for _ in range(32)];cases=[]
  for kind,modes,status,mutation in itertools.product(['module','tail'],queues,[0,1,0xffffffff],[0,0x12345678,0xffffffff]):cases.append((kind,modes,status,mutation,0,0,False))
  raw_values=[0,0xffffffff,*[1<<i for i in range(32)]]+[rng.getrandbits(32) for _ in range(32)]
  for raw,modes,decoded_value,mutate in itertools.product(raw_values,queues[:8]+queues[-8:],[0,1,0xffffffff],[False,True]):cases.append(('reset',modes,0,0,raw,decoded_value,mutate))
  for status in [0,1,0xffffffff,*[rng.getrandbits(32) for _ in range(32)]]:cases.extend([('rtc',(0,)*6,status,0,0,0,False),('thunk',(0,)*6,status,0,0,0,False),('noop',(0,)*6,status,0,0,0,False)])
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for index,(kind,modes,status,mutation,raw_reset,decoded_value,mutate_reset) in enumerate(cases):
   results=[];r0s=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20000000,b'\x96'*0x3e000);u.mem_write(0x20007690,struct.pack('<I',0x20001000));u.mem_write(0x40000400,struct.pack('<I',raw_reset));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,status)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    st={'source':candidate,'modes':modes,'mode_index':0,'calls':[],'writes':[],'check_status':status,'mutated_state':mutation,'second_handle':0x20001100,'open_status':status,'bind_status':status,'reset_raw':raw_reset,'decoded':decoded_value,'mutate_reset':mutate_reset};states[id(u)]=st;entry=syms[TARGETS[kind][0]] if candidate else TARGETS[kind][1]
    try:u.emu_start(entry|1,0x20000100,count=100000)
    except Exception as error:raise RuntimeError((kind,index,status,mutation,raw_reset,decoded_value,candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from error
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    r0=u.reg_read(UC_ARM_REG_R0);r0s.append(r0);ram=bytes(u.mem_read(0x20000000,0x3e000));reg=bytes(u.mem_read(0x40000400,4)).hex()
    typed_return=r0
    if kind in ['module','tail']:assert r0==1
    if kind=='reset':assert r0==decoded_value
    if kind=='reset':assert reg==struct.pack('<I',raw_reset).hex() and struct.unpack_from('<I',ram,0x64a8)[0]==decoded_value and st['writes']==[[0x200064a8,4,decoded_value],[0x40000400,4,raw_reset]]
    if kind in ['module','tail']:assert struct.unpack_from('<I',ram,0x7684)[0]==(mutation|0x10 if status==0 else mutation) and st['writes']==([[0x20007684,4,0],[0x20007684,1,(mutation&255)|0x10]] if status==0 else [[0x20007684,4,0]])
    results.append([typed_return,st['calls'],st['writes'],hashlib.sha256(ram).hexdigest(),reg])
   if kind=='module':raw_module_r0_equal &= r0s[0]==r0s[1]
   if results[0]!=results[1]:
    failure=dict(index=index,kind=kind,modes=modes,status=status,mutation=mutation,reset_raw=raw_reset,decoded=decoded_value,results=results,source_sha256=sha(ROOT/'r1/components/runtime/native_device_reset_startup.c'));(OUT/'counterexample.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError({k:v for k,v in failure.items() if k!='results'})
   counts[kind]+=1;calls_total+=len(results[0][1]);digest.update(json.dumps([kind,modes,status,mutation,raw_reset,decoded_value,mutate_reset,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=calls_total,trace_sha256=digest.hexdigest(),typed_calls_state_writes_full_ram_return_stack_and_callee_integer_checked=True,leaf_provider_bodies_are_named_fixtures=True,provider_source_integration_verified=False,source_module_shared_tail_rtc_thunk_reset_and_noop=True,source_noop_original_address_only_native_range_execution_allowed=True,source_noop_compiled_bytes_equal=2,selected_six_value_mode_queues=True,rtc_handle_reload_after_open=True,selfcheck_state_byte_rmw_after_callback=True,reset_snapshot_preserved_across_provider_mutation=True,reset_one_hot_flags_and_seeded_values=True,raw_module_r0_equal=raw_module_r0_equal,module_r0_excluded_from_typed_equivalence=False,all_entry_raw_r0_compared=True,unicorn_memory_write_hooks_disabled=True,runtime_no_unresolved=False,instruction_identity=False,application_sha256=sha(app),analysis_elf_sha256=sha(analysis),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),data_regions=str(region_file.relative_to(ROOT)),data_regions_sha256=sha(region_file),source_data_bytes=sum(n for _,_,n in regions if n!=2),limitations=['Typed leaf callbacks are fixtures; actual provider execution and other raw argument-register residue remain unproven.','MMIO readback does not emulate physical RESETREAS write-one-to-clear semantics or physical interrupt/bus effects.','Two-byte compiled source noop identity/placement is separate from other instruction bytes, raw ABI/private frames, source-owned initialization and byte-identical whole-image integration.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
