#!/usr/bin/env python3
"""Verify 43 ROM fault rows are relocatable source-owned C data."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/fault-code-table-round898';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/fault_code_table_6c8e60.c'
emitter=root/'analysis/c-source-completion-20261011/peripherals/emit_fault_code_table_round898.py'
subprocess.run(['python3',str(emitter)],check=True,capture_output=True,text=True)
obj=out/'fault_code_table_6c8e60.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
base=0x438000;start=0x6c8e60
rows=[]
for i in range(43):
 code,pad,ptr=struct.unpack_from('<HHI',blob,start-base+8*i)
 assert pad==0
 message=blob[ptr-base:ptr-base+256].split(b'\0')[0].decode('ascii')
 rows.append((code,message))
assert rows[-1][0]==0x2a and struct.unpack_from('<H',blob,start-base+43*8)[0]!=0x2b
with obj.open('rb') as f:
 elf=ELFFile(f);symtab=elf.get_section_by_name('.symtab')
 symbol=next(s for s in symtab.iter_symbols() if s.name=='audio_fault_code_table')
 assert symbol['st_size']==43*8
 section=elf.get_section(symbol['st_shndx'])
 data=section.data()[symbol['st_value']:symbol['st_value']+43*8]
 assert [struct.unpack_from('<HH',data,8*i)[0] for i in range(43)]==[r[0] for r in rows]
 assert all(struct.unpack_from('<HH',data,8*i)[1]==0 for i in range(43))
 reloc=[]
 for s in elf.iter_sections():
  if s['sh_type'] not in ('SHT_REL','SHT_RELA') or s['sh_info']!=symbol['st_shndx']:continue
  reloc.extend(r for r in s.iter_relocations()
               if symbol['st_value']<=r['r_offset']<symbol['st_value']+43*8)
 assert len(reloc)==43 and all(r['r_offset']==symbol['st_value']+8*i+4 for i,r in enumerate(reloc))
base_obj=root/'build/c-firmware/ring-command-validate-round897/apollo-main-ring-command-validate.o'
linked=out/'apollo-main-fault-code-table.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base_obj),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base_obj)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert before==after
receipt={'round':898,'status':'PASS_AUTHENTICATED_FAULT_CODE_TABLE',
         'component':'Apollo fault-code data at native 0x6c8e60',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'emitter':str(emitter.relative_to(root)),'emitter_sha256':hashlib.sha256(emitter.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_table_sha256':hashlib.sha256(blob[start-base:start-base+43*8]).hexdigest(),
         'rows':43,'pointer_relocations':len(reloc),
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Unknown-code native lookup beyond the 43-row table remains unmodeled',
                  'Fault handler 0x509b48, other Apollo imports, final placement and hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_AUTHENTICATED_FAULT_CODE_TABLE',len(rows),len(after))
