#!/usr/bin/env python3
"""Authenticate and unpack the accepted EM SDK without executing shell code."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import zipfile

HERE=Path(__file__).resolve().parent
CACHE=HERE.parents[1]/'third-party/local-vendor'
PAYLOAD='8b987ce7d292fc86adbdf77fcae79f3ce672bd499206b81b2fa80fe46ffbb2a4'

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');a=ap.parse_args()
    if not a.apply:
        print('Dry run: checksum-verify accepted EM ZIP and embedded gzip; safely extract into ignored local-vendor/sources/em9305-v4.6. Never execute shell code or binaries.')
        return
    manifest=json.loads((HERE/'manifest.json').read_text())
    if not manifest.get('acceptance_evidence'):ap.error('User acceptance must first be established')
    p=next(x for x in manifest['packages'] if x['id']=='em9305')
    if p['action']=='license-blocked':ap.error('EM agreement pending')
    archive=CACHE/'artifacts'/p['filename']
    if archive.is_symlink() or hashlib.sha256(archive.read_bytes()).hexdigest()!=p['sha256']:ap.error('ZIP hash mismatch')
    with zipfile.ZipFile(archive) as z:
        members=[m for m in z.infolist() if not m.is_dir()]
        if len(members)!=1 or members[0].file_size>800*1024**2:ap.error('Unexpected wrapper')
        installer=z.read(members[0])
    # The expected complete gzip digest authenticates the static offset.
    offset=installer.find(b'\x1f\x8b\x08')
    if offset<0 or hashlib.sha256(installer[offset:]).hexdigest()!=PAYLOAD:ap.error('Payload hash/offset mismatch')
    target=CACHE/'sources/em9305-v4.6';target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if target.is_symlink() or (target/'.payload-sha256').read_text().strip()!=PAYLOAD:ap.error('Existing destination provenance mismatch')
        print('SDK already extracted; no installer executed');return
    with tempfile.TemporaryDirectory(dir=target.parent) as temp:
        staging=Path(temp)/'sdk';staging.mkdir()
        with tarfile.open(fileobj=io.BytesIO(installer[offset:]),mode='r:gz') as t:
            members=t.getmembers()
            if len(members)>20000 or sum(m.size for m in members)>2*1024**3:ap.error('Expansion limit exceeded')
            t.extractall(staging,filter='data')
        (staging/'.payload-sha256').write_text(PAYLOAD+'\n');os.rename(staging,target)
    print('EM SDK v4.6 extracted locally. No installer, compiler, hardware tool or activation executed; use/confidentiality restrictions remain.')

if __name__=='__main__':main()
