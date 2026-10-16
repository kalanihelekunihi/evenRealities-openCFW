#!/usr/bin/env python3
"""Check authenticated image-A data placements in an isolated target link.

The input is an already compiled relocatable candidate. This checks named
sections only; it does not qualify final code, XIP, copy, or runtime aliasing.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / ('g2/build/offline-nationalchip-dsp-c-compiler-successor-'
               '20261009T195245Z/toolchain')
READELF = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/tools/'
                  'csky-binutils-001/install/bin/csky-elfabiv2-readelf')
SECTIONS = [
    ('vectors', 0x10023400, 0x100, 'PROGBITS'),
    ('clock_boot_25cd0', 0x10025cd0, 0x10, 'PROGBITS'),
    ('clock_boot_25ce0', 0x10025ce0, 0x14, 'PROGBITS'),
    ('clock_boot_25cf4', 0x10025cf4, 0x10, 'PROGBITS'),
    ('flash_state', 0x100264e4, 0x20, 'PROGBITS'),
    ('flash_api', 0x10026504, 0x78, 'PROGBITS'),
    ('otp_2657c', 0x1002657c, 0x28, 'PROGBITS'),
    ('otp_265a4', 0x100265a4, 0x38, 'PROGBITS'),
    ('otp_265dc', 0x100265dc, 0x48, 'PROGBITS'),
    ('flash_catalog', 0x10026624, 0xa8, 'PROGBITS'),
    ('flash_otp', 0x100266cc, 0x14, 'PROGBITS'),
    ('module_table', 0x100266e0, 0x1a0, 'PROGBITS'),
    ('module_config', 0x10026880, 0x48, 'PROGBITS'),
    ('clock_defaults', 0x100268c8, 0x3c, 'PROGBITS'),
    ('clock_sources_26904', 0x10026904, 0x50, 'PROGBITS'),
    ('clock_sources_26954', 0x10026954, 0x50, 'PROGBITS'),
    ('board_state', 0x100269a4, 0xf0, 'PROGBITS'),
    ('uart_channels', 0x10026a94, 0x100, 'PROGBITS'),
    ('aout_context', 0x10026b94, 0x34, 'PROGBITS'),
    ('aout_ops', 0x10026bc8, 0x54, 'PROGBITS'),
    ('aout_config', 0x10026c1c, 0x58, 'PROGBITS'),
    ('uart_rx_config', 0x10026c74, 0x8, 'PROGBITS'),
    ('kws_keywords', 0x10026c7c, 0xb0, 'PROGBITS'),
    ('sample_prestate', 0x10026d2c, 0x4, 'PROGBITS'),
    ('sample_registration', 0x10026d30, 0x2c, 'PROGBITS'),
    ('request_initial', 0x10026d5c, 0x20, 'PROGBITS'),
    ('console_port', 0x2002731c, 0x4, 'NOBITS'),
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    assert candidate.is_file()
    assert str(candidate).startswith(str(ROOT) + '/'), candidate
    assert str(output).startswith(str(ROOT) + '/'), output
    placed = output / 'placed.o'
    prefix = ['docker', 'run', '--rm', '--network=none', '--read-only',
              '--platform', 'linux/amd64',
              '--mount', f'type=bind,src={TOOL},dst=/tool,readonly',
              '--mount', f'type=bind,src={ROOT},dst=/repo,readonly',
              '--mount', f'type=bind,src={output},dst=/out',
              '--tmpfs', '/tmp:rw', 'opencfw/iar-base:10.10.2-local',
              '/tool/bin/csky-abiv2-elf-gcc']
    command = prefix + ['-mcpu=ck804ef', '-mhard-float', '-nostdlib',
                        '-nostartfiles', '-Wl,-r', '-Wl,-A,ck803',
                        '-Wl,-T,/repo/g2/analysis/c-source-completion-20261011/'
                        'codec/image_a_known_data.ld',
                        '/repo/' + str(candidate.relative_to(ROOT)),
                        '-o', '/out/placed.o']
    subprocess.run(command, check=True)
    listing = subprocess.run([str(READELF), '-SW', str(placed)],
                             capture_output=True, text=True, check=True).stdout
    parsed = {}
    for line in listing.splitlines():
        match = re.search(r'\]\s+(\.gx8002_\S+)\s+(PROGBITS|NOBITS)\s+'
                          r'([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)', line)
        if match:
            parsed[match.group(1)] = {
                'type': match.group(2), 'address': int(match.group(3), 16),
                'bytes': int(match.group(4), 16)}
    checks = []
    for short, address, size, kind in SECTIONS:
        name = '.gx8002_' + short
        value = parsed.get(name)
        assert value == {'type': kind, 'address': address, 'bytes': size}, (name, value)
        checks.append({'section': name, 'address': hex(address),
                       'bytes': size, 'type': kind})
    tail = checks[4:-1]
    assert all(int(a['address'], 16) + a['bytes'] == int(b['address'], 16)
               for a, b in zip(tail, tail[1:])), 'initialized tail not contiguous'
    assert sum(x['bytes'] for x in tail) == 2200
    assert 101776 - 87060 == 0x10026d7c - 0x10023400 == 14716
    assert 0x20026d80 <= 0x2002731c < 0x2002731c + 4 <= 0x2002ecec
    receipt = {
        'candidate_sha256': sha(candidate),
        'linker_script_sha256': sha(HERE / 'image_a_known_data.ld'),
        'placed_object_sha256': sha(placed),
        'section_checks': checks,
        'initialized_tail_bytes': 2200,
        'vector_bytes': 256,
        'console_bss_bytes': 4,
        'authenticated_normal_copy': {
            'package_offset': 87060, 'bytes': 14716,
            'iram_start': '0x10023400', 'iram_end_exclusive': '0x10026d7c',
            'execution_verified': False,
        },
        'target_link_passed': True,
        'required_final_inputs': [
            'XIP section and callable provider address map',
            'proof of 0x1002 executable to 0x2002 data alias or scatter mechanism',
            'package byte-offset 87060 copy execution and alternate loader branch',
            'resolved pointer relocation words for the final native map',
            'entry/reset execution and conditional BSS behavior',
        ],
        'limits': ['relocatable isolated section placement only',
                   'does not establish XIP/code addresses, source-to-runtime alias, '
                   'loaded copy, alternate loader path, resolved pointers, or runtime equality'],
    }
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'target_link_passed': True, 'sections': len(checks),
                      'initialized_tail_bytes': 2200,
                      'placed_object_sha256': receipt['placed_object_sha256']}))

if __name__ == '__main__':
    main()
