#!/usr/bin/env python3
"""Typed native module records and SDK color dispatch over original/mutated fields."""
import hashlib,itertools,json,struct,subprocess,tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-log-modules';rp=out/'report.json';r=json.loads(rp.read_text());obj=out/'log-modules.o';receipt=out/'verification.json';receipt.unlink(missing_ok=True);assert sha(obj)==r['selected_object_sha256']
 for p,d in r['inputs'].items():assert sha(ROOT/p)==d,p
 cp=out/'configuration-evidence.json';config=json.loads(cp.read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==config['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';comparisons=0;name_bytes=0
 with tempfile.TemporaryDirectory() as directory:
  t=Path(directory);ld=t/'layout.ld';elf=t/'test.elf';binary=t/'text.bin';ld.write_text('SECTIONS { .r1.log.modules 0xc441c : { *(.r1.log.modules) } '+''.join('.r1.log.module_name.'+str(row['index'])+' '+row['name_address']+' : { *(.r1.log.module_name.'+str(row['index'])+') } ' for row in config['rows'])+'.text 0x1000000 : { *(.text*) *(.rodata*) } .ARM.exidx : { *(.ARM.exidx*) } /DISCARD/ : { *(.comment) *(.note*) } }');subprocess.run(['arm-none-eabi-ld','-T',str(ld),'--entry=nrf_log_color_id_get',str(obj),'-o',str(elf)],check=True,capture_output=True);subprocess.run(['arm-none-eabi-objcopy','-O','binary','--only-section=.text',str(elf),str(binary)],check=True);syms={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(x.split())==3};assert syms['__start_log_const_data']==syms['r1_log_module_records']==0xc441c and syms['__stop_log_const_data']==0xc451c
  stock=Uc(UC_ARCH_ARM,UC_MODE_THUMB);candidate=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
  for u in (stock,candidate):u.mem_map(0x20000,0xc0000);u.mem_map(0x1000000,0x10000);u.mem_map(0x20000000,0x40000)
  stock.mem_write(0x27000,app.read_bytes());candidate.mem_write(0x1000000,binary.read_bytes())
  for section,a,z in [('.r1.log.modules',0xc441c,256)]+[('.r1.log.module_name.'+str(row['index']),int(row['name_address'],16),len(row['name'])+1) for row in config['rows']]:
   p=t/(str(a)+'.bin');subprocess.run(['arm-none-eabi-objcopy','--dump-section',section+'='+str(p),str(elf)],check=True);payload=p.read_bytes();assert len(payload)==z and payload==bytes(stock.mem_read(a,z)),section;candidate.mem_write(a,payload)
   if section!='.r1.log.modules':name_bytes+=z
  saved=[UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11]
  def compare(module,severity):
   nonlocal comparisons
   results=[]
   for u in (stock,candidate):
    u.reg_write(UC_ARM_REG_R0,module);u.reg_write(UC_ARM_REG_R1,severity);u.reg_write(UC_ARM_REG_SP,0x2003f000);u.reg_write(UC_ARM_REG_LR,0x20000101)
    for i,reg in enumerate(saved):u.reg_write(reg,0x12345600+i)
    u.emu_start((0x7965c if u is stock else syms['nrf_log_color_id_get'])|1,0x20000100,count=10000);assert u.reg_read(UC_ARM_REG_PC)==0x20000100 and u.reg_read(UC_ARM_REG_SP)==0x2003f000 and [u.reg_read(reg) for reg in saved]==[0x12345600+i for i in range(8)];results.append(u.reg_read(UC_ARM_REG_R0))
   assert results[0]==results[1],(module,severity,results);comparisons+=1
  for module,severity in itertools.product(range(32),list(range(8))+[255]):compare(module,severity)
  for module,value in itertools.product(range(32),range(256)):
   a=0xc441c+module*8+4
   for u in (stock,candidate):u.mem_write(a,bytes([value,255-value]))
   for severity in (1,2,3,4):compare(module,severity)
   for u in (stock,candidate):u.mem_write(a,bytes(2))
 receipt.write_text(json.dumps(dict(application_sha256=sha(app),report_sha256=sha(rp),configuration_evidence_sha256=sha(cp),comparisons=comparisons,records=32,record_bytes_compared=256,name_bytes_compared=name_bytes,scope='Unchanged SDK color lookup;32 typed records/names match native bytes, all color-byte values and error/warning precedence on bounded module IDs',limitations=['Record span and native start literal are authenticated; original end linker symbol/completeness beyond the span is not independently proven. Compiled aliases describe this source-owned array.','Out-of-range module IDs and enum values wider than8 bits are not admitted. Real calendar/pipeline/hardware and whole-image byte identity remain unresolved.'],instruction_identity_proven=False),indent=2)+'\n');print(comparisons,'module-color comparisons;',name_bytes,'name bytes')
if __name__=='__main__':main()
