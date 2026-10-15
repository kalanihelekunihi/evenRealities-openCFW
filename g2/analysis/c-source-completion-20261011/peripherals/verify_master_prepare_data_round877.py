#!/usr/bin/env python3
"""Verify native schedule-manager attributes and C diagnostic data."""
from pathlib import Path
import hashlib,json,struct,subprocess
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parents[3]
out=root/'build/c-firmware/master-prepare-data-round877';out.mkdir(parents=True,exist_ok=True)
src=root/'components/audio/uart_thread_source_candidate/master_prepare_data.c'
obj=out/'master_prepare_data.o'
subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
                '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
                '-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)],check=True)
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
word=lambda a:struct.unpack_from('<I',blob,a-0x438000)[0]
assert word(0x45da98)==0x200749d0 and word(0x45da9c)==0x77c184
assert word(0x45dc70)==0x75a878
assert word(0x45d7cc)==0x705fb8 and word(0x45d7d0)==0x77c07c
queue_native=[word(0x77c184+4*i) for i in range(6)]
thread_native=[word(0x75a878+4*i) for i in range(9)]
assert queue_native==[0x77c064,0,0x20072e48,0x50,0x2006eab8,0x258]
assert thread_native==[0x783c1c,0,0,0,0,0x1000,0x29,0,0]
cells={'function':0x45dc68,'e_queue':0x45dc64,'c_queue':0x45dc6c,
       'e_thread':0x45dc78,'c_thread':0x45dc7c,'e_ready':0x45dc80,
       'c_ready':0x45df10}
addresses={'audio_uart_master_'+k:word(c) for k,c in cells.items()}
with obj.open('rb') as f:
 elf=ELFFile(f);syms={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
 for name,a in addresses.items():
  sym=syms[name]
  data=elf.get_section(sym['st_shndx']).data()[sym['st_value']:].split(b'\0',1)[0]+b'\0'
  assert data==blob[a-0x438000:].split(b'\0',1)[0]+b'\0',(name,hex(a))
 for name,size in (('audio_uart_master_schedule_queue',4),
                   ('audio_uart_master_queue_control_mem',0x50),
                   ('audio_uart_master_queue_storage',0x258)):
  sym=syms[name]
  assert sym['st_size']==size and elf.get_section(sym['st_shndx'])['sh_type']=='SHT_NOBITS',name
 attr=syms['audio_uart_master_thread_attrs']
 assert attr['st_size']==36
 data=elf.get_section(attr['st_shndx']).data()[attr['st_value']:attr['st_value']+36]
 assert struct.unpack_from('<8I',data,4)==tuple(thread_native[1:])
 assert syms['audio_uart_master_queue_attrs']['st_size']==4
 all_data=b''.join(sec.data() for sec in elf.iter_sections() if sec['sh_type']=='SHT_PROGBITS')
 for addr in (0x77c064,0x783c1c):
  native=blob[addr-0x438000:].split(b'\0',1)[0]+b'\0'
  assert native in all_data
base=root/'build/c-firmware/ring-config-round876/apollo-main-ring-config-source.o'
linked=out/'apollo-main-master-data-source.o'
subprocess.run(['arm-none-eabi-ld','-r',
                '--defsym=audio_uart_master_module=audio_uart_begin0_module',
                '--defsym=audio_uart_master_source=audio_uart_begin0_source',
                str(base),str(obj),'-o',str(linked)],check=True)
before={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(base)],text=True).splitlines()}
after={x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm','-u',str(linked)],text=True).splitlines()}
resolved=set(addresses)|{'audio_uart_master_schedule_queue','audio_uart_master_queue_attrs',
                         'audio_uart_master_thread_attrs','audio_uart_master_module','audio_uart_master_source'}
assert resolved<=before and before-after==resolved and not after-before
assert 'audio_uart_master_scheduler_thread' in after
receipt={'round':877,'status':'PASS_NATIVE_SCHEDULE_MANAGER_SOURCE_DATA',
         'component':'Apollo schedule manager initialization',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),
         'native_string_addresses':{k:hex(v) for k,v in addresses.items()},
         'queue_attribute_words':[hex(x) for x in queue_native],
         'thread_attribute_words':[hex(x) for x in thread_native],
         'unresolved_before':len(before),'unresolved_after':len(after),
         'linked_object':str(linked.relative_to(root)),'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Scheduler thread body 0x45c058 remains unresolved',
                  'Final RAM/ROM placement, queue behavior, and hardware execution remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS_MASTER_PREPARE_DATA',len(resolved),len(after))
