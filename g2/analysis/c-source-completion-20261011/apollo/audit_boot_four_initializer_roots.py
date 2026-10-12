#!/usr/bin/env python3
"""Rebuild bounded four-record native/source runner and current ELF binding."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
OUT=HERE/'init-four-m4-oracle';OUT.mkdir(exist_ok=True)
SRC=ROOT/'g2/components/bootloader'
source_files=[SRC/'init_table/init_table.c',SRC/'init_table/qsort.c',
              SRC/'initializer_callbacks/callback_table.S']
objects=[]
for source in source_files:
 object=OUT/(source.stem+'.o');objects.append(object)
 command=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
          '-mfloat-abi=soft','-ffreestanding','-fno-builtin','-O2',
          '-ffunction-sections','-fdata-sections']
 if source.suffix=='.c':command+=['-std=c11','-fwrapv']
 subprocess.run(command+['-c',str(source),'-o',str(object)],check=True)
stock_callbacks=(0x4301d7,0x43194d,0x415591,0x41fd71)
names=('opencfw_boot_init_callback_platform_sequence',
       'opencfw_boot_init_callback_services',
       'opencfw_boot_init_callback_redirect','opencfw_boot_allocator_init')
bindings=dict(zip(names,stock_callbacks))
isolated=OUT/'init-four.elf'
subprocess.run(['arm-none-eabi-ld','--gc-sections',
 '-u','opencfw_boot_init_table_run','-u','opencfw_boot_init_priority_compare',
 '-T',str(OUT/'isolated.ld'),
 *(f'--defsym={name}={address:#x}' for name,address in bindings.items()),
 *(str(o) for o in objects),'-o',str(isolated)],check=True)
verify=OUT/'verify.json'
subprocess.run([sys.executable,str(SRC/'init_table/verify_init_table.py'),
 '--elf',str(isolated),'--output',str(verify)],check=True)
detail=json.loads(verify.read_text());assert detail['status']=='PASS'
stock=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
stock_table=stock[0x433440-0x410000:0x433460-0x410000]
with isolated.open('rb') as stream:
 elf=ELFFile(stream);section=elf.get_section_by_name('.boot_initializer_callbacks')
 assert section['sh_addr']==0x433440 and section.data()==stock_table
with (HERE/'boot-coplacement-spot-callback-identity-round/boot.elf').open('rb') as stream:
 elf=ELFFile(stream);syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name}
 address=syms['opencfw_boot_initializer_callback_records']
 segment=next(s for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_vaddr']<=address< s['p_vaddr']+s['p_filesz'])
 raw=segment.data()[address-segment['p_vaddr']:][:32]
 words=struct.unpack('<8I',raw)
 assert words[::2]==tuple(syms[name] for name in names)
 assert words[1::2]==(1,1,25,26)
current=json.loads((HERE/'boot-coplacement-spot-callback-identity-round/receipt.json').read_text())
assert all(current['source_sha256'][str(path.relative_to(ROOT))]==hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files)
receipt={
 'status':'PASS_BOUNDED_FOUR_INITIALIZER_ROOTS',
 'native_runner':'0x41f9f8','native_table':'0x433440..0x43345f',
 'native_scratch':'0x20022e00',
 'stock_table_sha256':hashlib.sha256(stock_table).hexdigest(),
 'isolated_compiled_table_exact':True,
 'isolated_compiled_source_runner_cases':detail['cases'],
 'isolated_compiled_source_qsort_cases':len(detail['qsort_cases']),
 'isolated_compiled_source_comparator_cases':len(detail['comparator_cases']),
 'isolated_oracle_elf_sha256':detail['elf_sha256'],
 'current_selected_table_address':hex(address),
 'current_selected_table_relocated_targets':[hex(w) for w in words[::2]],
 'current_selected_elf_sha256':hashlib.sha256((HERE/'boot-coplacement-spot-callback-identity-round/boot.elf').read_bytes()).hexdigest(),
 'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in source_files},
 'limits':['The four callback pointer identities and priority order are exact in the stock-coordinate isolated table; current selected ELF uses relocations to named source callbacks.',
           'The existing native/source runner oracle cuts callback bodies to record order and tests Cortex-M4/O2 selected C, not the selected Cortex-M55 linked runner.',
           'Current Boot ELF table has arbitrary source placement; final load placement, callback bodies, ROM and hardware remain separate gates.'],
}
(HERE/'boot-four-initializer-roots.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],detail['cases'],len(detail['qsort_cases']),len(detail['comparator_cases']))
