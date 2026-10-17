#!/usr/bin/env python3
"""Bound candidate registry callbacks by stock disassembly and owner literals."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OBJ = ROOT / 'g2/build/c-firmware/20261017/main-uart-sync-storage/candidate.o'
DIS = ROOT / 'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = ROOT / 'g2/analysis/c-source-completion-20261011/apollo/main-registry-callback-priorities-20261017.json'
BASE = 0x438000
LINE = re.compile(r'^\s*([0-9a-f]+):\s+([0-9a-f ]+)\s+(.+)$')
LITERAL = re.compile(r'@\s*\(?0x([0-9a-f]+)\)?')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    names = sorted({line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(OBJ)], text=True).splitlines()
        if 'audio_uart_registry_callback_' in line})
    wanted = {int(name.rsplit('_', 1)[-1], 16): name for name in names}
    lines = []
    for line in DIS.read_text(errors='replace').splitlines():
        match = LINE.match(line)
        if match:
            lines.append((int(match.group(1), 16), match.group(3).strip()))
    by_addr = {addr: i for i, (addr, _) in enumerate(lines)}
    payload = STOCK.read_bytes()[32:]
    def word(addr):
        off = addr-BASE
        return int.from_bytes(payload[off:off+4], 'little') if 0 <= off <= len(payload)-4 else 0
    def string(addr):
        off = addr-BASE
        if not 0 <= off < len(payload): return ''
        value = payload[off:off+150].split(b'\0')[0]
        return value.decode('utf-8', 'replace') if len(value)>3 and all(32<=c<127 for c in value) else ''
    records = []
    for start, name in sorted(wanted.items()):
        i = by_addr.get(start)
        if i is None: raise RuntimeError(f'missing disassembly {name}')
        window = [(a, op) for a, op in lines[i:] if a < start+0x120]
        first_return = next((a for a, op in window if re.search(r'\b(pop|bx)\b.*\b(pc|lr)\b', op)), None)
        literals = []
        for a, op in window:
            m = LITERAL.search(op)
            if m:
                value = string(word(int(m.group(1), 16)))
                if value and value not in literals: literals.append(value)
        owner = 'evenhub' if any('evenhub' in v.lower() for v in literals) else 'other-or-undetermined'
        records.append({'symbol': name, 'address': hex(start),
                        'first_return_offset': None if first_return is None else first_return-start,
                        'literal_strings': literals[:8], 'owner_hint': owner,
                        'limit': 'First return and nearby strings are triage hints, not a verified function extent or complete owner attribution.'})
    result = {'status': 'PASS_MAIN_REGISTRY_CALLBACK_TRIAGE',
              'candidate_object': str(OBJ.relative_to(ROOT)), 'candidate_sha256': sha(OBJ),
              'stock_package_sha256': sha(STOCK),
              'disassembly_sha256': sha(DIS), 'callback_count': len(records),
              'callbacks': records,
              'remaining_gate': 'Verify exact function bounds and behavior before implementing any callback; avoid EvenHub SDK owner candidates.'}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'], len(records), sha(OUT))

if __name__ == '__main__': main()
