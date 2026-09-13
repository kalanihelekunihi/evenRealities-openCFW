# SPDX-License-Identifier: MIT
"""Qualify exact source-built backup UART transmit completion instructions."""
import json
import shutil
import subprocess
from verify_gx8002_backup_uart_completions import verify as compare
from verify_gx8002_backup_memset_loader import execute
from build_gx8002_backup_uart_completions import ROOT, IMAGE, IMAGE_SHA, sha, Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths


def verify(prefix=None, sdk=None, output=None):
    check_paths(prefix, sdk)
    comparison = compare()
    row = comparison['candidate']['functions'][0]
    path = ROOT / 'build/gx8002-backup-uart-completions/transmit.elf'
    elf = Elf32(path.read_bytes(), str(path))
    allocated = [s for s in elf.sections if s['flags'] & 2 and s['size']]
    assert len(allocated) == 1
    section = allocated[0]
    stock = IMAGE.read_bytes()
    assert sha(stock) == IMAGE_SHA
    body = elf.contents(section)
    assert section['name'] == '.text' and section['address'] == 0x10004034
    assert body == stock[0x3c974:0x3c994] and len(body) == 32
    assert not any(elf.relocations(s['index']) for s in elf.sections)
    assert not any(s['name'] and s['section'] == 0 for s in elf.symbols())
    code = decode(subprocess.check_output([
        str(ROOT / 'build/csky-macos/install/bin/csky-unknown-elf-objdump'), '-D',
        '--start-address=0x396a0', '--stop-address=0x396ee',
        str(ROOT / 'build/gx8002-board/padmux-get-stock.elf')], text=True))
    image = bytearray(stock)
    image[0x3c974:0x3c994] = body
    cases = 0
    for mode in (0, 1, 0xffffffff, 0xaabbccdc):
        for seed in (0, 91, 0xffffffff):
            result, calls, memory = execute(code, bytes(image), mode, seed)
            loaded = b''.join(memory[a].to_bytes(4, 'little')
                              for a in range(section['address'], section['address'] + 32, 4))
            assert result == 0 and loaded == body
            cases += 1
    symbol = row['symbol']
    function = {'symbol': symbol, 'section_name': '.text', 'compiled_bytes': 32,
                'compiled_sha256': sha(body), 'stock_occurrences': [
                    {'symbol': symbol, 'package_offset': 0x3c974, 'bytes': 32,
                     'sha256': sha(body), 'region': 'image_b_sram_text'}]}
    files = ('build_gx8002_backup_uart_completions.py', 'verify_gx8002_backup_uart_completions.py',
             'verify_gx8002_backup_uart_transmit_source.py', 'verify_gx8002_backup_memset_loader.py',
             'verify_gx8002_uart_transmit_complete.py', 'verify_gx8002_uart_receive_complete.py',
             'verify_gx8002_memcpy_source.py')
    if output:
        output.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, output / 'transmit.elf')
    return {'functions': [function], 'comparison': comparison, 'normal_loader_cases': cases,
            'evidence_sha256': {name: sha((ROOT / 'tools' / name).read_bytes()) for name in files},
            'source_admitted': True, 'hardware_qualified': False,
            'limits': ['Exact original instruction replacement only; no fill or new runtime allocation.',
                       'Release, flush and registered callback remain separately reconstructed dependencies.',
                       'Normal loader modeled; no physical device or whole-firmware qualification.']}


if __name__ == '__main__':
    result = verify()
    (ROOT / 'docs/research/gx8002-backup-uart-transmit-source-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Backup transmit source gate:', result['normal_loader_cases'], 'loader cases')
