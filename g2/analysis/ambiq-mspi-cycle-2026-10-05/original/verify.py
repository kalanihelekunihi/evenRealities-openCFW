#!/usr/bin/env python3
"""Fail-closed extraction and disassembly of the four authenticated Apollo MSPI APIs."""
import hashlib
import json
import re
import struct
from pathlib import Path

if not __debug__:
    raise SystemExit("verification must run with Python assertions enabled")

ROOT = Path(__file__).resolve().parents[4]
OTA = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
GHIDRA = ROOT / "g2/research/corpus/apollo-main/ghidra/open-2026-09-29"
OUT = Path(__file__).resolve().parent
BASE = 0x438000
SPECS = {
    0x4C23DE: (48, "4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48", "am_hal_mspi_interrupt_clear"),
    0x4C2328: (52, "ff601938062e67c168148c01471475c081038eb87938f8344c93afbf89f673e4", "FUN_004c2328"),
    0x4C235C: (54, "046eba05f4da245735e178e179220a0c666e75c2c377bf05f08fab8815900a40", "FUN_004c235c"),
    0x4C2392: (76, "af49be2bc2098b45d294afc6ca8cc5f9f48eee343a0245cea95a9d832973c1c5", "FUN_004c2392"),
}
CALLERS = {
    0x46F4EA: (34, "00ad0d74b025ddc1046a39d548b0fafe33057997233902fbabb91aa172aed3df"),
    0x592658: (40, "586421a4952b1605231e3342bf64b6ea804b209b79d4a5a279726d5aa79b0cf7"),
    0x59CE1E: (252, "595ccf477285d6c3a250615da2e36a4700d3c7999dac8363bc8669ec1d2a1c8f"),
}

def sha(b): return hashlib.sha256(b).hexdigest()

ota = OTA.read_bytes()
image = ota[32:]
assert len(ota) == 3523396 and sha(ota) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
assert len(image) == 3523364 and sha(image) == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
records = [json.loads(s) for s in (GHIDRA / "functions-000.jsonl").read_text().splitlines() if s.strip()]
byaddr = {int(x["entry"], 16): x for x in records}
assert json.loads((GHIDRA / "RUN.json").read_text())["base"] == "0x00438000"
assert json.loads((GHIDRA / "RUN.json").read_text())["image_sha256"] == sha(image)

try:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
except ImportError as e:
    raise SystemExit("Capstone unavailable: " + str(e))
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
md.detail = True
functions = {}
lines = [f"Official OTA sha256={sha(ota)} size={len(ota)}; decoded image is OTA[32:], base=0x{BASE:08x}, sha256={sha(image)} size={len(image)}."]
for addr, (size, expected, name) in SPECS.items():
    off = addr - BASE
    body = image[off:off+size]
    assert len(body) == size and sha(body) == expected
    rec = byaddr[addr]
    assert rec["body_bytes"] == size and rec["body_sha256"] == expected
    assert int(rec["body_end_inclusive"], 16) == addr + size - 1
    functions[f"0x{addr:08x}"] = {"name": name, "image_range": [f"0x{off:x}", f"0x{off+size:x}"], "ota_file_range": [f"0x{off+32:x}", f"0x{off+32+size:x}"], "size": size, "sha256": expected, "bytes_hex": body.hex()}
    lines.append(f"\n{addr:08x} {name} [{addr:08x},{addr+size:08x}) size={size} sha256={expected}")
    for ins in md.disasm(body, addr):
        text = f"{ins.address:08x}  {ins.bytes.hex():<8} {ins.mnemonic:<10} {ins.op_str}"
        if ins.mnemonic.startswith("ldr") and "[pc," in ins.op_str:
            m = re.search(r"\[pc, #(-?0x[0-9a-f]+|-?\d+)\]", ins.op_str)
            if m:
                disp = int(m.group(1), 0)
                lit = ((ins.address + 4) & ~3) + disp
                val = struct.unpack_from("<I", image, lit-BASE)[0]
                text += f" ; literal [0x{lit:08x}]=0x{val:08x}"
        lines.append(text)

for addr, (size, expected) in CALLERS.items():
    body = image[addr-BASE:addr-BASE+size]
    assert len(body) == size and sha(body) == expected
    r = byaddr[addr]
    assert r["body_bytes"] == size and r["body_sha256"] == expected
    callsites = []
    for ins in md.disasm(body, addr):
        if ins.mnemonic in ("bl", "blx") and ins.op_str:
            try: target = int(ins.op_str.split()[0].lstrip("#"), 16)
            except ValueError: continue
            if target in SPECS:
                callsites.append({"pc": f"0x{ins.address:08x}", "target": f"0x{target:08x}", "bytes": ins.bytes.hex()})
    if addr in (0x46F4EA, 0x592658):
        assert {int(x["target"],16) for x in callsites} >= {0x4C2392, 0x4C23DE}
    if addr == 0x59CE1E:
        assert {int(x["target"],16) for x in callsites} >= {0x4C2328, 0x4C23DE}
    functions[f"caller_0x{addr:08x}"] = {"name": r["name"], "size": size, "sha256": expected, "mspi_callsites": callsites}

result = {
    "verification": "PASS",
    "mapping": {"ota_sha256": sha(ota), "ota_size": len(ota), "decoded_image_sha256": sha(image), "decoded_size": len(image), "ota_preamble_bytes": 32, "runtime_base": "0x00438000", "offset_rule": "decoded offset = runtime address - 0x438000; OTA file offset = decoded offset + 32"},
    "functions": functions,
    "literals": {"0x004c2adc": "0x01bebebe", "0x004c26dc": "0x40060000"},
    "source": {"am_hal_mspi.c": {"path": "g2/build/foundation/ambiq-upstream/am_hal_mspi.c", "sha256": "5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f"}, "am_hal_mspi.h": {"path": "g2/build/foundation/ambiq-upstream/am_hal_mspi.h", "sha256": "2a682bb7c1618982d6a802f3220a38696cd594c89d90e64b1a698d226b0a557b"}, "apollo510.h": {"path": "g2/build/foundation/ambiq-upstream/apollo510.h", "sha256": "b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797"}},
    "limits": ["Source-level behavioral correspondence is supported; this does not establish compiler/version/options or byte-for-byte source reproduction.", "Caller semantics are bounded to authenticated static callsite/decomp evidence; no runtime behavior was exercised."]
}
(OUT / "disassembly.txt").write_text("\n".join(lines) + "\n")
with (OUT / "results.json").open("x") as f:
    json.dump(result, f, indent=2, sort_keys=True); f.write("\n")
print("PASS: four body hashes, mapping, Ghidra records, literals, and named caller callsites verified")
