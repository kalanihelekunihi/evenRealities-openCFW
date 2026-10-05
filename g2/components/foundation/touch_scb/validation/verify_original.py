from pathlib import Path
import hashlib, struct
import capstone, unicorn
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
import json, sys
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
img=blob[32:32+0x8680]
assert hashlib.sha256(img).hexdigest()=='371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87'
BASE=0x3300; ADDR=0x9250; OFF=ADDR-BASE; STOP=0x10000000; SCB=0x20000000; DST=0x20001000; STACK=0x20002000
body=img[OFF:OFF+30]
assert hashlib.sha256(body).hexdigest()=='c7729e5dfb38b7391112b5eeeb9e0a8b0fc0d2ad0bc2e1e9b53b353b401e5e49'
md=capstone.Cs(capstone.CS_ARCH_ARM,capstone.CS_MODE_THUMB|capstone.CS_MODE_MCLASS)
ins=list(md.disasm(body,ADDR)); assert sum(i.size for i in ins)==30
u=unicorn.Uc(unicorn.UC_ARCH_ARM,unicorn.UC_MODE_THUMB|unicorn.UC_MODE_MCLASS)
u.mem_map(BASE & ~0xfff,0x10000); u.mem_write(BASE,img)
u.mem_map(0x20000000,0x10000);u.mem_map(STOP,0x1000)
# Keep first 56B callee as original bytes, but intercept its entry to observe args and return.
callee=img[0x5f18:0x5f18+56]
assert hashlib.sha256(callee).hexdigest()=='07627776d2bc275029e974a40d0944d6b87502cfea118880b8d60d6c3fa97cc7'
u.mem_write(STOP,bytes(4));u.mem_write(STOP+4,bytes(4))
calls=[]
trace=[]
active_case=-1
def hook(uc,addr,size,data):
 if addr==0x9218:
  args=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
  calls.append(args);trace.append(dict(case_index=active_case,pc=hex(addr),kind='callee_entry_stub',args=[hex(x) for x in args],stub_return='0xdecafbad'))
  uc.reg_write(UC_ARM_REG_R0,0xdecafbad);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  return
 assert ADDR<=addr<ADDR+30,hex(addr)
 fetched=bytes(uc.mem_read(addr,size))
 assert fetched==img[addr-BASE:addr-BASE+size],(hex(addr),size)
 decoded=list(md.disasm(fetched,addr));assert len(decoded)==1 and decoded[0].size==size
 trace.append(dict(case_index=active_case,pc=hex(addr),kind='original_wrapper_instruction',bytes=fetched.hex(),mnemonic=decoded[0].mnemonic,operands=decoded[0].op_str))
u.hook_add(unicorn.UC_HOOK_CODE,hook)
cases=[]
test_vectors=[(0,0,0),(0,5,0),(3,2,2),(3,9,3),(0x12340003,9,3),(0xffffffff,0x300,0x1ff),(3,3,3),(2,0xffffffff,2)]
for case_index,(status,requested,want) in enumerate(test_vectors):
 active_case=case_index
 trace_start=len(trace)
 # register at SCB+0x308
 u.mem_write(SCB+0x308,struct.pack('<I',status))
 u.reg_write(UC_ARM_REG_SP,STACK);u.reg_write(UC_ARM_REG_LR,STOP|1)
 for reg,val in [(UC_ARM_REG_R0,SCB),(UC_ARM_REG_R1,DST),(UC_ARM_REG_R2,requested)]:u.reg_write(reg,val)
 before=len(calls);u.emu_start(ADDR|1,STOP,count=1000)
 assert u.reg_read(UC_ARM_REG_PC)==STOP
 assert len(calls)==before+1
 got=calls[-1]
 assert got==[SCB,DST,want],(hex(status),requested,got,want)
 assert u.reg_read(UC_ARM_REG_R0)==want
 cases.append(dict(index=case_index,status=f'0x{status:08x}',requested=requested,available=status&0x1ff,expected_actual=want,callee_args=[hex(x) for x in got],return_value=u.reg_read(UC_ARM_REG_R0),trace=trace[trace_start:]))
disassembly=[dict(pc=hex(i.address),bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins]
script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
report=dict(status='PASS',script_path=str(Path(__file__).relative_to(ROOT)),script_sha256=script_sha256,firmware_path='g2/blobs/official/g2-2.2.6.10/firmware_touch.bin',firmware_sha256=hashlib.sha256(blob).hexdigest(),fwpk_image_sha256=hashlib.sha256(img).hexdigest(),runtime_base=hex(BASE),wrapper=dict(name='Cy_SCB_ReadArray',runtime_start=hex(ADDR),runtime_end_exclusive=hex(ADDR+30),image_range=[hex(OFF),hex(OFF+30)],payload_range=[hex(32+OFF),hex(32+OFF+30)],bytes=body.hex(),sha256=hashlib.sha256(body).hexdigest()),callee=dict(name='Cy_SCB_ReadArrayNoCheck',runtime_entry='0x9218',image_range=['0x5f18','0x5f50'],bytes=callee.hex(),sha256=hashlib.sha256(callee).hexdigest(),execution='stubbed at entry before first original callee instruction',stub_return='0xdecafbad (ignored by wrapper; wrapper returns actual count)'),interpreter=dict(python=sys.executable,unicorn=unicorn.__version__,capstone=capstone.__version__),disassembly=disassembly,cases=cases,case_count=len(cases),trace_event_count=len(trace),limits='Original wrapper instructions executed and byte-checked against authenticated image. Synthetic SCB+0x308 status; callee entry stub logs r0/r1/r2 and returns sentinel. No real MMIO/FIFO read or callee instruction executed.')
(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],case_count=report['case_count'],results=str(OUT/'results.json')),indent=2))
