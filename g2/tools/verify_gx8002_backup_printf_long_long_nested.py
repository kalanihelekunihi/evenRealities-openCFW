# SPDX-License-Identifier: MIT
"""Execute wide digit conversion with decoded stock/source libgcc callees."""
import itertools
import json
import subprocess
from build_gx8002_backup_printf_long_long import build, ROOT, Elf32, sha, IMAGE_SHA
from build_gx8002_backup_unsigned_division import build as build_division
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_printf_long_long import execute, oracle, M
from verify_gx8002_double_pack_target import execute as arithmetic_execute


def verify():
    converter = build()
    division = build_division()
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    stock = Elf32(wrapper.read_bytes(), 'stock')
    payload = stock.contents(next(s for s in stock.sections if s['name'] == '.data'))
    assert sha(payload) == IMAGE_SHA
    source_path = ROOT / 'build/gx8002-backup-unsigned-division/division.elf'
    source = Elf32(source_path.read_bytes(), 'division')
    assert sha(source_path.read_bytes()) == division['elf_sha256']
    table = bytes(i.bit_length() for i in range(256))
    assert payload[0x4df14:0x4e014] == table
    assert source.contents(next(s for s in source.sections if s['name'] == '.bit_lengths')) == table
    memory = {0x100155d4 + i: b for i, b in enumerate(table)}
    old_outer = decode(subprocess.check_output([pre, '-D', '--start-address=0x41688',
                                               '--stop-address=0x41760', str(wrapper)], text=True))
    new_outer = decode((ROOT / 'build/gx8002-backup-printf/long-long.disassembly.txt').read_text())
    old_inner = decode(subprocess.check_output([pre, '-D', '--start-address=0x49ddc',
                                               '--stop-address=0x4a434', str(wrapper)], text=True))
    new_inner = decode(subprocess.check_output([pre, '-d', str(source_path)], text=True))
    delta = 0x10000000 - 0x38940
    counts = {}
    calls = {}
    values = (0, 1, 9, 10, 255, M, M + 1, (1 << 63) - 1, 1 << 63, (1 << 64) - 1)
    for outer_name, outer, entry, relocation in (('stock', old_outer, 0x41688, delta),
                                                ('source', new_outer, 0x10008d48, 0)):
        for inner_name, inner, inner_delta in (('stock', old_inner, delta), ('source', new_inner, 0)):
            key = outer_name + '_converter_' + inner_name + '_arithmetic'
            counts[key] = 0
            calls[key] = {'quotient': 0, 'remainder': 0}

            def arithmetic(target, numerator, denominator):
                name = 'quotient' if target == 0x1001149c else 'remainder'
                assert denominator in (2, 8, 10, 16)
                result = arithmetic_execute(inner, target - inner_delta, bytes(20),
                                            arguments=[numerator & M, numerator >> 32,
                                                       denominator & M, denominator >> 32],
                                            return_pair=True, readonly=memory)
                assert result == divmod(numerator, denominator)[name == 'remainder']
                calls[key][name] += 1
                return result

            for value, base, flags in itertools.product(values, (2, 8, 10, 16), (0, 32, 1024, 1056)):
                # Exercise sign and padding arguments while the downstream formatter remains modeled.
                args = (value, base, value & 1, 8, 16, flags)
                actual = execute(outer, entry, relocation, *args, arithmetic=arithmetic)
                assert actual == oracle(*args), (key, args, actual)
                counts[key] += 1
            assert all(calls[key].values())
    report = {'converter_build': converter, 'division_build': division,
              'stock_sha256': IMAGE_SHA, 'cases': counts, 'decoded_calls': calls,
              'source_admitted': False,
              'limits': ['Decoded arithmetic runs in separately marshaled interpreter frames; this is not a shared-memory whole-program execution.',
                         'Formatter/callback remain modeled. Finite values and bases; no floating formats, hardware execution or firmware admission.',
                         'Stock 32-byte digit-buffer truncation is preserved, including wide binary conversion.']}
    (ROOT / 'docs/research/gx8002-backup-printf-long-long-nested.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    result = verify()
    print(json.dumps({'cases': result['cases'], 'decoded_calls': result['decoded_calls']}, indent=2))
