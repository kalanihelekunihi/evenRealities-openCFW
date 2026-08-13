#!/usr/bin/env python3
import csv
import collections
import hashlib
import pathlib
import re
import struct
import sys

from capstone import Cs, CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB

root = pathlib.Path(sys.argv[1]).resolve()
firmware = (root/"stock-firmware.bin").read_bytes()
base = 0x00437FE0

def all_hits(needle):
    result = []
    cursor = 0
    while True:
        found = firmware.find(needle, cursor)
        if found < 0:
            return result
        result.append(found)
        cursor = found + 1

markers = []
for label, needle in (
    ("source_basename_wsf_efs.c", b"wsf_efs.c"),
    ("symbol_prefix_WsfEfs", b"WsfEfs"),
    ("symbol_prefix_wsfEfs", b"wsfEfs"),
    ("profile_source_wdxs", b"wdxs_"),
    ("profile_text_WDXS", b"WDXS"),
):
    hits = all_hits(needle)
    markers.append((label, needle.hex(), len(hits), ",".join(hex(x) for x in hits)))

uuid_prefix = bytes((0x65,0x78,0x61,0x63,0x74,0x4c,0x45,0xb0,0xd5,0x4e,0xf2,0x2f))
for part in (2, 3, 4, 5):
    needle = uuid_prefix + bytes((part, 0, 0x5f, 0))
    hits = all_hits(needle)
    markers.append((f"wdx_uuid_{part}", needle.hex(), len(hits), ",".join(hex(x) for x in hits)))

unknown_hits = all_hits(b"Unknown\0")
markers.append(("fallback_Unknown_cstring_nonunique", b"Unknown\0".hex(), len(unknown_hits), ",".join(hex(x) for x in unknown_hits)))

with open(root/"out/marker-census.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("marker", "needle_hex", "stock_hits", "stock_file_offsets"))
    writer.writerows(markers)

# Linear Thumb census over the authenticated image. Skip-data keeps the pass
# deterministic across literal pools; hits are only triage candidates, never
# treated as function boundaries.
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
md.skipdata = True
hits = []
instruction_count = 0
window_queue = collections.deque(maxlen=36)
expected_offsets = {0, 52, 104, 156, 208, 260}
chunk_size = 0x10000
# The authenticated Apollo main executable/Cordio corpus occupies stock file
# offsets [0x40000,0x136000); later bytes are string/data assets and generated
# false Thumb decodes. Existing Cordio source-path xrefs and all bounded WSF
# functions fall within this interval.
scan_start, scan_end = 0x40000, 0x136000
for chunk_start in range(scan_start, scan_end, chunk_size):
    window_queue.clear()
    chunk = firmware[chunk_start:min(scan_end, chunk_start + chunk_size + 128)]
    for decoded in md.disasm(chunk, base + chunk_start):
        if decoded.mnemonic == ".byte":
            continue
        instruction_count += 1
        window_queue.append(decoded)
        if len(window_queue) != 36:
            continue
        window = list(window_queue)
        insn = window[0]
        if insn.mnemonic == "cmp" and re.search(r"#(5|6)$", insn.op_str):
            text = " | ".join(f"{item.mnemonic} {item.op_str}" for item in window)
            stride = any(re.search(r"#(0x34|52)(\D|$)", item.op_str) for item in window)
            multiply = any(item.mnemonic.startswith(("mul", "mla")) for item in window)
            invalid = any("#0xffffffff" in item.op_str or "#-1" in item.op_str for item in window)
            if stride or (multiply and invalid):
                hits.append((hex(insn.address), "handle_bound_plus_stride_or_invalid", int(stride), int(multiply), int(invalid), text))

        # Unrolled WsfEfsInit has stores of -1 to six 52-byte-spaced maxSize cells.
        init_window = window[:30]
        found = set()
        for item in init_window:
            if item.mnemonic.startswith("str"):
                match = re.search(r"#(0x[0-9a-f]+|[0-9]+)\]", item.op_str)
                if match:
                    found.add(int(match.group(1), 0))
                elif "[" in item.op_str and "," not in item.op_str.split("[",1)[1]:
                    found.add(0)
        if expected_offsets.issubset(found):
            text = " | ".join(f"{item.mnemonic} {item.op_str}" for item in init_window)
            hits.append((hex(insn.address), "six_52byte_spaced_stores", 1, 0, int(any("#0xffffffff" in item.op_str or "#-1" in item.op_str for item in init_window)), text))

# Coalesce duplicate sliding-window reports while retaining every distinct start.
unique = []
seen = set()
for row in hits:
    key = (row[0], row[1])
    if key not in seen:
        seen.add(key); unique.append(row)
with open(root/"out/semantic-triage-hits.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("address", "fingerprint", "has_stride_52", "has_multiply", "has_invalid_minus1", "instruction_window"))
    writer.writerows(unique)

# Authenticated archive consumer topology. Outside wsf_efs.c itself, every API
# reference should resolve to the WDXS profile family.
consumer_rows = []
for path in sorted((root/"consumer-corpus").glob("*")):
    if not path.is_file():
        continue
    text = path.read_text(errors="replace")
    names = sorted(set(re.findall(r"\bWsfEfs[A-Za-z0-9_]+", text)))
    consumer_rows.append((path.name, path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest(), len(names), ";".join(names)))
with open(root/"out/archive-consumer-topology.tsv", "w", newline="") as f:
    writer = csv.writer(f, delimiter="\t", lineterminator="\n")
    writer.writerow(("source_basename", "bytes", "sha256", "distinct_wsf_efs_apis", "api_names"))
    writer.writerows(consumer_rows)

print("instructions", instruction_count, "semantic_triage_hits", len(unique), "marker_zeroes", sum(row[2] == 0 for row in markers), "consumer_files", len(consumer_rows))
