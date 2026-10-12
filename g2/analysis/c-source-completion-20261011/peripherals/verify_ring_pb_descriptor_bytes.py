#!/usr/bin/env python3
"""Check generated nanopb C fields/counts against authenticated ROM records."""
from hashlib import sha256
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[3]
ota=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
assert sha256(ota).hexdigest()=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
stock=ota[32:];base=0x438000
source=ROOT/'components/audio/uart_thread_source_candidate/display_ble_ring_pb_descriptor.c'
with tempfile.TemporaryDirectory() as tmp:
    obj=Path(tmp)/'descriptor.o'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb','-O2',
        '-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(source),'-o',str(obj)],check=True)
    with obj.open('rb') as f:
        elf=ELFFile(f)
        symbols={s.name:s for s in elf.get_section_by_name('.symtab').iter_symbols()}
        fields=descs=0;size=0
        for name,symbol in symbols.items():
            if not (name.startswith('ring_fields_') or name.startswith('audio_ble_ring_pb_desc_') or name=='audio_ble_ring_connect_pb_descriptor'):
                continue
            section=elf.get_section(symbol['st_shndx'])
            data=section.data()[symbol['st_value']:symbol['st_value']+symbol['st_size']]
            if name.startswith('ring_fields_'):
                address=int(name[-6:],16)
                pointer=int.from_bytes(stock[address-base:address-base+4],'little')
                assert data==stock[pointer-base:pointer-base+len(data)],(name,'fields')
                fields+=1;size+=len(data)
            elif len(data)==24:
                address=0x7766dc if name=='audio_ble_ring_connect_pb_descriptor' else int(name[-6:],16)
                assert data[8:24]==stock[address-base+8:address-base+24],(name,'counts')
                descs+=1
        assert fields==descs==20,(fields,descs)
        assert size==488,size
print('PASS_RING_PB_DESCRIPTOR_20_RECORDS_488_FIELD_BYTES')
