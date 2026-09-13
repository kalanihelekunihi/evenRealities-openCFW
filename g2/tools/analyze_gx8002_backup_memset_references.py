# SPDX-License-Identifier: MIT
"""Conservative backup-image reference census; absence is not reachability proof."""
import json
import subprocess
from build_gx8002_backup_memset import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(path.read_bytes(), str(path))
    assert elf.contents(next(s for s in elf.sections if s['name'] == '.data')) == stock
    start, end = 0x49d04, 0x49da4
    runtime = 0x100113c4
    # Include the alternate stage-one loader and initialized SRAM. Direct
    # branches are checked only within the stage-two mapping; a loader branch
    # cannot be interpreted using that mapping.
    disassembly = subprocess.check_output([
        str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'),
        '-D', '--start-address=0x3b940', '--stop-address=0x4f9cc', str(path)
    ], text=True)
    branches = []
    indirect = []
    code = decode(disassembly)
    branch_ops = {'br', 'bsr', 'bt', 'bf', 'bez', 'bnez', 'bnezad', 'bhz', 'blz', 'bhsz', 'blsz'}
    for pc, (op, args, width) in code.items():
        if op in ('jmp', 'jsr'):
            indirect.append({'package_offset': pc, 'operation': op, 'operand': args})
        if op not in branch_ops:
            continue
        try:
            target = int(args.split(',')[-1].strip(), 0)
        except ValueError:
            continue
        if start <= target < end and not start <= pc < end:
            branches.append({'package_offset': pc, 'operation': op,
                             'target': target, 'interior': target != start})
    literals = []
    # Include unaligned words conservatively; limit interpretation to backup
    # initialized SRAM. Primary runtime overlaps are a different address space.
    for offset in range(0x3893c, 0x4f9cc - 3):
        value = int.from_bytes(stock[offset:offset + 4], 'little')
        if runtime <= value < runtime + end - start:
            literals.append({'package_offset': offset, 'value': value,
                             'interior': value != runtime})
    # First indirect transfer: unsigned range guard followed by a word table.
    # This describes the observed guarded path, not every possible entry into it.
    for pc, expected in {
        0x3c52c: ('subi', 'r3, r0, 7', 2),
        0x3c52e: ('cmphsi', 'r3, 18', 2),
        0x3c534: ('bt', '0x3c5e4', 2),
        0x3c536: ('lrw', 'r2, 0x1001295c', 2),
        0x3c538: ('ldr.w', 'r3, (r2, r3 << 2)', 4),
        0x3c53c: ('jmp', 'r3', 2),
    }.items():
        assert code[pc] == expected
    table_offset = 0x3b940 + 0x1001295c - 0x10003000
    targets = [int.from_bytes(stock[p:p+4], 'little')
               for p in range(table_offset, table_offset + 18 * 4, 4)]
    assert all(not runtime <= target < runtime + end - start for target in targets)
    observations = [{'transfer': 0x3c53c, 'table_package_offset': table_offset,
                     'targets': targets, 'no_memset_target_on_guarded_path': True,
                     'other_entry_paths_qualified': False}]
    for guard, branch, literal, load, transfer, count, address, index, base, dest, fallback in (
        (0x3c5a8, 0x3c5aa, 0x3c5ac, 0x3c5ae, 0x3c5b2, 19, 0x100129a4, 'r2', 'r1', 'r2', 0x3c61c),
        (0x3c636, 0x3c63a, 0x3c63c, 0x3c63e, 0x3c642, 19, 0x100129f0, 'r3', 'r2', 'r3', 0x3c650),
        (0x3c81c, 0x3c81e, 0x3c820, 0x3c822, 0x3c826, 10, 0x10012a64, 'r0', 'r3', 'r3', 0x3c8ee),
    ):
        assert code[guard] == ('cmphsi', f'{index}, {count}', 2)
        assert code[branch] == ('bt', hex(fallback), 2)
        assert code[literal] == ('lrw', f'{base}, {hex(address)}', 2)
        assert code[load] == ('ldr.w', f'{dest}, ({base}, {index} << 2)', 4)
        assert code[transfer] == ('jmp', dest, 2)
        offset = 0x3b940 + address - 0x10003000
        values = [int.from_bytes(stock[p:p+4], 'little')
                  for p in range(offset, offset + count * 4, 4)]
        assert all(not runtime <= value < runtime + end - start for value in values)
        observations.append({'transfer': transfer, 'table_package_offset': offset,
                             'targets': values, 'no_memset_target_on_guarded_path': True,
                             'other_entry_paths_qualified': False})
    return {'image_sha256': IMAGE_SHA, 'envelope': [start, end],
            'runtime_address': runtime, 'external_direct_branches': branches,
            'runtime_word_matches': literals, 'word_scan_interval': [0x3893c, 0x4f9cc],
            'unresolved_indirect_transfers': indirect, 'source_admitted': False,
            'guarded_table_observations': observations,
            'limits': ['Linear disassembly can decode literal pools as instructions.',
                       'Computed targets, loader control transfers and dynamically written pointers are not resolved.',
                       'No absent-reference claim establishes unreachable replacement tail.']}


if __name__ == '__main__':
    result = analyze()
    (ROOT / 'docs/research/gx8002-backup-memset-references.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
