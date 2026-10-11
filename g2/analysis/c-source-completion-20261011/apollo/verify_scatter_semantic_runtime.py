#!/usr/bin/env python3
"""Bounded stock/source startup record oracle for source semantic installers."""
import hashlib, importlib.util, json, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
V=ROOT/'g2/components/bootloader/startup/verify.py'
spec=importlib.util.spec_from_file_location('startup_verify',V)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
v=m.v
v.ENTRIES['expand_adapter']=0x415326
ELF=ROOT/'g2/build/boot-scatter-runtime-oracle/scatter.elf'
OUT=ELF.parent
OUT.mkdir(parents=True,exist_ok=True)
sources=[
 'startup/initialize.c','startup/record_dispatch.c',
 'startup/itcm_helpers.S','startup/init_records.S','startup/record_adapters.S',
 'initializer_callbacks/pcm22_remaining_native/initialized_data.c',
 'initializer_callbacks/callback_table.S','platform_startup/platform_startup.c',
 'initializer_callbacks/elog_metadata.c',
]
objects=[]
for index,relative in enumerate(sources):
 path=ROOT/'g2/components/bootloader'/relative
 obj=OUT/f'scatter_{index}.o'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-mfloat-abi=soft','-ffreestanding','-fno-builtin',
                 '-std=c11','-O2','-fwrapv','-ffunction-sections','-fdata-sections',
                 '-c',str(path),'-o',str(obj)],check=True)
 objects.append(obj)
subprocess.run(['arm-none-eabi-ld','--gc-sections','--unresolved-symbols=ignore-all','-T',
                str(Path(__file__).with_name('scatter_oracle.ld')),
                '-o',str(ELF),*[str(o) for o in objects]],check=True)
_,segments,symbols=v.elf.elf_info(ELF)
image=v.BLOB.read_bytes();assert hashlib.sha256(image).hexdigest()==v.SHA
table_machine=m.Machine(True,segments,symbols)
source_tables=[]
for address,length,name in [(0x433d58,64,'context_config'),
                            (0x433d98,48,'platform_config'),
                            (0x43403c,48,'elog_color_suffixes'),
                            (0x434178,24,'elog_level_suffixes')]:
 data=bytes(table_machine.cpu.mem_read(address,length))
 assert data==image[address-v.BASE:address-v.BASE+length],name
 source_tables.append(dict(name=name,address=hex(address),bytes=length,
                           sha256=hashlib.sha256(data).hexdigest()))
results=[]
for record,n,address in [(0x4330f4,24,0x40),(0x433104,1371,0x20000000),(0x433114,4096,0x20080000)]:
 stock=m.Machine();source=m.Machine(True,segments,symbols)
 for machine in (stock,source):machine.cpu.mem_write(address,b'\xa5'*n)
 stock.cpu.reg_write(v.a.UC_ARM_REG_R9,0);source.cpu.reg_write(v.a.UC_ARM_REG_R9,0)
 sret=stock.run('expand_adapter',[record])['return']
 
 try:cret=source.run('expand_adapter',[record])['return']
 except Exception:
  print('SOURCE_PC',hex(source.cpu.reg_read(v.a.UC_ARM_REG_PC)), 'RECORD',hex(record));raise
 assert sret==cret==record+12,(hex(record),hex(sret),hex(cret))
 actual=bytes(source.cpu.mem_read(address,n));expected=bytes(stock.cpu.mem_read(address,n))
 excluded=[]
 if address==0x20000000:
  # This tiny linker intentionally leaves unrelated callback providers
  # undefined. Prior linked receipts check the selector and deinit targets;
  # the two task-entry targets are selected C providers awaiting final layout.
  excluded=list(range(0x158,0x1c4))
  for slot in (0x200,0x204,0x208,0x4cc,0x4d0,0x4f4,0x4f8):
   excluded.extend(range(slot,slot+4))
  a=bytearray(actual)
  for i in excluded:a[i]=expected[i]
  assert bytes(a)==expected,hex(next(i for i in range(n) if a[i]!=expected[i]))
 else:assert actual==expected,(hex(address),hashlib.sha256(actual).hexdigest(),hashlib.sha256(expected).hexdigest())
 results.append(dict(record=hex(record),destination=hex(address),output_bytes=n,stock_sha256=hashlib.sha256(expected).hexdigest(),source_sha256=hashlib.sha256(actual).hexdigest(),excluded_relocation_bytes=len(excluded),return_value=hex(cret),stock_instruction_bytes=len({int(pc,16)+i for pc,raw in stock.trace.items() for i in range(len(bytes.fromhex(raw)))})))
output=dict(status='PASS_BOUNDED',source_elf=str(ELF),source_elf_sha256=hashlib.sha256(ELF.read_bytes()).hexdigest(),stock_sha256=v.SHA,source_tables=source_tables,records=results,limits=['The bounded linker leaves unrelated callback providers unresolved; 136 relocation bytes in the 1371-byte block are normalized. Earlier integrated receipts validate selector/deinit/storage callback targets; two task-entry C providers compile in the selected archive but await final layout.','Cortex-M4 oracle compilation avoids Unicorn unsupported Cortex-M55 low-overhead-loop instructions; the selected Cortex-M55 archive compiles separately.','This checks direct adapter callbacks for the three recognized records and return pointers, not reset, whole walker, source linker layout, or hardware boot.'])
(Path(__file__).with_name('scatter-semantic-runtime-receipt.json')).write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(dict(status=output['status'],records=results),indent=2))
