#!/usr/bin/env python3
"""Check source-owned halfword initializer and all getter input values."""
import hashlib,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 receipt=BASE/'connection-handle/verification.json';receipt.unlink(missing_ok=True);app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';report=BASE/'connection-handle/report.json';data=json.loads(report.read_text());obj=BASE/'connection-handle/connection_handle.o';assert sha(obj)==data['units'][0]['object_sha256']
 for path,digest in data['inputs'].items():assert sha(ROOT/path)==digest,path
 with tempfile.TemporaryDirectory() as directory:
  tmp=Path(directory);ld=tmp/'layout.ld';elf=tmp/'test.elf';binary=tmp/'test.bin';field=tmp/'field.bin';ld.write_text('SECTIONS { .text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } .r1.connection.field6 0x200064b8 : { *(.r1.connection.field6) } .r1.connection.field8 0x200064ba : { *(.r1.connection.field8) } .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);subprocess.run(['arm-none-eabi-objcopy','--dump-section','.r1.connection.field6='+str(field),str(elf)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_connection_field6']==0x200064b8
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB);stock.mem_map(0x20000,0xc0000);stock.mem_write(0x27000,app.read_bytes())
  for uc in (stock,candidate):uc.mem_map(0x1000000,0x10000);uc.mem_map(0x20000000,0x40000)
  stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208;assert bytes(stock.mem_read(0x200064b8,2))==field.read_bytes()==b'\xff\xff';candidate.mem_write(0x1000000,binary.read_bytes())
  getters=((6,0x200064b8,0x4cb28,'r1_conn_field6_get'),(8,0x200064ba,0x4cba4,'r1_phone_connection_handle_get'),(10,0x200064bc,0x4cb34,'r1_glasses_connection_handle_get'))
  for offset,address,stock_entry,name in getters:
   section='.r1.connection.field'+str(offset);subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(field),str(elf)],check=True);assert syms['r1_connection_field'+str(offset)]==address;assert bytes(stock.mem_read(address,2))==field.read_bytes()==b'\xff\xff'
  for offset,address,stock_entry,name in getters:
   for value in range(65536):
    for uc,entry in ((stock,stock_entry),(candidate,syms[name])):
     uc.mem_write(address-2,struct.pack('<3H',0x1234,value,0xabcd));uc.reg_write(UC_ARM_REG_SP,0x2003f000);uc.reg_write(UC_ARM_REG_LR,0x20000101);uc.reg_write(UC_ARM_REG_R0,0xffffffff);uc.emu_start(entry|1,0x20000100,count=1000);assert uc.reg_read(UC_ARM_REG_PC)==0x20000100;assert uc.reg_read(UC_ARM_REG_R0)==value
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(report),object_sha256=sha(obj),comparisons=196608,getter_count=3,initial_field_hex=field.read_bytes().hex() if field.exists() else 'ffff',scope='All three 16-bit getter values and unsigned widening; neighboring halfwords differ; source initializer matches stock scatter',limitations=['Only these three halfwords are source-owned; other connection fields and live connection transitions remain open.','Original instruction identity and physical BLE state remain unproven.'],instruction_identity_proven=False),indent=2)+'\n');print('196608 connection-handle comparisons passed')
if __name__=='__main__':main()
