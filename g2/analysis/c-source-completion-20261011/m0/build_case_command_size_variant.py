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
parser.add_argument('--override-source', action='append', default=[],
                    help='selected basename=replacement C path')
args = parser.parse_args()
overrides = {Path(name).name: Path(path).resolve()
             for name, path in (entry.split('=', 1) for entry in args.override_source)}
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
    compile_source = overrides.get(source.name, source)
    obj = objdir / f'{i:03d}-{source.stem}.o'
    opt = 'Os' if source.name in args.os_source else args.opt
    command = ['/usr/bin/clang', '--target=arm-none-eabi', '-mcpu=cortex-m0plus',
               '-mthumb', '-mfloat-abi=soft', '-std=c11', '-' + opt,
               '-ffreestanding', '-fno-builtin', '-ffunction-sections',
               '-fdata-sections', '-Wall', '-Wextra',
               *(['-fmerge-all-constants'] if args.merge_constants else []),
               '-c', str(compile_source), '-o', str(obj)]
    subprocess.run(command, check=True)
    objects.append(obj)
    records.append({'source': row['source'], 'sha256': digest,
                    'compiled_source': str(compile_source),
                    'compiled_sha256': hashlib.sha256(compile_source.read_bytes()).hexdigest(),
                    'optimization': opt,
                    'object_sha256': hashlib.sha256(obj.read_bytes()).hexdigest()})
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld', '-r', *map(str, objects), '-o', str(out)], check=True)
undefined = subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-nm', '-u', str(out)], text=True)
result = {'status': 'ISOLATED_SIZE_EXPERIMENT', 'optimization': args.opt,
          'merge_constants': args.merge_constants,
          'override_sources': args.override_source,
          'os_source': args.os_source, 'sources': records,
          'output_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
          'undefined_symbols': sorted(line.split()[-1] for line in undefined.splitlines() if line.split()),
          'limits': 'No admission into the selected firmware builder; stock root and formatter domain remain separate gates.'}
Path(str(out) + '.receipt.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'source_count': len(objects), 'undefined': result['undefined_symbols'],
                  'output_sha256': result['output_sha256']}, indent=2))
