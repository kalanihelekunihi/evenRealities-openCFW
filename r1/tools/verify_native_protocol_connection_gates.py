#!/usr/bin/env python3
"""Exhaustive halfword presence predicates with native return registers."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-connection-gates';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=Path(report['units'][0]['command'][-1]);assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={}
 for addr in (0x4cbb0,0x4cb40):
  p=OUT/('rea-'+format(addr,'x')+'.json');p.write_bytes((BASE/'native-battery-runtime'/('rea-next-'+format(addr,'x')+'-body.json')).read_bytes());j=json.loads(p.read_text());assert j['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and j['normalized_result']['body']['total_bytes']==20;evidence[p.name]=sha(p)
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(addr)+'&length=24']);assert bytes(json.loads(raw)['data'])==app.read_bytes()[addr-0x27000:addr-0x27000+24];p=OUT/('ghidra-'+format(addr,'x')+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 comparisons=0;counts={}
 with tempfile.TemporaryDirectory() as temp:
  d=Path(temp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_connection_field8=0x200064ba','--defsym=r1_connection_field10=0x200064bc',str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for name,entry,cell in [('r1_authenticated_phone_connection_gate',0x4cbb0,0x200064ba),('r1_peer_channel_b_valid',0x4cb40,0x200064bc)]:
   counts[name]=0
   for handle in range(65536):
    seed=(handle*997)&0xffffffff;expected=[int(handle!=65535),(handle-65535)&0xffffffff,seed,seed^0xffffffff];results=[]
    for index,u in enumerate(machines):
     u.mem_write(0x200064b0,b'\xa5'*32);u.mem_write(cell,struct.pack('<H',handle));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
     for reg,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(seed^55,seed^99,seed,seed^0xffffffff)):u.reg_write(reg,v)
     for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
     u.emu_start((syms[name] if index else entry)|1,0x20000100,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==expected,(name,handle,index,regs,expected);results.append(bytes(u.mem_read(0x200064b0,32)))
    assert results[0]==results[1];comparisons+=1;counts[name]+=1
 vp.write_text(json.dumps(dict(comparisons=comparisons,counts=counts,all_handle_halfwords=True,full_r0_r1_r2_r3_checked=True,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['Presence predicates only: the historically named authenticated gate does not establish authentication','Existing connection fields reused; live transition ordering, canonical composition and hardware remain gated']),indent=2)+'\n');print('Connection presence gates:',comparisons,counts)
if __name__=='__main__':main()
