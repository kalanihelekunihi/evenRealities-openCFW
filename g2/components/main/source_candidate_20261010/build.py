#!/usr/bin/env python3
"""Compile the source-owned main candidates; never reads a firmware oracle."""
from pathlib import Path
import hashlib
import json
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'g2/build/source-candidates/20261010-main'
SOURCES = [
    'g2/components/main/iar_runtime_candidates_20261010/runtime.c',
    'g2/components/main/smp_dispatch_candidates_20261010/smp_dispatch.c',
    'g2/components/main/flashdb_candidates_20261010/blob_read.c',
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cc = run(['xcrun', '--find', 'clang']).strip()
    ar = shutil.which('arm-none-eabi-ar')
    ld = shutil.which('arm-none-eabi-ld')
    nm = shutil.which('arm-none-eabi-nm')
    if not all((ar, ld, nm)):
        raise SystemExit('ARM binutils ar, ld and nm are required')
    flags = ['--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
             '-std=c11', '-Oz', '-ffreestanding', '-fno-builtin',
             '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
    objects, commands, inputs, tool_headers = [], [], {}, {}
    for source in SOURCES:
        src = ROOT / source
        obj = OUT / (src.parent.name + '.o')
        dep = obj.with_suffix('.d')
        cmd = [cc, *flags, '-MD', '-MF', str(dep), '-c', str(src), '-o', str(obj)]
        run(cmd)
        commands.append(cmd)
        objects.append(obj)
        dependencies = shlex.split(dep.read_text().split(':', 1)[1].replace('\\\n', ' '))
        for filename in dependencies:
            path = Path(filename).resolve()
            if path.is_relative_to(ROOT):
                key = str(path.relative_to(ROOT))
                if not key.startswith('g2/components/main/'):
                    raise RuntimeError('Unexpected repository dependency: ' + key)
                inputs[key] = digest(path)
            else:
                tool_headers[str(path)] = digest(path)
    archive = OUT / 'main-candidates.a'
    if archive.exists():
        archive.unlink()  # Only this build's generated archive is replaced.
    archive_cmd = [ar, 'rcsD', str(archive), *map(str, objects)]
    run(archive_cmd)
    commands.append(archive_cmd)
    combined = OUT / 'main-candidates.o'
    link_cmd = [ld, '-r', '-o', str(combined), *map(str, objects)]
    run(link_cmd)
    commands.append(link_cmd)
    undefined = run([nm, '-u', str(combined)])
    defined = run([nm, '--defined-only', str(combined)])
    (OUT / 'undefined-symbols.txt').write_text(undefined)
    (OUT / 'defined-symbols.txt').write_text(defined)
    receipt = {
        'status': 'source-only candidate compilation and relocatable composition PASS',
        'source_inputs': inputs,
        'compiler_header_inputs': tool_headers,
        'binutils': {name: {'path': path, 'sha256': digest(Path(path).resolve())}
                     for name, path in [('ar', ar), ('ld', ld), ('nm', nm)]},
        'compiler': {'path': cc, 'sha256': digest(Path(cc)), 'version': run([cc, '--version'])},
        'commands': commands,
        'outputs': {p.name: digest(p) for p in [*objects, archive, combined]},
        'unresolved_link_symbols': undefined.splitlines(),
        'limits': ['Not a firmware ELF or payload; address and provider contracts remain unresolved.',
                   'Function-pointer providers do not appear in the undefined-symbol list.',
                   'No byte identity or hardware execution is established by this build.'],
    }
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'objects': len(objects), 'archive': str(archive),
                      'unresolved_link_symbols': undefined.splitlines()}, indent=2))


if __name__ == '__main__':
    main()
