#!/usr/bin/env python3
"""Check Apollo MAC/role constants and source symbols against official ROM."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/mac-role-strings-round867';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/mac_role_log_strings.c'
obj=out/'mac_role_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'mac_source':0x4a3158,'mac_module':0x4a315c,'mac_e_hi':0x4a3530,
       'mac_function':0x4a3534,'mac_c_hi':0x4a3538,'mac_e_lo':0x4a353c,
       'mac_c_lo':0x4a3540,'mac_e_absent':0x4a3544,'mac_c_absent':0x4a3548,
       'role_function':0x45b0f8,'role_e_unstable':0x45b108,
       'role_c_unstable':0x45b10c,'role_e_stable':0x45b110,
       'role_c_stable':0x45b114}
addresses={'audio_uart_'+k:struct.unpack_from('<I',blob,cell-0x438000)[0] for k,cell in cells.items()}
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,addr in addresses.items():
  sym=syms[name];compiled=elf.get_section(sym['st_shndx']).data()[sym['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[addr-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,hex(addr),compiled,native)
 sym=syms['audio_uart_role_pin_config']
 compiled=elf.get_section(sym['st_shndx']).data()[sym['st_value']:sym['st_value']+4]
 native=blob[0x78ee44-0x438000:0x78ee48-0x438000]
 assert struct.unpack_from('<I',blob,0x45ade0-0x438000)[0]==0x78ee44
 assert compiled==native==struct.pack('<I',0x93)
base=root/'build/c-firmware/dashboard-load-strings-round866/apollo-main-dashboard-load-strings.o'
linked=out/'apollo-main-mac-role-strings.o'
aliases=['--defsym=audio_uart_role_module=audio_uart_begin0_module',
         '--defsym=audio_uart_role_source=audio_uart_begin0_source']
subprocess.run(['arm-none-eabi-ld','-r',*aliases,str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
resolved=set(addresses)|{'audio_uart_role_pin_config','audio_uart_role_module','audio_uart_role_source'}
assert resolved<=before and not resolved&after
assert len(before-after)==len(resolved) and not after-before
native_aliases={'audio_uart_role_module':0x77c07c,'audio_uart_role_source':0x705fb8}
assert struct.unpack_from('<I',blob,0x45b100-0x438000)[0]==native_aliases['audio_uart_role_module']
assert struct.unpack_from('<I',blob,0x45b0fc-0x438000)[0]==native_aliases['audio_uart_role_source']
symbols={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm','-a',str(linked)],text=True).splitlines() if len(x.split())==3 and x.split()[0].strip('0123456789abcdefABCDEF')==''}
assert symbols['audio_uart_role_module']==symbols['audio_uart_begin0_module']
assert symbols['audio_uart_role_source']==symbols['audio_uart_begin0_source']
receipt={'round':867,'status':'PASS_EXACT_NATIVE_MAC_ROLE_CONSTANTS','component':'Apollo ring MAC and role GPIO diagnostics',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'native_pin_config':hex(0x93),
         'same_entry_aliases':native_aliases,'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Product RAM, ROM placement, full image link, and runtime effects remain unresolved']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_MAC_ROLE_NATIVE_CONSTANTS',len(resolved),len(after))
