#!/usr/bin/env python3
"""Prepare isolated IAR image after packages and explicit agreement acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
CACHE = HERE.parents[1] / 'third-party/local-vendor'
NAMES = ['cxarm-10.10.2.27058.deb', 'iar-lmsc-tools_1.14_amd64.deb']

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--license-accepted', action='store_true', help='User has reviewed and accepted the IAR agreements; does not activate a license')
    args = ap.parse_args()
    if not args.apply:
        print('Dry run: verify both registered DEBs, create private build context, build isolated linux/amd64 Ubuntu 24.04 IAR image. No activation.')
        return
    if not args.license_accepted:
        ap.error('Explicit IAR agreement acceptance is required before installation')
    registered = {p['filename']:p for p in json.loads((HERE/'manifest.json').read_text())['packages']}
    for name in NAMES:
        if name not in registered:
            ap.error(name + ': completed download must first be inspected and checksum-registered')
        path = CACHE/'artifacts'/name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != registered[name]['sha256']:
            ap.error(name + ': missing package or checksum mismatch')
    context = CACHE/'container-build'
    context.mkdir(parents=True, exist_ok=True)
    # A fixed whitelist ensures no license material can enter the build context.
    if any(p.name not in NAMES + ['Dockerfile', '.dockerignore'] for p in context.iterdir()):
        ap.error('Unexpected build-context content; inspect manually')
    for name in NAMES:
        shutil.copy2(CACHE/'artifacts'/name, context/name)
    (context/'.dockerignore').write_text('*\n!Dockerfile\n!' + '\n!'.join(NAMES) + '\n')
    (context/'Dockerfile').write_text('FROM --platform=linux/amd64 ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55\nCOPY ' + ' '.join(NAMES) + ' /tmp/packages/\nRUN apt-get update && apt-get install -y /tmp/packages/*.deb && rm -rf /var/lib/apt/lists/* /tmp/packages\nWORKDIR /work\n')
    subprocess.run(['docker','build','--platform','linux/amd64','--tag','opencfw/iar:10.10.2-local',str(context)], check=True)
    print('Image installed. Compiler execution and secure license activation remain separate verification steps; no key was accessed.')

if __name__ == '__main__':
    main()
