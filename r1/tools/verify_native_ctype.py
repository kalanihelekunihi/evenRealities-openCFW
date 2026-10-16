#!/usr/bin/env python3
"""Native ctype EOF/byte lookup and pointer contract without ASCII substitution."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'r1/research/source-build/native-ctype';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_ctype.o';assert sha(obj)==r['units'][0]['object_sha256'] and not r['units'][0]['undefined']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 layout=ROOT/'r1/source-config/runtime/native_ctype_verification.ld';counts={'pointer':0,'space':0};digest=hashlib.sha256();nonascii=[]
 with tempfile.TemporaryDirectory() as tmp:
  d=Path(tmp);elf=d/'test.elf';binary=d/'text.bin';data=d/'data.bin';subprocess.run(['arm-none-eabi-ld','-T',str(layout),str(obj),'-o',str(elf)],check=True)
  for section,target in [('.text',binary),('.r1.ctype.window',data)]:subprocess.run(['arm-none-eabi-objcopy','-j',section,'-O','binary',str(elf),str(target)],check=True)
  assert len(data.read_bytes())==257 and data.read_bytes()==app.read_bytes()[0xbda90-0x27000:0xbdb91-0x27000]
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_native_ctype_window']==0xbda90
  machines=[]
  for source in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x10000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000)
   if source:u.mem_write(0xbda90,data.read_bytes())
   machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,value in [('pointer',x) for x in [0,1,0x80000000,0xffffffff]]+[('space',x) for x in [0xffffffff,*range(256)]]:
   results=[];symbol='r1_native_ctype_pointer' if kind=='pointer' else 'r1_native_isspace';native=0x275ec if kind=='pointer' else 0x275f4
   for candidate,u in enumerate(machines):
    u.reg_write(UC_ARM_REG_XPSR,0x01000000);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101);u.reg_write(UC_ARM_REG_R0,value)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((syms[symbol] if candidate else native)|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)]
    assert bytes(u.mem_read(0x20000000,0x3e000))==bytes(0x3e000)
    results.append(u.reg_read(UC_ARM_REG_R0))
   assert results[0]==results[1],(kind,value,results)
   if kind=='pointer':assert results[0]==0xbdb14
   elif value!=0xffffffff and value>=128 and results[0]:nonascii.append(value)
   counts[kind]+=1;digest.update(json.dumps([kind,value,results[0]]).encode())
 receipt=dict(comparisons=sum(counts.values()),counts=counts,trace_sha256=digest.hexdigest(),all_byte_inputs_and_eof=True,nonascii_indices_classified_as_space=nonascii,return_stack_callee_integer_and_nonstack_ram_checked=True,source_owned_data_bytes=257,raw_table_pointer_contract=True,source_owned_data_placed_at_authenticated_address=True,instruction_identity=False,application_sha256=sha(app),driver_sha256=sha(Path(__file__)),report_sha256=sha(rp),object_sha256=sha(obj),layout=str(layout.relative_to(ROOT)),layout_sha256=sha(layout),limitations=['Unchecked indices beyond EOF/byte input domain and descriptor/data aliasing remain open.','Neighbor lookup bytes overlap independently recovered numeric/configuration data; final shared placement remains unproven.','Full caller scratch/APSR/private frame, source startup, firmware and original instruction/image identity remain open.'])
 vp.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
