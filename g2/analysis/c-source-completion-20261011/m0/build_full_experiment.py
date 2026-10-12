#!/usr/bin/env python3
"""Deterministic relocatable CASE experiment; never emits a flash image."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
SELECTED = ROOT / 'g2/components/case/source_candidate_20261010/build/libcase_source_candidate.a'
SELECTED_RECEIPT = ROOT / 'g2/analysis/case-source-candidate-round2-20261010/receipt.json'
CANDIDATE = HERE / 'case-build/libcase_command_candidate.a'
LD = '/opt/homebrew/bin/arm-none-eabi-ld'
NM = '/opt/homebrew/bin/arm-none-eabi-nm'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path, required=True,
                    help='relocatable output .o path; no executable image is produced')
args = parser.parse_args()
expected = json.loads(SELECTED_RECEIPT.read_text())['archive_sha256']
if sha(SELECTED) != expected:
    raise SystemExit('selected CASE archive differs from its pinned build receipt')
selected_receipt = json.loads(SELECTED_RECEIPT.read_text())
public_selected = {'case_binary_command', 'case_legacy_command',
                   'case_vformat'} <= set(selected_receipt['provided_symbols'])
if not public_selected:
    subprocess.run(['python3', str(HERE / 'build_case_candidate.py')], check=True,
                   stdout=subprocess.DEVNULL)
args.output.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    hashes = []
    for index in range(2):
        result = temp / f'case-{index}.o'
        inputs = [str(SELECTED)] if public_selected else [str(SELECTED), str(CANDIDATE)]
        subprocess.run([LD, '-r', '--whole-archive', *inputs,
                        '--no-whole-archive', '-o', str(result)],
                       check=True, capture_output=True, text=True)
        hashes.append(sha(result))
    if hashes[0] != hashes[1]:
        raise SystemExit('combined relocatable build is not deterministic')
    args.output.write_bytes((temp / 'case-0.o').read_bytes())
names = subprocess.run([NM, '-u', str(args.output)], check=True,
                       capture_output=True, text=True).stdout
unresolved = sorted(line.split()[-1] for line in names.splitlines() if line.split())
receipt = {
    'status': 'CASE_EXPERIMENT_RELOCATABLE_ONLY',
    'output': str(args.output.resolve()),
    'sha256': sha(args.output),
    'rebuild_identical': True,
    'selected_archive_sha256': sha(SELECTED),
    'command_candidate_archive_sha256': None if public_selected else sha(CANDIDATE),
    'public_providers_selected': public_selected,
    'undefined_symbols': unresolved,
    'undefined_count': len(unresolved),
    'limits': ['not a flash image', 'not selected production firmware',
               'unresolved hardware/transport and source contracts remain'],
}
args.output.with_suffix(args.output.suffix + '.receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'output': receipt['output'], 'sha256': receipt['sha256'],
                  'undefined_count': len(unresolved)}, indent=2))
