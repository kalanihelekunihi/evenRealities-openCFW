#!/usr/bin/env python3
"""Conservative native Boot catalogue reachability from vector and scatter roots."""
import collections
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BLOB = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
LOCKED = 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
CATALOGUE = ROOT / 'g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl'
CROSSWALK = HERE / 'boot-body-crosswalk-current.json'
assert hashlib.sha256(BLOB.read_bytes()).hexdigest() == LOCKED
native = {int(row['entry'], 16): row for row in map(json.loads, CATALOGUE.open())}
cross = {int(row['entry'], 16): row for row in json.loads(CROSSWALK.read_text())['functions']}

spec = importlib.util.spec_from_file_location('startup_verify',
    ROOT / 'g2/components/bootloader/startup/verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
v = m.v
v.ENTRIES['expand_adapter'] = 0x415326
stock = m.Machine()
stock.cpu.mem_write(0x20000000, b'\xa5' * 1371)
stock.cpu.reg_write(v.a.UC_ARM_REG_R9, 0)
assert stock.run('expand_adapter', [0x433104])['return'] == 0x433110
expanded = bytes(stock.cpu.mem_read(0x20000000, 1371))
blob = BLOB.read_bytes()
vector_roots = {}
for slot in range(256):
    ptr = struct.unpack_from('<I', blob, slot * 4)[0]
    if ptr & 1 and (ptr & ~1) in native:
        vector_roots[slot] = ptr & ~1
callback_offsets = list(range(0x158, 0x158 + 27 * 4, 4)) + [
    0x200, 0x204, 0x208, 0x4cc, 0x4d0, 0x4f4, 0x4f8]
callback_roots = {}
for offset in callback_offsets:
    ptr = struct.unpack_from('<I', expanded, offset)[0]
    assert ptr & 1, (hex(offset), hex(ptr))
    callback_roots[offset] = ptr & ~1

root_addresses = set(vector_roots.values()) | set(callback_roots.values())
queue = collections.deque((address, 0) for address in root_addresses if address in native)
seen = {}
while queue:
    address, depth = queue.popleft()
    if address in seen:
        continue
    seen[address] = depth
    for callee in native[address]['callees']:
        try:
            target = int(str(callee), 16) & ~1
        except ValueError:
            continue
        if target in native and target not in seen:
            queue.append((target, depth + 1))

unmapped = [address for address in seen if cross[address]['status'] == 'no_machine_crosswalk']
root_unmapped = [address for address in root_addresses if address in native and
                 cross[address]['status'] == 'no_machine_crosswalk']
report = {
    'status': 'ROOTED_DIRECT_CALL_GRAPH_CENSUS',
    'original_sha256': LOCKED,
    'vector_slots': 256,
    'vector_catalogue_slots': len(vector_roots),
    'vector_distinct_catalogue_roots': len(set(vector_roots.values())),
    'scatter_callback_roots': len(callback_roots),
    'scatter_callback_catalogue_roots': sum(a in native for a in callback_roots.values()),
    'scatter_callback_entries_not_in_catalogue': [
        {'offset': hex(offset), 'entry': hex(address)}
        for offset, address in callback_roots.items() if address not in native],
    'reachable_catalogue_entries': len(seen),
    'reachable_without_machine_crosswalk': len(unmapped),
    'unattributed_root_entries': [hex(a) for a in sorted(root_unmapped)],
    'largest_reachable_unattributed': [
        {'entry': hex(a), 'name': native[a]['name'], 'body_bytes': native[a]['body_bytes'],
         'direct_depth': seen[a]}
        for a in sorted(unmapped, key=lambda a: native[a]['body_bytes'], reverse=True)[:40]],
    'limits': [
        'The native catalogue omits some valid function entries and may have incomplete direct-call edges.',
        'Reachability from vectors and one expanded callback payload excludes runtime-installed function pointers, task creation, computed dispatch and external ROM callbacks.',
        'Source attribution leads do not prove whole-body equality or physical behavior.',
    ],
}
output = HERE / 'boot-root-reachability-current.json'
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in (
    'vector_distinct_catalogue_roots', 'scatter_callback_catalogue_roots',
    'reachable_catalogue_entries', 'reachable_without_machine_crosswalk',
    'unattributed_root_entries')}))
