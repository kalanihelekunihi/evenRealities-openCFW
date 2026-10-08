#!/usr/bin/env python3
"""Authenticate the four startup handlers and emit bounded stock disassembly."""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
IMAGE = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
FUNCTIONS = ROOT / "g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/functions-000.jsonl"
EXPECTED_IMAGE = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
TARGETS = [0x42abbc, 0x42bdf0, 0x42d6c0, 0x42f670,
           0x41ce52, 0x41cc04, 0x421548, 0x4213e6, 0x41d28a,
           0x42d562, 0x42ced8, 0x42cfe0, 0x42d104, 0x42d3bc,
           0x42cea4, 0x42cdf8, 0x41f3f0, 0x41d1c0, 0x41b8ec]
MANUAL = {0x42d5c2:(0x42d5c2,0x42d5cb),
          0x42d5cc:(0x42d5cc,0x42d5f7),
          0x42d63a:(0x42d63a,0x42d691)}
image = IMAGE.read_bytes()
image_sha = hashlib.sha256(image).hexdigest()
if image_sha != EXPECTED_IMAGE:
    raise SystemExit(f"locked image hash mismatch: {image_sha}")
functions = {int(d["entry"], 16): d for d in map(json.loads, FUNCTIONS.read_text().splitlines())}
records = []
chunks = []
for address in TARGETS + list(MANUAL):
    d = functions.get(address)
    if d is None:
        start,end=MANUAL[address]
        d={"name":f"entry_{address:08x}","body_start":f"{start:08x}",
           "body_end_inclusive":f"{end:08x}","body_bytes":end-start+1,
           "callees":[],"body_sha256":None}
    start = int(d["body_start"], 16)
    end = int(d["body_end_inclusive"], 16)
    size = int(d["body_bytes"])
    assert end - start + 1 == size, d
    raw = image[start - 0x410000:end - 0x410000 + 1]
    assert len(raw) == size
    digest = hashlib.sha256(raw).hexdigest()
    if d["body_sha256"] is not None:
        assert digest == d["body_sha256"], (d["name"], digest, d["body_sha256"])
    dis = subprocess.run([
        "arm-none-eabi-objdump", "-D", "-b", "binary", "-m", "arm",
        "-M", "force-thumb", "--adjust-vma=0x410000",
        f"--start-address=0x{start:x}", f"--stop-address=0x{end+1:x}",
        str(IMAGE)], check=True, text=True, capture_output=True).stdout
    chunks.append(dis.rstrip())
    records.append(dict(entry=hex(address), name=d["name"], start=hex(start),
                        end_inclusive=hex(end), bytes=size, sha256=digest,
                        extent_source="byte-bounded return-entry analysis" if address in MANUAL else "Ghidra authenticated function range",
                        callees=[hex(int(c, 16)) for c in d["callees"]]))
(HERE / "stock-disassembly.txt").write_text("\n\n".join(chunks) + "\n")
result = {
    "status": "PASS",
    "image": str(IMAGE.relative_to(ROOT)),
    "image_sha256": image_sha,
    "load_address": "0x410000",
    "architecture": "ARMv8-M Thumb (Cortex-M33 compatible instruction set)",
    "function_source": str(FUNCTIONS.relative_to(ROOT)),
    "entries": records,
    "literal_values": {
        "42abbc": {"0x42ac50": "0x20026ba0", "0x42ad38": "0x400201bc", "0x42acec": "0x40021008", "0x42ace4": "0x1f01600d"},
        "42bdf0": {"0x42bfcc": "0x20026ba0", "0x42c02c": "0x400201bc", "0x42bfd8": "0x40021008", "0x42bfd0": "0x1f01600d"},
        "42d6c0": {"0x42d834": "0x4002000c", "0x42d838": "0x20000098", "0x42d810": "0x200271b3", "0x42d7ac": "0x200271b4", "0x42d844": "0x200271b5", "0x42d83c": "0x200267f8", "0x42d840": "0x3fe00000"}
    },
    "verification": "Indexed Ghidra extents and per-body SHA-256 match the locked image; 42d5c2, 42d5cc, and 42d63a use separately return-bounded extents. Objdump output is bounded to each inclusive extent.",
    "native_differential": "not run: Python Unicorn is unavailable in this execution environment; see REPORT.md."
}
(HERE / "evidence.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS", image_sha, [(r["entry"], r["bytes"], r["sha256"]) for r in records])
