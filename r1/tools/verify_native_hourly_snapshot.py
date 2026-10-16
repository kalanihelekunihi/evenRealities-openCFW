#!/usr/bin/env python3
"""Native hourly snapshot including record/output aliases and raw return word."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-hourly-snapshot';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SP=0x2003d000;TABLE=0x20016648;D=0x20010000
def main():
 rp=OUT/'report.json';r=json.loads(rp.read_text());obj=OUT/'native_hourly_snapshot.o';assert sha(obj)==r['units'][0]['object_sha256'] and not r['units'][0]['undefined']
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 e=json.loads((OUT/'rea-bytes.json').read_text())['structuredContent'];n=e['normalized_result'];assert e['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and n['complete'] and bytes.fromhex(n['bytes_hex'])==app.read_bytes()[0x5ab6c-0x27000:0x5aba0-0x27000]
 digest=hashlib.sha256();total=0
 with tempfile.TemporaryDirectory(prefix='r1-hourly-') as tmp:
  d=Path(tmp);ld=d/'layout.ld';ld.write_text('SECTIONS { .records 0x20016648 (NOLOAD) : { *(.bss.r1.hourly.accumulators) } .text 0x1000000 : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }');elf=d/'test.elf';binary=d/'text.bin'
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'-e','r1_hr_hour_query',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-j','.text','-O','binary',str(elf),str(binary)],check=True)
  syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3};assert syms['r1_hourly_accumulators']==TABLE
  machines=[]
  for i in range(2):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x20000,0xc0000);u.mem_write(0x27000,app.read_bytes());u.mem_map(0x1000000,0x20000);u.mem_write(0x1000000,binary.read_bytes());u.mem_map(0x20000000,0x40000);machines.append(u)
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  for kind,hour,recordhour,count,value,alias in itertools.product([0,1,2,3,4,5,6,0xffffffff],[0,1,23,255,256,0xffffffff],[0,1,23,255],[0,1,65535],[0,0x12345678,0xffffffff],range(8)):
   at=TABLE+(kind if kind<6 else 0)*8
   outputs=[(D,D+8),(0,D+8),(D,0),(D,D),(at+2,D+8),(D,at+4),(at+4,D+8),(D,at)][alias];results=[]
   for side,u in enumerate(machines):
    u.mem_write(TABLE,struct.pack('<BBHI',recordhour,0xaa,count,value)*6);u.mem_write(D,b'\x96'*16);u.mem_write(SP-128,b'\xa5'*256)
    for reg,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3],[kind,hour,*outputs]):u.reg_write(reg,v)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12340000+i)
    u.reg_write(UC_ARM_REG_SP,SP);u.reg_write(UC_ARM_REG_LR,0x20000101);u.emu_start((syms['r1_hr_hour_query'] if side else 0x5ab6c)|1,0x20000100,count=1000)
    assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==SP and [u.reg_read(reg) for reg in saved]==[0x12340000+i for i in range(8)]
    results.append([u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(TABLE,48)).hex(),bytes(u.mem_read(D,16)).hex()])
   assert results[0]==results[1],(kind,hour,recordhour,count,value,alias,results)
   total+=1;digest.update(json.dumps([kind,hour,recordhour,count,value,alias,results[0]],sort_keys=True).encode())
 receipt=dict(comparisons=total,trace_sha256=digest.hexdigest(),report_sha256=sha(rp),object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),application_sha256=sha(app),evidence={p.name:sha(p) for p in OUT.glob('rea-*.json')},actual_query_body_no_fixtures=True,raw_r0_callee_sp_table_and_output_ram_checked=True,output_record_alias_and_fresh_count_checked=True,source_zero_record_bytes=48,producer_lifecycle_proven=False,full_private_frame_history_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
