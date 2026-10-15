#!/usr/bin/env python3
"""Compile recovered providers; never count object compilation as image closure."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def undefined_symbols(path):
    data = path.read_bytes()
    if data[:6] != b'\x7fELF\x01\x01':
        raise ValueError(f'expected little-endian ELF32: {path}')
    machine = struct.unpack_from('<H', data, 18)[0]
    if machine != 40:
        raise ValueError(f'expected ARM object: {path}')
    offset = struct.unpack_from('<I', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 46)
    sections = [struct.unpack_from('<10I', data, offset + i * size)
                for i in range(count)]
    undefined = []
    defined = []
    for section in sections:
        if section[1] != 2:
            continue
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for at in range(section[4], section[4] + section[5], section[9]):
            name, _, _, info, _, index = struct.unpack_from('<IIIBBH', data, at)
            if not name or info >> 4 not in (1, 2):
                continue
            label = names[name:].split(b'\0', 1)[0].decode()
            (undefined if index == 0 else defined).append(label)
    return sorted(set(undefined)), sorted(set(defined))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cc', default='clang')
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'r1/research/source-build')
    args = parser.parse_args()
    compiler = shutil.which(args.cc)
    if not compiler:
        parser.error(f'compiler unavailable: {args.cc}')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'r1/reconstructed').rglob('*.c'))
    sources += sorted((ROOT / 'r1/source').rglob('*.c'))
    flags = ['--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
             '-mfpu=fpv4-sp-d16', '-mfloat-abi=hard', '-ffreestanding',
             '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
             '-I' + str(ROOT / 'r1/reconstructed'),
             '-I' + str(ROOT / 'r1/source/include')]
    rows = []
    for source in sources:
        relative = source.relative_to(ROOT).as_posix()
        obj = output / (relative.replace('/', '__') + '.o')
        command = [compiler, *flags, '-c', str(source), '-o', str(obj)]
        result = subprocess.run(command, capture_output=True, text=True)
        row = dict(source=relative, source_sha256=sha(source), command=command,
                   compiled=result.returncode == 0, diagnostics=result.stderr)
        if result.returncode == 0:
            undefined, defined = undefined_symbols(obj)
            row.update(object_sha256=sha(obj), undefined=undefined, defined=defined)
        else:
            obj.unlink(missing_ok=True)
        rows.append(row)
    definitions = {symbol for row in rows for symbol in row.get('defined', [])}
    unresolved = sorted({symbol for row in rows for symbol in row.get('undefined', [])}
                        - definitions)
    report = dict(schema=1, compiler=compiler, compiler_sha256=sha(Path(compiler)),
                  compiler_version=subprocess.check_output([compiler, '--version'], text=True),
                  target='ARM Cortex-M4F, hard float', units=rows,
                  compiled=sum(row['compiled'] for row in rows), total=len(rows),
                  unresolved_symbols=unresolved, image_linked=False,
                  byte_identity_proven=False, source_completeness_proven=False,
                  evidence_inputs={str(p.relative_to(ROOT)): sha(p) for p in
                                   sorted(list((ROOT / 'r1/reconstructed').rglob('*')) +
                                          list((ROOT / 'r1/source').rglob('*')))
                                   if p.is_file()})
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"ARM providers compiled: {report['compiled']}/{report['total']}; "
          f"{len(unresolved)} unresolved cross-unit symbols; no image closure")
    for row in rows:
        if not row['compiled']:
            print(row['source'] + '\n' + row['diagnostics'])
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
