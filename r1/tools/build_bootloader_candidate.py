#!/usr/bin/env python3
"""Build pinned Nordic bootloader units with recovered R1 configuration.
Clang cross-compilation is diagnostic only; original ArmCC matching remains open.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile
import tarfile

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--gnu-runtime', type=Path, required=True)
    args = parser.parse_args()
    sdk, runtime = args.sdk.resolve(), args.gnu_runtime.resolve()
    archive = sdk.parent / 'sdk.zip'
    assert digest(archive) == '5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    # Authenticate extracted SDK inputs too; the archive hash alone is insufficient.
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():
                continue
            relative = Path(member.filename).relative_to(sdk.name)
            assert hashlib.sha256(bundle.read(member)).hexdigest() == digest(sdk / relative), relative
    runtime_archive = runtime.parent / 'arm-gnu-9.tar.bz2'
    assert digest(runtime_archive) == '5adc2ee03904571c2de79d5cfc0f7fe2a5c5f54f44da5b645c17ee57b217f11f'
    with tarfile.open(runtime_archive) as bundle:
        for member in bundle:
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(runtime.name)
            if str(relative).startswith(('arm-none-eabi/include/', 'arm-none-eabi/lib/thumb/v7e-m+fp/hard/', 'lib/gcc/arm-none-eabi/9.3.1/thumb/v7e-m+fp/hard/')):
                assert hashlib.sha256(bundle.extractfile(member).read()).hexdigest() == digest(runtime / relative), relative
    make_dir = sdk / 'examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc'
    makefile = (make_dir / 'Makefile').read_text()

    def block(name):
        match = re.search(r'^' + name + r' \+= \\\n((?:.*\\\n)+)', makefile, re.M)
        assert match, name
        words = match[1].replace('\\\n', ' ').split()
        return [str((make_dir / word.replace('$(SDK_ROOT)', str(sdk))
                     .replace('$(PROJ_DIR)', str(make_dir.parent.parent))).resolve()) for word in words]

    sources, includes = block('SRC_FILES'), block('INC_FOLDERS')
    # The example's placeholder key is the sole replaced SDK C input.
    sources = [str(ROOT / 'r1/config-recovered/r1_dfu_public_key.c')
               if Path(path).name == 'dfu_public_key.c' else path for path in sources]
    defines = re.findall(r'^CFLAGS \+= (-D[^\n]+)', makefile, re.M)
    defines += ['-D__HEAP_SIZE=0', '-DR1_BUILD_PROFILE_CAPTURED=1']
    cc = shutil.which('clang')
    assert cc
    flags = ['--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
             '-mfpu=fpv4-sp-d16', '-mfloat-abi=hard', '-Oz', '-g',
             '-ffunction-sections', '-fdata-sections', '-fno-strict-aliasing',
             '-fno-builtin', '-fshort-enums', '-Wno-incompatible-pointer-types',
             '-isystem', str(runtime / 'arm-none-eabi/include'),
             '-include', str(ROOT / 'r1/config-recovered/r1_recovered_config.h'),
             *defines, *['-I' + path for path in includes]]
    output = ROOT / 'r1/research/source-build/bootloader'
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, source in enumerate(sources):
        obj = output / f'{index:02d}_{Path(source).stem}.o'
        command = [cc, *flags, '-c', source, '-o', str(obj)]
        result = subprocess.run(command, capture_output=True, text=True)
        row = dict(source=source, source_sha256=digest(Path(source)),
                   command=command, compiled=result.returncode == 0,
                   diagnostics=result.stderr)
        if result.returncode == 0:
            row['object_sha256'] = digest(obj)
        else:
            obj.unlink(missing_ok=True)
        rows.append(row)
    link = dict(attempted=False, linked=False)
    if all(row['compiled'] for row in rows):
        ld = shutil.which('arm-none-eabi-ld') or '/opt/homebrew/opt/arm-none-eabi-binutils/bin/arm-none-eabi-ld'
        syslib = runtime / 'arm-none-eabi/lib/thumb/v7e-m+fp/hard'
        gcc_lib = runtime / 'lib/gcc/arm-none-eabi/9.3.1/thumb/v7e-m+fp/hard'
        libraries = [sdk / 'external/nrf_oberon/lib/cortex-m4/hard-float/liboberon_3.0.8.a',
                     sdk / 'external/nrf_cc310_bl/lib/cortex-m4/hard-float/libnrf_cc310_bl_0.9.13.a']
        elf = output / 'bootloader-candidate.elf'
        script = output / 'candidate.ld'
        script.write_text((make_dir / 'secure_bootloader_gcc_nrf52.ld').read_text().replace(
            'GROUP(-lgcc -lc -lnosys)', 'GROUP(-lgcc -lc_nano -lnosys)'))
        startup = [gcc_lib / 'crti.o', gcc_lib / 'crtbegin.o', syslib / 'crt0.o',
                   gcc_lib / 'crtend.o', gcc_lib / 'crtn.o']
        link_command = [ld, '-T', str(script),
                        '-L' + str(sdk / 'modules/nrfx/mdk'), '-L' + str(syslib), '-L' + str(gcc_lib),
                        '--gc-sections', '-Map=' + str(output / 'bootloader-candidate.map'),
                        '-o', str(elf), *[str(output / f'{i:02d}_{Path(source).stem}.o') for i, source in enumerate(sources)],
                        *map(str, startup), '--start-group', *map(str, libraries), str(syslib / 'libc_nano.a'), '-lm', '-lgcc', '-lnosys', '--end-group']
        result = subprocess.run(link_command, capture_output=True, text=True, cwd=sdk / 'modules/nrfx/mdk')
        link = dict(attempted=True, linked=result.returncode == 0, command=link_command,
                    diagnostics=result.stderr, binary_dependencies={str(p): digest(p) for p in libraries})
        if result.returncode == 0:
            link['elf_sha256'] = digest(elf)
            prefix = str(Path(ld).parent / 'arm-none-eabi-')
            link['size'] = subprocess.check_output([prefix + 'size', str(elf)], text=True)
            link['undefined_symbols'] = subprocess.check_output([prefix + 'nm', '-u', str(elf)], text=True)
            assert not link['undefined_symbols'].strip()
            link['program_headers'] = subprocess.check_output([prefix + 'readelf', '-l', str(elf)], text=True)
            link['generated_linker_sha256'] = digest(script)
            link['runtime_dependencies'] = {str(path): digest(path) for path in
                                            [*startup, syslib / 'libc_nano.a', syslib / 'libm.a',
                                             syslib / 'libnosys.a', gcc_lib / 'libgcc.a']}
            link['linker_version'] = subprocess.check_output([ld, '--version'], text=True)
            link['linker_sha256'] = digest(Path(ld))
        else:
            elf.unlink(missing_ok=True)
    report = dict(schema=1, sdk_archive_sha256=digest(archive),
                  compiler_version=subprocess.check_output([cc, '--version'], text=True),
                  units=rows, compiled=sum(row['compiled'] for row in rows), total=len(rows),
                  linked=link['linked'], link=link, byte_identity_proven=False, stock_config_proven=False,
                  configuration={str(p.relative_to(ROOT)): digest(p) for p in
                                 (ROOT / 'r1/config-recovered').glob('*') if p.is_file()})
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"Bootloader candidate units compiled: {report['compiled']}/{report['total']}")
    for row in rows:
        if not row['compiled']:
            print(row['source'] + '\n' + row['diagnostics'][:2000])
    if link['attempted']:
        print('Bootloader candidate linked:', link['linked'])
        if not link['linked']:
            print(link['diagnostics'][:6000])
    return 0 if report['compiled'] == report['total'] and link['linked'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
