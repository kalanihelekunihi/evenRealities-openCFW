#!/usr/bin/env python3
"""Native Bosch write/power/feature graph through stateful transport fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_INVALID
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-bma-setup';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SP=0x2003d000;CTX=0x2001e4e8;ADDRESS=0x200076c0;BUS=0x200076b4;D=0x20010000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
def main():
 rp=OUT/'report.json';b=json.loads(rp.read_text());obj=OUT/'native-bma-setup-runtime.o';assert sha(obj)==b['linked_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';states={};digest=hashlib.sha256();counts=dict(enable=0,accel_config=0,fifo_config=0);obs=dict(read=0,write=0,delay=0);faults=0;failed_write_delay=0
 with tempfile.TemporaryDirectory(prefix='r1-bma-feature-io-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .context 0x2001e4e8 (NOLOAD) : { *(.bss.r1.bma.context) } .address 0x200076c0 : { *(.r1.bma.bus_address) } .bus 0x200076b4 : { *(.r1.bind.r1_motion_bus_device) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin';roots=b['roots']+['r1_bma_default_read','r1_bma_default_write'];subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in roots for v in ['-u',x]],'-T',str(ld),'-e',roots[0],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3}
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   if a not in [0x1100000,0x1100100,0x1100200,0x1100300,0x1100400,0x1100500]:return
   st=states[id(u)];args=[u.reg_read(x) for x in REGS]
   if a in [0x1100200,0x1100300]:kind='delay';st['trace'].append([kind,a,args[:2]]);result=0x12345678
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
      u.mem_write(ptr,data)
    elif length and result==0:st['registers'][regbyte]=u.mem_read(ptr,1)[0]
    if st['mutation']==2 and kind=='write' and length:u.mem_write(ptr,b'\x80')
    if st['mutation']==1:
     u.mem_write(CTX+50,b'\x01');put(u,CTX+44,0x1100301);put(u,CTX+4,0x87654321)
   if not st['side']:obs[kind]+=1
   for reg,v in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  def invalid(u,access,a,size,value,_):states[id(u)]['fault']=[access,a,size,value];return False
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_INVALID,invalid);machines.append(u)
  entries=dict(enable=(0x54640,'r1_bma4_set_accel_enable'),accel_config=(0x545ca,'r1_bma4_set_accel_config'),fifo_config=(0x546d0,'r1_bma4_set_fifo_config'));default=dict(kind='enable',val=1,config=0x7f,enable=1,odr=7,bw=1,perf_input=1,range_input=2,pointer=D+0x100,lo=0x55,hi=0xaa,perf=0,intf=1,transport=0,context=CTX,mask=7,fail_at=-1,status=8,persistent=0,written=1,mutation=0,seed=0xabcdef01);cases=[]
  for kind,val,config,enable,fail_at,status,transport,mutation in itertools.product(counts,[0,1,255],[0,0x7f,0xffffffff],[0,1,0x101],[-1,0,1,2],[8,0xffffffff,256],range(2),range(3)):cases.append(dict(default,kind=kind,val=val,config=config,enable=enable,fail_at=fail_at,status=status,transport=transport,mutation=mutation))
  for kind,mask,context in itertools.product(counts,range(8),[0,CTX]):cases.append(dict(default,kind=kind,mask=mask,context=context))
  for odr,bw,perf_input,range_input,fail_at in itertools.product([0,1,7,10,11,12,13,255],[0,1,2,7,8],[0,1,2],[0,2,255],[-1,0,1]):cases.append(dict(default,kind='accel_config',odr=odr,bw=bw,perf_input=perf_input,range_input=range_input,fail_at=fail_at))
  for pointer,seed in itertools.product([0,D+0x101,CTX+8],[0x02010007,0x00020102]):cases.append(dict(default,kind='accel_config',pointer=pointer,seed=seed))
  for case in cases:
   results=[];kind=case['kind']
   for side,u in enumerate(machines):
    u.mem_write(D,bytes(range(256))*32);u.mem_write(SP-4096,b'\x96'*8192);u.mem_write(CTX,b'\x00'*52);put(u,ADDRESS,24);put(u,CTX+4,ADDRESS);u.mem_write(CTX+8,bytes([case['intf'],0,0,0]));u.mem_write(CTX+20,struct.pack('<HB',16,32));u.mem_write(CTX+50,bytes([case['perf']]))
    read=((syms['r1_bma_default_read']|1) if side else 0x53ab5) if case['transport'] else 0x1100001;write=((syms['r1_bma_default_write']|1) if side else 0x53ad1) if case['transport'] else 0x1100101
    put(u,CTX+36,read if case['mask']&1 else 0);put(u,CTX+40,write if case['mask']&2 else 0);put(u,CTX+44,0x1100201 if case['mask']&4 else 0);put(u,BUS,D+0x2000);u.mem_write(D+0x2000,struct.pack('<6I',0,D+0x2100,0,0,0,0));u.mem_write(D+0x2100,struct.pack('<6I',0,0,0,0,0x1100401,0x1100501));states[id(u)]=dict(case,side=side,trace=[],fault=None,operations=0,registers={72:case['lo'],73:case['hi'],125:case['lo']})
    if kind=='accel_config':
     if case['pointer']:u.mem_write(case['pointer'],bytes([case['odr'],case['bw'],case['perf_input'],case['range_input']]))
     args=[case['pointer'],case['context'],0x12345678,case['seed']]
    elif kind=='enable':args=[case['val'],case['context'],0x12345678,case['seed']]
    else:args=[case['config'],case['enable'],case['context'],case['seed']]
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    try:u.emu_start((syms[entries[kind][1]] if side else entries[kind][0])|1,0x20000100,count=300000)
    except UcError as error:
     if not states[id(u)]['fault']:states[id(u)]['fault']=['cpu',str(error),u.reg_read(UC_ARM_REG_PC)]
    st=states[id(u)]
    if not st['fault']:assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    context=bytearray(u.mem_read(CTX,52))
    for off,name,native in [(36,'r1_bma_default_read',0x53ab5),(40,'r1_bma_default_write',0x53ad1)]:
     if struct.unpack_from('<I',context,off)[0]==((syms[name]|1) if side else native):struct.pack_into('<I',context,off,native)
    results.append([None if st['fault'] else u.reg_read(UC_ARM_REG_R0),st['trace'],st['fault'],context.hex(),bytes(u.mem_read(D,512)).hex(),st['registers']])
   assert results[0]==results[1],(case,results)
   if kind=='fifo_config' and case['fail_at']==-1 and case['mask']==7 and case['context']==CTX and case['mutation']==0:
    lowmask=case['config']&3;highmask=case['config']&252;expected0=(case['lo']|lowmask) if case['enable']==1 else case['lo']&(~lowmask&255);expected1=(case['hi']|highmask) if case['enable']==1 else case['hi']&(~highmask&255);assert results[0][-1][72]==expected0 and results[0][-1][73]==expected1
   if kind=='enable':
    trace=results[0][1];failed_write_delay+=any(v[0]=='write' and v[-1]!=0 and any(w[0]=='delay' and w[2][0]==25000 for w in trace[i+1:]) for i,v in enumerate(trace))
   counts[kind]+=1;faults+=bool(results[0][2]);digest.update(json.dumps([case,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,matching_faults=faults,failed_write_followed_by_25000_delay_cases=failed_write_delay,observation_counts=obs,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_three_setters_attributed_kernels_read_write_graph_requests_and_registry=True,only_bus_raw_transport_and_delay_callbacks_are_fixtures=True,failed_write_delay_fresh_callback_public_ram_alias_and_full_enable_word_checked=True,private_stack_input_aliases_explicitly_gated=True,fifo_configuration_against_independent_mask_oracle=True,native_callback_scratch_pointer_callee_sp_context_ram_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,real_sensor_bus_execution_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'setup-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
