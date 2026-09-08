#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build pinned C-SKY binutils and a freestanding C compiler on macOS.

Sources must already be fetched. No SDK binaries, Linux guest, system install,
or target-device operation is used. Target libc/libgcc qualification is separate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {'': '20c6b74f00ac3f464cb43ef2189a069d656933d5',
        'binutils': '32f97f3473656ee5d64e8e8c01a6006312c5828a',
        'gcc': '1e9b70447a8417f5c692370de4533e43d754e8fa'}

GCC_FIX = '9970b576b7e4ae337af1268395ff221348c4b34a'
GCC_HEADER_BEFORE = '30fb2a4db0a2eef1d40688f8cab8ede500f1bd9e073934d11b42286c8b016bf0'
GCC_HEADER_AFTER = '67f0ae1709121b4b9595a7a2641f6c89fe3a4ce4ce00fe0d8f178310986a5264'


def apply_macos_fix(source):
    patch = ROOT / 'tools/toolchain-patches/gcc-safe-ctype.patch'
    if hashlib.sha256(patch.read_bytes()).hexdigest() != '61bdf58e166c79c394513a8df0779e5a4eb53fd9b194498af512be8e5dab76af':
        raise RuntimeError('upstream macOS patch changed')
    header = source / 'gcc/gcc/system.h'
    digest = hashlib.sha256(header.read_bytes()).hexdigest()
    if digest == GCC_HEADER_BEFORE:
        subprocess.run(['git', '-C', str(source / 'gcc'), 'apply', '--check', str(patch)], check=True)
        subprocess.run(['git', '-C', str(source / 'gcc'), 'apply', str(patch)], check=True)
    elif digest != GCC_HEADER_AFTER:
        raise RuntimeError('GCC system.h differs from the pinned original and upstream backport')
    if hashlib.sha256(header.read_bytes()).hexdigest() != GCC_HEADER_AFTER:
        raise RuntimeError('upstream macOS patch result changed')


def configure_arguments(source, output, component):
    common = [str(source / component / 'configure'), '--target=csky-unknown-elf',
              f'--prefix={output / "install"}', '--disable-nls', '--disable-shared',
              '--with-system-zlib']
    if component == 'binutils':
        return common + ['--disable-werror', '--disable-gdb', '--disable-gdbserver',
                         '--disable-sim', '--disable-debuginfod', '--without-zstd']
    return common + ['--enable-languages=c', '--without-headers', '--with-newlib',
                     '--disable-bootstrap', '--disable-threads', '--disable-multilib',
                     '--disable-libssp', '--disable-libgomp', '--disable-libquadmath',
                     '--disable-libatomic', '--disable-libsanitizer', '--disable-libstdcxx',
                     '--disable-libcc1', '--with-cpu=ck804ef', '--with-endian=little',
                     '--with-float=hard', '--with-gmp=/opt/homebrew/opt/gmp',
                     '--with-mpfr=/opt/homebrew/opt/mpfr', '--with-mpc=/opt/homebrew/opt/libmpc']


def run_logged(command, directory, env, name):
    print(f'{directory.name}: {name}', flush=True)
    log = directory / f'{name}.log'
    with log.open('w') as handle:
        result = subprocess.run(command, cwd=directory, env=env,
                                stdout=handle, stderr=subprocess.STDOUT)
    if result.returncode:
        print('\n'.join(log.read_text(errors='replace').splitlines()[-25:]), file=sys.stderr)
        raise RuntimeError(f'{name} failed; see {log}')


def build(source, output, jobs, stage):
    if sys.platform != 'darwin':
        raise RuntimeError('this recipe is qualified only for the macOS host')
    if jobs < 1:
        raise ValueError('jobs must be positive')
    for component, expected in PINS.items():
        actual = subprocess.check_output(['git', '-C', str(source / component),
                                          'rev-parse', 'HEAD'], text=True).strip()
        if actual != expected:
            raise RuntimeError(f'upstream revision changed: {component or "build scripts"}')
    env = dict(os.environ, CC='/usr/bin/clang', CXX='/usr/bin/clang++', MAKEINFO='true')
    env['PATH'] = str(output / 'install/bin') + os.pathsep + env['PATH']
    components = ('binutils', 'gcc') if stage == 'all' else (stage,)
    if 'gcc' in components:
        apply_macos_fix(source)
    commands = {}
    for component in components:
        directory = output / f'{component}-build'
        directory.mkdir(parents=True, exist_ok=True)
        configure = configure_arguments(source, output, component)
        commands[component] = configure
        run_logged(configure, directory, env, 'configure')
        targets = ['all-binutils', 'all-gas', 'all-ld'] if component == 'binutils' else ['all-gcc']
        run_logged(['make', f'-j{jobs}', *targets, 'MAKEINFO=true'], directory, env, 'build')
        install = ['install-binutils', 'install-gas', 'install-ld'] if component == 'binutils' else ['install-gcc']
        run_logged(['make', *install, 'MAKEINFO=true'], directory, env, 'install')
    report = {'source_revisions': PINS, 'host': subprocess.check_output(['uname', '-sm'], text=True).strip(),
              'gcc_upstream_backport': GCC_FIX if 'gcc' in components else None,
              'host_compiler': subprocess.check_output(['/usr/bin/clang', '--version'], text=True).splitlines()[0],
              'configure_commands': commands, 'target': 'csky-unknown-elf', 'cpu': 'ck804ef',
              'target_libc_qualified': False, 'target_libgcc_qualified': False,
              'hardware_operations': []}
    (output / f'{stage}-build-receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'build/upstream-csky-toolchain-build')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/csky-macos')
    parser.add_argument('--jobs', type=int, default=8)
    parser.add_argument('--stage', choices=('all', 'binutils', 'gcc'), default='all')
    args = parser.parse_args()
    print(json.dumps(build(args.source.resolve(), args.output.resolve(), args.jobs, args.stage), indent=2))


if __name__ == '__main__':
    main()
