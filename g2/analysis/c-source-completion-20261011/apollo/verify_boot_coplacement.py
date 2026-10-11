#!/usr/bin/env python3
"""Audit a linked source Boot ELF with live callback symbol relocations."""
import hashlib
import argparse
import json
from pathlib import Path
import re
import struct
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, default=HERE / 'boot-coplacement-experiment/boot.elf')
parser.add_argument('--receipt', type=Path, default=HERE / 'boot-coplacement-receipt.json')
args = parser.parse_args()
ELF = args.elf
stock = (HERE.parents[3] / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
bindings = json.loads((HERE / 'scatter-full-relocations-receipt.json').read_text())['bindings']
with ELF.open('rb') as stream:
    elf = ELFFile(stream)
    symtab = elf.get_section_by_name('.symtab')
    symbols = {symbol.name: symbol['st_value'] for symbol in symtab.iter_symbols() if symbol.name}
    initializers = [symbol for symbol in symtab.iter_symbols()
                    if symbol.name == 'initialized' and symbol['st_size'] == 0x55c]
    assert len(initializers) == 1
    initializer = initializers[0]['st_value']
    loads = [segment for segment in elf.iter_segments() if segment['p_type'] == 'PT_LOAD'
             and segment['p_filesz']]
    assert len(loads) == 1
    load = loads[0]
    assert load['p_vaddr'] == 0x410000
    # Main starts at 0x438000; preserve its 32-byte OTA preamble coordinate.
    partition_bytes = 0x437fe0 - 0x410000
    assert load['p_filesz'] <= partition_bytes
    image = load.data()
    read32 = lambda address: struct.unpack_from('<I', image, address - 0x410000)[0]
    relocation_targets = set()
    for section in elf.iter_sections():
        if section['sh_type'] not in ('SHT_REL', 'SHT_RELA'):
            continue
        linked_symbols = elf.get_section(section['sh_link'])
        for relocation in section.iter_relocations():
            if relocation['r_info_type'] == 2:  # R_ARM_ABS32
                relocation_targets.add((relocation['r_offset'],
                                        linked_symbols.get_symbol(relocation['r_info_sym']).name))
    assert symbols['opencfw_boot_vectors'] == 0x410000
    assert read32(0x410000) == 0x2007fb00
    assert read32(0x410004) == symbols['opencfw_boot_reset_entry']
    irq_bindings = {int(index): row['source_symbol'] for index, row in
                    json.loads((HERE / 'boot-vector-census.json').read_text())
                    ['external_unique_handlers'].items()}
    for index in range(16, 256):
        stock_pointer = struct.unpack_from('<I', stock, index * 4)[0]
        expected = (symbols[irq_bindings[index]] if index in irq_bindings else
                    0 if stock_pointer == 0 else symbols['opencfw_boot_reserved_loop'])
        assert read32(0x410000 + index * 4) == expected, index
    relocated = []
    for binding in bindings:
        offset = int(binding['offset'], 16)
        symbol = binding['symbol']
        value = read32(initializer + offset)
        assert value == symbols[symbol], (symbol, hex(value), hex(symbols[symbol]))
        assert (initializer + offset, symbol) in relocation_targets
        assert 0x410000 <= (value & ~1) < 0x410000 + load['p_filesz']
        relocated.append({'offset': binding['offset'], 'symbol': symbol,
                          'linked_pointer': hex(value),
                          'stock_pointer': binding['stock_pointer']})
    assert len(relocated) == 34
    assert all(row['linked_pointer'] != row['stock_pointer'] for row in relocated)
    for index in (24, 25, 26):
        name = f'event_a_transition_sequence_{index}'
        assert symbols[name] != 0 and symbols[name] & 1
    assert len({symbols[f'event_a_transition_sequence_{i}'] for i in (24, 25, 26)}) == 3
    locale_pointer_fields = []
    for offset in [*range(0x518, 0x534, 4), 0x540, 0x544]:
        name = 'opencfw_boot_locale_empty'
        assert read32(initializer + offset) == symbols[name]
        assert (initializer + offset, name) in relocation_targets
        locale_pointer_fields.append({'offset': hex(offset), 'symbol': name,
                                      'linked_pointer': hex(symbols[name])})
    assert read32(initializer + 0x53c) == symbols['opencfw_boot_locale_decimal_point']
    assert (initializer + 0x53c, 'opencfw_boot_locale_decimal_point') in relocation_targets
    locale_pointer_fields.append({'offset': '0x53c',
                                  'symbol': 'opencfw_boot_locale_decimal_point',
                                  'linked_pointer': hex(symbols['opencfw_boot_locale_decimal_point'])})
    assert image[symbols['opencfw_boot_locale_empty'] - 0x410000:
                 symbols['opencfw_boot_locale_empty'] - 0x410000 + 1] == b'\0'
    assert image[symbols['opencfw_boot_locale_decimal_point'] - 0x410000:
                 symbols['opencfw_boot_locale_decimal_point'] - 0x410000 + 2] == b'.\0'
    callback_table = symbols['opencfw_boot_initializer_callback_records']
    initializer_callbacks = ('opencfw_boot_init_callback_platform_sequence',
        'opencfw_boot_init_callback_services', 'opencfw_boot_init_callback_redirect',
        'opencfw_boot_allocator_init')
    for index, name in enumerate(initializer_callbacks):
        assert read32(callback_table + index * 8) == symbols[name]
        assert (callback_table + index * 8, name) in relocation_targets
    assert [read32(callback_table + index * 8 + 4) for index in range(4)] == [1, 1, 25, 26]
    cmdq = symbols['opencfw_bl_cmdq_resources']
    assert image[cmdq - 0x410000:cmdq - 0x410000 + 480] == stock[0x430880 - 0x410000:0x430880 - 0x410000 + 480]
    mode_values = symbols['opencfw_boot_mode_values']
    assert image[mode_values - 0x410000:mode_values - 0x410000 + 8] == stock[0x434158 - 0x410000:0x434158 - 0x410000 + 8]
    mutex_attr = symbols['opencfw_boot_service_mutex_attributes']
    assert read32(mutex_attr) == symbols['opencfw_boot_service_mutex_name']
    assert (mutex_attr, 'opencfw_boot_service_mutex_name') in relocation_targets
    assert [read32(mutex_attr + i * 4) for i in range(1, 4)] == [0, 0x20026cb0, 80]
    name = symbols['opencfw_boot_service_mutex_name']
    assert image[name - 0x410000:name - 0x410000 + 10] == b'elogMutex\0'
    scatter = symbols['opencfw_boot_init_records']
    for offset, name in ((0, 'opencfw_boot_zero_adapter'),
                         (24, 'opencfw_boot_expand_adapter'),
                         (40, 'opencfw_boot_expand_adapter'),
                         (56, 'opencfw_boot_expand_adapter')):
        assert (scatter + offset + read32(scatter + offset)) & 0xffffffff == symbols[name]
    profile = symbols['opencfw_boot_shared_memory_profile']
    assert image[profile - 0x410000:profile - 0x410000 + 5] == stock[0x434024 - 0x410000:0x434024 - 0x410000 + 5]
    for name, stock_address in (('opencfw_boot_conditional_power_value', 0x434154),
                                ('opencfw_boot_sleep_fields_initial', 0x434160)):
        assert read32(symbols[name]) == struct.unpack_from('<I', stock, stock_address - 0x410000)[0]
    format_bytes = 0
    for name, stock_address in (('opencfw_nor_read_transfer_format', 0x431420),
                                ('opencfw_nor_write_transfer_format', 0x431468),
                                ('lfs_read_failure', 0x4317cc),
                                ('lfs_prog_failure', 0x43180c),
                                ('lfs_erase_failure', 0x432568)):
        original = stock[stock_address - 0x410000:]
        original = original[:original.index(b'\0') + 1]
        address = symbols[name]
        assert image[address - 0x410000:address - 0x410000 + len(original)] == original
        format_bytes += len(original)
    dfu_attributes = symbols['attributes']
    assert read32(dfu_attributes) == symbols['opencfw_boot_dfu_thread_name']
    assert (dfu_attributes, 'opencfw_boot_dfu_thread_name') in relocation_targets
    assert image[symbols['opencfw_boot_dfu_thread_name'] - 0x410000:
                 symbols['opencfw_boot_dfu_thread_name'] - 0x410000 + 4] == b'dfu\0'
    path = symbols['opencfw_update_path_4336e4']
    original_path = stock[0x4336e4 - 0x410000:]
    original_path = original_path[:original_path.index(b'\0') + 1]
    assert image[path - 0x410000:path - 0x410000 + len(original_path)] == original_path
    gpio = symbols['opencfw_boot_gpio_descriptors']
    assert image[gpio - 0x410000:gpio - 0x410000 + 97 * 12] == stock[0x42f674 - 0x410000:0x42f674 - 0x410000 + 97 * 12]
    diagnostic_source = (HERE.parents[3] / 'g2/components/bootloader/initializer_callbacks/startup_diagnostics.c').read_text()
    diagnostic_bindings = re.findall(r'/\* Stock 0x([0-9a-f]+)\. \*/\nconst char (\w+)\[\]', diagnostic_source)
    assert len(diagnostic_bindings) == 21
    diagnostic_bytes = 0
    for old, name in diagnostic_bindings:
        original = stock[int(old, 16) - 0x410000:]
        original = original[:original.index(b'\0') + 1]
        address = symbols[name]
        assert image[address - 0x410000:address - 0x410000 + len(original)] == original, name
        diagnostic_bytes += len(original)
    adc = symbols['opencfw_boot_adc_descriptor']
    assert image[adc - 0x410000:adc - 0x410000 + 8] == stock[0x43402c - 0x410000:0x43402c - 0x410000 + 8]
    for name, old in (('opencfw_boot_adc_power_initial', 0x434170),
                      ('opencfw_boot_adc_power_final', 0x434174)):
        assert read32(symbols[name]) == struct.unpack_from('<I', stock, old - 0x410000)[0]
    manager_attr = symbols['opencfw_boot_manager_attributes']
    assert read32(manager_attr) == symbols['opencfw_boot_manager_name']
    assert (manager_attr, 'opencfw_boot_manager_name') in relocation_targets
    assert image[symbols['opencfw_boot_manager_name'] - 0x410000:
                 symbols['opencfw_boot_manager_name'] - 0x410000 + 8] == b'manager\0'
    flash_mutex_attr = symbols['mutex_attributes']
    assert read32(flash_mutex_attr) == symbols['opencfw_boot_flash_mutex_name']
    assert (flash_mutex_attr, 'opencfw_boot_flash_mutex_name') in relocation_targets
    assert image[symbols['opencfw_boot_flash_mutex_name'] - 0x410000:
                 symbols['opencfw_boot_flash_mutex_name'] - 0x410000 + 12] == b'flash_mutex\0'
    assert read32(symbols['opencfw_boot_post_special_register_value']) == struct.unpack_from('<I', stock, 0x43419c - 0x410000)[0]
    required_async = ('idle_entry', 'opencfw_boot_timer_task',
                      'opencfw_boot_timer_callback_dispatcher',
                      'opencfw_bl_task_return', 'opencfw_boot_manager_task',
                      'opencfw_provider_42e53c', 'opencfw_boot_event_thread',
                      'opencfw_boot_event_timer_callback')
    for name in required_async:
        assert 0x410000 <= (symbols[name] & ~1) < 0x410000 + load['p_filesz'], name
    for stock_absolute in (0x4189ad, 0x419445, 0x41639b, 0x41b391,
                           0x42e645, 0x42e6f5, 0x417c62, 0x415732,
                           0x42dad0, 0x42dad4, 0x42dad8, 0x42dadc, 0x42dae0,
                           0x42dae4):
        assert struct.pack('<I', stock_absolute) not in image, hex(stock_absolute)
    receipt = {
        'status': 'PASS_BOUNDED_LINK',
        'elf_sha256': hashlib.sha256(ELF.read_bytes()).hexdigest(),
        'image_start': hex(load['p_vaddr']),
        'image_file_bytes': load['p_filesz'],
        'stock_file_bytes': len(stock),
        'partition_bytes_before_main_preamble': partition_bytes,
        'vector_stack': hex(read32(0x410000)),
        'vector_reset': hex(read32(0x410004)),
        'vector_words_checked': 256,
        'external_irq_source_handlers': len(irq_bindings),
        'initialized_object': hex(initializer),
        'callbacks_relocated_to_live_source_symbols': relocated,
        'locale_data_pointer_relocations': locale_pointer_fields,
        'source_initializer_callback_records': len(initializer_callbacks),
        'source_cmdq_data_bytes_compared': 480,
        'source_mode_values_bytes_compared': 8,
        'source_scatter_record_callbacks': 4,
        'source_shared_memory_profile_bytes_compared': 5,
        'source_startup_scalar_values_compared': 2,
        'source_diagnostic_format_bytes_compared': format_bytes,
        'source_dfu_attribute_relocations': 1,
        'source_gpio_descriptor_bytes_compared': 97 * 12,
        'source_startup_diagnostic_strings_compared': len(diagnostic_bindings),
        'source_startup_diagnostic_bytes_compared': diagnostic_bytes,
        'source_adc_config_bytes_compared': 16,
        'source_manager_and_flash_mutex_relocations': 2,
        'retained_async_source_roots': list(required_async),
        'limitations': [
            'A final ELF is co-placed inside the stock file occupied extent; all 256 vector words are checked structurally, but full IRQ behavior and source semantic equivalence are not established.',
            'Three resident ROM interfaces are linked to authenticated ROM entry addresses and remain physical platform contracts.',
            'Unreferenced selected archive functions may be garbage collected; reachability and all runtime code/data/scatter ownership remain incomplete.',
            'The former even absolute locale literals are now source symbols; other absolute references across the image still require a whole-image audit.'
        ],
    }
    args.receipt.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({key: receipt[key] for key in ('status', 'image_file_bytes', 'stock_file_bytes', 'vector_reset', 'initialized_object')}))
