#!/usr/bin/env python3
"""Native/source temperature bodies with explicit bus/mode/NV/RTOS/log fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-temperature';EVIDENCE=OUT.parent/'native-temperature-analysis';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;D=0x20010000;CAL=0x200076f0;REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3];SAVED=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
FIXTURES={'r1_gxt310_bus_acquire':0x50f28,'r1_gxt310_enable_pair_native':0x50f9c,'osDelay':0x7d154,'r1_gxt310_disable_pair_native':0x50f88,'r1_gxt310_bus_release':0x50efc,'r1_kv_class_read':0x73930,'r1_gxt310_transfer_read_native':0x6f640,'r1_gxt310_transfer_write_native':0x6f644,'r1_structured_log_mode_get':0x914ec,'r1_structured_log_format':0x91638,'nrf_log_frontend_std_1':0x799c8}
def main():
 b=json.loads((OUT/'report.json').read_text());obj=OUT/'native-temperature-runtime.o';assert sha(obj)==b['linked_sha256'];contracts=json.loads((OUT/'contracts.json').read_text());entries={int(k,16):v for k,v in contracts['names'].items()};states={};counts=dict.fromkeys(b['roots'],0);digest=hashlib.sha256();observations=dict.fromkeys(FIXTURES,0)
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 with tempfile.TemporaryDirectory(prefix='r1-temp-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';rom=''.join(' .s'+x['address'][2:]+' '+x['address']+' : { *('+x['section']+') } ' for x in json.loads((OUT/'text-spans.json').read_text()));ld.write_text('SECTIONS { .cal 0x200076f0 : { *(.r1.temp.calibration) } '+rom+' .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';text=d/'text.bin';bindings={name:0x1100001+256*i for i,name in enumerate(FIXTURES)};bindings['r1_device_info_kv_handle']=0x20007dfc
  subprocess.run(['arm-none-eabi-ld','--gc-sections',*[v for x in b['roots'] for v in ['-u',x]],'-T',str(ld),'-e',b['roots'][0],*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(text)],check=True);syms={v[2]:int(v[0],16) for l in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=l.split())==3};assert syms['r1_temperature_calibration']==CAL
  hooks={addr:name for name,addr in FIXTURES.items()};hooks.update({v&~1:k for k,v in bindings.items() if k in FIXTURES})
  def hook(u,a,size,_):
   if a not in hooks:return
   name=hooks[a];st=states[id(u)];c=st['case'];args=[u.reg_read(x) for x in REGS];value=c['status'];trace=args[:];extra=None
   if name=='r1_gxt310_transfer_read_native':
    assert args[1]==0 and args[3]==2;bits=c['bits'][int(args[0]==0x94)];data=struct.pack('>H',bits);u.mem_write(args[2],data[:c['written']]);extra=data[:c['written']].hex()
   elif name=='r1_gxt310_transfer_write_native':
    assert args[1]==1 and args[3]==2;extra=bytes(u.mem_read(args[2],4)).hex();assert extra=='01c10000'
    if c['mutate']:u.mem_write(args[2],bytes.fromhex('efbeadde'))
   elif name=='r1_kv_class_read':
    assert args==[D+0x1000,SP-(152 if c['entry']==0x50e4c else 136),124,args[3]];length=min(c['nv_length'],124);data=bytearray([0x69]*124);data[62:68]=bytes.fromhex(c['calibration']);u.mem_write(args[1],bytes(data[:length]));trace=args[:3];extra=bytes(data[:length]).hex()
   elif name=='r1_structured_log_mode_get':value=c['modes'][min(st['modes'],len(c['modes'])-1)];st['modes']+=1;trace=[value]
   elif name=='r1_structured_log_format':trace=args[:4]
   elif name=='nrf_log_frontend_std_1':trace=args[:3]
   elif name=='osDelay':assert args[0]==80;trace=[80]
   else:trace=[]
   st['trace'].append([name,trace,extra,value]);
   if not st['side']:observations[name]+=1
   for reg,v in zip(REGS,[value,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,v)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for side in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x40000);u.mem_write(0x1000000,text.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  default=dict(entry=0x6f600,args=[0x90,0xabcdef01,0x12345678,0x98765432],bits=[0,0],status=1,written=2,nv_length=124,calibration='ffffffffffff',modes=[0],mutate=0,seed=0x96,rounding=0);cases=[]
  for bits in range(65536):cases.append(dict(default,bits=[bits,bits]))
  for entry,bits,status,written,rounding in itertools.product([0x6f600,0x6f80c,0x6f826],[0,1,0x7fff,0x8000,0xffff],[0,1,256,0xffffffff],range(3),range(4)):cases.append(dict(default,entry=entry,bits=[bits,bits],status=status,written=written,rounding=rounding))
  for entry,status,modes,mutate in itertools.product([0x6f738,0x6f818,0x6f832],[0,1,256,0xffffffff],[[0],[1],[2],[4],[7],[0,4,2]],range(2)):cases.append(dict(default,entry=entry,status=status,modes=modes,mutate=mutate))
  calibrations=['ffffffffffff','000100000200','01ffff01ffff','020102020304','ff0000ff0000']+['ff'*i+'00'+'ff'*(5-i) for i in range(6)];pairs=[(0,0),(1,0xffff),(0x7fff,0x8000),(0xffff,0xffff),(0x8000,0x8000),(0x1234,0xabcd)]
  for entry,cal,pair,nv_length,status in itertools.product([0x50e4c,0x7badc],calibrations,pairs,[0,62,63,64,65,66,67,68,124],[0,1,0xffffffff]):cases.append(dict(default,entry=entry,calibration=cal,bits=list(pair),nv_length=nv_length,status=status))
  for c in cases:
   results=[]
   for side,u in enumerate(machines):
    u.mem_write(SP-2048,bytes([c['seed']])*4096);u.mem_write(D,b'\x96'*8192);u.mem_write(CAL,b'\xff'*6);u.mem_write(0x20007dfc,struct.pack('<I',D+0x1000));args=c['args'][:]
    if c['entry']==0x7badc:args[0]=D
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    for i,reg in enumerate(SAVED):u.reg_write(reg,0x12340000+i)
    for reg in [UC_ARM_REG_S0,UC_ARM_REG_S1]:u.reg_write(reg,0x12345678)
    u.reg_write(UC_ARM_REG_FPSCR,c['rounding']<<22);u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);states[id(u)]=dict(case=c,side=side,trace=[],modes=0);u.emu_start((syms[entries[c['entry']]] if side else c['entry'])|1,0x20000100,count=10000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(x) for x in SAVED]==[0x12340000+i for i in range(8)]
    result=u.reg_read(UC_ARM_REG_R0)
    if c['entry'] in [0x6f600,0x6f80c,0x6f826] and c['written']==2:
     sample=c['bits'][int(c['entry']==0x6f826)];sample=sample if sample<32768 else sample-65536;expected=(abs(sample)*125//16)*(-1 if sample<0 else 1);assert result==expected&0xffffffff
    results.append([result,states[id(u)]['trace'],bytes(u.mem_read(CAL,6)).hex(),bytes(u.mem_read(D,8)).hex(),[u.reg_read(x) for x in [UC_ARM_REG_S0,UC_ARM_REG_S1,UC_ARM_REG_FPSCR]],u.reg_read(UC_ARM_REG_R3) if c['entry'] in [0x6f600,0x6f80c,0x6f826,0x6f738,0x6f818,0x6f832] else None])
   assert results[0]==results[1],(c,results)
   counts[entries[c['entry']]]+=1;digest.update(json.dumps([c,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,observation_counts=observations,trace_sha256=digest.hexdigest(),report_sha256=sha(OUT/'report.json'),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in EVIDENCE.glob('rea-*.json')},all_65536_sample_words_checked_with_independent_integer_oracle=True,actual_eight_temperature_bodies=True,bus_mode_registry_nv_rtos_and_log_dependencies_are_fixtures=True,whole_source_consumer_graph_executed=False,raw_r0_callee_sp_fp_state_data_and_typed_call_records_checked=True,full_private_frame_history_verified=False,full_raw_abi_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
