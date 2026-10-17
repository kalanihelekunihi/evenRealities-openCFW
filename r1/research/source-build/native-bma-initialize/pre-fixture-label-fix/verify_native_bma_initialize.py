#!/usr/bin/env python3
"""Native Bosch write/power/feature graph through stateful transport fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-initialize';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-bma-initialize-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(base=0,variant=0,configure=0);obs=dict(read=0,write=0,delay=0,cycles=0,mode=0,ring=0,sdk=0);faults=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-feature-io-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';spans=json.loads((OUT/'configuration-text-spans.json').read_text());rom=' .remap 0x9a768 : { *(.r1.bma.remap.span) } '+''.join(' .s'+x['address'][2:]+' '+x['address']+' : { *('+x['section']+') } ' for x in spans);ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } '+rom+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';roots=b['roots']+['r1_bma_default_read','r1_bma_default_write'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],'--defsym=r1_rtt_delay_cycles=0x1100601','--defsym=r1_structured_log_mode_get=0x1100701','--defsym=r1_structured_log_format=0x1100801','--defsym=nrf_log_frontend_std_1=0x1100901',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   a={0x9a760:0x1100600,0x914ec:0x1100700,0x91638:0x1100800,0x799c8:0x1100900}.get(a,a)
   if a not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500,0x1100600,0x1100700,0x1100800,0x1100900]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS]
   if a in [0x1100200,0x1100300,0x1100600]:kind='cycles' if a==0x1100600 else 'delay';st['trace'].append([kind,args[0]]);result=0x12345678
   elif a==0x1100700:kind='mode';result=st['modes'][min(st['mode_index'],len(st['modes'])-1)];st['mode_index']+=1;st['trace'].append([kind,result])
   elif a in [0x1100800,0x1100900]:kind='ring' if a==0x1100800 else 'sdk';st['trace'].append([kind,args if kind=='ring' else args[:3]]);result=0
   else:
    kind='read' if a in [0x1100000,0x1100400] else 'write';record=None
    if a in [0x1100400,0x1100500]:record=bytes(u.mem_read(args[2],20));reg=struct.unpack_from('<H',record,2)[0];ptr=struct.unpack_from('<I',record,12 if kind=='read' else 4)[0];length=struct.unpack_from('<H',record,16 if kind=='read' else 8)[0]
    else:reg,ptr,length=args[:3]
    index=st['operations'];result=st['status'] if st['fail_at']>=0 and (index==st['fail_at'] or st['persistent'] and index>=st['fail_at']) else 0;st['operations']+=1;regbyte=reg&127
    payload=bytes(u.mem_read(ptr,min(length,64))) if kind=='write' else None
    st['trace'].append([kind,a,args,record.hex() if record else None,payload.hex() if payload else '',result])
    if kind=='read':
     if st['written'] and length:
      if regbyte==94:
       base=((st['registers'][92]<<4)|(st['registers'][91]&15))*2;data=bytes((base+i)&255 for i in range(min(length,128)))
      else:data=bytes(st['registers'].get((regbyte+i)&127,0x96) for i in range(min(length,128)))
      u.mem_write(ptr,data[:1] if st['written']==2 else data)
    elif length and result==0:st['registers'][regbyte]=u.mem_read(ptr,1)[0]
    if st['mutation']==1:
     put(u,CTX+4,0x87654321)
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries=dict(base=(0x5447e,'r1_bma4_initialize'),variant=(0x543c4,'r1_bma456w_initialize'),configure=(0x53c6c,'r1_bma456w_configure_boundary'));default=dict(kind='base',rate=25,chip=0x16,mask=7,context=CTX,intf=1,transport=0,fail_at=-1,status=8,persistent=0,written=1,mutation=0,seed=0xabcdef01,modes=[0],bus=2);cases=[]
  for kind,context,mask,intf,fail_at,status,written,chip in itertools.product(['base','variant'],[0,CTX,D+0x3000,D+0x3001],range(8),range(2),[-1,0,1],[8,0xffffffff,256],[0,1,2],[0,0x16,255]):cases.append(dict(default,kind=kind,context=context,mask=mask,intf=intf,fail_at=fail_at,status=status,written=written,chip=chip))
  for rate,fail_at,status,modes in itertools.product([0,25,50,100,200,0xffffffff,0x7fffffff],range(-1,21),[8,0xffffffff,256],[[0],[1],[2],[4],[7],[0,4,2]]):cases.append(dict(default,kind='configure',rate=rate,fail_at=fail_at,status=status,modes=modes,transport=1))
  for chip,written,modes,bus,mutation in itertools.product([0,0x16,255],[0,1,2],[[0],[7],[0,4,2]],range(3),range(2)):cases.append(dict(default,kind='configure',chip=chip,written=written,modes=modes,bus=bus,mutation=mutation,transport=1))
  for case in cases:
   if case['kind']=='configure' and case['written']==2:continue
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,b'\x96'*0x5000);u.mem_write(SP-4096,b'\x96'*8192);context=case['context'];u.mem_write(CTX,b'\x00'*52)
    if context:u.mem_write(context,b'\x96'*52);put(u,context+4,ADDRESS);u.mem_write(context+8,bytes([case['intf'],0,0,0]));put(u,context+36,0x1100001 if case['mask']&1 else 0);put(u,context+40,0x1100101 if case['mask']&2 else 0);put(u,context+44,0x1100201 if case['mask']&4 else 0)
    put(u,ADDRESS,24);put(u,BUS,D+0x2000 if case['bus'] else 0);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100401 if case['bus']==2 else 0,0x1100501 if case['bus']==2 else 0));states[id(u)]=dict(case,side=side,trace=[],fault=None,operations=0,mode_index=0,registers={0:case['chip'],1:case['chip'],72:0x55,73:0xaa,125:0x96,124:1})
    args=[case['rate'] if kind=='configure' else context,0x11111111,0x12345678,case['seed']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=300000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    context=bytearray(u.mem_read(CTX if kind=='configure' or not case['context'] else case['context'],52))
    for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1),(44,'r1_bma_delay_us',0x53aa5)]:
     if struct.unpack_from('<I',context,off)[0]==((syms[name]|1) if side else native):struct.pack_into('<I',context,off,native)
    results.append([None if st['fault'] else [u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R2) if kind!='configure' else None,u.reg_read(UC_ARM_REG_R3)],st['trace'],st['fault'],context.hex(),bytes(u.mem_read(D,512)).hex(),st['registers']])
   assert results[0]==results[1],(case,results)
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_three_initialization_configuration_bodies_full_bosch_graph_requests_registry=True,only_bus_raw_transport_and_delay_callbacks_are_fixtures=True,raw_restored_r2_r3_observed_span_fresh_logging_failures_and_rates_checked=True,prior_private_stack_input_alias_gate_retained=True,partial_successful_configuration_read_histories_explicitly_gated=True,native_callback_scratch_pointer_callee_sp_context_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
