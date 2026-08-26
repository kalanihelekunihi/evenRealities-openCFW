#!/usr/bin/env python3
"""Fail-closed G2 Cordio WSF assert/trace recovery audit."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

TRACE_START, TRACE_END = 0x0052A63C, 0x0052A672
TRACE_SHA256 = "80980ca4a2a21e3a3223b6dae5bb0a5a06d9e754f047cc7ee0a1119e035a71a5"
TRACE_DATA_START, TRACE_DATA_END = 0x0052A672, 0x0052A67C
TRACE_DATA_SHA256 = "d47ac31e6dcdb63fa60f3c338e671d53e34ca4d78e68a5ae22910c4d64fbdb8c"
ASSERT_START, ASSERT_END = 0x00569A44, 0x00569ADE
ASSERT_SHA256 = "526251ab7ee29a39694834da3f57bb85498c282bde7c017b2841ce97da6f3406"
ASSERT_DATA_START, ASSERT_DATA_END = 0x00569ADE, 0x00569B04
ASSERT_DATA_SHA256 = "79487c70333bae49261c027afea943ddd5bfdc4c9d47b9841bbe68ac9b0ddd33"

TRACE_CALLER_COUNT = 126
TRACE_CALLER_SHA256 = "c59e067215d93c6223ba1bfc5bbb016907230efec5ad235715985b76214bf1b4"
ASSERT_CALLERS = [0x0052A660]

FUNCTION_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-assert-trace-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-assert-trace-provenance.tsv"
MATRIX_MANIFEST = ROOT / "research/readiness/wsf-assert-trace/SHA256SUMS"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"

PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.c": "6550117694d15172060094d177c12785cc4af2810af6fdda21a01157986d101a",
    ROOT / "components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.h": "6e0a5a9f95889a32e24e3c56f0990e719bc34e232bfa6236c6d917907e420f42",
    FUNCTION_MAP: "47df6f62617303f24bed39e7e0b13e7c35efb2eae86bae4e662d309350c96da9",
    PROVENANCE: "95f6c236f755e1e327c31b323b03cc7871986d46a2425a1f13f165dd3bca6c13",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-best-size.tsv": "c1fb6888e072c7fe5ce81d9f6fae77b26db6ce5572a5e1ad45159ac5f8f0e584",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-config-summary.tsv": "3f639fa0c05e50001617f0f8291dce56a22654603201e71c3747b969ebcdc89e",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-functions.tsv": "e5e9e4bdcead5f73eb192328f95a83797ee928aeba8fdfd068cfff02ecdb4910",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-include-closure.tsv": "27899d513114fbee152fa597771cadaeb6d735980671c9188d1ba402709a12ea",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-provider-closure.tsv": "db66eaa39e9a1cdc8a3dd90ef9319b236fe603b49c9423788432c92d5a570aa3",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-source-config-variants.tsv": "e2ed57a38ae8f226d884dce6c1d5da14ff8f208906cbb64ace61487e20a7cf58",
    ROOT / "tools/manifests/readiness-cordio-wsf-assert-trace-source-identities.tsv": "6bb3b1906095778190fb8bfcd8fd3e17816f5127e0f411d9f17ad370632f48fa",
    MATRIX_MANIFEST: "ed6bb9cf572b3e791d992893fbbf33e1cc3e7431c07de3a28f779aa92e66b739",
}

CALLEES = {
    TRACE_START: [(0x0052A64C,0x00473036),(0x0052A652,0x004733EE),(0x0052A660,ASSERT_START),(0x0052A666,0x004733EE)],
    ASSERT_START: [(0x00569A52,0x0043D0CE),(0x00569A72,0x0043D574),(0x00569A76,0x0043D0CE),(0x00569A7E,0x0043D0CE),(0x00569A94,0x0043CE9E),(0x00569ABE,0x0043D574),(0x00569AC2,0x0044B0AE)],
}


class AuditError(RuntimeError):
    """Raised when closed WSF assert/trace evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _cstr(blob: bytes, address: int, limit: int = 160) -> str:
    return _slice(blob, address, address + limit).split(b"\0", 1)[0].decode("ascii")


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("wsf_assert_trace_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _callers(blob: bytes, decoder: Any, target: int) -> list[int]:
    return [
        address
        for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2)
        if decoder._thumb_bl_target(blob, address) == target
    ]


def _packed_address_sha256(addresses: list[int]) -> str:
    return _sha256(b"".join(struct.pack("<I", value) for value in addresses))


def _verify_no_stored_pointers(blob: bytes) -> None:
    intervals = [(TRACE_START, TRACE_END), (ASSERT_START, ASSERT_END)]
    targets = {
        address | thumb
        for start, end in intervals
        for address in range(start, end, 2)
        for thumb in (0, 1)
    }
    excluded = {
        offset
        for start, end in intervals
        for offset in range(start - LOAD_BASE, end - LOAD_BASE, 4)
    }
    for offset in range(0, len(blob) - 3, 4):
        if offset not in excluded and struct.unpack_from("<I", blob, offset)[0] in targets:
            raise AuditError(f"unexpected stored assert/trace pointer at 0x{LOAD_BASE + offset:08x}")


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned assert/trace input changed: {path.name}")

    for start, end, expected in (
        (TRACE_START, TRACE_END, TRACE_SHA256),
        (TRACE_DATA_START, TRACE_DATA_END, TRACE_DATA_SHA256),
        (ASSERT_START, ASSERT_END, ASSERT_SHA256),
        (ASSERT_DATA_START, ASSERT_DATA_END, ASSERT_DATA_SHA256),
    ):
        if _sha256(_slice(blob, start, end)) != expected:
            raise AuditError(f"assert/trace stock span changed at 0x{start:08x}")

    decoder = _load_decoder()
    trace_callers = _callers(blob, decoder, TRACE_START)
    assert_callers = _callers(blob, decoder, ASSERT_START)
    if len(trace_callers) != TRACE_CALLER_COUNT or _packed_address_sha256(trace_callers) != TRACE_CALLER_SHA256:
        raise AuditError("WsfTrace direct caller closure changed")
    if assert_callers != ASSERT_CALLERS:
        raise AuditError("WsfAssert direct caller closure changed")
    for entry, calls in CALLEES.items():
        for site, target in calls:
            if decoder._thumb_bl_target(blob, site) != target:
                raise AuditError(f"assert/trace callee changed at 0x{site:08x}")
    _verify_no_stored_pointers(blob)

    trace_path = _cstr(blob, 0x006DF094)
    assert_path = _cstr(blob, 0x006DEFD4)
    suffixes = (
        r"third_party\cordio\wsf\sources\port\freertos\wsf_trace.c",
        r"third_party\cordio\wsf\sources\port\freertos\wsf_assert.c",
    )
    if not trace_path.endswith(suffixes[0]) or not assert_path.endswith(suffixes[1]):
        raise AuditError("retained assert/trace source path changed")
    assert_words = struct.unpack("<9I", _slice(blob, 0x00569AE0, 0x00569B04))
    if assert_words != (0x00789F60,0x0078C938,0x006DEFD4,0x0078C944,0x00774A84,0x2007456C,0x0078EE14,0x0075D35C,0x0078EE0C):
        raise AuditError("WsfAssert literal/global table changed")

    source_path = "components/shared/cordio/runtime_cordio_wsf_assert_trace_candidate.c"
    names = [
        "open_cfw_cordio_wsf_trace_candidate",
        "open_cfw_cordio_wsf_assert_candidate",
    ]
    spans = [
        (TRACE_START, TRACE_END, TRACE_SHA256),
        (ASSERT_START, ASSERT_END, ASSERT_SHA256),
    ]
    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves = [
        row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == source_path
    ]
    if len(leaves) != 2 or any(
        row.get("source", {}).get("sha256") != PINNED_INPUTS[ROOT / source_path]
        for row in leaves
    ):
        raise AuditError("WSF assert/trace production inventory changed")
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, ((start, end, expected), function) in enumerate(
        zip(spans, names), 1
    ):
        site = sites.get(f"replace_cordio_wsf_assert_trace_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"WSF assert/trace production route {index} changed")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - 335208
    alignment += (
        leaves[1]["expected"]["offset"] - leaves[0]["expected"]["offset"]
        - leaves[0]["expected"]["size"]
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (170, 0, 5):
        raise AuditError("WSF assert/trace production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        build["overlay"]["size"] != 404796
        or build["overlay"]["sha256"] != "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d"
        or build["component"]["size"] != 3928192
        or build["component"]["sha256"] != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or override["provider"].get("size") != 3928192
        or override["provider"].get("sha256") != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or len([row for row in override["regions"] if row["name"].startswith("cordio_wsf_assert_trace_")]) != 4
    ):
        raise AuditError("WSF assert/trace component/manifest changed")
    if (
        PACKAGE.stat().st_size != 4706686
        or _sha256(PACKAGE.read_bytes()) != "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
    ):
        raise AuditError("WSF assert/trace package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != 4071097
        or _sha256(FLASH_PLAN.read_bytes()) != "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d"
        or (
            len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]),
        ) != (5863, 2, 5, 6)
    ):
        raise AuditError("WSF assert/trace flash plan changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "functions": {
            "WsfTrace": {"start": TRACE_START, "end_exclusive": TRACE_END, "size": 54, "sha256": TRACE_SHA256, "direct_bl_callers": trace_callers, "direct_callees": CALLEES[TRACE_START]},
            "WsfAssert": {"start": ASSERT_START, "end_exclusive": ASSERT_END, "size": 154, "sha256": ASSERT_SHA256, "direct_bl_callers": assert_callers, "direct_callees": CALLEES[ASSERT_START]},
        },
        "abi_and_config": {
            "trace_buffer_bytes": 1024, "trace_assert_line": 137,
            "assert_log_line": 43, "assert_internal_line": 44,
            "assert_hook_global": "0x2007456C", "assert_backend_mask": "0x04800000",
            "AM_DEBUG_PRINTF": True, "WSF_TRACE_ENABLED": True,
            "WSF_TOKEN_ENABLED": False, "normal_WSF_ASSERT_macros_effective": False,
        },
        "lineage": {
            "trace": "AmbiqSuite 2.5.1 exact implementation family/semantics with six-line local drift",
            "assert": "AmbiqSuite translation-unit identity plus downstream EasyLogger extension",
            "packetcraft_exact_body_route": False,
            "proprietary_source_copied": False,
            "dead_stripped_source_apis": ["WsfPacketTrace","WsfToken","WsfTokenService"],
            "trace_path": trace_path, "assert_path": assert_path,
        },
        "candidate": {
            "production": "routed", "functions": 2, "stock_bytes": 208,
            "compiled_text_bytes": compiled, "alignment_bytes": alignment,
            "strict_relocations": relocations, "guarded_redirects": 2,
            "production_assert_diagnostic_wrappers": "omitted; hook/reset/fail-stop retained",
        },
        "compiler_matrix": {
            "archive": str(MATRIX_MANIFEST), "archive_sha256": PINNED_INPUTS[MATRIX_MANIFEST],
            "compiler_profiles": 13, "comparison_rows": 26,
            "linked_unresolved_symbols": 0, "raw_matches": 0,
            "strict_normalized_matches": 0,
            "best_size_gaps": {"WsfTrace": 18, "WsfAssert_pristine_baseline": 118},
            "wall_seconds": 2.097948391,
        },
        "stored_entry_or_interior_pointers": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("WSF assert/trace audit: 2 functions / 208 bytes, 126+1 callers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
