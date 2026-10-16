#!/usr/bin/env python3
"""Locked ledger/native-call-site registration proof; REA boundary gap explicit."""
import csv,hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-send-registration';CELL=0x20006c20;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=OUT/'report.json';report=json.loads(rp.read_text());obj=Path(report['units'][0]['command'][-1]);assert sha(obj)==report['units'][0]['object_sha256']
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';ah=sha(app);assert ah=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';evidence={};ledger=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv';row=next(r for r in csv.DictReader(ledger.open()) if r['image']=='application' and int(r['entry'],16)==0x83448);assert int(row['end'],16)==0x83457 and int(row['size'])==16
 gap=OUT/'rea-boundary-gap.json';g=json.loads(gap.read_text());assert g['procedure']=='0x83448' and g['error']['code']=='invalid_request';evidence[gap.name]=sha(gap)
 for label,address,length in [('body',0x83448,20),('callsite',0x830a8,20)]:
  raw=subprocess.check_output(['curl','-fsS','--max-time','20','--unix-socket','/var/folders/mh/nz9vzlpn7kzff18f77pztg880000gn/T/ghidra-mcp-kalani/ghidra-11353.sock','http://localhost/read_memory?program=stock-r1-native-analysis.elf&address='+hex(address)+'&length='+str(length)]);assert bytes(json.loads(raw)['data'])==app.read_bytes()[address-0x27000:address-0x27000+length];p=OUT/('ghidra-'+label+'.json');p.write_bytes(raw);evidence[p.name]=sha(p)
 # Decode the Thumb BL at0x830b4 independently; do not infer a function from span alone.
 a,b=struct.unpack_from('<HH',app.read_bytes(),0x830b4-0x27000);sign=(a>>10)&1;i1=1^((b>>13)&1)^sign;i2=1^((b>>11)&1)^sign;offset=(sign<<24)|(i1<<23)|(i2<<22)|((a&1023)<<12)|((b&2047)<<1);offset-=((1<<25) if sign else 0);assert (a&0xf800)==0xf000 and (b&0xd000)==0xd000 and 0x830b8+offset==0x83448
 comparisons=0;success=0;failure=0
 with tempfile.TemporaryDirectory() as temp:
  d=Path(temp);ld=d/'layout.ld';elf=d/'test.elf';binary=d/'text.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--defsym=r1_protocol_send_hook='+hex(CELL),str(obj),'-o',str(elf)],check=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True);syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};machines=[]
  for _ in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,65536);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  callbacks=itertools.chain(range(65536),(0x10000,0x10001,0x80000000,0xffffffff,0x20000201,0x20000221,0x32409,0))
  for index,callback in enumerate(callbacks):
   old=(index*997)^0xdeadbeef;incoming=[(index*37)&0xffffffff,(index*71)&0xffffffff,(index*13)&0xffffffff];expected=[0 if callback else 0xffffffff,CELL if callback else incoming[0],*incoming[1:]];results=[]
   for candidate,u in enumerate(machines):
    u.mem_write(CELL-4,b'\x96'*12);u.mem_write(CELL,struct.pack('<I',old));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),[callback,*incoming]):u.reg_write(reg,value)
    for k,reg in enumerate(saved):u.reg_write(reg,0x12345600+k)
    u.emu_start((syms['r1_protocol_send_callback_set'] if candidate else 0x83448)|1,0x20000100,count=100);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+k for k in range(8)];regs=[u.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)];assert regs==expected,(index,callback,candidate,regs,expected);memory=bytes(u.mem_read(CELL-4,12));assert memory==b'\x96'*4+struct.pack('<I',callback or old)+b'\x96'*4;results.append((regs,memory))
   assert results[0]==results[1];comparisons+=1;success+=bool(callback);failure+=not callback
 vp.write_text(json.dumps(dict(comparisons=comparisons,successful_registrations=success,null_rejections=failure,null_preserves_previous=True,full_r0_r1_r2_r3_checked=True,rea_boundary_available=False,boundary_proof='Locked ownership row plus independently decoded native BL and exact Ghidra-MCP body bytes',ownership_row=row,ownership_sha256=sha(ledger),native_callsite='0x830b4',native_entry='0x83448',native_size=16,report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=ah,evidence=evidence,application_linked=False,instruction_identity=False,limitations=['REA does not define this procedure; no metadata edit or inferred REA ownership claim','Registration accepts any nonzero word; pointer validity, lifecycle, concurrency and physical transport remain gated']),indent=2)+'\n');print('Send registration:',comparisons,success,failure)
if __name__=='__main__':main()
