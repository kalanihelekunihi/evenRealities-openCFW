#!/usr/bin/env python3
"""Compile the CASE integration candidate without admitting it to firmware."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SRC = ROOT / 'g2/components/case/legacy_default_candidate_20261010'
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path,
                    default=HERE / 'case-build/libcase_command_candidate.a',
                    help='destination for the candidate-only archive')
args = parser.parse_args()
archive = args.output.resolve()
OUT = archive.parent / (archive.stem + '-objects')
OUT.mkdir(exist_ok=True)
CC = '/usr/bin/clang'
AR = '/opt/homebrew/bin/arm-none-eabi-ar'
NM = '/opt/homebrew/bin/arm-none-eabi-nm'
FLAGS = ['--target=arm-none-eabi', '-mcpu=cortex-m0plus', '-mthumb',
         '-mfloat-abi=soft', '-std=c11', '-Os', '-ffreestanding',
         '-fno-builtin', '-Wall', '-Wextra', '-Werror']
sources = sorted(SRC.glob('*.c'))
objects = []
records = []
for source in sources:
    output = OUT / (source.stem + '.o')
    dep = OUT / (source.stem + '.d')
    command = [CC, *FLAGS, '-MD', '-MF', str(dep), '-c', str(source), '-o', str(output)]
    subprocess.run(command, check=True)
    objects.append(output)
    dependencies = dep.read_text().replace('\\\n', ' ').split(':', 1)[1].split()
    records.append({'path': str(source.relative_to(ROOT)),
                    'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                    'object_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                    'headers': [{'path': str(Path(d).resolve()),
                                 'sha256': hashlib.sha256(Path(d).read_bytes()).hexdigest()}
                                for d in dependencies if Path(d).resolve() != source.resolve()]})
archive.unlink(missing_ok=True)
subprocess.run([AR, 'rcsD', str(archive), *map(str, objects)], check=True)
nm = subprocess.run([NM, '-g', *map(str, objects)], check=True,
                    capture_output=True, text=True).stdout
provided, needed = set(), set()
for line in nm.splitlines():
    words = line.split()
    if len(words) < 2:
        continue
    typ, name = words[-2:]
    if typ == 'U':
        needed.add(name)
    elif typ.upper() in ('T', 'D', 'B', 'R', 'W'):
        provided.add(name)
receipt = {
    'status': 'COMPILED_RELOCATABLE_CANDIDATE',
    'target': 'arm-none-eabi cortex-m0plus thumb',
    'source_count': len(sources),
    'sources': records,
    'archive': str(archive),
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'compiler_sha256': hashlib.sha256(Path(CC).read_bytes()).hexdigest(),
    'archiver_sha256': hashlib.sha256(Path(AR).read_bytes()).hexdigest(),
    'flags': FLAGS,
    'provided_symbols': sorted(provided),
    'unresolved_imports': sorted(needed - provided),
    'limits': ['Candidate archive is not selected by the CASE firmware build.',
               'Imported lower calls require ABI and physical effect validation.',
               'No whole-handler original-byte equality is claimed.'],
}
archive.with_suffix(archive.suffix + '.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
if archive == (HERE / 'case-build/libcase_command_candidate.a').resolve():
    (HERE / 'case-build-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'sources': len(sources),
                  'imports': len(needed-provided)}, indent=2))
