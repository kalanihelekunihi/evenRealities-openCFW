#!/usr/bin/env python3
"""Checksum-verified local SDK staging. Never executes vendor installers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / 'third-party/local-vendor'

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def identity(path, kind):
    if path.is_symlink():
        raise ValueError('Symlink input refused')
    if kind == 'file':
        return digest(path)
    rows = []
    for p in sorted(path.rglob('*')):
        if p.is_symlink():
            raise ValueError('Symlink in source tree refused')
        if p.is_file():
            rows.append(dict(path=p.relative_to(path).as_posix(), bytes=p.stat().st_size, sha256=digest(p)))
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def clone_file(src, dst):
    # APFS clone is independent copy-on-write, never a hard link to Downloads.
    if sys.platform == 'darwin':
        result = subprocess.run(['/bin/cp', '-c', str(src), str(dst)], capture_output=True)
        if result.returncode == 0:
            return
        if dst.exists():
            dst.unlink()
    shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=['stage', 'check', 'extract'])
    ap.add_argument('--downloads', type=Path, default=Path.home() / 'Downloads')
    ap.add_argument('--id', action='append')
    ap.add_argument('--apply', action='store_true', help='Perform local copies or safe ZIP extraction; default is dry run')
    args = ap.parse_args()
    packages = json.loads((HERE / 'manifest.json').read_text())['packages']
    known = {p['id'] for p in packages}
    if args.id and not set(args.id) <= known:
        ap.error('Unknown package id')
    for p in packages:
        if args.id and p['id'] not in args.id:
            continue
        if p['action'] == 'license-blocked':
            print(p['id'] + ': BLOCKED pending explicit EM agreement decision; no payload copy/use')
            continue
        dest = CACHE / ('sources' if p['kind'] == 'directory' else 'artifacts') / p['filename']
        src = dest if args.command == 'check' else args.downloads / p['filename']
        if not src.exists():
            raise FileNotFoundError(src)
        if identity(src, p['kind']) != p['sha256']:
            raise ValueError(p['id'] + ': checksum mismatch; refusing operation')
        print(p['id'] + ': checksum OK')
        if args.command == 'check':
            continue
        if args.command == 'extract':
            if p['id'] != 'csky':
                raise ValueError('Only the C-SKY outer ZIP is approved for data-only extraction here')
            target = CACHE / 'extracted' / p['id']
            if target.exists():
                raise ValueError('Extraction destination already exists; inspect it rather than overwrite')
            with zipfile.ZipFile(src) as z:
                seen = set()
                for m in z.infolist():
                    path = Path(m.filename)
                    mode = m.external_attr >> 16
                    if path.is_absolute() or '..' in path.parts or '\\' in m.filename or m.filename in seen or (mode & 0o170000) not in (0, 0o100000, 0o040000):
                        raise ValueError('Unsafe ZIP member')
                    seen.add(m.filename)
                if len(seen) > 20000 or sum(m.file_size for m in z.infolist()) > 4 * 1024**3:
                    raise ValueError('Archive expansion limit exceeded')
                print('Extract data only -> ' + str(target))
                if args.apply:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with tempfile.TemporaryDirectory(dir=target.parent) as tmp:
                        z.extractall(tmp)
                        os.rename(tmp, target)
            continue
        if dest.exists():
            if identity(dest, p['kind']) != p['sha256']:
                raise ValueError('Existing destination differs; refusing overwrite')
            print('Already staged: ' + str(dest))
            continue
        print(('Copy -> ' if args.apply else 'Would copy -> ') + str(dest))
        if args.apply:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=dest.parent) as tmp:
                staging = Path(tmp) / p['filename']
                if p['kind'] == 'directory':
                    shutil.copytree(src, staging, copy_function=clone_file)
                else:
                    clone_file(src, staging)
                if identity(staging, p['kind']) != p['sha256']:
                    raise ValueError('Copied content checksum mismatch')
                os.rename(staging, dest)

if __name__ == '__main__':
    main()
