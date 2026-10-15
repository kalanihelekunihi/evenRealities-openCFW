#!/usr/bin/env python3
"""Verify sync timer diagnostics and same ROM entry aliases."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/sync-timer-strings-round868';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/sync_timer_log_strings.c';obj=out/'sync_timer_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-fshort-enums',
                '-std=c11','-ffreestanding','-fno-builtin','-O2','-Wall','-Wextra','-Werror',
                '-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'function':0x45dd40,'e_sem':0x45dd3c,'c_sem':0x45dd44,
       'e_create':0x45dd50,'c_create':0x45dd54,'e_start':0x45dd58,
       'c_start':0x45dd5c,'e_ok':0x45dd60,'c_ok':0x45dfcc}
addresses={'audio_uart_timer_'+k:struct.unpack_from('<I',blob,c-0x438000)[0] for k,c in cells.items()}
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,a in addresses.items():
  s=syms[name];compiled=elf.get_section(s['st_shndx']).data()[s['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[a-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,hex(a),compiled,native)
assert struct.unpack_from('<I',blob,0x45d7cc-0x438000)[0]==0x705fb8
assert struct.unpack_from('<I',blob,0x45d7d0-0x438000)[0]==0x77c07c
base=root/'build/c-firmware/mac-role-strings-round867/apollo-main-mac-role-strings.o'
linked=out/'apollo-main-sync-timer-strings.o'
subprocess.run(['arm-none-eabi-ld','-r',
                '--defsym=audio_uart_timer_source=audio_uart_begin0_source',
                '--defsym=audio_uart_timer_module=audio_uart_begin0_module',
                str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
resolved=set(addresses)|{'audio_uart_timer_source','audio_uart_timer_module'}
assert resolved<=before and not resolved&after and before-after==resolved and not after-before
symbols={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm','-a',str(linked)],text=True).splitlines() if len(x.split())==3 and x.split()[0].strip('0123456789abcdefABCDEF')==''}
assert symbols['audio_uart_timer_source']==symbols['audio_uart_begin0_source']
assert symbols['audio_uart_timer_module']==symbols['audio_uart_begin0_module']
receipt={'round':868,'status':'PASS_EXACT_NATIVE_TIMER_DIAGNOSTICS','component':'Apollo sync timeout timer',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'same_entry_aliases':{'source':'0x705fb8','module':'0x77c07c'},
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['CMSIS timer construction behavior and full image placement remain unresolved']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_SYNC_TIMER_NATIVE_DIAGNOSTICS',len(resolved),len(after))
