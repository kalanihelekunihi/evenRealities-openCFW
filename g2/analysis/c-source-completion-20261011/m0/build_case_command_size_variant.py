#!/usr/bin/env python3
"""Isolated size experiment from the pinned CASE selected-source receipt."""
from pathlib import Path
import argparse, hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SELECTED = ROOT / 'g2/analysis/case-source-candidate-round2-20261010/receipt.json'
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--opt', choices=('Os', 'Oz'), default='Oz')
parser.add_argument('--os-source', action='append', default=[], help='source basename to retain at -Os')
parser.add_argument('--merge-constants', action='store_true')
args = parser.parse_args()
out = args.output.resolve()
out.parent.mkdir(parents=True, exist_ok=True)
receipt = json.loads(SELECTED.read_text())
objects = []
records = []
objdir = out.with_suffix('.objects')
objdir.mkdir(exist_ok=True)
for i, row in enumerate(receipt['sources']):
    source = ROOT / row['source']
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != row['sha256']:
        raise SystemExit(f'selected source drift: {source}')
    obj = objdir / f'{i:03d}-{source.stem}.o'
    opt = 'Os' if source.name in args.os_source else args.opt
    command = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m0plus',
               '-mthumb', '-mfloat-abi=soft', '-std=c11', '-' + opt,
               '-ffreestanding', '-fno-builtin', '-ffunction-sections',
               '-fdata-sections', '-Wall', '-Wextra',
               *(['-fmerge-all-constants'] if args.merge_constants else []),
               '-c', str(source), '-o', str(obj)]
    subprocess.run(command, check=True)
    objects.append(obj)
    records.append({'source': row['source'], 'sha256': digest, 'optimization': opt,
                    'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest()})
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld', '-r', *map(str, objects), '-o', str(out)], check=True)
undefined = subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm', '-u', str(out)], text=True)
result = {'status': 'ISOLATED_SIZE_EXPERIMENT', 'optimization': args.opt,
          'merge_constants': args.merge_constants,
          'os_source': args.os_source, 'sources': records,
          'output_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
          'undefined_symbols': sorted(line.split()[-1] for line in undefined.splitlines() if line.split()),
          'limits': 'No admission into the selected firmware builder; stock root and formatter domain remain separate gates.'}
Path(str(out) + '.receipt.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'source_count': len(objects), 'undefined': result['undefined_symbols'],
                  'output_sha256': result['output_sha256']}, indent=2))
