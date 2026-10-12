#!/usr/bin/env python3
"""Measure complete C-SKY function-section sizes for three XIP overflow sites."""
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
OUT = HERE / 'xip-size-probe'
SITES = [
    ('tfp_format', 'resident_xip_tinyprintf.c', 'gx8002_xip_tfp_format_10206a84', 416),
    ('audio_io', 'resident_xip_audio_output.c', 'gx8002_xip_audio_input_output_10207070', 452),
    ('uart_rx', 'resident_xip_uart_receive_callback.c',
     'gx8002_xip_uart_receive_callback_10208098', 532),
]
VARIANTS = {
    'O2': ['-O2'],
    'Os': ['-Os'],
    'O1': ['-O1'],
    'Os_no_inline': ['-Os', '-fno-inline-functions'],
    'Os_no_jumptable': ['-Os', '-fno-jump-tables', '-fno-tree-switch-conversion'],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def measure(obj, symbol):
    symbols = subprocess.run([str(READELF), '-sW', str(obj)], check=True,
                             capture_output=True, text=True).stdout
    matches = []
    for line in symbols.splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[-1] == symbol and fields[3] == 'FUNC':
            matches.append((int(fields[2]), int(fields[6])))
    assert len(matches) == 1, (obj, symbol, matches)
    section_index = matches[0][1]
    sections = subprocess.run([str(READELF), '-SW', str(obj)], check=True,
                              capture_output=True, text=True).stdout
    for line in sections.splitlines():
        match = re.search(r'\[\s*(\d+)\]\s+(\S+)\s+PROGBITS\s+'
                          r'[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)', line)
        if match and int(match.group(1)) == section_index:
            return matches[0][0], int(match.group(3), 16), match.group(2)
    raise AssertionError((obj, symbol, section_index))

def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for label, filename, symbol, slot in SITES:
        source = ROOT / 'g2/components/gx8002/app_callback_candidate' / filename
        for variant, flags in VARIANTS.items():
            obj = OUT / f'{label}-{variant}.o'
            command = [
                'docker', 'run', '--rm', '--network=none', '--read-only',
                '--platform', 'linux/amd64',
                '--mount', f'type=bind,src={TOOL},dst=/tool,readonly',
                '--mount', f'type=bind,src={ROOT},dst=/repo,readonly',
                '--mount', f'type=bind,src={OUT},dst=/out',
                '--tmpfs', '/tmp:rw', 'opencfw/iar-base:10.10.2-local',
                '/tool/bin/csky-abiv2-elf-gcc', '-mcpu=ck804ef', '-mhard-float',
                *flags, '-fno-builtin', '-fstrict-volatile-bitfields',
                '-ffunction-sections', '-fdata-sections', '-std=c11',
                '-c', '/repo/' + str(source.relative_to(ROOT)),
                '-o', '/out/' + obj.name,
            ]
            subprocess.run(command, check=True)
            func_size, section_size, section = measure(obj, symbol)
            rows.append({'site': label, 'source': str(source.relative_to(ROOT)),
                         'source_sha256': sha(source), 'symbol': symbol,
                         'native_fixed_slot_bytes': slot, 'variant': variant,
                         'compiler_flags': flags, 'function_bytes': func_size,
                         'section_bytes': section_size,
                         'section': section,
                         'section_fits_native_slot': section_size <= slot,
                         'object_sha256': sha(obj)})
    receipt = {'compiler_sha256': sha(TOOL/'bin/csky-abiv2-elf-gcc'),
               'rows': rows,
               'scope': 'isolated target section size only; semantic and final-link equality unqualified'}
    (OUT/'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps([{r['site']+':'+r['variant']: r['section_bytes']}
                      for r in rows]))

if __name__ == '__main__':
    main()
