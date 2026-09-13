# SPDX-License-Identifier: MIT
"""Relink recovered UART completion C at backup addresses; no source admission."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def build():
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    pre = str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-')
    out = ROOT / 'build/gx8002-backup-uart-completions'
    out.mkdir(parents=True, exist_ok=True)
    stock_path = ROOT / 'build/gx8002-board/padmux-get-stock.elf'
    elf = Elf32(stock_path.read_bytes(), str(stock_path))
    assert elf.contents(next(s for s in elf.sections if s['name'] == '.data')) == stock
    runtime = lambda offset: offset - 0x3b940 + 0x10003000
    rows = []
    for kind, offset, size, primary, helper, target in (
        ('transmit', 0x3c974, 32, 0xc650, 'uart_flush', 0x3cec4),
        ('receive', 0x3c994, 36, 0xc670, 'dma_complete_cache', 0x3d850),
    ):
        source = ROOT / ('components/shared/gx8002/runtime_gx8002_uart_' + kind + '_complete.c')
        symbol = 'open_cfw_gx8002_uart_' + kind + '_complete'
        obj = out / (kind + '.o')
        subprocess.run([pre + 'gcc', '-Os', *FLAGS[1:], '-c', str(source), '-o', str(obj)], check=True)
        script = out / (kind + '.ld')
        script.write_text('SECTIONS { .text %#x : { *(.text.%s) } }\n'
                          'open_cfw_gx8002_dma_release = %#x;\nopen_cfw_gx8002_%s = %#x;\n'
                          % (runtime(offset), symbol, runtime(0x3d5bc), helper, runtime(target)))
        path = out / (kind + '.elf')
        subprocess.run([pre + 'ld', '-T', str(script), str(obj), '-o', str(path)], check=True)
        elf = Elf32(path.read_bytes(), str(path))
        section = next(s for s in elf.sections if s['name'] == '.text')
        body = elf.contents(section)
        assert len(body) <= size and not elf.relocations(section['index'])
        assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
        decoded = []
        for start in (primary, offset):
            code = decode(subprocess.check_output([pre + 'objdump', '-D',
                '--start-address=' + hex(start), '--stop-address=' + hex(start + size), str(stock_path)], text=True))
            decoded.append([(pc-start, op, '<direct-call>' if op == 'bsr' else args, width)
                            for pc, (op, args, width) in sorted(code.items())])
        assert decoded[0] == decoded[1], 'Non-call instruction mismatch'
        (out / (kind + '.disassembly.txt')).write_text(subprocess.check_output([pre + 'objdump', '-d', str(path)], text=True))
        rows.append({'symbol': symbol, 'package_offset': offset, 'runtime_address': runtime(offset),
                     'source_sha256': sha(source.read_bytes()), 'compiled_bytes': len(body),
                     'compiled_sha256': sha(body), 'stock_envelope_bytes': size,
                     'stock_sha256': sha(stock[offset:offset+size]),
                     'primary_instruction_structure_matches': True})
    return {'functions': rows, 'source_admitted': False, 'limits': [
        'Direct-call destinations are mapped from backup disassembly; callee equivalence remains separate.',
        'Callback registration, decoded candidate behavior and replacement placement require qualification.']}


if __name__ == '__main__':
    result = build()
    (ROOT / 'docs/research/gx8002-backup-uart-completions-candidate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
