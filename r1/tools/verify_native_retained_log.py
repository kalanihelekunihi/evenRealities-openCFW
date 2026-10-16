#!/usr/bin/env python3
"""Compare retained-log control/state/frame contracts; callees are fixtures."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-retained-log'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;CTX=0x20007a34;D=0x20010000;F=0x20016000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_retained_log.o'
 assert sha(obj)==r['units'][0]['object_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 rea=BASE/'native-retained-log-rea.json';e=json.loads(rea.read_text());n=e['structuredContent']['normalized_result'];assert n['procedure']['address']=='0x7f030' and n['procedure']['body']['total_bytes']==146
 states={};counts=dict(clear=0,initialize=0,format=0,output=0);digest=hashlib.sha256();total=0
 with tempfile.TemporaryDirectory(prefix='r1-retained-log-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }')
  elf=d/'test.elf';binary=d/'text.bin'
  bindings={'r1_reset_trace_context':CTX,'__aeabi_memclr':0x1100001,'r1_health_crash_record_initializer':0x1100011,'r1_native_vsnprintf':0x1100021,'r1_stdout_write':0x1100031}
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_retained_log_printf_sink',*[f'--defsym={k}={v}' for k,v in bindings.items()],str(obj),'-o',str(elf)],check=True,capture_output=True)
  subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
  def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def hook(u,a,size,_):
   kind={0x277aa:'clear',0x1100000:'clear',0x5a2b8:'initialize',0x1100010:'initialize',0x380dc:'format',0x1100020:'format',0x319e0:'output',0x1100030:'output'}.get(a)
   if not kind:return
   st=states[id(u)];args=[u.reg_read(reg) for reg in REGS];result=0xabcdef00
   if kind=='clear':
    st['trace'].append([kind,args[:2]]);u.mem_write(args[0],bytes(args[1]))
    if st['mode']==1 and args[1]==3008:put(u,CTX+8,D+0x3000)
   elif kind=='initialize':
    st['trace'].append([kind])
    if st['mode']==2:u.mem_write(CTX+2,struct.pack('<H',3007))
   elif kind=='format':
    st['trace'].append([kind,args,bytes(u.mem_read(args[3],12)).hex()])
    result=st['result']&0xffffffff
    if st['result']>0:u.mem_write(args[0],b'X'*min(st['result'],args[1]-1)+b'\0')
    if st['mode']==3:u.mem_write(CTX+2,struct.pack('<H',2999));put(u,CTX+12,D+0x4000)
   else:
    st['trace'].append([kind,args[:3],bytes(u.mem_read(args[1],args[2])).hex()]);result=0x87654321
   if st['side']==0:counts[kind]+=1
   for reg,value in zip(REGS,[result,0x11111111,0x22222222,0x33333333]):u.reg_write(reg,value)
   u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x1100000,4096);u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_CODE,hook);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for null,flag,cursor,result,mode,seed in itertools.product([0,1],[0,1,255],[0,1,2999,3006,3007,3008,65535],[-1,0,1,8,3008,65536],range(4),[0,0xaa]):
   observed=[]
   for side,u in enumerate(machines):
    u.mem_write(D,bytes([seed])*0x6000);u.mem_write(F,b'%u\0');u.mem_write(SP-1024,bytes([seed])*2048)
    u.mem_write(CTX,struct.pack('<6I',flag|(cursor<<16),D+0x2000,D+0x3000,D+0x1000,0,D+0x5800))
    args=[0 if null else F,0x12345678,0x87654321,0xabcdef01]
    for reg,value in zip(REGS,args):u.reg_write(reg,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101)
    states[id(u)]={'side':side,'trace':[],'mode':mode,'result':result}
    u.emu_start((syms['r1_retained_log_printf_sink'] if side else 0x7f030)|1,0x20000100,count=100000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP
    assert [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    observed.append([u.reg_read(UC_ARM_REG_R0),states[id(u)]['trace'],bytes(u.mem_read(CTX,24)).hex(),bytes(u.mem_read(D,0x6000)).hex(),bytes(u.mem_read(SP-32,32)).hex()])
   assert observed[0]==observed[1],(null,flag,cursor,result,mode,seed,observed[0][:3],observed[1][:3])
   total+=1;digest.update(json.dumps([null,flag,cursor,result,mode,seed,observed[0]],sort_keys=True).encode())
 receipt=dict(comparisons=total,observation_counts=counts,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),rea_sha256=sha(rea),actual_sink_body=True,callees_are_fixtures=True,external_frame32_and_varargs_pointer_checked=True,raw_r0_callee_sp_context_output_ram_checked=True,full_private_frame_history_verified=False,composed_formatter_rtt_crash_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
