#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio legacy advertising module."""

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
READINESS_MANIFEST = ROOT / "research/readiness/dm-adv-leg/SHA256SUMS"
READINESS_BYTES = 1_300
READINESS_SHA256 = "046b744f785a3f2a79936fe4ee027f7d963518f0de5b201fbf0808012d76dee3"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-adv-leg-provenance.tsv": "f7b7f088b9faf776ea46f5fde54f89a8b5e30c3437af32719983677bb10684c4",
    ROOT / "tools/manifests/packetcraft-cordio-dm-adv-leg-function-map.tsv": "4dd027e26e294157316a5425be63405fa0cf779975a3d469a45ed5f6327b8949",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-leg-build-results.tsv": "15d353a17b43bcbf55728bbc4a2d1196a398393a6b67817e81ccfdda3ea35bad",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-leg-closure-results.tsv": "3474e6b27813ccd0b0dde22bcba0e03e8d25e8eba9713f7dc484fce3a570dfe8",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-leg-source-identities.tsv": "665622fa3fb0c0a1c3d602f1009b7b569fe48f4ae639e97fcbe23ef57080ec8f",
    ROOT / "tools/manifests/readiness-cordio-dm-adv-leg-undefined-providers.tsv": "935ad302f28bcfaa11460d625c860a385d4778125de70d5a62cab32530096eb1",
}
PRODUCTION_SOURCE = ROOT / "components/shared/cordio/runtime_cordio_dm_adv_leg.c"
PRODUCTION_HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_adv_leg.h"
PRODUCTION_TEST = ROOT / "tests/test_runtime_cordio_dm_adv_leg.py"
PRODUCTION_PINS = {
    PRODUCTION_SOURCE: (18_680, "440c36fdaa0f7d675afa7700ba14aa4e129561df2f2990127b456d563a431f1b"),
    PRODUCTION_HEADER: (6_138, "dac94792519aa89732e14b5e48a5cfcc9e0b2cdde2c585be499dc88f29e545c5"),
    PRODUCTION_TEST: (12_435, "fcfb8307ff77036a4fc29cdd936c25c6180ef95ac21c4a961ac0caab3bf0d1ac"),
}
PRODUCTION_LEAVES = (
    ("open_cfw_cordio_dm_adv_legacy_configure_parameters", 355836, 94, 2, 2, "3f4818f7ab2b59d911baa003b46ea9db42aa5161e594c808a4b2d983e6e15a04"),
    ("open_cfw_cordio_dm_adv_legacy_action_configure", 355932, 46, 2, 1, "dbcc68eada1ad2c1aa0bb03fdc5c77c43e39bfabae8df0a2dacfe73704fc1249"),
    ("open_cfw_cordio_dm_adv_legacy_action_set_data", 355980, 52, 2, 2, "70d4b77ec35f3d45929ab51ae9f5633695722715ba928b777e898b9a008f15df"),
    ("open_cfw_cordio_dm_adv_legacy_action_start", 356032, 56, 0, 1, "b16bf2203038cf75e6a30172f2773370feeb59e285d2fda7e5fa255b2656ddb3"),
    ("open_cfw_cordio_dm_adv_legacy_action_stop", 356088, 40, 0, 1, "823804fbc7679c704ace6e4be8d2f0dfe7aa74b08f1f228b429f1405557be4cd"),
    ("open_cfw_cordio_dm_adv_legacy_action_remove_set", 356128, 2, 0, 0, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("open_cfw_cordio_dm_adv_legacy_action_clear_sets", 356132, 2, 2, 0, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("open_cfw_cordio_dm_adv_legacy_action_set_random_address", 356136, 2, 2, 0, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    ("open_cfw_cordio_dm_adv_legacy_action_timeout", 356140, 26, 2, 1, "7a9bee8004c34f860451a3ea2078f3904e80daf64d2742a9b78abd4fc059e0ad"),
    ("open_cfw_cordio_dm_adv_legacy_reset", 356168, 70, 2, 2, "29ea49ca4bec4d2eb375c5ae60d7e79551085bdbad5dc72ecc3345624680073b"),
    ("open_cfw_cordio_dm_adv_legacy_hci_handler", 356240, 226, 2, 5, "5f7dd79f7b122e9a0d253316c582685b46dbc6ff15ab5c8eb3e7fee446dbd679"),
    ("open_cfw_cordio_dm_adv_legacy_message_handler", 356468, 72, 2, 8, "e3b7cf8787e9a20ac170be8b672611ee203261a21bfeeb31551d6f4242d499e6"),
    ("open_cfw_cordio_dm_adv_legacy_start_directed", 356540, 90, 0, 1, "7dcec22b87c98cc02988b1ada0ee8c9da5778fde3a0510fe4685d04667552747"),
    ("open_cfw_cordio_dm_adv_legacy_stop_directed", 356632, 46, 2, 1, "cc8bb1920a3360fb78d159e7818ee7aeca08925ee73e23f603bc9f83eeeb4b75"),
    ("open_cfw_cordio_dm_adv_legacy_connected", 356680, 38, 2, 2, "1750b237bde5251305fa839b6d9c6ff4ba7f2264194b26054edf7ec09cee0bd0"),
    ("open_cfw_cordio_dm_adv_legacy_connect_failed", 356720, 38, 2, 2, "fd74e07473ad023a4a66955d71fd6073193760ef2fbbe29bc601c4606349511e"),
    ("open_cfw_cordio_dm_adv_legacy_initialize", 356760, 48, 2, 3, "1cb25828f054159d8a4b5db35b694e35d1a0910806cd61007c174e495cbe4f50"),
)
PRODUCTION_OVERLAY = (404_796, "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d")
PRODUCTION_COMPONENT = (3_928_192, "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73")
PRODUCTION_PACKAGE = (4_706_686, "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf")
PRODUCTION_FLASH_PLAN = (4_071_097, "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d")

FUNCTIONS = [
    ("dmAdvConfig", 0x004B9A80, 0x004B9AC0, "f687db593110076bcf1e6a2512b05cc86e323cef21a59e98575065570003002a", [0x004B9D14]),
    ("dmAdvActConfig", 0x004B9AC0, 0x004B9D1A, "14f5b5f1cb3b9562c0d8747178ae5f5ba67472861828b12d022ae1278e9ea988", []),
    ("dmAdvActSetData", 0x004B9D24, 0x004B9E7A, "2ca537c902e749d9bf9ce4bc6a23acad52110516ade22eaae9b9195ed92176b6", []),
    ("dmAdvActStart", 0x004B9E88, 0x004BA0E6, "2c7f58b67c890c19a5505eb562c47588888e5a86347d63e0913697df5acea8c5", []),
    ("dmAdvActStop", 0x004BA0F4, 0x004BA332, "24239117f14103d04e7f2b15e3cd8b1f2e243f794db39f4df872a064843ebf62", []),
    ("dmAdvActRemoveSet", 0x004BA33C, 0x004BA33E, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", []),
    ("dmAdvActClearSets", 0x004BA33E, 0x004BA340, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", []),
    ("dmAdvActSetRandAddr", 0x004BA340, 0x004BA342, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8", []),
    ("dmAdvActTimeout", 0x004BA342, 0x004BA456, "d0e55f6bd6c174c05e60496ee00304cb4fa5ae324d496980813e23bdf2794fe5", []),
    ("dmAdvReset", 0x004BA45C, 0x004BA490, "5c30215302bedc9322e389ee8f3d26f4e120239a391a590e663f9a49b067cff2", []),
    ("dmAdvHciHandler", 0x004BA4B0, 0x004BA6AC, "14ada43062d8d253493ede7d24e43e5a89740fcd706a551760338ad6c7e55054", []),
    ("dmAdvMsgHandler", 0x004BA6AC, 0x004BA6C0, "888e710987e18eb7ac608a7521af400e6bd8db864b21a3e790a150ea3f22116c", []),
    ("dmAdvStartDirected", 0x004BA6D4, 0x004BA848, "6b939a502d0a86ca1c10c1fae3f6f0a5a13eaa112076cd15c56c03b5b1cd570a", [0x00536AD6]),
    ("dmAdvStopDirected", 0x004BA864, 0x004BA9C8, "e010ef6ab44be58fae6ed5edbff56739d5df23458c094361c067f359b4844527", [0x00536AE2]),
    ("dmAdvConnected", 0x004BA9D4, 0x004BAAF8, "894996038f13a66c0f3ba2a6c98dd60e4fc59cdc52f5ca182e6383677a248867", [0x00536AF6]),
    ("dmAdvConnectFailed", 0x004BAB04, 0x004BAC28, "ae277a1e0906b38cf0239285a32a972a58e9cf7337162a5871cbca9c737d8737", [0x00536B0A]),
    ("DmAdvInit", 0x004BAC2C, 0x004BAC4E, "898b50b09149a491ef0bc117025b07d708eeeca74bead2a3103e2879be37f11f", [0x004B800E]),
]
CODE_SPAN = (0x004B9A80, 0x004BAC4E)
CODE_SPAN_SHA256 = "ed16c32511418334908972bef992cff618aed4ef27eba43d97d72f7ab45ee5df"
LOGICAL_TU_SHA256 = "902fea4c30311567807f9760ee68e22f7f065bf371847c4336b2d1e4033e1a19"
PHYSICAL_ENVELOPE = (0x004B9A80, 0x004BACC8)
PHYSICAL_ENVELOPE_SHA256 = "fc58ec3553867362832beb6c7beffb32fdde45ba452bdc7c1780aa69c25f8d7d"
CONCATENATED_BODY_SHA256 = "6e9615c53d77a5e28ee26f6c7f8075cc2b2a02c9664ea857b44537c75726a2d7"
DATA_GAPS = [
    (0x004B9D1A, 0x004B9D24), (0x004B9E7A, 0x004B9E88),
    (0x004BA0E6, 0x004BA0F4), (0x004BA332, 0x004BA33C),
    (0x004BA456, 0x004BA45C), (0x004BA490, 0x004BA4B0),
    (0x004BA6C0, 0x004BA6D4), (0x004BA848, 0x004BA864),
    (0x004BA9C8, 0x004BA9D4), (0x004BAAF8, 0x004BAB04),
    (0x004BAC28, 0x004BAC2C),
]
CONCATENATED_DATA_SHA256 = "60afde82215ab7e112a46dc9e59d6f12f3db93f92be3182ce20ff22bb19b61c0"
FOREIGN_ACCESSOR = (0x004BAC4E, 0x004BAC64)
FOREIGN_ACCESSOR_SHA256 = "58e1200869cceff1b8ef14e1368e2b6893a2064301644db5c564fd92aafd29a5"
TRAILING_POOL = (0x004BAC64, 0x004BACC8)
TRAILING_POOL_SHA256 = "b5fe4293aec9465fbb1357187d1287f11e9b96895400b5defc181e442620bad0"
ACTION_TABLE = (0x0075F550, [
    0x004B9AC1, 0x004B9D25, 0x004B9E89, 0x004BA0F5,
    0x004BA33D, 0x004BA33F, 0x004BA341, 0x004BA343,
])
ACTION_TABLE_SHA256 = "ab90462f58d0893ca3786bde192ac5831a9bbdc2a54ab9a4d878c31c0f4806ff"
INTERFACE_TABLE = (0x0078A808, [0x004BA45D, 0x004BA4B1, 0x004BA6AD])
INTERFACE_TABLE_SHA256 = "0804b469e20875ee7afd3f0a272279187d98f02a5091b254428a483ce5306232"
SOURCE_PATH = 0x006DD0B4
SOURCE_PATH_SHA256 = "48c345419ac5f13cfcb98c257fc9214ecb8e7303441be526ec0099292a506c09"
SOURCE_PATH_POINTER_CELLS = [0x004BA4AC, 0x004BAC8C]
SOURCE_PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\"
    b"ble-host\\sources\\stack\\dm\\dm_adv_leg.c\x00"
)
EXPECTED_ALIGNED_ENTRY_POINTERS = {
    0x0075F550 + 4 * index: value
    for index, value in enumerate(ACTION_TABLE[1])
} | {
    0x0078A808 + 4 * index: value
    for index, value in enumerate(INTERFACE_TABLE[1])
}


class AuditError(RuntimeError):
    """Raised when authenticated legacy advertising evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_adv_leg_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _all_callers(blob: bytes, decoder: Any) -> dict[int, list[int]]:
    callers = {start: [] for _, start, _, _, _ in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def _occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [
        LOAD_BASE + offset
        for offset in range(len(blob) - 3)
        if blob[offset:offset + 4] == packed
    ]


def _verify_aligned_entry_pointers(blob: bytes) -> None:
    entry_or_interior = {
        target
        for _, start, end, _, _ in FUNCTIONS
        for address in range(start, end, 2)
        for target in (address, address | 1)
    }
    found: dict[int, int] = {}
    for offset in range(0, len(blob) - 3, 4):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in entry_or_interior:
            found[LOAD_BASE + offset] = value
    if found != EXPECTED_ALIGNED_ENTRY_POINTERS:
        raise AuditError(
            "legacy advertising stored entry/interior pointer closure changed"
        )


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES:
        raise AuditError("Lorelei legacy advertising artifact size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei legacy advertising artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned legacy advertising input changed: {path}")

    decoder = _load_decoder()
    all_callers = _all_callers(blob, decoder)
    bodies: list[bytes] = []
    reports = []
    for name, start, end, expected, callers in FUNCTIONS:
        body = _slice(blob, start, end)
        if _sha256(body) != expected:
            raise AuditError(f"legacy advertising stock span changed at 0x{start:08x}")
        if all_callers[start] != callers:
            raise AuditError(f"legacy advertising caller closure changed for {name}")
        bodies.append(body)
        reports.append({
            "name": name,
            "start": start,
            "end_exclusive": end,
            "size": end - start,
            "sha256": expected,
            "direct_bl_callers": callers,
        })
    if _sha256(b"".join(bodies)) != CONCATENATED_BODY_SHA256:
        raise AuditError("legacy advertising concatenated body identity changed")
    if _sha256(_slice(blob, *CODE_SPAN)) != CODE_SPAN_SHA256:
        raise AuditError("legacy advertising executable interval changed")
    if _sha256(b"".join(_slice(blob, *gap) for gap in DATA_GAPS)) != CONCATENATED_DATA_SHA256:
        raise AuditError("legacy advertising inline data changed")
    if _sha256(_slice(blob, *FOREIGN_ACCESSOR)) != FOREIGN_ACCESSOR_SHA256:
        raise AuditError("adjacent advertising state accessor changed")
    if _sha256(_slice(blob, *TRAILING_POOL)) != TRAILING_POOL_SHA256:
        raise AuditError("legacy advertising trailing literal pool changed")
    if _sha256(_slice(blob, *CODE_SPAN) + _slice(blob, *TRAILING_POOL)) != LOGICAL_TU_SHA256:
        raise AuditError("legacy advertising logical TU identity changed")
    if _sha256(_slice(blob, *PHYSICAL_ENVELOPE)) != PHYSICAL_ENVELOPE_SHA256:
        raise AuditError("legacy advertising physical envelope changed")

    for address, values, expected_hash in (
        (*ACTION_TABLE, ACTION_TABLE_SHA256),
        (*INTERFACE_TABLE, INTERFACE_TABLE_SHA256),
    ):
        table_bytes = _slice(blob, address, address + 4 * len(values))
        if _sha256(table_bytes) != expected_hash:
            raise AuditError(f"legacy advertising function table hash changed at 0x{address:08x}")
        observed = list(struct.unpack_from(f"<{len(values)}I", blob, address - LOAD_BASE))
        if observed != values:
            raise AuditError(f"legacy advertising function table changed at 0x{address:08x}")
    if _occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("legacy advertising source-path pointer closure changed")
    if _slice(blob, SOURCE_PATH, SOURCE_PATH + len(SOURCE_PATH_BYTES)) != SOURCE_PATH_BYTES:
        raise AuditError("legacy advertising retained source path changed")
    if _sha256(SOURCE_PATH_BYTES) != SOURCE_PATH_SHA256:
        raise AuditError("legacy advertising retained source-path hash changed")
    _verify_aligned_entry_pointers(blob)

    for path, (size, digest) in PRODUCTION_PINS.items():
        data = path.read_bytes()
        if len(data) != size or _sha256(data) != digest:
            raise AuditError(f"legacy advertising production input changed: {path}")
    report_path = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    source_path = PRODUCTION_SOURCE.relative_to(ROOT).as_posix()
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path") == source_path
    ]
    observed_leaves = tuple(
        (
            row["extraction"]["function"], row["placement"]["offset"],
            row["extraction"]["size"], row["placement"]["padding_before"],
            row["extraction"]["relocation_count"],
            row["extraction"]["sha256"],
        )
        for row in leaves
    )
    if observed_leaves != PRODUCTION_LEAVES:
        raise AuditError("legacy advertising production leaf pins changed")
    overlay = report["overlay"]
    component = report["component"]
    if (overlay["size"], overlay["sha256"]) != PRODUCTION_OVERLAY:
        raise AuditError("legacy advertising aggregate overlay changed")
    if (component["size"], component["sha256"]) != PRODUCTION_COMPONENT:
        raise AuditError("legacy advertising aggregate component changed")
    config = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    patches = [
        row for row in config["patch_sites"]
        if row.get("name", "").startswith("replace_cordio_dm_adv_leg_")
    ]
    if len(patches) != 17 or sum(row["expected_size"] for row in patches) != 4_396:
        raise AuditError("legacy advertising production redirect closure changed")
    if [row["branch"] for row in patches].count("copy") != 3:
        raise AuditError("legacy advertising empty-action copy closure changed")
    manifest = json.loads((ROOT / "manifests/g2-2.2.6.10-core-source.json").read_text())
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    if sum(row["name"].startswith("cordio_dm_adv_leg_") for row in regions) != 47:
        raise AuditError("legacy advertising manifest ownership changed")
    package = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
    flash_plan = ROOT / "build/source/flash-plan.json"
    if (package.stat().st_size, _sha256(package.read_bytes())) != PRODUCTION_PACKAGE:
        raise AuditError("legacy advertising production package changed")
    if (flash_plan.stat().st_size, _sha256(flash_plan.read_bytes())) != PRODUCTION_FLASH_PLAN:
        raise AuditError("legacy advertising production flash plan changed")
    flash = json.loads(flash_plan.read_text())
    flash_counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions", "container_only_regions",
        "protected_regions",
    ))
    if flash_counts != (5863, 2, 5, 6):
        raise AuditError("legacy advertising flash-plan region counts changed")

    linked_bytes = sum(end - start for _, start, end, _, _ in FUNCTIONS)
    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "code_start": CODE_SPAN[0],
            "code_end_exclusive": CODE_SPAN[1],
            "code_interval_bytes": CODE_SPAN[1] - CODE_SPAN[0],
            "code_interval_sha256": CODE_SPAN_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": linked_bytes,
            "concatenated_body_sha256": CONCATENATED_BODY_SHA256,
            "inline_literal_and_alignment_bytes": sum(end - start for start, end in DATA_GAPS),
            "concatenated_inline_data_sha256": CONCATENATED_DATA_SHA256,
            "trailing_literal_pool_start": TRAILING_POOL[0],
            "trailing_literal_pool_bytes": TRAILING_POOL[1] - TRAILING_POOL[0],
            "logical_tu_sha256": LOGICAL_TU_SHA256,
            "physical_envelope_sha256": PHYSICAL_ENVELOPE_SHA256,
            "functions": reports,
            "source_only_dead_stripped": ["DmAdvModeLeg"],
            "direct_bl_ingress_sites": sum(len(item[-1]) for item in FUNCTIONS),
            "registered_function_entries": len(EXPECTED_ALIGNED_ENTRY_POINTERS),
            "unexpected_aligned_entry_or_interior_pointers": 0,
            "foreign_interleaved_accessor": {
                "start": FOREIGN_ACCESSOR[0],
                "end_exclusive": FOREIGN_ACCESSOR[1],
                "classification": "adjacent vendor advertising-state accessor; not dm_adv_leg.c",
            },
        },
        "abi": {
            "dm_num_adv_sets": 2,
            "dmAdvCb_address": 0x20073394,
            "dmAdvCb_offsets": {
                "timer": 0x00, "intervalMin": 0x10, "intervalMax": 0x14,
                "advType": 0x18, "channelMap": 0x1A, "localAddrType": 0x1C,
                "advState": 0x1D, "duration": 0x20, "enabled": 0x24,
                "peerAddr": 0x25, "peerAddrType": 0x31,
            },
            "dmLegAdvCb_address": 0x20074FB3,
            "message_data_payload_offset": 8,
            "message_data_layout": "Ambiq flexible array; not public Packetcraft pointer field",
            "action_entries": 8,
            "state_accessor_handle_bound": 2,
        },
        "lineage": {
            "selected_public_definition_oracle": "Packetcraft r20.05c commit 3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "definition_interval": "identical r19.02/AmbiqSuite 2.4.2-2.5.1 through r20.05c",
            "stock_header_oracle": "AmbiqSuite 2.4.2/2.5.1 dm_adv.h flexible-array ABI",
            "retained_source_path": SOURCE_PATH_BYTES[:-1].decode("ascii"),
            "license": "Apache-2.0",
            "stock_qualification": "exact public definition bodies plus Ambiq header ABI and vendor diagnostics",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "anchored_functions_in_probe": 5,
            "anchored_bytes_in_probe": 1_914,
            "source_inventory_functions": 18,
            "compiler_profiles": 2,
            "provider_seams": 20,
            "linked_unresolved_symbols": 0,
        },
        "production": {
            "status": "production-routed",
            "source_owned_bytes_added": 948,
            "alignment_bytes_added": 26,
            "strict_relocations": 32,
            "redirected_stock_functions": 17,
            "redirected_stock_bytes": 4_396,
            "source_only_target_compiled": ["DmAdvModeLeg"],
            "manifest_regions": 47,
            "flash_plan_counts": flash_counts,
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
        module = report["module"]
        print(
            "Cordio legacy advertising evidence authenticated: "
            f"{module['linked_function_count']} linked functions / "
            f"{module['linked_function_bytes']} code bytes"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
