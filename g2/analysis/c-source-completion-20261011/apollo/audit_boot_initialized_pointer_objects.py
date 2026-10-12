#!/usr/bin/env python3
"""Compare all 63 Boot initialized pointer words to native/source objects."""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
stock = (ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
spec = importlib.util.spec_from_file_location('startupv', ROOT/'g2/components/bootloader/startup/verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
assert hashlib.sha256(stock).hexdigest() == v.v.SHA
v.v.ENTRIES['expand_adapter'] = 0x415326
machine = v.Machine()
machine.cpu.mem_write(0x20000000, b'\xa5'*1371)
machine.cpu.reg_write(v.v.a.UC_ARM_REG_R9, 0)
assert machine.run('expand_adapter', [0x433104])['return'] == 0x433110
native = bytes(machine.cpu.mem_read(0x20000000, 1371))
bindings = {int(row['offset'], 16):row for row in
            json.loads((HERE/'scatter-full-relocations-receipt.json').read_text())['bindings']}
assert len(bindings) == 34

def data_group(off):
    if 0x31c <= off <= 0x330 and (off-0x31c)%4 == 0:
        return 'elog_level_suffix', 4, 'opencfw_boot_elog_level_suffixes'
    if 0x334 <= off <= 0x348 and (off-0x334)%4 == 0:
        return 'elog_color_suffix', 8, 'opencfw_boot_elog_color_suffixes'
    if off in (0x39c,0x3bc,0x3cc,0x3ec):
        return 'context_config_record', 16, 'opencfw_boot_context_config_records'
    if off in (0x478,0x494,0x4b0):
        return 'platform_config_record', 16, 'opencfw_boot_platform_config_table'
    if off in (0x518,0x51c,0x520,0x524,0x528,0x52c,0x530,0x540,0x544):
        return 'locale_empty', 1, 'opencfw_boot_locale_empty'
    if off == 0x53c:
        return 'locale_decimal_point', 2, 'opencfw_boot_locale_decimal_point'
    raise AssertionError(hex(off))

rows = []
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    symtab = elf.get_section_by_name('.symtab')
    initialized = next(s['st_value'] for s in symtab.iter_symbols()
                       if s.name == 'initialized' and s['st_size'] == 1372)
    flash = next(seg for seg in elf.iter_segments() if seg['p_type'] == 'PT_LOAD'
                 and seg['p_vaddr'] == 0x410000 and seg['p_filesz'])
    image = flash.data()
    relocations = {}
    for sec in elf.iter_sections():
        if sec['sh_type'] not in ('SHT_REL','SHT_RELA'):
            continue
        names = elf.get_section(sec['sh_link'])
        for rel in sec.iter_relocations():
            off = rel['r_offset']-initialized
            if 0 <= off < 1371 and rel['r_info_type'] == 2:
                assert off not in relocations
                relocations[off] = names.get_symbol(rel['r_info_sym'])
    assert len(relocations) == 63
    for off,sym in sorted(relocations.items()):
        src = struct.unpack_from('<I',image,initialized+off-0x410000)[0]
        nat = struct.unpack_from('<I',native,off)[0]
        assert 0x410000 <= nat < 0x410000+len(stock)
        if off in bindings:
            kind = ('transition_sequence_callback' if 0x158 <= off < 0x1c4 else
                    'storage_callback' if off in (0x200,0x204,0x208) else
                    'task_lifecycle_callback')
            assert sym.name == bindings[off]['symbol']
            assert nat == int(bindings[off]['stock_pointer'],16)
            assert src == sym['st_value'] and (src & 1) and (nat & 1)
            assert sym['st_info']['type'] == 'STT_FUNC'
            rows.append(dict(offset=hex(off),kind=kind,native_target=hex(nat),
                             source_target=hex(src),source_symbol=sym.name,
                             source_function_bytes=sym['st_size']))
        else:
            kind,extent,expected = data_group(off)
            assert sym.name == expected
            assert sym['st_info']['type'] == 'STT_OBJECT'
            addend = src-sym['st_value']
            assert 0 <= addend and addend+extent <= sym['st_size']
            assert nat+extent <= 0x410000+len(stock)
            native_data = stock[nat-0x410000:nat-0x410000+extent]
            source_data = image[src-0x410000:src-0x410000+extent]
            assert native_data == source_data
            rows.append(dict(offset=hex(off),kind=kind,native_target=hex(nat),
                             source_target=hex(src),source_symbol=sym.name,
                             source_object_bytes=sym['st_size'],source_addend=addend,
                             compared_bytes=extent,pointee_sha256=hashlib.sha256(native_data).hexdigest()))
assert len(rows) == 63
counts = {kind:sum(row['kind']==kind for row in rows) for kind in sorted(set(row['kind'] for row in rows))}
assert counts == {'context_config_record':4,'elog_color_suffix':6,'elog_level_suffix':6,
                  'locale_decimal_point':1,'locale_empty':9,'platform_config_record':3,
                  'storage_callback':3,'task_lifecycle_callback':4,'transition_sequence_callback':27}
receipt = {
    'status':'PASS_BOUNDED_INITIALIZED_POINTER_OBJECTS',
    'stock_sha256':hashlib.sha256(stock).hexdigest(),
    'selected_elf_sha256':hashlib.sha256(args.elf.read_bytes()).hexdigest(),
    'initialized_bytes':1371,'relocated_words':63,'data_pointer_words':29,
    'callback_pointer_words':34,'data_pointee_bytes_compared':sum(row.get('compared_bytes',0) for row in rows),
    'counts':counts,'rows':rows,
    'limits':[
        'The 29 data pointers are compared at their per-entry source-declared extents against stock flash bytes. Repeated locale-empty pointers are individually checked.',
        'The 34 callback pointers match the authenticated stock relocation binding inventory and linked named Thumb function symbols. Callback bodies and native consumers are not executed here.',
        'Native pointers come from an executed stock expansion adapter; selected source pointer words come from the current linked ELF. Final runtime placement, complete indirect caller discovery, ROM behavior and hardware remain open.'
    ]
}
args.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],receipt['relocated_words'],receipt['data_pointee_bytes_compared'])
