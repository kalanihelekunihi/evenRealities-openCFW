#!/usr/bin/env python3
"""Verify timeout listener strings and shared ROM entry aliases."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/timeout-end-round872';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/timeout_end_log_strings.c'
obj=out/'timeout_end_log_strings.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
cells={'name_peer':0x45e000,'name_user':0x45e020,'name_slave':0x45e65c,
       'name_input':0x45e8b0,'name_display':0x45ebb0,'running_text':0x45e004,
       'compact':0x45e008,'submit_failed':0x45dff8,'submit_compact':0x45dffc}
addresses={'audio_uart_timeout_'+k:struct.unpack_from('<I',blob,c-0x438000)[0] for k,c in cells.items()}
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,a in addresses.items():
  s=syms[name];compiled=elf.get_section(s['st_shndx']).data()[s['st_value']:].split(b'\0',1)[0]+b'\0'
  native=blob[a-0x438000:].split(b'\0',1)[0]+b'\0'
  assert compiled==native,(name,hex(a),compiled,native)
# All three listener families use the same native source and module entry.
for cell in (0x45d7cc,0x45e010,0x45e8bc):
 assert struct.unpack_from('<I',blob,cell-0x438000)[0]==0x705fb8
for cell in (0x45d7d0,0x45e014,0x45e8c0):
 assert struct.unpack_from('<I',blob,cell-0x438000)[0]==0x77c07c
assert struct.unpack_from('<I',blob,0x45ebb8-0x438000)[0]==addresses['audio_uart_timeout_compact']
assert struct.unpack_from('<I',blob,0x45e654-0x438000)[0]==addresses['audio_uart_timeout_submit_compact']
base=root/'build/c-firmware/work-submit-round871/apollo-main-work-submit-source.o'
linked=out/'apollo-main-timeout-end-source.o'
aliases=[(f'audio_uart_timeout_{suffix}',f'audio_uart_begin0_{kind}')
         for suffix,kind in (('module','module'),('source','source'),
                             ('module_peer','module'),('source_peer','source'),
                             ('module_display','module'),('source_display','source'))]
aliases += [('audio_uart_timeout_compact_peer','audio_uart_timeout_compact'),
            ('audio_uart_timeout_compact_display','audio_uart_timeout_compact'),
            ('audio_uart_timeout_submit_compact_peer','audio_uart_timeout_submit_compact')]
subprocess.run(['arm-none-eabi-ld','-r',*[f'--defsym={a}={b}' for a,b in aliases],
                str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
provided=set(addresses)|{a for a,b in aliases}
resolved=provided & before
assert before-after==resolved and not after-before
assert provided<={x.split()[-1] for x in subprocess.check_output(
    ['arm-none-eabi-nm','-g','--defined-only',str(linked)],text=True).splitlines()
    if x.split()}
symbols={x.split()[-1]:int(x.split()[0],16) for x in subprocess.check_output(['arm-none-eabi-nm','-a',str(linked)],text=True).splitlines() if len(x.split())==3 and x.split()[0].strip('0123456789abcdefABCDEF')==''}
for a,b in aliases:assert symbols[a]==symbols[b],(a,b)
receipt={'round':872,'status':'PASS_EXACT_NATIVE_TIMEOUT_LISTENER_DIAGNOSTICS',
         'component':'Apollo sync timeout listeners',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'matched_strings':len(addresses),'same_entry_aliases':len(aliases),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Timeout queue and mutex RAM are still unresolved',
                  'Final image placement and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_TIMEOUT_LISTENER_NATIVE_DIAGNOSTICS',len(resolved),len(after))
