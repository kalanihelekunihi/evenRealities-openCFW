#!/usr/bin/env python3
"""Differential native PRNG/scanf primitive behavior, distinct from raw ABI proof."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-libc-primitives';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TARGETS={'rand':('r1_native_rand',0x276a4,20),'srand':('r1_native_srand',0x276b8,6),'digit':('r1_native_scanf_digit',0x27ff4,28),'getc':('r1_native_scanf_format_getc',0x28010,12)}
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_libc_primitives.o';assert sha(obj)==report['units'][0]['object_sha256'] and not report['units'][0]['undefined']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_libc_primitives_verification.ld';states={};counts=dict.fromkeys(TARGETS,0);digest=hashlib.sha256()
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
  def write(u,access,address,size,value,_):
   if address<0x2003e000:states[id(u)].append([address,size,value])
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
  rng=random.Random(0x276a4);seeds=list(range(256))+[0x7fffffff,0x80000000,0xfffffffe,0xffffffff]+[rng.getrandbits(32) for _ in range(1024)]
  digit_values=list(range(256))+[0xffffff00,0xffffffcf,0xffffffd0,0xfffffffe,0xffffffff,0x80000000,0x7fffffff]+[rng.getrandbits(32) for _ in range(256)]
  cases=itertools.chain((('srand',seed,0,seed) for seed in seeds),(('rand',0,0,seed) for seed in seeds),(('digit',ch,radix,0) for ch,radix in itertools.product(digit_values,[*range(38),0x100,0x10000,0x80000000,0xffffffff])),(('getc',0x20001000,advance,byte) for byte,advance in itertools.product(range(256),[0,1,2,0xffffffff,0x80000000])))
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,a,b,state in cases:
   results=[]
   for candidate,u in enumerate(machines):
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,b);u.mem_write(0x20007db0,struct.pack('<I',state));u.mem_write(0x20001000,struct.pack('<I',0x20002000));u.mem_write(0x20002000,bytes([state&255]));states[id(u)]=[]
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[TARGETS[kind][0]] if candidate else TARGETS[kind][1])|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(r) for r in saved]==[0x12345600+i for i in range(8)]
    results.append([None if kind=='srand' else u.reg_read(UC_ARM_REG_R0),states[id(u)],bytes(u.mem_read(0x20007db0,4)).hex(),bytes(u.mem_read(0x20001000,4)).hex()])
   assert results[0]==results[1],(kind,hex(a),hex(b),hex(state),results)
   counts[kind]+=1;digest.update(json.dumps([kind,a,b,state,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),return_stack_callee_integer_and_nonstack_writes_checked=True,all_byte_digit_values=True,malformed_unsigned_digit_inputs=True,all_byte_getc_values=True,zero_negative_and_wrapping_cursor_advances=True,seeded_random_prng_states=True,source_complete_for_selected_bodies=True,runtime_no_unresolved=True,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Individual seeded calls do not prove source startup or PRNG initialization.','Typed behavior does not prove caller scratch/APSR/private frames, invalid memory behavior, full domain or hardware behavior.','Full firmware and instruction/image identity remain separate gates.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
