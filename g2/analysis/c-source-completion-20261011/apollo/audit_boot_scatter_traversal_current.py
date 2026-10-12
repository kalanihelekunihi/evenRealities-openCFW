#!/usr/bin/env python3
"""Bind native scatter traversal, source descriptors and 34 live callbacks."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
from elftools.elf.elffile import ELFFile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
STOCK=ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
ELF=HERE/'boot-coplacement-spot-callback-identity-round/boot.elf'
parser=argparse.ArgumentParser()
parser.add_argument('--elf',type=Path,default=ELF)
parser.add_argument('--receipt',type=Path,default=HERE/'boot-scatter-traversal-current.json')
args=parser.parse_args()
ELF=args.elf
SOURCE=ROOT/'g2/components/bootloader/startup/record_dispatch.c'
DATA=ROOT/'g2/components/bootloader/initializer_callbacks/pcm22_remaining_native/initialized_data.c'
RECORDS=ROOT/'g2/components/bootloader/startup/init_records.S'
spec=importlib.util.spec_from_file_location('startupv',ROOT/'g2/components/bootloader/startup/verify.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
stock=STOCK.read_bytes();assert hashlib.sha256(stock).hexdigest()==base.v.SHA
u32=lambda address:struct.unpack_from('<I',stock,address-0x410000)[0]
assert 0x4329bc+u32(0x4329bc)==0x4330d8
assert 0x4329c0+u32(0x4329c0)==0x433120
native_words=struct.unpack('<18I',stock[0x4330d8-0x410000:0x433120-0x410000])
callback_offsets=(0,24,40,56)
native_targets=[(0x4330d8+offset+native_words[offset//4])&0xffffffff for offset in callback_offsets]
assert native_targets==[0x431e39,0x415327,0x415327,0x415327]
assert 'while(cursor!=end)' in SOURCE.read_text()
assert 'opencfw_boot_init_records+18' in SOURCE.read_text()
assert 'if(record[1]==44u && record[2]==0x40u)' in DATA.read_text()
assert 'if(record[1]==1250u && record[2]==0x20000000u)' in DATA.read_text()
assert 'if(record[1]==96u && record[2]==0x20080000u)' in DATA.read_text()

with ELF.open('rb') as stream:
 elf=ELFFile(stream)
 symtab=elf.get_section_by_name('.symtab')
 syms={s.name:s['st_value'] for s in symtab.iter_symbols() if s.name}
 load=next(s for s in elf.iter_segments() if s['p_type']=='PT_LOAD' and s['p_filesz'] and s['p_vaddr']==0x410000)
 image=load.data()
 read=lambda address,size:image[address-0x410000:address-0x410000+size]
 address=syms['opencfw_boot_init_records']
 words=struct.unpack('<18I',read(address,72))
 actual_targets=[(address+off+words[off//4])&0xffffffff for off in callback_offsets]
 expected_targets=[syms['opencfw_boot_zero_adapter']]+[syms['opencfw_boot_expand_adapter']]*3
 assert actual_targets==expected_targets
 descriptor_differences=[off for off in range(4,72,4)
                         if off not in callback_offsets and words[off//4]!=native_words[off//4]]
 assert descriptor_differences==[0x1c,0x2c,0x3c]
 assert [words[off//4] for off in descriptor_differences]==[0,0,0]
 initialized=next(s['st_value'] for s in symtab.iter_symbols()
                  if s.name=='initialized' and s['st_size']==1372)
 source_bytes=read(initialized,1371)
 relocation_pairs=set()
 relocated_words=set()
 for section in elf.iter_sections():
  if section['sh_type'] not in ('SHT_REL','SHT_RELA'):continue
  names=elf.get_section(section['sh_link'])
  for relocation in section.iter_relocations():
   if relocation['r_info_type']==2:
    relocation_pairs.add((relocation['r_offset'],names.get_symbol(relocation['r_info_sym']).name))
    if initialized<=relocation['r_offset']<initialized+1371:
     relocated_words.add(relocation['r_offset']-initialized)

base.v.ENTRIES['expand_adapter']=0x415326
machine=base.Machine();machine.cpu.mem_write(0x20000000,b'\xa5'*1371)
machine.cpu.reg_write(base.v.a.UC_ARM_REG_R9,0)
assert machine.run('expand_adapter',[0x433104])['return']==0x433110
decoded=bytes(machine.cpu.mem_read(0x20000000,1371))
bindings=json.loads((HERE/'scatter-full-relocations-receipt.json').read_text())['bindings']
relocated=set()
for row in bindings:
 offset=int(row['offset'],16);name=row['symbol'];relocated.update(range(offset,offset+4))
 assert struct.unpack_from('<I',source_bytes,offset)[0]==syms[name]
 assert struct.unpack_from('<I',decoded,offset)[0]==int(row['stock_pointer'],16)
 assert (initialized+offset,name) in relocation_pairs
assert len(bindings)==34 and len(relocated)==136
all_relocated={i for off in relocated_words for i in range(off,off+4)}
assert all(a==b for i,(a,b) in enumerate(zip(source_bytes,decoded)) if i not in all_relocated)
assert len(relocated_words)==63 and set(int(row['offset'],16) for row in bindings)<=relocated_words
receipt={
 'status':'PASS_BOUNDED_SCATTER_TRAVERSAL_AND_RELOCATIONS',
 'native_dispatcher':'0x43299c','native_record_range':'0x4330d8..0x43311f',
 'native_callback_targets':[hex(value) for value in native_targets],
 'source_callback_targets':[hex(value) for value in actual_targets],
 'descriptor_words':18,'identical_noncallback_descriptor_words':11,
 'intentional_source_stream_offset_word_differences':[hex(v) for v in descriptor_differences],
 'initialized_bytes':1371,'exact_nonrelocated_bytes':1371-len(all_relocated),
 'all_relocated_words':len(relocated_words),
 'relocated_callback_words':len(bindings),'original_decoded_sha256':hashlib.sha256(decoded).hexdigest(),
 'current_selected_elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),
 'source_sha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in (SOURCE,DATA,RECORDS)},
 'limits':['Native traversal starts at 0x4330d8 and ends at 0x433120, using each relative callback and returned next-record pointer. The selected C loop uses the same 18-word bound and caller-relative callbacks.',
           'Three compressed stream offsets are deliberately zero in source records; selected adapter dispatches authenticated descriptors to source-owned ITCM, initialized SRAM and zero SRAM producers.',
           'Original decoded SRAM bytes match current source outside 63 source-owned relocation words; 34 of these are callback words. The other relocations include pointers to relocated logging, configuration and locale data.',
           'Native decoder execution is bounded and source compiler/runtime, final flash load placement, callback bodies and hardware behavior remain separate gates.'],
}
args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['exact_nonrelocated_bytes'],receipt['relocated_callback_words'])
