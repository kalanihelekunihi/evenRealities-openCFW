#!/usr/bin/env python3
"""Install supplied C-SKY Linux x86-64 toolchain locally, then test in Docker."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tarfile
import tempfile
import os

HERE = Path(__file__).resolve().parent
CACHE = HERE.parents[1] / 'third-party/local-vendor'
OUTER = '0c6bb77fec9c11b1f7a9b8d73305d12598ca3d3d7527cec742be0a68a84b1688'
INNER = 'df33d1e101d9b0c1d4cc68286bb97a98e3a3095cf321f9e253f0ddf805d8d9f9'
NAME = 'csky-abiv2-elf-toolchain-v3.10.15/csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz'
IMAGE = 'ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55'

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    if not args.apply:
        print('Dry run: authenticate nested archives, safely extract Linux x86-64 tools to ignored local-vendor/toolchains, run gcc --version in isolated amd64 Docker (no network or keys).')
        return
    archives = list((CACHE/'extracted/csky').rglob('csky-abiv2-elf-toolchain-v3.10.15.tar.gz'))
    if len(archives) != 1:
        ap.error('First run setup.py extract --id csky --apply')
    archive = archives[0]
    if archive.is_symlink() or hashlib.sha256(archive.read_bytes()).hexdigest() != OUTER:
        ap.error('Nested archive hash mismatch')
    with tarfile.open(archive) as t:
        member = t.getmember(NAME)
        if not member.isfile() or member.size > 150 * 1024**2:
            ap.error('Unexpected inner archive member')
        data = t.extractfile(member).read()
    if hashlib.sha256(data).hexdigest() != INNER:
        ap.error('Linux toolchain archive hash mismatch')
    target = CACHE/'toolchains/csky-linux-x86_64'
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with tempfile.TemporaryDirectory(dir=target.parent) as temp:
            inner = Path(temp)/'toolchain.tar.gz'
            inner.write_bytes(data)
            staging = Path(temp)/'extracted'
            staging.mkdir()
            with tarfile.open(inner) as t:
                members = t.getmembers()
                if len(members) > 20000 or sum(m.size for m in members) > 2 * 1024**3:
                    ap.error('Expansion bound exceeded')
                t.extractall(staging, filter='data')
            (staging/'.archive-sha256').write_text(INNER+'\n')
            os.rename(staging, target)
    if target.is_symlink() or (target/'.archive-sha256').read_text().strip() != INNER:
        ap.error('Existing installation lacks matching provenance')
    compilers = list(target.rglob('bin/csky-abiv2-elf-gcc'))
    if len(compilers) != 1:
        ap.error('Expected compiler not found uniquely')
    compiler = '/opt/csky/'+compilers[0].relative_to(target).as_posix()
    subprocess.run(['docker','run','--rm','--network','none','--platform','linux/amd64',
                    '--mount','type=bind,src='+str(target)+',dst=/opt/csky,readonly',
                    IMAGE,compiler,'--version'], check=True)
    check = CACHE/'toolchain-checks/csky'
    check.mkdir(parents=True, exist_ok=True)
    (check/'probe.c').write_text('unsigned rotate_word(unsigned x) { return (x << 3) | (x >> 29); }\n')
    # Only this owned scratch directory is writable; neither repo nor keys mounted.
    base = ['docker','run','--rm','--network','none','--platform','linux/amd64',
            '--mount','type=bind,src='+str(target)+',dst=/opt/csky,readonly',
            '--mount','type=bind,src='+str(check)+',dst=/check',IMAGE]
    subprocess.run(base+[compiler,'-mcpu=ck804','-ffreestanding','-O2','-c','/check/probe.c','-o','/check/probe.o'], check=True)
    readelf = compiler.removesuffix('gcc')+'readelf'
    subprocess.run(base+[readelf,'-h','/check/probe.o'], check=True)
    print('Installed local toolchain: version execution and CK804 freestanding object compilation passed. Full GX8002 SDK/runtime and stock flags remain unverified.')

if __name__ == '__main__':
    main()
