#!/usr/bin/env python3
"""Native vector setup and complete DFU graph against unmodified upstream plus R1 ports."""
import hashlib,itertools,json,random,re,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-vector-set';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PROVIDERS=[('nrf_dfu_svci_vector_table_set',0x78590),('r1_structured_log_mode_get',0x914ec),('r1_structured_log_format',0x91638),('nrf_log_frontend_std_0',0x799c0),('nrf_log_frontend_std_1',0x799c8)]
SET_REGIONS=[('set_info_ring',0x78664,52),('set_info_sdk',0x78698,44),('set_error_ring',0x786c4,60),('set_error_sdk',0x78700,52),('set_missing_ring',0x78734,32),('set_missing_sdk',0x78754,24)]
REGIONS=SET_REGIONS+[('app_start',0x787f0,4),('info_ring',0x787f4,48),('bounds',0x78824,8),('info_sdk',0x7882c,44),('error_ring',0x78858,60),('error_sdk',0x78894,52)]
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);report=OUT/'report.json';r=json.loads(report.read_text());runtime=BASE/'native-dfu-vector-runtime/report.json';bundle=json.loads(runtime.read_text());obj=runtime.parent/'native-dfu-vector-runtime.o';assert sha(obj)==bundle['dfu_runtime_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';layout=ROOT/'r1/source-config/runtime/native_dfu_vector_set_verification.ld';states={};counts={'entry':0,'set':0};observations=0;svc_counts={0:0,19:0};digest=hashlib.sha256();rng=random.Random(0x52018)
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert symbols['nrf_dfu_set_adv_name_svci_async_def']==0x2002c12c
  sections=[]
  for name,a,n in [('text',0x1000000,None),*REGIONS]:
   b=d/(name+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.'+name,'-O','binary',str(elf),str(b)],check=True);content=b.read_bytes();sections.append((a,content))
   if n is not None:assert len(content)==n and content==raw[a-0x27000:a-0x27000+n],name
  native={a:i for i,(_,a) in enumerate(PROVIDERS) if i};compiled={symbols[n]&~1:i for i,(n,_) in enumerate(PROVIDERS) if i}
  decoded={}
  for image in [BASE/'i2c5/stock-analysis-exec.elf',elf]:
   for line in subprocess.check_output(['arm-none-eabi-objdump','-d',str(image)],text=True).splitlines():
    m=re.match(r'\s*([0-9a-f]+):\s+(?:[0-9a-f]{4}\s+)+(\S+)\s*(.*)',line)
    if m:decoded[int(m[1],16)]=(m[2],m[3].split('@')[0].strip())
  registers={f'r{i}':globals()[f'UC_ARM_REG_R{i}'] for i in range(13)};registers.update(ip=UC_ARM_REG_R12,sl=UC_ARM_REG_R10,fp=UC_ARM_REG_R11,sp=UC_ARM_REG_SP,lr=UC_ARM_REG_LR)
  def poison(u,value,keep=()):
   for i,reg in enumerate([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R12]):
    if reg not in keep:u.reg_write(reg,(value+i*0x11111111)&0xffffffff)
  def hook(u,address,size,_):
   st=states[id(u)];index=(compiled if st['source'] else native).get(address)
   if index is not None:
    regs=[u.reg_read(reg) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]
    if index==0:st['events'].append(['set']);value=st['status'][0]
    elif index==1:
     i=st['mode_index'];assert i<len(st['modes']);value=st['modes'][i];st['mode_index']+=1;st['events'].append(['mode',value])
    else:
     arity=4 if index==2 and regs[0]==0xc400000 else 3 if index in [2,4] else 2
     st['events'].append(['log',index,regs[:arity]]);value=0x55aa55aa
    poison(u,0xabcdef01);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
   assert not st['source'] or not 0x27000<=address<0xc4d08
   mnemonic,operands=decoded.get(address,('',''))
   if mnemonic.startswith('ldr') and '[' in operands:
    terms=operands.split('[',1)[1].split(']',1)[0].split(',');base=terms[0].strip()
    if base in registers:
     target=u.reg_read(registers[base])
     if len(terms)>1:target+=int(terms[1].strip()[1:],0) if terms[1].strip().startswith('#') else u.reg_read(registers[terms[1].strip()])
     target&=0xffffffff
     if target in [0xff8,0x10001014]:st['events'].append(['boot_read',target,struct.unpack('<I',u.mem_read(target,4))[0]])
   opcode=struct.unpack('<H',u.mem_read(address,2))[0]
   if opcode&0xff00==0xdf00:
    imm=opcode&255
    if imm==0:
     pointer=u.reg_read(UC_ARM_REG_R0);assert pointer==0x2002c12c and u.reg_read(UC_ARM_REG_R12)==3
     before=bytes(u.mem_read(pointer,12));st['events'].append(['svc0',pointer,3,before.hex()]);u.mem_write(pointer,st['mutation']);value=st['status'][1]
    elif imm==19:
     base=u.reg_read(UC_ARM_REG_R0);expected_base=st['boot'] if st['vector_calls']==0 else 0x27000;assert base==expected_base;st['events'].append(['svc19',base]);value=st['status'][0 if st['vector_calls']==0 else 2];st['vector_calls']+=1
    else:raise AssertionError(imm)
    poison(u,0x13579bdf);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PC,(address+2)|1)
  machines=[]
  for candidate in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0xe0000);u.mem_map(0x10001000,0x1000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
   if candidate:
    for address,data in sections:u.mem_write(address,data)
   u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11];statuses=[0,1,4,0x12345678,0x80000000,0xffffffff]
  mode_queues=[list(q)+list(reversed(q)) for q in itertools.product(range(8),repeat=3)]+[[rng.randrange(8) for _ in range(6)] for _ in range(128)]
  addresses=[(0,0xffffffff),(1,0xffffffff),(0xf0000,0x12345678),(0xfffffffe,0),(0xffffffff,0xf0000),(0xffffffff,0),(0xffffffff,0xfffffffe),(0xffffffff,0xffffffff)]
  cases=[]
  for pair,q,status,fill in itertools.product(addresses,mode_queues,statuses,[0,0x96]):cases.append(('set',(status,0,0),q+q,pair,fill))
  for i,(pair,status) in enumerate(itertools.product(addresses,itertools.product(statuses,repeat=3))):
   for q in [mode_queues[(i*13)%len(mode_queues)],[0]*6,[7]*6]:
    for fill in [0,0x96]:cases.append(('entry',status,q+list(reversed(q)),pair,fill))
  for q,status,pair in itertools.product(mode_queues,[0,1,0xffffffff],[addresses[2],addresses[4],addresses[7]]):cases.append(('entry',(0,0,status),q+list(reversed(q)),pair,0x96))
  for kind,status,modes,pair,fill in cases:
   boot=pair[0] if pair[0]!=0xffffffff else pair[1]
   mutation=bytes(rng.randrange(256) for _ in range(12));results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0xff8,struct.pack('<I',pair[0]));u.mem_write(0x10001000,b'\x69'*0x1000);u.mem_write(0x10001014,struct.pack('<I',pair[1]));u.mem_write(0x20000000,bytes([fill])*0x3e000);initial=bytearray(u.mem_read(0x20000000,0x3e000));u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    poison(u,0x11223344);st=dict(source=candidate,status=status,modes=modes,mode_index=0,events=[],mutation=mutation,boot=boot,vector_calls=0);states[id(u)]=st
    entry=symbols['ble_dfu_buttonless_async_svci_init' if kind=='entry' else 'nrf_dfu_svci_vector_table_set'] if candidate else 0x52018 if kind=='entry' else 0x78590
    try:u.emu_start(entry|1,0x20000100,count=10000)
    except Exception as err:raise RuntimeError((kind,status,modes,candidate,hex(u.reg_read(UC_ARM_REG_PC)))) from err
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    svc0=any(e[0]=='svc0' for e in st['events'])
    if svc0:initial[0x2c12c:0x2c138]=mutation
    assert struct.unpack('<I',u.mem_read(0xff8,4))[0]==pair[0] and struct.unpack('<I',u.mem_read(0x10001014,4))[0]==pair[1]
    actual=bytes(u.mem_read(0x20000000,0x3e000));assert initial==actual,('unexpected RAM writes',kind,status,candidate)
    result=[st['events'],st['mode_index'],u.reg_read(UC_ARM_REG_R0),hashlib.sha256(actual).hexdigest()];results.append(result)
   expected=4 if boot==0xffffffff else status[0] if status[0] or kind=='set' else status[1] if status[1] else status[2]
   if results[0]!=results[1] or results[0][2]!=expected:
    fail=dict(kind=kind,status=status,modes=modes,boot_pair=pair,fill=fill,results=results,expected=expected);(OUT/'counterexample.json').write_text(json.dumps(fail,indent=2)+'\n');raise AssertionError(fail)
   counts[kind]+=1;observations+=len(results[0][0]);svc_counts[0]+=sum(e[0]=='svc0' for e in results[0][0]);svc_counts[19]+=sum(e[0]=='svc19' for e in results[0][0]);digest.update(json.dumps([kind,status,modes,pair,fill,mutation.hex(),results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_observations_per_side=observations,supervisor_calls_per_side=svc_counts,trace_sha256=digest.hexdigest(),upstream_setter_entry_and_source_restore_executed=True,actual_svc0_and_svc19_bridges_executed=True,supervisor_behavior_is_fixture=True,logging_bodies_are_named_fixtures=True,vector_set_provider_is_source_not_fixture=True,all_entry_raw_r0_compared=True,callee_integer_stack_and_full_nonstack_ram_checked=True,mode_queues_and_early_errors_exercised=True,boot_mbr_precedence_uicr_fallback_and_both_missing=True,boot_zero_one_unaligned_and_high_bit_values=True,boot_read_order_and_inputs_unchanged=True,source_selected_constant_data_bytes=sum(n for _,_,n in REGIONS),setter_source_data_bytes=272,setter_selected_source_data_bytes=264,source_data_at_native_verification_addresses=True,candidate_native_body_execution_forbidden=True,unicorn_memory_write_hooks_disabled=True,instruction_identity=False,full_raw_abi_verified=False,physical_svc_verified=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(report),runtime_report_sha256=sha(runtime),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['SVC0/SVC19 handlers and logging are explicit fixtures, not source or physical provider proof.','Low flash MBR and UICR values are explicit test fixtures, not authenticated readings from a device.','Selected strings occupy native verification addresses; the8-byte source log bounds compile to a folded tag and are retained only in the raw source object, not selected layout.','Typed boot reads/supervisor args/log calls, raw R0/callee/SP and full RAM match; raw scratch/APSR/private frame, physical transitions and original image remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
