#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Use pinned C-SKY Ghidra sources to harvest named codec analysis evidence.

No downloaded binaries are executed. Firmware slicing is solely an analysis
input; it does not feed the source-built firmware provider. Decompilation is
not automatically admitted as reviewed C.
"""
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from analyze_gx8002_upstream_objects import analyze, IMAGE, IMAGE_SHA, sha

ROOT = Path(__file__).resolve().parents[1]
MODULE_COMMIT = '0daaa056e8c570ba514fc0d0226384ecf9f9df05'


def prepare_processor(module, output):
    processor = output / 'processor'
    tracked = subprocess.check_output(['git', '-C', str(module), 'ls-files', 'C-SKY'], text=True)
    for name in tracked.splitlines():
        relative = Path(name).relative_to('C-SKY')
        destination = processor / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(module / name, destination)
    rule = processor / 'data/languages/32b_data.sinc'
    if sha(rule.read_bytes()) != '3dde82aa3bc3bfbb70dc8950705cd0c2a59173e924ee6f92f9005ed880d5210b':
        raise ValueError('reviewed movih processor source changed')
    original = 'i32_imm16_rx = zext( i32_imm16_imm:2 << 16 );'
    fixed = 'i32_imm16_rx = zext( i32_imm16_imm:2 ) << 16;'
    text = rule.read_text()
    if text.count(original) != 1:
        raise ValueError('movih rule is not the reviewed original')
    rule.write_text(text.replace(original, fixed))
    return processor, sha(rule.read_bytes())


def harvest(module, sdk, ghidra, java, output):
    if subprocess.check_output(['git', '-C', str(module), 'rev-parse', 'HEAD'], text=True).strip() != MODULE_COMMIT:
        raise ValueError('processor module revision changed')
    if subprocess.check_output(['git', '-C', str(module), 'diff', 'HEAD', '--', 'C-SKY'], text=True):
        raise ValueError('processor module tracked sources changed')
    candidates = analyze(sdk)
    output.mkdir(parents=True, exist_ok=True)
    processor, patched_sha = prepare_processor(module, output)
    settings, cache = output / 'settings', output / 'cache'
    env = dict(os.environ, JAVA_HOME=str(java), XDG_CONFIG_HOME=str(settings), XDG_CACHE_HOME=str(cache))
    env['GHIDRA_HEADLESS_JAVA_OPTIONS'] = '-Dghidra.external.modules=' + str(processor)
    with (output / 'sleigh.log').open('w') as log:
        subprocess.run([str(ghidra / 'support/sleigh'), '-a', str(processor / 'data/languages')],
                       env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('codec oracle changed')
    image = output / 'image-b-analysis-only.bin'
    image.write_bytes(stock[0x3b940:0x4f9cc])
    selected = [m for m in candidates['matches'] if m['region'] == 'image_b_sram_text']
    seeds = output / 'known-functions.tsv'
    rows = sorted({(0x10003000 + m['package_offset'] - 0x3b940, m['symbol']) for m in selected})
    seeds.write_text(''.join(f'0x{address:08x}\t{name}\n' for address, name in rows))
    projects = output / 'projects'
    projects.mkdir(exist_ok=True)
    command = [str(ghidra / 'support/analyzeHeadless'), str(projects), 'codec-known-image-b',
               '-import', str(image), '-loader', 'BinaryLoader', '-loader-baseAddr', '0x10003000',
               '-processor', 'CSKY_V2:LE:32:default', '-noanalysis',
               '-scriptPath', str(ROOT / 'tools/ghidra_scripts'),
               '-postScript', 'PrepareGx8002KnownFunctions.java', str(seeds),
               '-postScript', 'CheckCskyMovih.java',
               '-postScript', 'ExportAllFunctionDecomp.java', str(output / 'export'), '0', '1',
               'respect-read-only', '-deleteProject']
    with (output / 'headless.log').open('w') as log:
        subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    headless_log = (output / 'headless.log').read_text()
    if 'ERROR ' in headless_log:
        raise ValueError('headless analysis reported an error; see headless.log')
    if 'CSKY_MOVIH_CHECK_OK 0xa0a00000' not in headless_log:
        raise ValueError('processor movih semantic regression check did not pass')
    records = [json.loads(line) for line in (output / 'export/functions-000.jsonl').read_text().splitlines()]
    if len(records) != len(rows) or not all(r['decompiled'] for r in records):
        raise ValueError('not all named function seeds were exported')
    analog_probe = (output / 'export/decomp/10008048.c').read_text().lower()
    if 'a0005088' not in analog_probe or 'dword_10008060' in analog_probe:
        raise ValueError('known analog literal pool was not resolved in decompilation')
    report = {'processor_repository': 'https://github.com/taligentx/ghidra_csky_WinnerMicro',
              'processor_commit': MODULE_COMMIT, 'firmware_sha256': IMAGE_SHA,
              'local_processor_fix': 'zero-extend movih immediate before shifting',
              'patched_32b_data_sha256': patched_sha,
              'movih_semantic_regression_passed': True,
              'respect_read_only_literal_memory': True,
              'analog_literal_regression_passed': True,
              'analysis_script_sha256': {name: sha((ROOT / 'tools/ghidra_scripts' / name).read_bytes())
                  for name in ('PrepareGx8002KnownFunctions.java', 'CheckCskyMovih.java', 'ExportAllFunctionDecomp.java')},
              'volatile_mmio_windows': ['0xa0003000+0x1000', '0xa0005000+0x1000',
                                        '0xa0a00000+0x1000', '0xe000f000+0x1000'],
              'analysis_image_sha256': sha(image.read_bytes()), 'load_address': '0x10003000',
              'seed_count': len(rows), 'exported_functions': len(records),
              'firmware_bytes_emitted': 0, 'source_admitted': False,
              'limits': ['Named stock matches are analysis candidates, not complete callable-boundary proof.',
                         'Processor semantics and decompiler output require function-by-function qualification.']}
    (output / 'harvest-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', type=Path, default=ROOT / 'build/upstream-ghidra-csky-winnermicro')
    parser.add_argument('--sdk', type=Path, default=ROOT / 'build/upstream-nationalchip-lvp-kws')
    parser.add_argument('--ghidra', type=Path, default=Path('/opt/homebrew/Cellar/ghidra/12.1.3/libexec'))
    parser.add_argument('--java', type=Path, default=Path('/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home'))
    parser.add_argument('--output', type=Path, default=ROOT / 'build/gx8002-known-functions')
    args = parser.parse_args()
    print(json.dumps(harvest(args.module.resolve(), args.sdk.resolve(), args.ghidra.resolve(),
                             args.java.resolve(), args.output.resolve()), indent=2))


if __name__ == '__main__':
    main()
