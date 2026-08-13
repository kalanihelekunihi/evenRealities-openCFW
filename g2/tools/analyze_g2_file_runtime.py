#!/usr/bin/env python3
"""Fail-closed object/provider/production audit for the G2 file runtime."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-file-runtime-function-map.tsv"
CL = ROOT / "tools/manifests/g2-file-runtime-closure.tsv"
PM = ROOT / "tools/manifests/g2-file-runtime-provider-map.tsv"
PINS = {
    FM: "06cc6de63d0ab9acd28305f5beadcb1b4e78ed4f37d5d0337c2f05655516d6fd",
    CL: "95a02044b73eb3386e638cd4f717d982646f3cb44df676fceb6759c2617ee3a2",
    PM: "63ce26618565ad0b7318680bb0e62352979b9cc4d5df2e17d4fe6cba87cdffed",
}
F = (
    (0x474550, 0x4745F4), (0x4745F4, 0x474634), (0x474634, 0x474682),
    (0x474682, 0x474802), (0x474814, 0x474870), (0x474870, 0x4748B4),
    (0x4748B4, 0x474910), (0x474910, 0x47498C), (0x47498C, 0x474A02),
    (0x474A02, 0x474A76), (0x474A76, 0x474B02), (0x474B02, 0x474BB8),
    (0x474BB8, 0x474C66), (0x474C66, 0x474CD2), (0x474CD2, 0x474D16),
    (0x474D16, 0x474D54), (0x474D54, 0x474D9C), (0x474D9C, 0x474E3C),
)
PHYS = (0x474550, 0x474EB4)
DATA = ((0x474802, 0x474814), (0x474E3C, 0x474EB4))
STARTS = {start for start, _ in F}
CMSIS = {0x44971C, 0x4497B6, 0x44981C}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
OWNED_RUNTIME = {0x439CC4, 0x4733EE}
IAR = {0x44B5A0, 0x44B63A}
BACKEND = {
    0x4CFA76, 0x4CFA80, 0x4CFA94, 0x4CFAD0, 0x4CFB08, 0x4CFB40,
    0x4CFB7C, 0x4CFBB2, 0x4CFBE8, 0x4CFC2E, 0x4CFC5C, 0x4CFC66,
    0x4CFCF8, 0x4CFD02,
}
TLSF = {0x4D0722, 0x4D0808, 0x4D0868}
ASSERT = {0x4D09B4}
EXTERNAL_TARGET_COUNTS = {
    0x439CC4: 29, 0x43CE9E: 6, 0x43D0CE: 18, 0x43D574: 6,
    0x44971C: 2, 0x4497B6: 17, 0x44981C: 17,
    0x44B5A0: 2, 0x44B63A: 4, 0x4733EE: 3,
    0x4CFA76: 1, 0x4CFA80: 1, 0x4CFA94: 1, 0x4CFAD0: 1,
    0x4CFB08: 1, 0x4CFB40: 1, 0x4CFB7C: 1, 0x4CFBB2: 1,
    0x4CFBE8: 1, 0x4CFC2E: 1, 0x4CFC5C: 1, 0x4CFC66: 1,
    0x4CFCF8: 1, 0x4CFD02: 1,
    0x4D0722: 1, 0x4D0808: 1, 0x4D0868: 1, 0x4D09B4: 3,
}
PATH_REFS = [
    0x4746AE, 0x47470C, 0x474774, 0x4747C8, 0x474D06, 0x474D46,
    0x474D8C, 0x474DD2, 0x474E12,
]
STORED = [(0x6D1E34, 0x474D9D), (0x791AF1, 0x474CD3), (0x791AF5, 0x474D17)]
SOURCE_OWNED_PATCHES = {
    0x474550: "open_cfw_file_open",
    0x4745F4: "open_cfw_file_close",
    0x474634: "open_cfw_file_read",
    0x474682: "open_cfw_file_write",
    0x474814: "open_cfw_file_seek",
    0x474870: "open_cfw_file_tell",
    0x4748B4: "open_cfw_file_size",
    0x474910: "open_cfw_file_flush",
    0x47498C: "open_cfw_file_remove",
    0x474A02: "open_cfw_file_rename",
    0x474A76: "open_cfw_file_mkdir",
    0x474B02: "open_cfw_file_opendir",
    0x474BB8: "open_cfw_file_readdir",
    0x474C66: "open_cfw_file_closedir",
    0x474CD2: "open_cfw_file_heap_allocate",
    0x474D16: "open_cfw_file_heap_free",
    0x474D54: "open_cfw_file_heap_reallocate",
    0x474D9C: "open_cfw_file_runtime_initialize",
}


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _provenance() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    littlefs = json.loads((ROOT / "third_party/littlefs/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise c.AuditError("FreeRTOS-Kernel source selection changed")
    if littlefs["upstream"]["selected_commit"] != "0494ce7169f06a734a7bd7585f49a9fa91fa7318":
        raise c.AuditError("littlefs source selection changed")
    if littlefs["selection"]["exact_historical_checkout_proven"]:
        raise c.AuditError("littlefs historical provenance overclaim")
    tlsf = (ROOT / "third_party/tlsf/README.openCFW.md").read_text()
    if "deff9ab509341f264addbd3c8ada533678591905" not in tlsf:
        raise c.AuditError("TLSF source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")


def _production_patches() -> None:
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    observed = {
        item.get("runtime_address"): item.get("target_function")
        for item in overlay["patch_sites"]
        if item.get("runtime_address") in SOURCE_OWNED_PATCHES
    }
    if observed != SOURCE_OWNED_PATCHES:
        raise c.AuditError("file-runtime production ownership changed")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    _provenance()
    _production_patches()
    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(F):
        raise c.AuditError("function inventory changed")

    starts, interiors, instructions = set(), set(), {}
    body, calls, indirect, anchored = b"", [], [], 0
    for row, bounds in zip(rows, F):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = c._slice(blob, start, end)
        if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
            raise c.AuditError("function body changed")
        decoded, direct, dynamic = q._recover_function(blob, start, end)
        if c._uncovered(bounds, decoded):
            raise c.AuditError("function has uncovered bytes")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        instructions.update(decoded)
        calls.extend(direct)
        indirect.extend(dynamic)
        body += raw
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(
        c._slice(blob, address, address + item.size)
        for address, item in sorted(instructions.items())
    )
    if anchored != 5 or len(body) != 2266 or sh(body) != "5fd2d6ab6b12aaff1ad96cccffee0c3fd5519dcdb064e684f2d8c33ec8b3ffe7":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 864:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "de955d35e9e218aeffd4cadc5baaccd0d07ce78b7d7c635d504966032a2d39cd":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    data = b"".join(c._slice(blob, *bounds) for bounds in DATA)
    if len(data) != 138 or sh(data) != "ad115f89722dffe579521a2c9f7c3f0b5c8102f10276d94c96b26a27eae69765":
        raise c.AuditError("object data changed")
    if sh(c._slice(blob, *PHYS)) != "594ee91b915f3aca5249480e694ffb053b17537b72fff3f1fca3e338cacbb3b7":
        raise c.AuditError("physical object changed")
    if c._slice(blob, 0x474802, 0x474814) != b"\0\0r\0\0\0w\0\0\0a\0\0\0+\0\0\0":
        raise c.AuditError("file mode literals changed")
    if sh(c._slice(blob, 0x474474, 0x474550)) != "e797384728b5d5f3574d8df7b19d5b615a80b22ade981f382f7963102b360052":
        raise c.AuditError("preceding object boundary changed")
    if sh(c._slice(blob, 0x474EB4, 0x474EFA)) != "774d224f4dce5aa43a0e4f6db01001d5b13fc0f92fbccacfbc3f163212b44acb":
        raise c.AuditError("following cache object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (CMSIS, EASY, OWNED_RUNTIME, IAR, BACKEND, TLSF, ASSERT)
    if len(calls) != 132 or sum(target in starts for _, target in calls) != 8:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "cbeafb5f6b090240e27585fb00fff0b2572da7b7d438c7adb1f914ecc1bebc66":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (36, 30, 32, 6, 14, 3, 3):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 644 or c._pair_digest(entries) != "7cc5b01e9a58767e0b50a2857e1e47d06541d575db340d91d3f76fb8b92db279":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != STORED or c._pair_digest(stored) != "552a439b8468eccbfaf6976003cbece695a6a913186670303b13fd2ab821faf8":
        raise c.AuditError("stored entry topology changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\product\s200\app\config\redirect.c"
    if _cstring(blob, 0x6FC7C4) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x474E54) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure plus production redirect audit",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"product\s200\app\config\redirect.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 18,
            "ghidra_discovered_functions": 18,
            "restored_functions": 0,
            "path_anchored_functions": 5,
            "raw_path_references": 9,
            "raw_path_referencing_functions": 5,
            "body_bytes": 2266,
            "physical_bytes": 2404,
            "data_bytes": 138,
            "reachable_instructions": 864,
            "direct_body_calls": 132,
            "internal_direct_body_calls": 8,
            "external_direct_body_calls": 124,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 644,
            "stored_entry_pointers": 3,
        },
        "provider_boundary": {
            "cmsis_freertos_calls": 36,
            "easylogger_and_compact_calls": 30,
            "production_owned_errno_log_calls": 32,
            "iar_dlib_calls": 6,
            "littlefs_backend_adapter_calls": 14,
            "tlsf_calls": 3,
            "first_party_assert_calls": 3,
            "embedded_third_party_definitions": 0,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "littlefs_version": "v2.10.1-equivalent",
            "littlefs_commit": "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "tlsf_commit": "deff9ab509341f264addbd3c8ada533678591905",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "production_routed": True,
            "source_owned_functions": 18,
            "source_owned_function_entries": [f"0x{address:08X}" for address in sorted(STARTS)],
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
