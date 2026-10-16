#!/usr/bin/env python3
"""Verify pinned FAL readiness reads and recovered partition configuration."""
import hashlib,json,struct,subprocess,tempfile,shutil
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-fal-readiness';rp=out/'report.json';obj=out/'fal-readiness.o';r=json.loads(rp.read_text());receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['units'][0]['object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .bss.r1_fal_initialized 0x200077b1 (NOLOAD) : { *(.bss.r1_fal_initialized) } .text 0x1000000 : { *(.text*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }')
  subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=fal_init_check',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True)
  syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['r1_fal_initialized']==0x200077b1 and syms['r1_fal_is_initialized']==syms['fal_init_check']
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes());stock.reg_write(UC_ARM_REG_SP,0x2003f000);stock.emu_start(0x283a1,0x27208,count=2000000);assert stock.reg_read(UC_ARM_REG_PC)==0x27208 and bytes(stock.mem_read(0x200077b1,1))==b'\0'
  for value in range(256):
   for u in (stock,candidate):
    u.mem_write(0x200077b0,bytes([0x57,value,0x93]));u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)):u.reg_write(reg,0x12345600+i)
    u.emu_start((0x62fe8 if u is stock else syms['fal_init_check'])|1,0x20000100,count=100)
    assert u.reg_read(UC_ARM_REG_R0)==value and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and bytes(u.mem_read(0x200077b0,3))==bytes([0x57,value,0x93])
    assert [u.reg_read(reg) for reg in (UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)]==[0x12345600+i for i in range(8)]
  # Recover full constant records independently from the configured upstream C table.
  records=bytes(stock.mem_read(0x9c250,448));names=[]
  for i in range(7):
   magic,name,device,offset,length,reserved=struct.unpack('<I24s24sIII',records[i*64:(i+1)*64]);names.append((name.split(b'\0')[0].decode(),device.split(b'\0')[0].decode(),offset,length));assert magic==0x45503130 and reserved==0
  (out/'native-partitions.json').write_text(json.dumps(names,indent=2)+'\n')
  public_path=BASE/'public-providers/report.json';public=json.loads(public_path.read_text());part=BASE/'public-providers/flashdb-2.0.0-fal_partition.o';part_row=next(x for x in public['units'] if x['source'].endswith('/fal_partition.c'));assert sha(part)==part_row['object_sha256']
  for p,d in public['configuration'].items():assert sha(ROOT/p)==d,p
  table=t/'table.bin';part_copy=t/'partition.o';shutil.copyfile(part,part_copy);subprocess.run(['arm-none-eabi-objcopy','--dump-section','.rodata='+str(table),str(part_copy)],check=True);assert table.read_bytes()[:448]==records

 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),object_sha256=sha(obj),comparisons=256,cold_zero_bytes_compared=1,partition_record_bytes_decoded=448,compiled_partition_record_bytes_compared=448,public_report_sha256=sha(public_path),partition_object_sha256=sha(part),native_partition_decode_sha256=sha(out/'native-partitions.json'),scope='Unchanged upstream readiness byte getter, all 256 field values, source-owned cold byte, guards/registers; native partition decoding retained for subsequent configuration checks',limitations=['This does not select FAL initialization or lookup/assert/log paths.','All seven compiled constant partition records match stock, but live FAL registry initialization and assertion/log paths remain unresolved.','Complete image and instruction identity remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print('256 FAL readiness comparisons passed; 448 native partition bytes decoded')
if __name__=='__main__':main()
