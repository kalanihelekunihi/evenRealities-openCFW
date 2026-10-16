#!/usr/bin/env python3
"""Native callback tail ABI and independently observed cold callback storage."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-send-hook';CELL=0x20006c20;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);report=OUT/'report.json';r=json.loads(report.read_text());unit=r['units'][0];obj=Path(unit['command'][-1]);assert sha(obj)==unit['object_sha256'] and sha(ROOT/unit['source'])==unit['source_sha256']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 for src,dst in [('rea-next-827f8-body.json','rea-827f8.json'),('ghidra-next-827f8.json','ghidra-body.json')]:
  p=OUT/dst;p.write_bytes((BASE/'native-battery-runtime'/src).read_bytes());evidence[dst]=sha(p)
 q=json.loads((OUT/'rea-827f8.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==14
 assert bytes(json.loads((OUT/'ghidra-body.json').read_text())['data'])==app.read_bytes()[0x827f8-0x27000:0x827f8-0x27000+20]
 cold=[]
 for poison in (165,90,255,60):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x20000000,0x40000);u.mem_write(0x20000000,bytes([poison])*0x40000);writes=[]
  def wh(u,access,a,n,v,_):
   if a<CELL+4 and a+n>CELL:writes.append({'pc':u.reg_read(UC_ARM_REG_PC),'address':a,'bytes':n,'value':v})
  u.hook_add(UC_HOOK_MEM_WRITE,wh);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.emu_start(0x283a1,0x27208,count=2000000);assert u.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(u.mem_read(CELL,4))==b'\0'*4 and writes;cold.append({'poison':poison,'writes':writes})
 machines=[];states={};comparisons=0;callbacks=0
 with tempfile.TemporaryDirectory() as temp:
  d=Path(temp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .send_hook 0x20006c20 : { *(.r1.protocol.send_hook) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);section=d/'hook.bin';subprocess.run(['arm-none-eabi-objcopy','-j','.send_hook','-O','binary',str(elf),str(section)],check=True);assert section.read_bytes()==b'\0'*4;section_sha=sha(section)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
  def hook(u,a,n,_):
   f=states[id(u)]
   if a in (0x20000200,0x20000220):
    args=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert args==[*f['args'],f['callback']];assert u.reg_read(UC_ARM_REG_SP)==0x2003f000 and u.reg_read(UC_ARM_REG_LR)==0x20000101
    f['trace'].append(args);u.mem_write(CELL,struct.pack('<I',f['replacement']));u.mem_write(0x20001000,struct.pack('<4I',*args))
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),f['returns']):u.reg_write(reg,value)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   elif u is machines[1] and a<0x1000000:raise AssertionError(('unexpected native',hex(a)))
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u);u.hook_add(UC_HOOK_CODE,hook)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  values=(0,1,65535,65536,0x80000000,0xffffffff,0x20001000)
  for callback,args,ret,replacement in itertools.product((0,0x20000201,0x20000221),itertools.product(values,repeat=3),(0,1,7,0xffffffff),(0,0x20000221)):
   results=[];returns=[ret,ret^0xa5a5a5a5,(ret+13)&0xffffffff,ret^0x55aa55aa]
   for index,u in enumerate(machines):
    states[id(u)]={'args':list(args),'callback':callback,'returns':returns,'replacement':replacement,'trace':[]};u.mem_write(CELL-4,b'\x96'*12);u.mem_write(CELL,struct.pack('<I',callback));u.mem_write(0x20001000,b'\x5a'*16);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),[*args,0xdeadbeef]):u.reg_write(reg,value)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    u.emu_start((syms['r1_protocol_send_hook_call'] if index else 0x827f8)|1,0x20000100,count=1000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)]
    regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==(returns if callback else [0xffffffff,args[1],args[2],0]);results.append((regs,bytes(u.mem_read(CELL-4,12)),bytes(u.mem_read(0x20001000,16)),states[id(u)]['trace']))
   assert results[0]==results[1];comparisons+=1;callbacks+=bool(callback)
 vp.write_text(json.dumps(dict(comparisons=comparisons,callback_calls_per_side=callbacks,full_r0_r1_r2_r3_checked=True,tail_stack_and_lr_checked=True,live_registration_mutation=True,source_owned_section={'address':CELL,'bytes':4,'sha256':section_sha},cold_runs=cold,report_sha256=sha(report),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Callback targets and registration lifecycle remain external seams; no physical delivery or concurrency proof','Cold zero initialization is source-owned; warm initialization, full startup and exact image identity remain gated']),indent=2)+'\n');print('Protocol send hook:',comparisons,'callbacks',callbacks)
if __name__=='__main__':main()
