#!/usr/bin/env python3
"""Check persistent ring NOLOAD layout against the official Apollo image."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/ring-persist-backing-round875';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/ring_persist_backing_storage.c'
linker=root/'components/audio/uart_thread_source_candidate/ring_persist_noload.ld'
raw=out/'ring_persist_backing_storage.o';noload=out/'ring_persist_noload.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(raw)],check=True)
subprocess.run(['arm-none-eabi-ld','-r','-T',str(linker),str(raw),'-o',str(noload)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert (word(0x75d3d0),word(0x75d3cc))==(0x20004558,0x70af0)
zero_start,zero_end=0x20004558,0x20004558+0x70af0
native={'audio_uart_ring_persist_storage':(0x48ed74,0x200761f4,0x1000),
        'audio_uart_ring_persist_queue_state':(0x48ed78,0x200771f4,24),
        'audio_uart_ring_persist_event_pending':(0x47e290,0x20074ad0,4)}
for name,(cell,addr,size) in native.items():assert word(cell)==addr,(name,hex(cell))
assert native['audio_uart_ring_persist_storage'][1]==zero_end+0x11ac
assert native['audio_uart_ring_persist_queue_state'][1]==native['audio_uart_ring_persist_storage'][1]+0x1000
assert zero_start<=native['audio_uart_ring_persist_event_pending'][1]<zero_end
with noload.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 storage,queue,event=(syms[k] for k in native)
 for name,(cell,addr,size) in native.items():
  sym=syms[name]
  assert sym['st_size']==size and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS',name
 assert storage['st_shndx']==queue['st_shndx']
 assert queue['st_value']==storage['st_value']+storage['st_size']
 assert event['st_shndx']!=storage['st_shndx']
base=root/'build/c-firmware/pool-backing-round874/apollo-main-pool-backing-source.o'
linked=out/'apollo-main-ring-persist-backed.o'
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(noload),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
assert set(native)<=before and before-after==set(native) and not after-before
with linked.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 storage,queue=(syms[k] for k in ('audio_uart_ring_persist_storage','audio_uart_ring_persist_queue_state'))
 assert queue['st_shndx']==storage['st_shndx']
 assert queue['st_value']==storage['st_value']+0x1000
 assert elf.get_section(storage['st_shndx'])['sh_type']=='SHT_NOBITS'
receipt={'round':875,'status':'PASS_NATIVE_RING_PERSIST_NOLOAD_STORAGE',
         'component':'Apollo retained ring-persistence backing',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'linker_fragment':str(linker.relative_to(root)),'linker_sha256':hashlib.sha256(linker.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_pointer_cells':{k:{'cell':hex(c),'address':hex(a),'bytes':s} for k,(c,a,s) in native.items()},
         'startup_zero_range':[hex(zero_start),hex(zero_end)],
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Final linker script must honor NOLOAD and absolute contiguous 0x200761f4 storage',
                  'Other startup data records and hardware retention remain unverified',
                  'Remaining imports and whole-image placement remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_RING_PERSIST_NOLOAD',len(native),len(after))
