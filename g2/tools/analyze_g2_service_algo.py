#!/usr/bin/env python3
"""Fail-closed object/provider audit for platform/audio/service_algo.c."""

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
FM = ROOT / "tools/manifests/g2-service-algo-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-algo-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-algo-provider-map.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/service_algo.c"
HEADER = ROOT / "components/apollo_main/core_overlay/service_algo.h"
SOURCE_PATH = "components/apollo_main/core_overlay/service_algo.c"
HEADER_PATH = "components/apollo_main/core_overlay/service_algo.h"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (11663, "29d1fd5bde0b54d22dd7ec7c355ce76ee35baaf83b33006fe8646ebf329b0265")
HEADER_PIN = (1431, "3bd1145adc91d431cd272d34378e045d2fa76d41e073d083758e83669952101c")
PINS = {
    FM: "c10156f2111df6f073143bb57c9b4e87940b5510eb0b24010b25edad5734e89f",
    CL: "056aa96096da837dd70ee3bf51f754b792253c4e47a0e567a8a78673081499dc",
    PM: "14a2cfc0e0f5ed0032e9728a729f1e2e79ba13bf1e750e080fe19248bc12ca90",
}
F = (
    (0x5915DC, 0x5915EA), (0x5915EA, 0x59173A), (0x59173A, 0x59187A),
    (0x59187A, 0x59188E), (0x59188E, 0x5918B0), (0x5918B0, 0x5918CC),
    (0x5918CC, 0x591BA4), (0x591BA4, 0x591BFC), (0x591BFC, 0x591C26),
    (0x591C26, 0x591C8C),
)
FUNCTIONS = (
    "open_cfw_service_algo_front_buffer_get",
    "algo_front_data_preprocess",
    "SVC_SSRProcess",
    "open_cfw_service_algo_quiet_nan",
    "open_cfw_service_algo_float_hook",
    "open_cfw_service_algo_delay_to_angle",
    "open_cfw_service_algo_cross_correlation",
    "open_cfw_service_algo_source_angle",
    "open_cfw_service_algo_process",
    "open_cfw_service_algo_energy_window_update",
)
APPLE_OFFSETS = (368332, 368360, 368972, 369212, 369228, 369236, 369876, 372620, 372780, 372848)
APPLE_SIZES = (26, 610, 238, 16, 2, 640, 2744, 160, 68, 258)
LINUX_OFFSETS = (153056, 153084, 153700, 153956, 153972, 153980, 154620, 157364, 157524, 157592)
LINUX_SIZES = (26, 614, 256, 16, 2, 640, 2744, 160, 68, 248)
PHYS = (0x5915DC, 0x591D14)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x43C0E4, 0x43C260, 0x59C7AC, 0x59C800}
DIVISION = {0x47CC60}
EXTERNAL_TARGET_COUNTS = {
    0x43C0E4: 3, 0x43C260: 1, 0x43CE9E: 3, 0x43D0CE: 9,
    0x43D574: 3, 0x47CC60: 6, 0x59C7AC: 4, 0x59C800: 2,
}
PATH_REFS = [0x59161E, 0x591764, 0x5917E2]


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
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    redirects = {
        item.get("runtime_address"): item.get("target_function")
        for item in overlay["patch_sites"]
        if item.get("runtime_address") == 0x47CC60
    }
    if redirects != {0x47CC60: "open_cfw_aeabi_uldivmod"}:
        raise c.AuditError("64-bit division production ownership changed")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    _provenance()
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
    if anchored != 2 or len(body) != 1712 or sh(body) != "3305e7f03d2467f82f7eee882a91a397175e7d8f83c2b7c182eb814d559fac78":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 574:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "c498644a69a2a0eaaeafb8a2104feacc0daaab776442fd5656994f957c0bae7d":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, 0x591C8C, 0x591D14)
    if len(pool) != 136 or sh(pool) != "e08361f2d9bbcf8c65bedb898254ba263631f14fefc98f77598c7ca75f843459":
        raise c.AuditError("object pool changed")
    if sh(c._slice(blob, *PHYS)) != "192014709d2eb4d2060037484a59e6594b0aabe7044c99a340da8070b9256322":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x5915CA, 0x5915DC)) != "a2cc2b4f9f725756d6e8a0889886aec7b4eecbc1ad773fe66761f21b5ee8c3b5":
        raise c.AuditError("preceding object boundary changed")
    if sh(c._slice(blob, 0x591D14, 0x591D54)) != "8a20256bb273bfb5689c2ddae82bba3296413ab86568c4d9a3308c93b4f9ffb7":
        raise c.AuditError("following object boundary changed")

    # Pin the exact compiler-math bodies that explain every reusable math edge.
    for bounds, expected in {
        (0x43C260, 0x43C36E): "b69e1f84d2bade8702adfb2fd50ac4cb218a8d50af0fbc28a9c8f92d7692b558",
        (0x59C7AC, 0x59C800): "eebedaca845140b15ab5ffbe3ed94e135d303dc976ac2e5d320bcdb7e4d0b596",
        (0x59C800, 0x59C81C): "dbb01d401deb7e25eb46eaa901dfae2231f08896ef1eb4ab488c1cc61c2a35bd",
    }.items():
        if sh(c._slice(blob, *bounds)) != expected:
            raise c.AuditError("IAR math helper changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, DIVISION)
    if len(calls) != 43 or sum(target in starts for _, target in calls) != 12:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "028d48f20b6996de8a5b761340193d872ee91672cc7e711ac23a7e2ffb477673":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (15, 10, 6):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 15 or c._pair_digest(entries) != "f4efe303d946087acb4fdbda3a44aac01bf1e08b790d420208db1121e67e2a85":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored:
        raise c.AuditError("unexpected stored entry pointer")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_algo.c"
    if _cstring(blob, 0x7052B4) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x591CA0) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x770B14: "algo_front_data_preprocess",
        0x788680: "SVC_SSRProcess",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("audio algorithm symbol changed")

    source = SOURCE.read_bytes()
    header = HEADER.read_bytes()
    if (len(source), sh(source)) != SOURCE_PIN or (len(header), sh(header)) != HEADER_PIN:
        raise c.AuditError("production service-algorithm source changed")
    source_text = source.decode("utf-8")
    required_source_contract = (
        "size != OPEN_CFW_SERVICE_ALGO_INPUT_BYTES",
        "OPEN_CFW_SERVICE_ALGO_FRAMES 800u",
        "OPEN_CFW_SERVICE_ALGO_ENERGY_WINDOWS 10u",
        "for (lag = -maximum_lag; lag <= maximum_lag; ++lag)",
        "open_cfw_service_algo_delay_to_angle",
    )
    combined_text = source_text + "\n" + header.decode("utf-8")
    if any(token not in combined_text for token in required_source_contract):
        raise c.AuditError("production service-algorithm contract changed")

    overlay = json.loads(OVERLAY.read_text())
    header_records = [item for item in overlay["sources"] if item.get("path") == HEADER_PATH]
    if len(header_records) != 1 or (header_records[0].get("size"), header_records[0].get("sha256")) != HEADER_PIN:
        raise c.AuditError("production service-algorithm header admission changed")
    leaves = [
        item for item in overlay["relocated_leaves"]
        if item.get("source", {}).get("path") == SOURCE_PATH
    ]
    if tuple(item.get("function") for item in leaves) != FUNCTIONS:
        raise c.AuditError("production service-algorithm leaf inventory changed")
    if tuple(item["expected"]["offset"] for item in leaves) != APPLE_OFFSETS or tuple(item["expected"]["size"] for item in leaves) != APPLE_SIZES:
        raise c.AuditError("Apple service-algorithm placement changed")
    linux = [item.get("toolchain_profiles", {}).get("linux-clang", {}) for item in leaves]
    if tuple(item.get("expected", {}).get("offset") for item in linux) != LINUX_OFFSETS or tuple(item.get("expected", {}).get("size") for item in linux) != LINUX_SIZES:
        raise c.AuditError("Linux service-algorithm placement changed")
    if sum(len(item.get("relocations", [])) for item in leaves) != 20 or sum(len(item.get("relocations", [])) for item in linux) != 20:
        raise c.AuditError("service-algorithm relocation closure changed")
    if any(
        item.get("profiles") != ["apple-clang", "linux-clang"] or
        item.get("strict_relocation_contract") is not True or
        item.get("source", {}).get("license") != "MIT" or
        (item.get("source", {}).get("size"), item.get("source", {}).get("sha256")) != SOURCE_PIN
        for item in leaves
    ):
        raise c.AuditError("service-algorithm production policy changed")

    patches = [item for item in overlay["patch_sites"] if item.get("name", "").startswith("replace_service_algo_")]
    if len(patches) != 10:
        raise c.AuditError("service-algorithm redirect count changed")
    for index, (patch, bounds, function) in enumerate(zip(patches, F, FUNCTIONS), 1):
        start, end = bounds
        if (
            patch.get("name") != f"replace_service_algo_{index:02d}" or
            patch.get("runtime_address") != start or
            patch.get("expected_size") != end - start or
            patch.get("expected_sha256") != sh(c._slice(blob, start, end)) or
            patch.get("target_function") != function or
            patch.get("branch") != "b_w" or
            patch.get("profiles") != ["apple-clang", "linux-clang"]
        ):
            raise c.AuditError(f"service-algorithm redirect {index:02d} changed")

    report = json.loads(REPORT.read_text())
    built = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path") == SOURCE_PATH
    ]
    if (
        report.get("toolchain", {}).get("profile") != "apple-clang" or
        len(built) != 10 or
        sum(item["extraction"]["size"] for item in built) != 4762 or
        sum(item["placement"]["padding_before"] for item in built) != 14 or
        sum(item["extraction"]["relocation_count"] for item in built) != 20
    ):
        raise c.AuditError("built service-algorithm leaf closure changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    tiled = []
    for region in manifest["component_overrides"]["apollo_main"]["regions"]:
        start = region.get("target_address")
        if start is None:
            continue
        end = start + region.get("size", 0)
        lo, hi = max(PHYS[0], start), min(PHYS[1], end)
        if lo < hi:
            tiled.append((lo, hi, region.get("address_status"), region.get("name")))
    if len(tiled) != 25 or tiled[0][0] != PHYS[0] or tiled[-1][1] != PHYS[1] or any(a[1] != b[0] for a, b in zip(tiled, tiled[1:])):
        raise c.AuditError("service-algorithm manifest tiling changed")
    status_bytes = Counter()
    status_regions = Counter()
    for lo, hi, status, _ in tiled:
        status_bytes[status] += hi - lo
        status_regions[status] += 1
    if status_bytes != Counter({"official_blob": 1808, "generated_source_data_replacement": 40}) or status_regions != Counter({"generated_source_data_replacement": 15, "official_blob": 10}):
        raise c.AuditError("service-algorithm manifest ownership changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\audio\service_algo.c",
            "nationalchip_lvp_code_linked": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 10,
            "ghidra_discovered_functions": 10,
            "restored_functions": 10,
            "path_anchored_functions": 2,
            "raw_path_references": 3,
            "raw_path_referencing_functions": 2,
            "body_bytes": 1712,
            "physical_bytes": 1848,
            "outer_pool_bytes": 136,
            "reachable_instructions": 574,
            "direct_body_calls": 43,
            "internal_direct_body_calls": 12,
            "external_direct_body_calls": 31,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 15,
            "stored_entry_pointers": 0,
        },
        "behavior": {
            "stereo_frame_count": 800,
            "required_input_bytes": 3200,
            "stock_size_check": "non-null, four-byte aligned, and <= 3200",
            "stock_short_aligned_input_is_accepted_but_read_as_3200_bytes": True,
            "production_size_check": "non-null and exactly 3200 bytes",
            "production_short_input_rejected": True,
            "rolling_energy_windows": 10,
            "correlation_lag_min": -10,
            "correlation_lag_max": 10,
            "angle_output_unit": "signed degrees",
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 15,
            "iar_dlib_memory_math_calls": 10,
            "source_owned_unsigned_64_division_calls": 6,
            "iar_memset_calls": 3,
            "iar_asin_calls": 1,
            "iar_signed_64_to_double_calls": 4,
            "iar_sqrt_calls": 2,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "source_admitted": True,
            "production_routed": True,
            "candidate": SOURCE_PATH,
            "source_functions": 10,
            "compiled_text_bytes": 4762,
            "linux_compiled_text_bytes": 4774,
            "generated_alignment_bytes": 14,
            "linux_generated_alignment_bytes": 12,
            "strict_relocations": 20,
            "guarded_redirects": 10,
            "functionally_displaced_stock_body_bytes": 1712,
            "manifest_changed_entry_bytes": 40,
            "physically_retained_compatibility_bytes": 1808,
            "retained_literal_pool_bytes": 136,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": "Acoustic equivalence, G2 microphone spacing/polarity, and live lag-to-angle behavior require an authorized physical G2 pair or authenticated golden microphone vectors; validation is blocked by unavailable physical evidence.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
