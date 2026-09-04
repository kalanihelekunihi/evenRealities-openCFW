#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio connection state machine."""

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
READINESS_MANIFEST = ROOT / "research/readiness/dm-conn-sm/SHA256SUMS"
READINESS_BYTES = 943
READINESS_SHA256 = "aaa2c00f94b74ba11b625c0df329b225fa3d52a28952b16b227b00cc9d238aac"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_dm_conn_sm.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_conn_sm.h"
TEST = ROOT / "tests/test_runtime_cordio_dm_conn_sm.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
SOURCE_PIN = (3_950, "5d4698908c44e578d3da2d9eb09f07b7e0e60ce2ecb5deb9c67f96c2ac0bca1b")
HEADER_PIN = (1_655, "8299ae5795d1fce5323c66c86fafc320b1ed166b8ce0546a198bfb0d8d497ad4")
TEST_PIN = (6_313, "5e2e1c8ae8ae7011715b89aed920797b6ef2bccd3cc0933d6da833445866d6e2")
PRODUCTION_LEAF = (288328, 120, 2, "c79fbbc1083c7a8e935c1d2acb9a0d05f9a4ad918aa6b3003593e8f63bf8d817")
PRODUCTION_OVERLAY = (380_444, "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622")
PRODUCTION_COMPONENT = (3_956_672, "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6")
PRODUCTION_PACKAGE = (4_750_780, "1bb3f8c84d288a30cfd252e832ec4a51ac5eca42b5de8e8817db11a938c6a771")
PRODUCTION_FLASH_PLAN = (5_485_925, "d931ff83e416a91a87f40690c1ed2dc65cee4ee7b1bdc8fb37eaf9cd2cf624ef")
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-sm-function-map.tsv": "b0a42e95ba82522214623e7357945309ab3a5876e0ced618f30390db6e4cc0ff",
    ROOT / "tools/manifests/packetcraft-cordio-dm-conn-sm-provenance.tsv": "66ce42fad423210c94b002a83b7f9ffcba3f4d484e77771d1ee387d608744923",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-build-results.tsv": "f19ff646355051f8d8ca699564b6527c3cf214eaea44b11ba6fe4eb3983b8858",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-closure-results.tsv": "8745e62c739c625be7c75a7d6a49cb3e4f03ef15c2c84f9aafcf7ca91b9566f0",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-compiler-probe-sizes.tsv": "9309f70969a1b7b28bf31502f1e8384485e1258b67708e0e727fbf890b121988",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-include-closure.tsv": "2948ec7cb1f2c7b6c8224248cd0794fb0ef4519fe6d011c663fe5f70661a4b7b",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-source-identities.tsv": "bf13d23990a36dfd5efcc7335663e624b89b1c87279d7410901136c85c21e6d0",
    ROOT / "tools/manifests/readiness-cordio-dm-conn-sm-undefined-providers.tsv": "9059232fece6c874bbfcaf2d926229a746a4a37984b0987fa2fa9fca8dfe38dd",
}

BODY = (0x00533EF4, 0x00534532)
BODY_SHA256 = "ea6b9b7e93733482471e6bbad05ac3096b859f3cf6293c19e97fe496bb0185fb"
TAIL = (0x00534532, 0x0053456C)
TAIL_SHA256 = "fce6e989a351144680aeb36ec0c67c98251c270dfa15681bec7d8b1152ebedf2"
PHYSICAL = (0x00533EF4, 0x0053456C)
PHYSICAL_SHA256 = "dc8d749ab17a2a225e784c1e722eb3a17d72ccfec595f674295a373281021575"
CALLERS = [0x004B689E, 0x004B690E]
STATE_TABLE = (0x006ECC58, 0x006ECCA8)
STATE_TABLE_SHA256 = "cc9cd86fde8eb6a514c7fa4451aea535db9616af7dd6615c5cbee3827584254a"
STATE_TABLE_BYTES = bytes.fromhex(
    "01100000022000000322000000000000"
    "01000411010000030302000301000100"
    "02000021020000230322002302000200"
    "03000401030003000300000403050300"
    "04000400040000040401000404000400"
)
SOURCE_PATH = 0x006DD114
SOURCE_PATH_POINTER_CELLS = [0x0053454C]
SOURCE_PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\"
    b"ble-host\\sources\\stack\\dm\\dm_conn_sm.c\x00"
)
SOURCE_PATH_SHA256 = "3d1e59f930c95f95b4b1f0523a95feb93e61be949559b3668cdc9c598076ccd1"
SOURCE_PATH_LOAD_SITES = [
    0x00533F32, 0x00533F78, 0x00533FBC, 0x00533FF0,
    0x0053408A, 0x005340D6, 0x00534120, 0x00534164,
    0x005341D8, 0x00534220, 0x00534264, 0x00534294,
    0x005342FE, 0x0053433C, 0x00534382, 0x005343B2,
    0x00534422, 0x0053445E, 0x0053449A, 0x005344C8,
]
DIRECT_CALLEES = {
    0x0043D0CE: [0x00533F14,0x00533F5A,0x00533F9E,0x00533FD2,0x00534066,0x005340B2,0x005340FC,0x00534140,0x005341B8,0x00534200,0x00534246,0x00534278,0x005342E2,0x00534320,0x00534366,0x00534396,0x00534408,0x00534444,0x00534480,0x005344AE],
    0x0043D574: [0x00533F3A,0x00533F80,0x00533FC4,0x00533FF8,0x00534092,0x005340DE,0x00534128,0x0053416C,0x005341E0,0x00534228,0x0053426A,0x0053429A,0x00534304,0x00534342,0x00534388,0x005343B8,0x00534428,0x00534464,0x005344A0,0x005344CE],
    0x0044B610: [0x00533F0C,0x00533F52,0x00533F96,0x0053400C,0x0053405E,0x005340AA,0x005340F4,0x00534180,0x005341B0,0x005341F8,0x0053423E,0x005342AE,0x005342DA,0x00534318,0x0053435E,0x005343CC,0x00534400,0x0053443C,0x00534478,0x005344E2],
    0x004C9C50: [0x00533EFC,0x00533F40,0x00533F86,0x00533FCA,0x00533FFE,0x0053404E,0x00534098,0x005340E4,0x00534138,0x00534172,0x005341A0,0x005341E6,0x0053422E,0x00534270,0x005342A0,0x005342C6,0x0053430A,0x00534350,0x0053438E,0x005343BE,0x005343F2,0x0053442E,0x0053446A,0x005344A6,0x005344D4],
    0x0052A63C: [0x00534020,0x0053419C,0x005342C2,0x005343E0,0x005344F6],
}
EXPECTED_TAIL_WORDS = {
    0x00534540: 0x0078D434,
    0x00534544: 0x0073E030,
    0x00534548: 0x00785BF0,
    0x0053454C: SOURCE_PATH,
    0x00534550: 0x0078D43C,
    0x00534554: STATE_TABLE[0],
    0x00534558: 0x0071DFB8,
    0x0053455C: 0x007331F4,
    0x00534560: 0x0073E05C,
    0x00534564: 0x0073E088,
    0x00534568: 0x20073FE4,
}
EXPECTED_ACTION_TABLES = {
    0x00776A84: [0x004B63CB,0x004B63CD,0x004B63D9,0x004B6489,0x004B64CF,0x004B6509],
    0x0078D424: [0x00536A87,0x0055BC5D],
    0x00785BE0: [0x00536AC9,0x00536ADD,0x00536AF1,0x00536B05],
}


class AuditError(RuntimeError):
    """Raised when authenticated DM state-machine evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [LOAD_BASE + i for i in range(len(blob) - 3) if blob[i:i + 4] == packed]


def _verify_file(path: Path, pin: tuple[int, str], label: str) -> None:
    data = path.read_bytes()
    if (len(data), _sha256(data)) != pin:
        raise AuditError(f"{label} changed")


def _verify_production() -> dict[str, Any]:
    _verify_file(SOURCE, SOURCE_PIN, "DM connection state-machine source")
    _verify_file(HEADER, HEADER_PIN, "DM connection state-machine header")
    _verify_file(TEST, TEST_PIN, "DM connection state-machine host test")
    report = json.loads(REPORT.read_text())
    config = json.loads(CONFIG.read_text())
    manifest = json.loads(MANIFEST.read_text())
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path", "").endswith(SOURCE.name)
    ]
    if len(leaves) != 1:
        raise AuditError("DM connection state-machine production leaf count changed")
    leaf = leaves[0]
    observed = (
        leaf["pins"]["offset"], leaf["extraction"]["size"],
        leaf["extraction"]["relocation_count"], leaf["extraction"]["sha256"],
    )
    if (leaf["extraction"]["function"] !=
            "open_cfw_cordio_dm_connection_state_machine_execute"
            or observed != PRODUCTION_LEAF
            or leaf["placement"]["padding_before"] != 0):
        raise AuditError("DM connection state-machine production leaf changed")
    sites = [
        row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_dm_conn_sm_")
    ]
    if len(sites) != 1:
        raise AuditError("DM connection state-machine route count changed")
    site = sites[0]
    if (
        site["name"] != "replace_cordio_dm_conn_sm_01"
        or site["runtime_address"] != BODY[0]
        or site["expected_size"] != BODY[1] - BODY[0]
        or site["expected_sha256"] != BODY_SHA256
        or site["branch"] != "b_w"
        or site["target_function"] !=
            "open_cfw_cordio_dm_connection_state_machine_execute"
    ):
        raise AuditError("DM connection state-machine production route changed")
    override = manifest["component_overrides"]["apollo_main"]
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_dm_conn_sm_")
    ]
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
            != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
            != PRODUCTION_COMPONENT
        or (override["provider"].get("size"),
            override["provider"].get("sha256")) != PRODUCTION_COMPONENT
        or len(regions) != 2
    ):
        raise AuditError("DM connection state-machine component ownership changed")
    _verify_file(PACKAGE, PRODUCTION_PACKAGE, "DM connection state-machine package")
    _verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN,
                 "DM connection state-machine flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (7822, 0, 8, 6):
        raise AuditError("DM connection state-machine flash counts changed")
    return {
        "status": "production-routed",
        "redirected_stock_functions": 1,
        "redirected_stock_bytes": BODY[1] - BODY[0],
        "source_owned_bytes_added": PRODUCTION_LEAF[1],
        "alignment_bytes_added": 0,
        "strict_relocations": PRODUCTION_LEAF[2],
        "retained_state_table_bytes": STATE_TABLE[1] - STATE_TABLE[0],
        "retained_literal_pool_bytes": TAIL[1] - TAIL[0],
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
    }


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_conn_sm_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei dm_conn_sm readiness size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_conn_sm readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_conn_sm input changed: {path}")
    if _sha256(_slice(blob, *BODY)) != BODY_SHA256:
        raise AuditError("dmConnSmExecute stock body changed")
    if _sha256(_slice(blob, *TAIL)) != TAIL_SHA256:
        raise AuditError("DM connection state-machine literal pool changed")
    if _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("DM connection state-machine physical TU changed")
    table = _slice(blob, *STATE_TABLE)
    if table != STATE_TABLE_BYTES or _sha256(table) != STATE_TABLE_SHA256:
        raise AuditError("DM connection state table changed")
    path = _slice(blob, SOURCE_PATH, SOURCE_PATH + len(SOURCE_PATH_BYTES))
    if path != SOURCE_PATH_BYTES or _sha256(path) != SOURCE_PATH_SHA256:
        raise AuditError("retained dm_conn_sm source path changed")
    if _occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("dm_conn_sm source path pointer closure changed")

    decoder = _load_decoder()
    callers = []
    direct: dict[int, list[int]] = {target: [] for target in DIRECT_CALLEES}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target == BODY[0]:
            callers.append(address)
        if BODY[0] <= address < BODY[1] and target in direct:
            direct[target].append(address)
    if callers != CALLERS:
        raise AuditError("dmConnSmExecute caller closure changed")
    if direct != DIRECT_CALLEES:
        raise AuditError("dmConnSmExecute direct-callee closure changed")
    if _occurrences(blob, BODY[0] | 1):
        raise AuditError("unexpected stored dmConnSmExecute Thumb pointer")

    for address, expected in EXPECTED_TAIL_WORDS.items():
        actual = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"dm_conn_sm literal changed at 0x{address:08x}")
    action_tables = {}
    for address, expected in EXPECTED_ACTION_TABLES.items():
        values = list(struct.unpack(f"<{len(expected)}I", _slice(blob, address, address + 4 * len(expected))))
        if values != expected:
            raise AuditError(f"DM action table changed at 0x{address:08x}")
        action_tables[f"0x{address:08x}"] = values

    rows = [[list(table[(state * 16 + event * 2):(state * 16 + event * 2 + 2)]) for event in range(8)] for state in range(5)]
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": BODY[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "physical_sha256": PHYSICAL_SHA256,
            "linked_function_count": 1,
            "linked_function_bytes": BODY[1] - BODY[0],
            "function_sha256": BODY_SHA256,
            "literal_pool_bytes": TAIL[1] - TAIL[0],
            "literal_pool_sha256": TAIL_SHA256,
            "direct_bl_ingress_sites": len(callers),
            "direct_logger_relocations": sum(len(v) for v in direct.values()),
            "indirect_action_dispatch_sites": [0x00534522],
            "stored_function_pointers": 0,
            "source_only_functions": [],
        },
        "state_machine": {
            "states": 5, "events": 8, "entry_bytes": 2,
            "table_address": STATE_TABLE[0], "table_sha256": STATE_TABLE_SHA256,
            "rows_next_state_action": rows,
            "event_mask": 7,
            "ccb_state_offset": 0x15,
            "message_event_offset": 2,
            "action_set_count": 3,
            "action_set_global": 0x20073FE4,
            "action_tables": action_tables,
        },
        "lineage": {
            "selected_public_oracle": "Packetcraft r20.05 through r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "58c5c6e1e4df5744c9a41902634cdd23a1aef906",
            "r20_discriminator": "five states by eight events, mask 7, separated DM_ID_CONN_UPD",
            "stock_qualification": "exact public r20 table plus vendor diagnostics and action-set validation",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "source_inventory_functions": 1,
            "compiler_profiles": 2,
            "provider_seams": 2,
            "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
            "minimum_retained_text": 232,
            "retained_bss": 1036,
        },
        "production": _verify_production(),
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
        print("Cordio DM connection state-machine audit: 1 linked function / 1,598 bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
