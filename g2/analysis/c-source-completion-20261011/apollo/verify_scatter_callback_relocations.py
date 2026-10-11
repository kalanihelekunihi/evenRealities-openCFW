#!/usr/bin/env python3
"""Compare all 34 source-owned Boot callback relocations at stock addresses.

The bounded linker binds each selected provider symbol to its authenticated
original address. This checks the source data layout and pointer ownership;
it does not prove that a final loadable source image places functions there.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
V = ROOT / 'g2/components/bootloader/startup/verify.py'
spec = importlib.util.spec_from_file_location('startup_verify', V)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
v = m.v
v.ENTRIES['expand_adapter'] = 0x415326

sequence = [
    'event_a_pcm22_transition_sequence_0', 'opencfw_spot_pcm22_transition1',
    'event_a_pcm22_transition_sequence_2', 'opencfw_spot_pcm22_transition3',
    'opencfw_spot_pcm22_transition4', 'opencfw_spot_pcm22_transition5',
    'opencfw_spot_pcm22_transition6', 'opencfw_spot_pcm22_transition7',
    'event_a_transition_sequence_8_timer_native', 'opencfw_spot_pcm22_transition9',
    'opencfw_spot_pcm22_transition10', 'opencfw_spot_pcm22_transition11',
    'opencfw_spot_pcm22_transition12', 'opencfw_spot_pcm22_transition13',
    'opencfw_spot_pcm22_transition14', 'opencfw_spot_pcm22_transition15',
    'opencfw_spot_pcm22_transition16', 'opencfw_spot_pcm22_transition17',
    'opencfw_spot_pcm22_transition18', 'opencfw_spot_pcm22_transition19',
    'opencfw_spot_pcm22_transition20', 'opencfw_spot_pcm22_transition21',
    'opencfw_spot_pcm22_transition22', 'opencfw_spot_pcm22_transition23',
    'event_a_transition_sequence_24', 'event_a_transition_sequence_25',
    'event_a_transition_sequence_26',
]
extra = {
    0x200: 'opencfw_boot_storage_read',
    0x204: 'opencfw_boot_storage_program',
    0x208: 'opencfw_boot_storage_erase_validate',
    0x4cc: 'opencfw_boot_dfu_thread_init',
    0x4d0: 'opencfw_boot_dfu_thread_deinit_native',
    0x4f4: 'opencfw_boot_main_callback',
    0x4f8: 'opencfw_boot_manager_thread_deinit',
}
assert len(sequence) + len(extra) == 34

stock = m.Machine()
stock.cpu.mem_write(0x20000000, b'\xa5' * 1371)
stock.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
assert stock.run('expand_adapter', [0x433104])['return'] == 0x433110
expected = bytes(stock.cpu.mem_read(0x20000000, 1371))
bindings = {0x158 + 4 * index: name for index, name in enumerate(sequence)} | extra
providers = json.loads((HERE / 'boot-source-audit-build/inventory.json').read_text())['global_weak_providers']
for offset, name in bindings.items():
    assert name in providers, (hex(offset), name)
    pointer = struct.unpack_from('<I', expected, offset)[0]
    assert pointer & 1, (hex(offset), hex(pointer))
    if name.startswith('event_a_transition_sequence_2'):
        assert pointer == {24: 0x42a031, 25: 0x42a033, 26: 0x42a035}[int(name[-2:])]

out = HERE / 'boot-scatter-full-relocations'
out.mkdir(exist_ok=True)
sources = [
    'startup/initialize.c', 'startup/record_dispatch.c',
    'startup/itcm_helpers.S', 'startup/init_records.S',
    'startup/record_adapters.S',
    'initializer_callbacks/pcm22_remaining_native/initialized_data.c',
    'initializer_callbacks/callback_table.S',
    'platform_startup/platform_startup.c',
    'initializer_callbacks/elog_metadata.c',
]
objects = []
for index, relative in enumerate(sources):
    path = ROOT / 'g2/components/bootloader' / relative
    obj = out / f'scatter_{index}.o'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-mfloat-abi=soft', '-ffreestanding', '-fno-builtin', '-std=c11',
                    '-O2', '-fwrapv', '-ffunction-sections', '-fdata-sections',
                    '-c', str(path), '-o', str(obj)], check=True)
    objects.append(obj)
address_by_name = {name: struct.unpack_from('<I', expected, offset)[0]
                   for offset, name in bindings.items()}
assert len(address_by_name) == 34
# These two bytestrings are now separate source data definitions. The bounded
# stock-address comparison binds them to their authenticated native literals;
# the co-placement experiment instead links the actual source definitions.
assert v.BLOB.read_bytes()[0x417c62-v.BASE:0x417c63-v.BASE] == b'\0'
assert v.BLOB.read_bytes()[0x415732-v.BASE:0x415734-v.BASE] == b'.\0'
address_by_name.update({'opencfw_boot_locale_empty': 0x417c62,
                        'opencfw_boot_locale_decimal_point': 0x415732})
# Link the three trivial native callback bodies at their distinct original
# halfword entries. The selected archive uses separate 4-byte-aligned input
# sections; SUBALIGN(2) gives the final linker a valid six-byte placement.
callback_source = ROOT / 'g2/components/bootloader/source_candidate_20261010/event_a_sequence24.c'
callback_obj = out / 'callbacks_24_26.o'
callback_elf = out / 'callbacks_24_26.elf'
callback_ld = out / 'callbacks_24_26.ld'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-mfpu=fpv5-sp-d16', '-mfloat-abi=softfp', '-O2',
                '-ffreestanding', '-ffunction-sections', '-c',
                str(callback_source), '-o', str(callback_obj)], check=True)
callback_ld.write_text('SECTIONS { . = 0x42a030; .text : SUBALIGN(2) { '
                       '*(.text.event_a_transition_sequence_24) '
                       '*(.text.event_a_transition_sequence_25) '
                       '*(.text.event_a_transition_sequence_26) } '
                       '/DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }\n')
subprocess.run(['arm-none-eabi-ld', '-T', str(callback_ld), '-o',
                str(callback_elf), str(callback_obj)], check=True)
with callback_elf.open('rb') as stream:
    callback_image = ELFFile(stream)
    callback_symbols = {s.name: s['st_value'] for s in
                        callback_image.get_section_by_name('.symtab').iter_symbols()}
    callback_bytes = callback_image.get_section_by_name('.text').data()
assert callback_bytes == bytes.fromhex('704770477047')
for index in (24, 25, 26):
    name = f'event_a_transition_sequence_{index}'
    assert callback_symbols[name] == 0x42a031 + 2 * (index - 24)
assert callback_bytes == v.BLOB.read_bytes()[0x42a030-v.BASE:0x42a036-v.BASE]
elf = out / 'scatter.elf'
subprocess.run(['arm-none-eabi-ld', '--gc-sections',
                '--unresolved-symbols=ignore-all',
                *[f'--defsym={name}=0x{address:x}' for name, address in address_by_name.items()],
                '-T', str(HERE / 'scatter_oracle.ld'), '-o', str(elf),
                *[str(obj) for obj in objects]], check=True)
_, segments, symbols = v.elf.elf_info(elf)
source = m.Machine(True, segments, symbols)
source.cpu.mem_write(0x20000000, b'\xa5' * 1371)
source.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
assert source.run('expand_adapter', [0x433104])['return'] == 0x433110
actual = bytes(source.cpu.mem_read(0x20000000, 1371))
assert actual == expected, next((hex(i), hex(a), hex(b)) for i, (a, b) in
                               enumerate(zip(actual, expected)) if a != b)
receipt = {
    'status': 'PASS_BOUNDED',
    'stock_sha256': v.SHA,
    'source_elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    'source_data_sha256': hashlib.sha256(actual).hexdigest(),
    'stock_data_sha256': hashlib.sha256(expected).hexdigest(),
    'initialized_bytes_compared': len(actual),
    'callback_relocations_compared': len(bindings),
    'normalized_bytes': 0,
    'placed_callback_fragment': {'start': '0x42a030', 'bytes': callback_bytes.hex(),
                                 'source_elf_sha256': hashlib.sha256(callback_elf.read_bytes()).hexdigest(),
                                 'native_entries': ['0x42a031', '0x42a033', '0x42a035']},
    'bindings': [{'offset': hex(offset), 'symbol': name,
                  'stock_pointer': hex(address_by_name[name]),
                  'provider': providers[name]['source']}
                 for offset, name in sorted(bindings.items())],
    'limits': ['Bounded linker assigns selected provider symbols their authenticated stock addresses. This proves exact source-initialized data bytes under that placement, not final loadable source function placement or callback behavior.',
               'The direct scatter adapter runs in a Cortex-M4 emulator; the selected firmware archive compiles for Cortex-M55 separately.'],
}
(HERE / 'scatter-full-relocations-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print('PASS_BOOT_SCATTER_CALLBACK_RELOCATIONS', len(actual), len(bindings))
