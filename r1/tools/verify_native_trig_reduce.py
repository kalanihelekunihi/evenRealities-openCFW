#!/usr/bin/env python3
"""Bounded raw-slot differential verification of native float trig reducer."""
import hashlib,itertools,json,random,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-trig-reduce';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=OUT/'native_trig_reduce.o'
 assert sha(obj)==report['units'][0]['object_sha256'] and not report['units'][0]['undefined']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 data=app.read_bytes();evidence={}
 for a,n in [(0x3bb04,316),(0x3bc44,20),(0xbdb48,48)]:
  p=OUT/f'ghidra-{a:x}.json';assert bytes(json.loads(p.read_text())['data'])==data[a-0x27000:a-0x27000+n];evidence[p.name]=sha(p)
 rea=OUT/'rea-3bb04.json';r=json.loads(rea.read_text())['structuredContent'];assert r['normalized_result']['body']['ranges']==[{'start':'0x3bb04','end':'0x3bc3f'}];evidence[rea.name]=sha(rea)
 layout=ROOT/'r1/source-config/runtime/native_trig_reduce_verification.ld';digest=hashlib.sha256();count=0;states={};saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]+list(range(UC_ARM_REG_D8,UC_ARM_REG_D15+1))
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),'-e','r1_native_trig_reduce32',str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  for section,a,n in [('table',0xbdb48,48),('coeff',0x3bc44,20)]:
   p=d/'section.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.r1.math.trig_reduce_'+section,'-O','binary',str(obj),str(p)],check=True);assert p.read_bytes()==data[a-0x27000:a-0x27000+n]
  def write(u,access,address,size,value,_):
   if 0x20000000<=address<0x2003e000:states[id(u)].append([address,size,value])
  machines=[]
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,data);u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000);u.hook_add(UC_HOOK_MEM_WRITE,write);machines.append(u)
  rng=random.Random(0x3bb04);inputs=[(s<<31)|(e<<23)|f for s,e,f in itertools.product(range(2),range(256),[0,1,0x3fffff,0x400000,0x7fffff])]+[rng.getrandbits(32) for _ in range(4096)]
  modes=[(r<<22)|(fz<<24)|(dn<<25)|flags for r,fz,dn,flags in itertools.product(range(4),range(2),range(2),[0,0x10])]
  for index,(x,mode) in enumerate(itertools.product(inputs,modes)):
   incoming=(index*0x1234567)&0xffffffff;results=[]
   for candidate,u in enumerate(machines):
    states[id(u)]=[];u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.mem_write(0x20001000,b'\x96'*4);states[id(u)].clear();u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_FPSCR,mode);u.reg_write(UC_ARM_REG_R0,0x20001000);u.reg_write(UC_ARM_REG_R1,x);u.reg_write(UC_ARM_REG_S0,incoming)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    try:u.emu_start((syms['r1_native_trig_reduce32'] if candidate else 0x3bb04)|1,0x20000100,count=2000)
    except Exception as exc:raise AssertionError((index,hex(x),hex(mode),candidate,hex(u.reg_read(UC_ARM_REG_PC)),[hex(u.reg_read(reg)) for reg in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_CPSR]])) from exc
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000
    assert [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(len(saved))]
    results.append([u.reg_read(UC_ARM_REG_S0),u.reg_read(UC_ARM_REG_FPSCR),bytes(u.mem_read(0x20001000,4)).hex(),states[id(u)].copy()])
   assert results[0]==results[1],(hex(x),hex(mode),hex(incoming),results)
   digest.update(json.dumps([x,mode,incoming,results[0]],sort_keys=True).encode());count+=1
 receipt=dict(comparisons=count,trace_sha256=digest.hexdigest(),all_binary32_exponents=True,both_signs=True,all_rounding_flush_to_zero_default_nan_modes=True,initial_inexact_flag_zero_and_one=True,independent_incoming_s0=True,return_fpscr_quadrant_write_order_stack_and_callee_registers_checked=True,source_owned_numeric_bytes=68,report_sha256=sha(rp),object_sha256=sha(obj),layout_sha256=sha(layout),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence=evidence,instruction_identity=False,limitations=['Selected mantissas and random values do not exhaust all inputs.','Caller scratch/APSR/private stack shape, pointer faults and stack aliasing remain unverified.','Authenticated table prefix is shared numeric data; this is not additive whole-firmware coverage.','Consumer graph and aggregate runtime admission remain separate gates.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
