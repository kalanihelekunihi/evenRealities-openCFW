#!/usr/bin/env python3
"""Verify native thread-pool extents and link their C backing storage."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/pool-backing-round874';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/pool_backing_storage.c'
obj=out/'pool_backing_storage.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
native={'audio_uart_pool_names':(0x49168c,0x20071710,0xa0),
        'audio_uart_pool_stacks':(0x491690,0x20033558,0x8000),
        'audio_uart_pool_controls':(0x491694,0x2006d0bc,0x380),
        'audio_uart_pool_threads':(0x491698,0x200739dc,0x20),
        'audio_uart_pool_queue_control_mem':(0x77ccac+8,0x20072e98,0x50),
        'audio_uart_pool_queue_storage':(0x77ccac+16,0x203737c0,0xbb8)}
assert struct.unpack_from('<I',blob,0x491678-0x438000)[0]==0x77ccac
assert struct.unpack_from('<I',blob,0x491684-0x438000)[0]==0x75bd00
assert struct.unpack_from('<I',blob,0x77ccac+12-0x438000)[0]==0x50
assert struct.unpack_from('<I',blob,0x77ccac+20-0x438000)[0]==0xbb8
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,(cell,addr,size) in native.items():
  assert struct.unpack_from('<I',blob,cell-0x438000)[0]==addr,(name,hex(cell))
  sym=syms[name]
  assert sym['st_size']==size and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS',name
base=root/'build/c-firmware/pool-state-round873/apollo-main-pool-state-selected-source.o'
linked=out/'apollo-main-pool-backing-source.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(native)<=before and before-after==set(native) and not after-before
receipt={'round':874,'status':'PASS_NATIVE_THREAD_POOL_BACKING_EXTENTS',
         'component':'Apollo thread-pool source-owned RAM backing',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_pointer_cells':{k:{'cell':hex(c),'address':hex(a),'bytes':s} for k,(c,a,s) in native.items()},
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Absolute placement and initialization of 0x203737c0 backing RAM remain open',
                  'Remaining provider imports, full image placement, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_POOL_BACKING_EXTENTS',len(native),len(after))
