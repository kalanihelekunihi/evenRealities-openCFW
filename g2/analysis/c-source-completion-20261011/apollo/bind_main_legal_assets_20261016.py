#!/usr/bin/env python3
"""Integrate all authenticated legal resources into the Apollo Main C object."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
BASE = G2 / 'build/c-firmware/20261016/main-legal-regulatory-chain/apollo-main-legal-regulatory-chain.o'
ASSETS = G2 / 'build/c-firmware/20261016/main-legal-assets/legal-regulatory-assets.o'
ORACLE = G2 / 'build/c-firmware/20261016/main-legal-assets/receipt.json'
OUT = G2 / 'build/c-firmware/20261016/main-legal-assets-bound'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-g', flag, str(path)], text=True).splitlines()}

def main():
    proof = json.loads(ORACLE.read_text())
    if proof['status'] != 'PASS_SOURCE_OWNED_MAIN_LEGAL_ASSETS' or \
            proof['rows'] != 38 or proof['images'] != 10 or \
            proof['object_sha256'] != sha(ASSETS):
        raise RuntimeError('legal asset evidence changed')
    before = symbols(BASE, '-u')
    if len(before) != 182 or 'audio_legal_regulatory_build_5bf332' not in before:
        raise RuntimeError('Apollo main legal base frontier changed')
    provided = symbols(ASSETS, '--defined-only')
    if len(provided) != 39 or 'audio_legal_asset_slots' not in provided or \
            provided & symbols(BASE, '--defined-only') or symbols(ASSETS, '-u'):
        raise RuntimeError('legal asset source ownership changed')
    OUT.mkdir(parents=True, exist_ok=True)
    linked = OUT / 'apollo-main-legal-assets-bound.o'
    subprocess.run(['arm-none-eabi-ld', '-r', str(BASE), str(ASSETS),
                    '-o', str(linked)], check=True)
    after = symbols(linked, '-u')
    if after != before:
        raise RuntimeError('legal asset link changed import frontier')
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_LEGAL_ASSETS_BOUND',
               'asset_oracle': str(ORACLE.relative_to(ROOT)), 'asset_oracle_sha256': sha(ORACLE),
               'asset_object': str(ASSETS.relative_to(ROOT)), 'asset_object_sha256': sha(ASSETS),
               'source_owned_symbols': sorted(provided),
               'base_object': str(BASE.relative_to(ROOT)), 'base_sha256': sha(BASE),
               'linked_object': str(linked.relative_to(ROOT)), 'linked_sha256': sha(linked),
               'unresolved_before': 182, 'unresolved_after': 182,
               'imports_resolved': [], 'imports_added': [],
               'source_complete': False, 'full_payload_linked': False, 'hardware_proof': False,
               'limits': ['The page builder 0x5bf332 is not yet source-bound.',
                          'Resource bytes are C-owned, but stock linker placement and runtime display behavior remain unproved.']}
    path = OUT / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], 182, 182, sha(path))

if __name__ == '__main__': main()
