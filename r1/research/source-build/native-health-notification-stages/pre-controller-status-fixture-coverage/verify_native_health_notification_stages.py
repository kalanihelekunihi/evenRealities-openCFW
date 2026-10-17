#!/usr/bin/env python3
"""Native sync controllers and status packing with explicit provider/callback fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-notification-stages';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CACHE=0x20012000;BUILDER=0x20014000;DB=0x20016000;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
SPECS={0x8c150:dict(kind=0,index=0,size=0x94,base=0x3fa84,buffered=0x3fb90,feed=0x3fef4,finish=0x4011c,close=0x40700,notify=0x2000679a),0x8cd60:dict(kind=1,index=1,size=0x94,base=0x43c80,buffered=0x43d90,feed=0x440c4,finish=0x442f4,close=0x448b0,notify=0x2000679d),0x8c750:dict(kind=5,index=3,size=0xdc,base=0x40964,buffered=0x40a74,feed=0x40de0,finish=0x4101c,close=0x41638,notify=0x200067ad),0x8baec:dict(kind=4,index=4,size=0x49c,base=0x3bdac,buffered=0x3bed0,feed=0x3c304,finish=0x3c578,close=0x3cb80,notify=0x200067aa)}
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-health-notification-stages-runtime.o';assert sha(obj)==b['linked_sha256'];c=json.loads((OUT/'contracts.json').read_text());providers={int(a,16):n for a,n in c['providers'].items()};app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==c['application_sha256'];states={};digest=hashlib.sha256();counts={hex(a):0 for a in [*SPECS,0x8b818]};obs=dict.fromkeys([hex(a) for a in providers],0)
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 with tempfile.TemporaryDirectory(prefix='r1-sync-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';elf=d/'test.elf';rom=''.join(' .b'+str(i)+' '+x['address']+' : { *(.text.'+x['symbol']+') } ' for i,x in enumerate(c['bodies']));rom+=''.join(' .kind'+str(i)+' '+hex(0x99bf4+16*i)+' : { *(.r1.health.sync.kind'+str(i)+') } ' for i in range(6));ram=''.join(' .pending_'+n+' '+a+' : { *(.r1.health.sync.pending.'+n+') } ' for n,a in c['pending_bytes'].items());ld.write_text('SECTIONS { '+rom+ram+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');bindings={n:a|1 for a,n in providers.items()};subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for n in b['roots'] for v in ['-u',n]],'-T',str(ld),*[f'--defsym={n}={a}' for n,a in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};source_spans=[];identity=[]
  for i,x in enumerate(c['bodies']):
   file=d/(str(i)+'.bin');subprocess.run(['arm-none-eabi-objcopy','-j','.b'+str(i),'-O','binary',str(elf),str(file)],check=True);data=file.read_bytes();address=int(x['address'],16);native=raw[address-0x27000:address-0x27000+x['source_span_bytes']];assert data==native,(x['address'],len(data),len(native),next(((j,a,z) for j,(a,z) in enumerate(zip(data,native)) if a!=z),None));source_spans.append((address,data));identity.append(dict(address=x['address'],size=len(data),compiled_sha256=hashlib.sha256(data).hexdigest(),native_sha256=hashlib.sha256(native).hexdigest(),byte_identical=True))
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in providers:return
   st=states[id(u)];case=st['case'];args=[u.reg_read(x) for x in REGS];value=case['result'];extra=None;spec=SPECS.get(case['entry'])
   if a==0x277aa:u.mem_write(args[0],bytes(args[1]));value=(args[0]+args[1])&0xffffffff;extra=args[:2]
   elif a==0x738f4:u.mem_write(args[0],bytes(st['sync'][:case['read_bytes']]));extra=bytes(u.mem_read(args[0],24)).hex()
   elif a==0x7390c:st['sync']=bytearray(u.mem_read(args[0],24));extra=st['sync'].hex()
   elif a==0x8ada4:value=case['now']
   elif a==0x8ad64:value=case['today']
   elif a==0x914ec:value=case['modes'][min(st['modes'],len(case['modes'])-1)];st['modes']+=1;args=[value]
   elif a==0x91638:
    count=(args[0]>>22)&15;extra=list(struct.unpack('<'+'I'*max(0,count-1),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-1)*4)));args=args[:3+min(count,1)]
   elif a in [0x799c0,0x799c8,0x799d6,0x799e6]:
    count=[0x799c0,0x799c8,0x799d6,0x799e6].index(a);extra=list(struct.unpack('<'+'I'*max(0,count-2),u.mem_read(u.reg_read(UC_ARM_REG_SP),max(0,count-2)*4)));args=args[:2+min(count,2)]
   elif a==0x70028:value=DB
   elif a==0x855a0:
    index=len(st['allocations']);st['allocations'].append(args[0]);assert args[0]==(128 if index==0 else spec['size']);value=0 if case['fail_alloc']==index else CACHE if index==0 else BUILDER
   elif a==0x63694:assert args[0]==DB and args[1]==6;put(u,args[2],case['oldest']);extra=case['oldest']
   elif a==0x63cb4:value=case['flash_count'];st['queries'].append(args[:]);extra=args[:]
   elif a==0x63ad8:
    context=struct.unpack('<I',u.mem_read(u.reg_read(UC_ARM_REG_SP),4))[0];extra=[context,bytes(u.mem_read(context,20)).hex()];st['iterators'].append(args[:]);value=case['result']
   elif a==0x95d48:st['frees'].append(args[0])
   elif a==0x5b39c:
    extra=bytes(u.mem_read(args[2],4)).hex();assert args[0]==1 and args[1]==0x8f955;expected=bytes([case['first']&255,(case['seed']>>8)&255])+struct.pack('<H',case['second']&65535);assert extra==expected.hex();
    if case['mutate']:u.mem_write(args[2]+1,b'\xaa')
   elif spec and a==spec['buffered']:value=case['buffered']
   elif spec and a in [spec['base'],spec['feed'],spec['finish'],spec['close']]:
    assert args[0]==BUILDER;extra=bytes(u.mem_read(BUILDER,spec['size'])).hex()
    if case['mutate']:u.mem_write(spec['notify'],bytes([(u.mem_read(spec['notify'],1)[0]+1)&255]))
   else:raise AssertionError(('unexpected callback entry executed',hex(a),case))
   st['trace'].append([hex(a),args,extra,value]);
   if not st['side']:obs[hex(a)]+=1
   for reg,v in zip(REGS,[value,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,raw);u.mem_map(0x1000000,0x40000);
   if side:
    for address,data in source_spans:u.mem_write(address,data)
   u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(entry=0x8c150,first=0,second=0,last=0,now=0x60000000,today=0x60000000,oldest=0,read_bytes=24,fail_alloc=-1,flash_count=0,buffered=1,result=0,modes=[0],pending=0,mutate=0,seed=0x98765432);cases=[]
  for entry,last,now,today,fail,count,buffered,modes in itertools.product(SPECS,[0,0x5ff00000,0x60000000,0xffffffff],[0,0x38640900,0x60000000],[0,0x38640900,0x60000000],[-1,0,1],[0,1],[0,1],[[0],[7],[0,4,2]]):cases.append(dict(default,entry=entry,last=last,now=now,today=today,fail_alloc=fail,flash_count=count,buffered=buffered,modes=modes))
  for entry,oldest,read_bytes,pending,mutate,first in itertools.product(SPECS,[0,0x5fffffff,0x60000000,0xffffffff],[0,4,24],[0,1,255],range(2),[0,0xffffffff]):cases.append(dict(default,entry=entry,oldest=oldest,read_bytes=read_bytes,pending=pending,mutate=mutate,first=first))
  for first,second,seed,result,mutate in itertools.product(list(range(256))+[256,0xffffffff],[0,1,65535,65536,0x12345678,0xffffffff],[0,0x98765432],[0,1,0xffffffff],range(2)):cases.append(dict(default,entry=0x8b818,first=first,second=second,seed=seed,result=result,mutate=mutate))
  for case in cases:
   results=[];spec=SPECS.get(case['entry'])
   for side,u in enumerate(machines):
    u.mem_write(SP-2048,b'\x96'*4096);u.mem_write(CACHE-4,b'\xa5'*136);u.mem_write(BUILDER-4,b'\xa5'*0x4a4)
    for address in c['pending_bytes'].values():u.mem_write(int(address,16),bytes([case['pending']]))
    sync=bytearray(struct.pack('<6I',*[0x10203040+i for i in range(6)]))
    if spec:struct.pack_into('<I',sync,spec['index']*4,case['last'])
    st=dict(case=case,side=side,trace=[],sync=sync,modes=0,allocations=[],frees=[],queries=[],iterators=[]);states[id(u)]=st
    for reg,v in zip(REGS,[case['first'],case['second'],0xabcdef01,case['seed']]):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);name='r1_health_notification_stage_%08x'%case['entry'];u.emu_start((syms[name] if side else case['entry'])|1,0x20000100,count=100000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)],(case,side,hex(u.reg_read(UC_ARM_REG_PC)))
    if spec:
     assert st['frees']==([] if case['fail_alloc']==0 else [CACHE] if case['fail_alloc']==1 else [BUILDER,CACHE]);assert not st['queries'] or st['queries'][0][3]==2
    else:
     expected=bytes([case['first']&255,0xaa if case['mutate'] else (case['seed']>>8)&255])+struct.pack('<H',case['second']&65535);assert u.reg_read(UC_ARM_REG_R3)==int.from_bytes(expected,'little')
    results.append([[u.reg_read(x) for x in REGS],st['trace'],st['sync'].hex(),bytes(u.mem_read(CACHE-4,136)).hex(),bytes(u.mem_read(BUILDER-4,0x4a4)).hex(),[u.mem_read(int(a,16),1)[0] for a in c['pending_bytes'].values()]])
   if results[0]!=results[1]:(OUT/'counterexample.json').write_text(json.dumps(dict(case=case,results=results),indent=2)+'\n');raise AssertionError(case)
   counts[hex(case['entry'])]+=1;digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),all_five_controller_bodies_execute=True,source_placement_identity_spans=identity,byte_identical_source_span_bytes=sum(x['size'] for x in identity),source_spans_include_code_typed_literals_text_and_zero_padding=True,heap_io_time_database_builder_and_log_are_fixtures=True,iterator_callbacks_and_builder_encoder_callbacks_executed=False,native_provider_addresses_are_explicit_verification_bindings=True,raw_r0_r3_callee_sp_typed_arguments_heap_sync_and_pending_bytes_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,full_descriptor_or_context_extent_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
