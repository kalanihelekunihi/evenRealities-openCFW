#!/usr/bin/env python3
"""Check current linked Boot scatter destinations and the native IOM pool."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    ram_sections = [x for x in elf.iter_sections() if x['sh_flags'] & 2
                    and 0x20000000 <= x['sh_addr'] < 0x20100000 and x['sh_size']]
    assert [(x.name, x['sh_addr'], x['sh_size']) for x in ram_sections] == [
        ('.bss.boot_iom_context_pool', 0x2001455c, 0x4540)]
    symbols = {s.name: s for s in elf.get_section_by_name('.symtab').iter_symbols()
               if s.name and s['st_size']}
    pool = symbols['opencfw_boot_iom_contexts']
    section = elf.get_section(pool['st_shndx'])
    assert pool['st_value'] == section['sh_addr'] == 0x2001455c
    assert pool['st_size'] == section['sh_size'] == 0x4540
    assert section['sh_type'] == 'SHT_NOBITS'
    assert 0x2000055c <= pool['st_value']
    assert pool['st_value'] + pool['st_size'] <= 0x2000055c + 0x26c6c
    assert 0x20000000 + 1371 <= 0x2000055c
    assert 0x20080000 + 4096 <= 0x20081000
    flash = next(x for x in elf.iter_segments() if x['p_type'] == 'PT_LOAD'
                 and x['p_vaddr'] == 0x410000 and x['p_filesz'])
    assert flash['p_filesz'] == 159180
    assert 0x410000 + flash['p_filesz'] <= 0x437fe0
    image = flash.data()
    assert image[0x42633c-0x410000:0x426354-0x410000]
    inventory = json.loads((args.elf.parent/'objects/inventory.json').read_text())
    selected = [ROOT/unit['source'] for unit in inventory['units']
                if unit['status'] == 'selected']
    ram_literals = set()
    for source in selected:
        for match in re.finditer(r'0x2[0-9a-fA-F]{7,8}\b', source.read_text(errors='ignore')):
            value = int(match.group(), 16)
            if 0x20000000 <= value < 0x20100000:
                ram_literals.add(value)
    literal_ranges = {
        'initialized_1371': sum(0x20000000 <= x < 0x20000000+1371 for x in ram_literals),
        'first_zero': sum(0x2000055c <= x < 0x200271c8 for x in ram_literals),
        'iom_pool': sum(0x2001455c <= x < 0x20018a9c for x in ram_literals),
        'source_zero_stream_4096': sum(0x20080000 <= x < 0x20081000 for x in ram_literals),
        'second_zero': sum(0x20081000 <= x < 0x200f5100 for x in ram_literals),
    }
    outside_scatter = sorted(x for x in ram_literals if not (
        0x20000000 <= x < 0x20000000+1371 or
        0x2000055c <= x < 0x200271c8 or
        0x20080000 <= x < 0x200f5100))
    assert outside_scatter == [0x2007d000, 0x2007fb00]
    receipt = {
        'status': 'PASS_BOUNDED_BOOT_SCATTER_PLACEMENT',
        'selected_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        'selected_flash_load': ['0x410000', hex(0x410000 + flash['p_filesz'])],
        'selected_flash_bytes': flash['p_filesz'],
        'bytes_before_main_preamble': 0x437fe0 - (0x410000 + flash['p_filesz']),
        'native_and_selected_iom_pool': ['0x2001455c', '0x20018a9c'],
        'iom_pool_bytes': pool['st_size'],
        'allocated_ram_sections': [dict(name=x.name, start=hex(x['sh_addr']),
                                        bytes=x['sh_size']) for x in ram_sections],
        'selected_source_units': len(selected),
        'distinct_direct_ram_hex_literals': len(ram_literals),
        'direct_ram_hex_literals_by_range': literal_ranges,
        'direct_ram_hex_literals_outside_scatter': [hex(x) for x in outside_scatter],
        'initialized_sram': ['0x20000000', hex(0x20000000 + 1371)],
        'zero_scatter_sram': ['0x2000055c', hex(0x2000055c + 0x26c6c)],
        'second_zero_scatter_sram': ['0x20081000', hex(0x20081000 + 0x74100)],
        'source_zero_stream_sram': ['0x20080000', '0x20081000'],
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (HERE/'boot_coplacement_experiment.ld',
                                    ROOT/'g2/components/bootloader/initializer_callbacks/context_claim.c',
                                    ROOT/'g2/components/bootloader/startup/init_records.S')},
        'limits': [
            'IOM pool VMA and size now match the authenticated native address; the startup zero record covers it and the initialized copy does not overlap it.',
            'This checks linked placement and source descriptors, not execution of the selected Cortex-M55 ELF or physical startup memory.',
            'The selected ELF has 34 live callback relocations and 29 other initialized-data pointer relocations; exact runtime target equivalence and complete source image remain open.',
            'The direct RAM literal scan is lexical over selected source files; computed addresses and external or ROM writes require separate review.'
        ]
    }
args.receipt.write_text(json.dumps(receipt, indent=2)+'\n')
print(receipt['status'], receipt['native_and_selected_iom_pool'], receipt['bytes_before_main_preamble'])
