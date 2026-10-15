#!/usr/bin/env python3
"""Compile pinned public R1 providers without copying or patching their bodies."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_source_candidates import undefined_symbols

ROOT = Path(__file__).resolve().parents[2]
PINS = {'tiny-aes-c':'e72b6eff0884673997d0ca6385169bbd9b31936d',
        'flashdb-2.0.0':'4e5677408256f82d47cd56a6b04605dcee35ed9a'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / 'r1/research/source-build/public-providers'
    output.mkdir(parents=True, exist_ok=True)
    flags = ['--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
             '-mfpu=fpv4-sp-d16', '-mfloat-abi=hard', '-Os', '-std=c11', '-ffreestanding',
             '-isystem', str(ROOT / 'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),
             '-I' + str(ROOT / 'r1/config-recovered')]
    rows = []
    dependencies = []
    for name, pin in PINS.items():
        tree = ROOT / 'third-party/upstream' / name
        assert (tree / '.git').exists(), f'initialize submodule {name}'
        assert subprocess.check_output(['git', '-C', str(tree), 'rev-parse', 'HEAD'], text=True).strip() == pin
        assert not subprocess.check_output(['git', '-C', str(tree), 'status', '--porcelain'], text=True).strip(), name
        dependencies.append(dict(name=name, pin=pin, direct_upstream=True,
                                 remote=subprocess.check_output(['git','-C',str(tree),'remote','get-url','origin'],text=True).strip()))
        if name == 'tiny-aes-c':
            sources = [tree / 'aes.c']
            options = ['-DECB=1', '-DCBC=0', '-DCTR=0']
        else:
            sources = [tree / 'src' / filename for filename in ('fdb.c', 'fdb_tsdb.c', 'fdb_utils.c')]
            sources += sorted((tree / 'port/fal/src').glob('*.c'))
            options = ['-I' + str(tree/'inc'), '-I' + str(tree/'port/fal/inc')]
        for source in sources:
            obj = output / f'{name}-{source.stem}.o'
            command = ['clang', *flags, *options, '-c', str(source), '-o', str(obj)]
            result = subprocess.run(command, capture_output=True, text=True)
            row = dict(source=str(source.relative_to(ROOT)), source_sha256=sha(source),
                       command=command, compiled=result.returncode == 0, diagnostics=result.stderr)
            if row['compiled']:
                undefined, defined = undefined_symbols(obj)
                row.update(undefined=undefined, defined=defined, object_sha256=sha(obj))
            else:
                obj.unlink(missing_ok=True)
            rows.append(row)
    defined = {symbol for row in rows for symbol in row.get('defined', [])}
    report = dict(schema=1, dependencies=dependencies, units=rows,
                  compiled=sum(row['compiled'] for row in rows), total=len(rows),
                  unresolved=sorted({symbol for row in rows for symbol in row.get('undefined', [])} - defined),
                  configuration={str(p.relative_to(ROOT)):sha(p) for p in
                                 [ROOT/'r1/config-recovered/fal_cfg.h', ROOT/'r1/config-recovered/fdb_cfg.h']},
                  stock_configuration_proven=False, image_linked=False, byte_identity_proven=False,
                  limitations=['FAL/TSDB feature modes are stock-supported; write granularity 32 is inferred.',
                               'No-op diagnostic routing is historical configuration, not recovered stock routing.',
                               'AES inverse-core lineage is supported; exact original vendor checkout is not unique.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Public provider units compiled: {report['compiled']}/{report['total']}")
    for row in rows:
        if not row['compiled']:
            print(row['source']+'\n'+row['diagnostics'])
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
