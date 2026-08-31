#!/usr/bin/env python3
"""Fail-closed G2 Cordio WSF buffer/message recovery audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

BUF_START, BUF_END = 0x00530364, 0x00530512
BUF_SHA256 = "01bc4ff2164b21f29f84a393ac4865a7175d1bb569f30b21d578fa6b2919906f"
BUF_LITERALS_START, BUF_LITERALS_END = 0x00530514, 0x00530538
BUF_LITERALS_SHA256 = "9bfb07aae3ab33e2c28570849f7d81e322c71222769ba25ea7153e1e85745687"
MSG_START, MSG_END = 0x004BF990, 0x004BFA0E
MSG_SHA256 = "31eadd387ba3baa7888ade2a0d4b6bedfcf4edc1baee5b29754fc499dd2683dd"

BUF_MAP = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-buf-function-map.tsv"
BUF_PROVENANCE = ROOT / "tools/manifests/ambiqsuite-cordio-wsf-buf-provenance.tsv"
POOL_MAP = ROOT / "tools/manifests/g2-cordio-wsf-buffer-pools.tsv"
MSG_MAP = ROOT / "tools/manifests/packetcraft-cordio-wsf-msg-function-map.tsv"
MSG_PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-wsf-msg-provenance.tsv"
READINESS_ARCHIVE = ROOT / "research/readiness/wsf-buf/SHA256SUMS"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"

PINNED_INPUTS = {
    ROOT / "components/shared/cordio/runtime_cordio_wsf_buf_candidate.c": "293a6a08c7babaef099c34d63400a2cfea6aef5dd6febd31deefbeadfb32c124",
    ROOT / "components/shared/cordio/runtime_cordio_wsf_buf_candidate.h": "d8bc569994a9ac212d59a1cf75309e71710282aa330b17a86adaefc287cde146",
    ROOT / "components/shared/cordio/runtime_cordio_wsf_msg_candidate.c": "d402234e563dcdb7b60835c958be5d56783600a538ed56183b23491b46b021da",
    ROOT / "components/shared/cordio/runtime_cordio_wsf_msg_candidate.h": "c6690996e70d66a7d62dec7c43b1a80854e05ed950974100f33fc99dacfded63",
    BUF_MAP: "b2dbe31dd1e118fa82aba44fd043f6ec0276ea5cd8d42e1c39cc0ded522b4e74",
    BUF_PROVENANCE: "c5c58be9517d27af53f7c56d0e625f2a7ff3e06c48982d458d4c93b9d0fe6661",
    POOL_MAP: "4db4f75f59ce894ef9b8dcc1f1ecbce9d75f0f5c03572f01a70e6a7fce5e09ec",
    MSG_MAP: "83407ebbfcb0caa40dc01174deaad223300ec5b7facbe90f0ad945afdb6089d4",
    MSG_PROVENANCE: "61d71a97947a51c6d4f67fecdf78af6f7e105e96c233b75740836050f85472d7",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-best-size.tsv": "2bcf1e4cdba8c5fc2ff3153bb16e2aaa1f76a074eb8db5b47f6c85febba6ba0a",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-config-summary.tsv": "77f7deac87a29e66bdf0b3d11809991f11d34dd64a2199789fcf4f484430dd4e",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-functions.tsv": "36dbcba6a01d174e602c4c157107c17fb90b7cf3f2a1656262a3ceecaab98a97",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-include-closure.tsv": "3182740d7f2ace2ec75d92596e8b8ca02b9758534ee7425c8351d57b918a6b74",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-provider-closure.tsv": "a82e0929f2e566bd56f0ba917475f910a2451e0d623b40fab7e63395a0800c1f",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-source-config-variants.tsv": "c04f7e577605bcac53771409b5366ac53c693c01c4fd5b8b308d4d18b97a2df5",
    ROOT / "tools/manifests/readiness-cordio-wsf-buf-source-identities.tsv": "2adb205e273d003b0d2efb750284e01c6e414f8ccf1fcb05c49bb68909972f62",
    READINESS_ARCHIVE: "926da386fc9f6818ef61f5e57cb590b8a2771a261793a0aa1ee84408f70be40f",
}

BUF_PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_wsf_buffer_init_candidate",
    "open_cfw_cordio_wsf_buffer_allocate_candidate",
    "open_cfw_cordio_wsf_buffer_free_candidate",
]
MSG_PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_wsf_message_data_allocate_candidate",
    "open_cfw_cordio_wsf_message_allocate_candidate",
    "open_cfw_cordio_wsf_message_free_candidate",
    "open_cfw_cordio_wsf_message_send_candidate",
    "open_cfw_cordio_wsf_message_enqueue_candidate",
    "open_cfw_cordio_wsf_message_dequeue_candidate",
    "open_cfw_cordio_wsf_message_peek_candidate",
]

BUF_CALLERS = {
    0x00530364: [0x004B7F7C],
    0x00530446: [0x004BF9A4,0x0052BCCE,0x005333FC,0x005335C4,0x005352C0,0x0056A3A8,0x0056A46E,0x0056A5D2,0x0056A750,0x0056A90E,0x0056AB60,0x0056B120,0x0056B33E,0x0056B754,0x0056CDCE,0x0056CDE0,0x0056CDF2,0x0056CE04,0x0056CE16,0x0056CF0E,0x0056DEE2,0x005A607C,0x005E3138,0x005E3906],
    0x005304D4: [0x004B4EC4,0x004BF9B4,0x0052BF7C,0x00532164,0x005331B8,0x005348B8,0x005348DC,0x00534CE4,0x00534D7E,0x00534E08,0x00537D34,0x0056A42A,0x0056A522,0x0056A630,0x0056A8FC,0x0056AAC2,0x0056ABC8,0x0056B138,0x0056B36C,0x0056B784,0x0056CE5E,0x0056CE74,0x0056CE8A,0x0056CEA0,0x0056CEB6,0x0056CEEE,0x0056E5EC,0x005A6210],
}

MSG_CALLERS = {
    0x004BF990: [0x004B50B4,0x0052A9F6,0x0052AAA2,0x005302C0,0x00530B2E,0x00537BD0],
    0x004BF99E: [0x0046EE74,0x0046EEF0,0x0046F066,0x0046F0F0,0x004775FE,0x0047771E,0x004A0244,0x004A1E40,0x004A1EC2,0x004A1F82,0x004A1FD2,0x004A2220,0x004A229C,0x004B3036,0x004B3174,0x004B31B2,0x004B31F6,0x004B3258,0x004B56C2,0x004B6354,0x004B6C8C,0x004B6D2E,0x004B6DF8,0x004B6E1C,0x004B6E4E,0x004B6E76,0x004B74AA,0x004B74FA,0x004B7564,0x004B7598,0x004B8228,0x004B8D26,0x004BB98C,0x004BC47A,0x004BDB74,0x004BDD54,0x004BDD9C,0x004BE0AE,0x004BE1A8,0x004BE320,0x004BE5F6,0x004BE910,0x004BEACC,0x004BF998,0x004C4C04,0x004D24DE,0x004D2800,0x004D283C,0x004D288A,0x004D28B4,0x004D28D2,0x004D28FA,0x0052AE42,0x0052BAD8,0x0052BB08,0x0052BB2E,0x005302E2,0x00533CF4,0x00534918,0x0053557A,0x00536434,0x0053666C,0x0053674A,0x00536784,0x0055BABA,0x0055BB22,0x0055BBF6,0x0055BC28,0x0056EA60],
    0x004BF9B0: [0x004B50E4,0x004B5228,0x004B5716,0x0052A6D8,0x0052A6EC,0x0052A842,0x0052A94A,0x0052A95C,0x0052A9B0,0x0052AB80,0x0052ABE6,0x0052ABF8,0x0052AC70,0x0052AC8E,0x0052ACA2,0x0052AD94,0x0052AEBA,0x0052B668,0x0052BA08,0x00530A96,0x00530CE2,0x00530D2A,0x00531ACC,0x00533BE8,0x00533C0A,0x00533D90,0x005362C8,0x005362EA,0x005362F2,0x005375BE,0x00537B9C,0x00537E8A,0x0056CA56,0x0056DD48,0x0056E24A,0x0056EB44],
    0x004BF9BA: [0x0046EE90,0x0046EF0C,0x0046F08A,0x0046F152,0x00477614,0x00477738,0x004A02A4,0x004A1EA2,0x004A1F28,0x004A1FA4,0x004A2044,0x004A2244,0x004A22C0,0x004B3046,0x004B3196,0x004B31E2,0x004B324A,0x004B328C,0x004B56E4,0x004B63A4,0x004B6CAA,0x004B6D62,0x004B6E0E,0x004B6E40,0x004B6E66,0x004B6E90,0x004B74E8,0x004B752C,0x004B7584,0x004B75AE,0x004B8244,0x004B8D54,0x004BB9A6,0x004BC494,0x004BDB8A,0x004BDD6A,0x004BDDB4,0x004BE106,0x004BE1C0,0x004BE338,0x004BE64E,0x004BE968,0x004BEAE2,0x004C4C1C,0x004D2828,0x004D2878,0x004D28AA,0x004D28C6,0x004D28EA,0x004D291A,0x0052BB58,0x00533D84,0x00535590,0x00536488,0x0053661A,0x0053670C,0x00536738,0x00537BE0,0x0055BB18,0x0055BB34,0x0055BC4E,0x0056EA78],
    0x004BF9DE: [0x004BF9CE,0x0052AD3E,0x0052AE6C,0x00530CA2,0x005363D4,0x0053645A,0x00536764,0x0053679E],
    0x004BF9EC: [0x0052A7D4,0x0052A83E,0x0052AC7A,0x0052AEAE,0x0052B674,0x0052BA12,0x00530CEC,0x00536288,0x005362B4,0x005362C0,0x005362D4,0x005362E2,0x005362FC,0x00537E82],
    0x004BFA00: [0x0052A800,0x0052AE82],
}

CALLEES = {
    0x00530364: [],
    0x00530446: [(0x00530454,0x0052B8B6),(0x0053046E,0x0052B8A4),(0x00530482,0x0052B8B6),(0x0053048A,0x0043D0CE),(0x005304AA,0x0043D574),(0x005304AE,0x0043D0CE),(0x005304B6,0x0043D0CE),(0x005304CA,0x0043CE9E)],
    0x005304D4: [(0x005304FC,0x0052B8A4),(0x0053050A,0x0052B8B6)],
    0x004BF990: [(0x004BF998,0x004BF99E)],
    0x004BF99E: [(0x004BF9A4,0x00530446)],
    0x004BF9B0: [(0x004BF9B4,0x005304D4)],
    0x004BF9BA: [(0x004BF9C4,0x0052B97C),(0x004BF9CE,0x004BF9DE),(0x004BF9D8,0x0052B95E)],
    0x004BF9DE: [(0x004BF9E6,0x00538C24)],
    0x004BF9EC: [(0x004BF9F0,0x00538C4A)],
    0x004BFA00: [],
}


class AuditError(RuntimeError):
    """Raised when closed buffer/message evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines(), delimiter="\t"))


def _load_module(name: str, path: Path):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _cstr(blob: bytes, address: int, limit: int = 160) -> str:
    return _slice(blob, address, address + limit).split(b"\0", 1)[0].decode("ascii")


def _direct_callers(blob: bytes, decoder: Any, targets: set[int]) -> dict[int, list[int]]:
    found = {target: [] for target in targets}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in found:
            found[target].append(address)
    return found


def _verify_no_stored_pointers(blob: bytes, intervals: list[tuple[int, int]]) -> None:
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
    hits = []
    for offset in range(0, len(blob) - 3, 4):
        if offset in excluded:
            continue
        if struct.unpack_from("<I", blob, offset)[0] in targets:
            hits.append(LOAD_BASE + offset)
    if hits:
        raise AuditError(f"unexpected stored buffer/message pointer ingress: {hits[:4]}")


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    for path, expected in PINNED_INPUTS.items():
        if not path.is_file() or _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned buffer/message input changed: {path.name}")

    decoder = _load_module(
        "wsf_buf_msg_thumb",
        ROOT / "tools/recover_apollo_embedded_source_paths.py",
    )
    flashdb = _load_module(
        "wsf_buf_msg_flashdb",
        ROOT / "tools/analyze_g2_flashdb.py",
    )
    if _sha256(_slice(blob, BUF_START, BUF_END)) != BUF_SHA256:
        raise AuditError("complete WSF buffer code cluster changed")
    if _sha256(_slice(blob, BUF_LITERALS_START, BUF_LITERALS_END)) != BUF_LITERALS_SHA256:
        raise AuditError("WSF buffer literal table changed")
    if _sha256(_slice(blob, MSG_START, MSG_END)) != MSG_SHA256:
        raise AuditError("complete WSF message code cluster changed")

    rows = [("buffer", row) for row in _rows(BUF_MAP)] + [
        ("message", row) for row in _rows(MSG_MAP)
    ]
    if (sum(unit == "buffer" for unit, _ in rows), sum(unit == "message" for unit, _ in rows)) != (3, 7):
        raise AuditError("WSF buffer/message function census changed")
    entries = {int(row["stock_start"], 0) for _, row in rows}
    callers = _direct_callers(blob, decoder, entries)
    functions: dict[str, list[dict[str, Any]]] = {"buffer": [], "message": []}
    for unit, row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"stock body changed for {row['stock_name']}")
        expected_callers = (BUF_CALLERS if unit == "buffer" else MSG_CALLERS)[start]
        if callers[start] != expected_callers:
            raise AuditError(f"direct caller closure changed for {row['stock_name']}")
        for site, target in CALLEES[start]:
            if decoder._thumb_bl_target(blob, site) != target:
                raise AuditError(f"callee changed at 0x{site:08x}")
        functions[unit].append({
            "name": row["stock_name"], "start": start, "end_exclusive": end,
            "size": len(body), "sha256": row["stock_sha256"],
            "direct_bl_callers": callers[start], "direct_callees": CALLEES[start],
            "candidate_symbol": row["candidate_symbol"],
        })
    _verify_no_stored_pointers(blob, [(BUF_START, BUF_END), (MSG_START, MSG_END)])

    literal_words = struct.unpack("<9I", _slice(blob, BUF_LITERALS_START, BUF_LITERALS_END))
    expected_literals = (
        0x20074EEC,0x20075044,0x20074F4A,0x00774AA0,0x0078C950,
        0x006E20C4,0x0078EE1C,0x0075D380,0xFAABD00D,
    )
    if literal_words != expected_literals:
        raise AuditError("WSF buffer globals/string literals changed")
    source_path = _cstr(blob, 0x006E20C4)
    if source_path != r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_buf.c":
        raise AuditError("retained WSF buffer source path changed")

    initialized = flashdb._decode_initialized_sram(blob)
    descriptor_bytes = flashdb._sram_slice(initialized, 0x200003B0, 16)
    if descriptor_bytes.hex() != "100008002000040040000a00e0011400":
        raise AuditError("G2 WSF buffer descriptors changed")
    if _sha256(descriptor_bytes) != "042b678d2537323145f48d4c7e0ae3deb68d58bf8b81a0cb97a4b1aa0b522c2e":
        raise AuditError("G2 WSF buffer descriptor SHA-256 changed")
    pools = _rows(POOL_MAP)
    if len(pools) != 4 or sum(int(row["bytes"]) for row in pools) + 48 != 0x2930:
        raise AuditError("G2 WSF buffer pool allocation changed")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    production = {}
    for unit, source_name, prefix, mapped, names, first_offset, expected_metrics in (
        (
            "buffer", "runtime_cordio_wsf_buf_candidate.c",
            "replace_cordio_wsf_buf_", _rows(BUF_MAP),
            BUF_PRODUCTION_FUNCTIONS, 264832, (582, 0, 5),
        ),
        (
            "message", "runtime_cordio_wsf_msg_candidate.c",
            "replace_cordio_wsf_msg_", _rows(MSG_MAP),
            MSG_PRODUCTION_FUNCTIONS, 265414, (114, 12, 8),
        ),
    ):
        source_path = f"components/shared/cordio/{source_name}"
        leaves = [
            row for row in overlay["relocated_leaves"]
            if row.get("source", {}).get("path") == source_path
        ]
        source_sha = PINNED_INPUTS[ROOT / source_path]
        if len(leaves) != len(names) or any(
            row.get("source", {}).get("sha256") != source_sha for row in leaves
        ):
            raise AuditError(f"WSF {unit} production source inventory changed")
        sites = {row["name"]: row for row in overlay["patch_sites"]}
        for index, (row, function) in enumerate(zip(mapped, names), 1):
            start = int(row["stock_start"], 0)
            end = int(row["stock_end_exclusive"], 0)
            site = sites.get(f"{prefix}{index:02d}")
            if (
                site is None
                or site.get("runtime_address") != start
                or site.get("target_function") != function
                or site.get("branch") != "b_w"
                or site.get("expected_size") != end - start
                or site.get("expected_sha256") != row["stock_sha256"]
                or function not in overlay["functions"]
            ):
                raise AuditError(f"WSF {unit} production route {index} changed")
        compiled = sum(row["expected"]["size"] for row in leaves)
        alignment = leaves[0]["expected"]["offset"] - first_offset
        alignment += sum(
            leaves[index + 1]["expected"]["offset"]
            - leaves[index]["expected"]["offset"]
            - leaves[index]["expected"]["size"]
            for index in range(len(leaves) - 1)
        )
        relocations = sum(len(row["relocations"]) for row in leaves)
        if (compiled, alignment, relocations) != expected_metrics:
            raise AuditError(f"WSF {unit} production metrics changed")
        production[unit] = {
            "functions": names,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": len(names),
        }

    build = json.loads(BUILD_REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, AuditError, "WSF buffer/message")
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    provider = override["provider"]
    regions = override["regions"]
    if (
        len([row for row in regions if row["name"].startswith("cordio_wsf_buf_")]) != 6
        or len([row for row in regions if row["name"].startswith("cordio_wsf_msg_")]) != 20
    ):
        raise AuditError("WSF buffer/message package ownership changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "modules": {
            "wsf_buf": {"start": BUF_START, "end_exclusive": BUF_END, "size": 430, "sha256": BUF_SHA256, "functions": functions["buffer"]},
            "wsf_msg": {"start": MSG_START, "end_exclusive": MSG_END, "size": 126, "sha256": MSG_SHA256, "functions": functions["message"]},
            "stored_entry_or_interior_pointers": 0,
        },
        "buffer_abi": {
            "pool_descriptor_size": 4, "buffer_block_size": 8,
            "internal_pool_size": 12, "free_marker": "0xFAABD00D",
            "globals": {"memory": "0x20074EEC", "pool_count": "0x20075044", "used_length": "0x20074F4A"},
        },
        "message_abi": {"internal_header_size": 8, "next_offset": 0, "handler_id_offset": 4, "payload_offset": 8},
        "pool_configuration": {
            "descriptor_address": "0x200003B0", "descriptor_sha256": _sha256(descriptor_bytes),
            "descriptors": [[16,8],[32,4],[64,10],[480,20]],
            "memory_address": "0x2004FA98", "capacity": 0x2940,
            "used": 0x2930, "spare": 0x10,
        },
        "effective_config": {
            "WSF_BUF_FREE_CHECK": True, "WSF_BUF_STATS": False,
            "WSF_BUF_STATS_HIST": False, "WSF_OS_DIAG": False,
            "WSF_ASSERT_ENABLED": False, "allocation_warning_retained": True,
        },
        "lineage": {
            "buffer": "AmbiqSuite 2.5.1 exact FreeRTOS implementation family; proprietary oracle only; byte-identical in 2.4.2",
            "message": "Packetcraft r19.02 Apache-2.0 exact seven-definition source route",
            "retained_buffer_source_path": source_path,
            "unbounded_buffer_source_apis": ["WsfBufGetAllocStats","WsfBufGetNumPool","WsfBufGetPoolStats","WsfBufDiagRegister"],
        },
        "candidate": {
            "production": "routed", "behaviorally_recreated_functions": 10,
            "behaviorally_recreated_bytes": 556,
            "proprietary_source_copied": False,
            "message_apache_source_route": True,
            "production_metrics": production,
            "retained_buffer_literal_table_bytes": 36,
        },
        "compiler_matrix": {
            "archive": str(READINESS_ARCHIVE), "archive_sha256": PINNED_INPUTS[READINESS_ARCHIVE],
            "variants": 2, "compiler_profiles": 13, "comparison_rows": 78,
            "raw_matches": 0, "strict_normalized_matches": 0,
            "best_aggregate_lane": "stock_warn_seam__O3", "best_aggregate_abs_delta": 34,
            "best_function_gaps": {"WsfBufInit": 10, "WsfBufAlloc": 10, "WsfBufFree": 2},
        },
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
        print(
            "WSF buffer/message audit: "
            f"{len(report['modules']['wsf_buf']['functions'])} buffer + "
            f"{len(report['modules']['wsf_msg']['functions'])} message functions, "
            f"{report['candidate']['behaviorally_recreated_bytes']} bytes"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
