#!/usr/bin/env python3
"""Check Apollo dashboard-load C strings against native ROM literal targets."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/dashboard-load-strings-round866';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/dashboard_load_log_strings.c'
obj=out/'dashboard_load_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'path':0x50261c,'module':0x50262c,'source':0x502628,'function':0x502624,'none':0x5025e8,
       'e_absent':0x502620,'c_absent':0x502630,'e_open':0x502634,'c_open':0x502638,
       'e_seek_end':0x50263c,'c_seek_end':0x502640,'e_size':0x502644,'c_size':0x502648,
       'e_seek_set':0x50264c,'c_seek_set':0x502650,'e_read':0x502658,'c_read':0x50265c,
       'e_decode':0x502668,'c_decode':0x50266c,'e_success':0x502670,'c_success':0x502674}
addresses={'audio_uart_dashboard_'+k:struct.unpack_from('<I',blob,cell-0x438000)[0] for k,cell in cells.items()}
addresses['audio_uart_dashboard_mode']=0x5020ec
assert len(addresses)==22
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,addr in addresses.items():
  symbol=syms[name];compiled=elf.get_section(symbol['st_shndx']).data()[symbol['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[addr-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,addr,compiled,native)
base=root/'build/c-firmware/send-begin-strings-round865/apollo-main-send-begin-strings.o'
linked=out/'apollo-main-dashboard-load-strings.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(addresses)<=before and not set(addresses)&after
assert len(before-after)==22 and not after-before
receipt={'round':866,'status':'PASS_EXACT_NATIVE_STRING_CONTENTS','component':'Apollo dashboard loader diagnostics',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Loader buffers, product state, schema descriptor, and full runtime effects remain unresolved',
                  'Final ROM placement and whole image link remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_DASHBOARD_LOAD_NATIVE_STRINGS',len(addresses),len(after))
