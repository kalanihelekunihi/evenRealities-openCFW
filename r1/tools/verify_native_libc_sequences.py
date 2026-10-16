#!/usr/bin/env python3
"""Native sequence behavior including callback transcript and exact write order."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE,UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-libc-sequences';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'qsort':('r1_native_qsort',0x27606,156),'strcat':('r1_native_strcat',0x277c0,24),'strncpy':('r1_native_strncpy',0x277d8,24),'memcmp':('r1_native_memcmp',0x2781a,26),'strtok':('r1_native_strtok',0x27854,62)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_libc_sequences.o';assert sha(obj)==r['units'][0]['object_sha256'] and not r['units'][0]['undefined']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_libc_sequences_verification.ld';states={};counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256();callback_count=0
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
  def write(u,access,address,size,value,_):
   if address<0x2003e000:states[id(u)]['writes'].append([address,size,value])
  def callback(u,address,size,_):
   if address!=0x20000200:return
   st=states[id(u)];a=u.reg_read(UC_ARM_REG_R0);b=u.reg_read(UC_ARM_REG_R1);x=u.mem_read(a,1)[0];y=u.mem_read(b,1)[0];mode=st['mode']
   if mode==3:x=(x^128)-128;y=(y^128)-128
   result=0 if mode==2 else (y-x if mode==1 else x-y)
   st['callbacks'].append([a,b,result]);u.reg_write(UC_ARM_REG_R0,result&0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_CODE,callback);machines.append(u)
  rng=random.Random(0x27606);cases=[]
  for count,width,mode,pattern in itertools.product([*range(17),32,64],[0,1,2,3,4,8],range(4),range(4)):
   data=bytes(rng.randrange(256) if pattern==0 else ((i&255) if pattern==1 else (255-i)&255 if pattern==2 else 7) for i in range(count*width));cases.append(('qsort',data,b'',count,width,mode))
  for length,zero,fill in itertools.product(range(34),[0,1,7,16,32],[1,128,255]):cases.append(('strncpy',b'\x96'*64,bytes([fill])*zero+b'\0'+bytes([fill])*64,length,0,0))
  for a,b in itertools.product(range(256),repeat=2):cases.append(('memcmp',bytes([a,17,0]),bytes([b,17,0]),1,0,0))
  for length in range(34):
   for _ in range(16):
    a=bytes(rng.randrange(256) for _ in range(64));b=bytearray(a)
    if length and rng.randrange(2):b[rng.randrange(length)]^=255
    cases.append(('memcmp',a,bytes(b),length,0,0))
  for left,right in itertools.product([b'',b'a',b'hello',bytes([128,255]),b'long_string'],repeat=2):cases.append(('strcat',left+b'\0',right+b'\0',0,0,0))
  for inp,delim in itertools.product([b'',b',',b',,a,,b,c,,',b'abc',b' a b ',bytes([128,255,1,128,2]),b'aaa'],[b'',b',',b' ',b', ',bytes([128,255]),b'a']):cases.append(('strtok',inp+b'\0',delim+b'\0',0,0,0))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,left,right,n,width,mode in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(0x20001000,b'\x96'*2048);u.mem_write(0x20001000,left);u.mem_write(0x20001400,right);u.mem_write(0x20007db4,struct.pack('<I',0x20001000));states[id(u)]={'writes':[],'callbacks':[],'mode':mode};returns=[]
    for step in range(10 if kind=='strtok' else 1):
     u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     args=[0x20001000 if not step else 0, n if kind=='qsort' else 0x20001400,width if kind=='qsort' else n,0x20000201]
     for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],args):u.reg_write(reg,value)
     for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
     u.emu_start((syms[TARGETS[kind][0]] if candidate else TARGETS[kind][1])|1,0x20000100,count=1000000)
     assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)],(kind,n,width,candidate)
     returns.append(None if kind=='qsort' else u.reg_read(UC_ARM_REG_R0))
    st=states[id(u)];results.append([returns,st['writes'],st['callbacks'],bytes(u.mem_read(0x20001000,2048)).hex(),bytes(u.mem_read(0x20007db4,4)).hex()])
   assert results[0]==results[1],(kind,left.hex(),right.hex(),n,width,mode,results)
   counts[kind]+=1;callback_count+=len(results[0][2]);digest.update(json.dumps([kind,left.hex(),right.hex(),n,width,mode,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,callback_comparisons=callback_count,trace_sha256=digest.hexdigest(),return_stack_callee_integer_full_arena_and_nonstack_write_order_checked=True,qsort_callback_transcripts_checked=True,qsort_comparator_fixture=True,all_first_byte_memcmp_pairs=True,strncpy_padding_and_truncation=True,strtok_ten_call_continuations=True,runtime_no_unresolved=True,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Qsort comparator fixture returns byte comparisons; full arbitrary callback behavior and huge counts/widths remain open.','Typed return/callee and memory behavior do not prove caller scratch/APSR/private frames or invalid-memory/overlap behavior.','Token cursor startup, full firmware integration, hardware and instruction/image identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
