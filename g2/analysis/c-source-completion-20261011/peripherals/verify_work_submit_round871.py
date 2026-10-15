#!/usr/bin/env python3
"""Verify thread-pool submit_work ROM diagnostics and selected C link."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/work-submit-round871';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/work_submit_log_strings.c'
obj=out/'work_submit_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'module':0x491628,'source':0x491624,'function':0x491638,
       'e_unready':0x491634,'c_unready':0x49163c,'e_null':0x491640,'c_null':0x491644,
       'e_submit':0x491648,'c_submit':0x49164c,'e_queue':0x491654,'c_queue':0x491658,
       'e_lock':0x49165c,'c_lock':0x491660}
addresses={'audio_uart_work_'+k:struct.unpack_from('<I',blob,c-0x438000)[0] for k,c in cells.items()}
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,a in addresses.items():
  sym=syms[name];compiled=elf.get_section(sym['st_shndx']).data()[sym['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[a-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,hex(a),compiled,native)
base=root/'build/c-firmware/corrected-user-response-round870/apollo-main-corrected-selected-source.o'
linked=out/'apollo-main-work-submit-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(addresses)<=before and before-after==set(addresses) and not after-before
receipt={'round':871,'status':'PASS_EXACT_NATIVE_WORK_SUBMIT_DIAGNOSTICS',
         'component':'Apollo thread-pool submit_work',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Thread-pool RAM, CMSIS queue identity, final image placement, and hardware execution remain unresolved']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_WORK_SUBMIT_NATIVE_DIAGNOSTICS',len(addresses),len(after))
