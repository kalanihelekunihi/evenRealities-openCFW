#!/usr/bin/env python3
"""Check native XIP font records and workspace source/linker contracts."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-config-round876';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_config_storage.c'
linker=root/'components/audio/uart_thread_source_candidate/ring_config_noload.ld'
raw=out/'ring_config_storage.o';noload=out/'ring_config_noload.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(raw)],check=True)
subprocess.run(['arm-none-eabi-ld','-r','-T',str(linker),str(raw),'-o',str(noload)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert (word(0x75d3d0),word(0x75d3cc))==(0x20004558,0x70af0)
native={'audio_uart_ring_config_idle':(0x46d60c,0x20074fe3,1),
        'audio_uart_ring_config_workspace':(0x46d610,0x20324600,0x5000),
        'audio_uart_ring_config_primary':(0x46d614,0x80100000,None),
        'audio_uart_ring_config_name':(0x46d630,0x20073e94,16),
        'audio_uart_ring_config_secondary':(0x46d640,0x80700000,None)}
for name,(cell,addr,size) in native.items():assert word(cell)==addr,(name,hex(cell))
zero_start,zero_end=0x20004558,0x20075048
for name in ('audio_uart_ring_config_idle','audio_uart_ring_config_name'):
 _,addr,size=native[name];assert zero_start<=addr and addr+size<=zero_end
assert native['audio_uart_ring_config_workspace'][1]>=zero_end
with noload.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name in ('audio_uart_ring_config_idle','audio_uart_ring_config_workspace','audio_uart_ring_config_name'):
  sym=syms[name];size=native[name][2]
  assert sym['st_size']==size and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS',name
 assert syms['audio_uart_ring_config_workspace']['st_shndx']!=syms['audio_uart_ring_config_name']['st_shndx']
base=root/'build/c-firmware/ring-persist-backing-round875/apollo-main-ring-persist-backed.o'
linked=out/'apollo-main-ring-config-source.o'
subprocess.run(['arm-none-eabi-ld','-r',
                '--defsym=audio_uart_ring_config_primary=0x80100000',
                '--defsym=audio_uart_ring_config_secondary=0x80700000',
                str(base),str(noload),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(native)<=before and before-after==set(native) and not after-before
symbol_rows={x.split()[-1]:(int(x.split()[0],16),x.split()[1]) for x in subprocess.check_output(['arm-none-eabi-nm','-g','--defined-only',str(linked)],text=True).splitlines() if len(x.split())==3}
for name in ('audio_uart_ring_config_primary','audio_uart_ring_config_secondary'):
 assert symbol_rows[name]==(native[name][1],'A'),name
with linked.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 sym=syms['audio_uart_ring_config_workspace']
 assert sym['st_size']==0x5000 and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS'
receipt={'round':876,'status':'PASS_NATIVE_XIP_FONT_CONFIG_CONTRACTS',
         'component':'Apollo XIP font configuration',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'linker_fragment':str(linker.relative_to(root)),'linker_sha256':hashlib.sha256(linker.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_pointer_cells':{k:{'cell':hex(c),'address':hex(a),'bytes':s} for k,(c,a,s) in native.items()},
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['External XIP records at 0x80100000 and 0x80700000 are referenced, not reconstructed',
                  'Final 0x20324600 workspace placement and external RAM initialization remain open',
                  'Remaining imports, whole-image placement, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_RING_CONFIG_CONTRACTS',len(native),len(after))
