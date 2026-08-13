#!/usr/bin/env python3
"""Fail-closed audit for the linked G2 Cordio local-device module."""

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
READINESS_MANIFEST = ROOT / "research/readiness/dm-dev/SHA256SUMS"
READINESS_BYTES = 1_209
READINESS_SHA256 = "4707648b66a73ca9a30ecadc9e318c014d6ad7314da81bc4090e380779152d11"
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-dev-function-map.tsv": "44575e5f2bcb2b596191e0b7c0fce142690f289de727b306cedec57530022ccd",
    ROOT / "tools/manifests/packetcraft-cordio-dm-dev-provenance.tsv": "53d3afab77b0f8ed03c9d8b19316bcd4dbb9d0e55a722f853ae2e6ade81a292e",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-build-results.tsv": "af5c159ec1785fb1c2c17f68ca7029e493292f98fd3f087ff65b5c92d826edb6",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-closure-results.tsv": "b7aa34078ecafe7117373ac6f6ad1ec35defb2050c71101b2cd33f6c7ce67005",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-include-closure.tsv": "a696d840595eacc50a6e983a7adb82a213c4456560232b7b951013c4e31fbf7e",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-source-identities.tsv": "76babff3ec994a9ea93e3c445351f3f4cf696325edb6c24b9b54c65f901bf842",
    ROOT / "tools/manifests/readiness-cordio-dm-dev-undefined-providers.tsv": "7d7a02f56e9d24adb7f73d81abae771432f74fd87965644d0eb83601f44c5533",
}

FUNCTIONS = {
    "dmDevActReset": (0x004B2DF8, 0x004B2E28, "91967cb83911bd29109f0d21bd9c1a7c5625e035662050e4503e503c22a72901"),
    "dmDevHciEvtReset": (0x004B2E28, 0x004B2E3A, "48aa36048ef5e321b055832d32ccd883cca9faff71cc3bd032c520a6de9e0ef4"),
    "dmDevHciEvtVendorSpecCmdCmpl": (0x004B2E3A, 0x004B2E48, "dfe81b4e9c74bb053b543332c630ab2f8df13c500299b9e983b7389bc8c084a5"),
    "dmDevHciEvtVendorSpec": (0x004B2E48, 0x004B2E56, "dd96c85703da73f6cb466cd499880bc139fbca2a5a30e00fe5af5ec80c27403b"),
    "dmDevHciEvtHwError": (0x004B2E56, 0x004B2E64, "432100d15fd5ee350cda124028fc496e8fc6e8f89ff65d860b19b9f53aba6e11"),
    "dmDevHciHandler": (0x004B2E64, 0x004B2E94, "3359e2509625fd1d9a8a4923e855857546a6be30c88fc9e333342fd3b7491a56"),
    "dmDevMsgHandler": (0x004B2E94, 0x004B2EA6, "32df7fdde0ebdd1fe81674cdd74c243228a98ed8c415f16daef5c793254dfd45"),
    "dmDevPassEvtToDevPriv": (0x004B2EA6, 0x004B3008, "27a81d71b84b52ea142867a8b1d533cbade64918c07353c1610bab98739e807c"),
    "dmDevPassEvtToConnCte": (0x004B3008, 0x004B3026, "9efd8e97a9a6147c399f8517d8ba7a7c3b2e7997eca9b1a26de0dcef12220a7d"),
    "DmDevReset": (0x004B3026, 0x004B304C, "91065f6d1a91ecec6a2f11fc5854db96ec432f1dadc49a106cfeaac909ae07d3"),
    "DmDevSetRandAddr": (0x004B304C, 0x004B3060, "6127d0b2092ed9812aa20c3da5c9f2dd2ebc6ea2686a49328fbcf90596dfcac5"),
    "DmDevVsInit": (0x004B308C, 0x004B3096, "058828ca551b9136228f90db0d56c746a664209740aeeb2bd73b4363a4a9787a"),
}
BODY_CONCAT_SHA256 = "18db99eb155b8e577a441b25aecd914e7d64953c7674b9e6f37739d131c32dd8"
POOL = (0x004B3060, 0x004B308C)
POOL_SHA256 = "34b8b350c04cf996ad08a0ad3ca87696ec0739c3fa5e8e3125a635f69bb6d930"
PAD = (0x004B3096, 0x004B3098)
PAD_SHA256 = "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"
PHYSICAL = (0x004B2DF8, 0x004B3098)
PHYSICAL_SHA256 = "1fced11091cb40594dae51a943c599abd9a58562f6a5bfa9152e2dd2c7cf5cbc"
SOURCE_PATH = 0x006E0010
SOURCE_PATH_POINTER_CELLS = [0x004B3084]
SOURCE_PATH_BYTES = (
    b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\"
    b"ble-host\\sources\\stack\\dm\\dm_dev.c\x00"
)
SOURCE_PATH_SHA256 = "2e71334bdb0b61d84490ca88993476c9adcceeff0ce474691772026ecdde75db"
SOURCE_PATH_LOAD_SITES = [0x004B2EEC, 0x004B2F32, 0x004B2F78, 0x004B2FB0]

CALLERS = {
    "dmDevActReset": [],
    "dmDevHciEvtReset": [0x004B2E7A],
    "dmDevHciEvtVendorSpecCmdCmpl": [0x004B2E80],
    "dmDevHciEvtVendorSpec": [0x004B2E86],
    "dmDevHciEvtHwError": [0x004B2E8C],
    "dmDevHciHandler": [],
    "dmDevMsgHandler": [],
    "dmDevPassEvtToDevPriv": [0x004B6458,0x004B646C,0x004B64A2,0x004B64B6,0x004B64F8,0x004BA632,0x004BA670,0x004BAAEA,0x004BAC1A,0x004D2798,0x005369CA,0x00536A80,0x0055BC6A],
    "dmDevPassEvtToConnCte": [0x004B6474, 0x004B64D8],
    "DmDevReset": [0x004B4226,0x004B4C24,0x004B4C80,0x004B4DDA,0x004B79FC,0x004B810E,0x00503D0C,0x0052AEF2],
    "DmDevSetRandAddr": [0x0046DBFC],
    "DmDevVsInit": [0x004B800A],
}
DIRECT_CALLEES = {
    0x004B2E28: [0x004B2E7A],
    0x004B2E3A: [0x004B2E80],
    0x004B2E48: [0x004B2E86],
    0x004B2E56: [0x004B2E8C],
    0x0043D0CE: [0x004B2EC8,0x004B2F0E,0x004B2F54,0x004B2F8C],
    0x0043D574: [0x004B2EF2,0x004B2F38,0x004B2F7E,0x004B2FB6],
    0x0044B610: [0x004B2EC0,0x004B2F06,0x004B2F4C,0x004B2FCA],
    0x004C9C50: [0x004B2EB2,0x004B2EF8,0x004B2F3E,0x004B2F84,0x004B2FBC],
    0x004D293C: [0x004B3054],
    0x004BF99E: [0x004B3036],
    0x004BF9BA: [0x004B3046],
    0x0052A63C: [0x004B2FE4],
    0x0052AC6A: [0x004B2E22],
    0x0052B4BA: [0x004B305A],
}
EXPECTED_TABLES = {
    (0x0078A844, 0x0078A850): ("adacb3acaa5f73026e275351903ab11abbfb15c9b98c5065654dd04db9abf21e", [0x004D29BF,0x004B2E65,0x004B2E95]),
    (0x0078EFF4, 0x0078EFF8): ("ea3eaeae11daa10b9ef498eee7912ee607654ffe538e2db0e0726044556b7566", [0x004B2DF9]),
}
EXPECTED_POOL_WORDS = {
    0x004B306C: 0x20073B78,
    0x004B3070: 0x20000694,
    0x004B3074: 0x0078EFF4,
    0x004B3078: 0x0078D444,
    0x004B307C: 0x00714440,
    0x004B3080: 0x00776A9C,
    0x004B3084: SOURCE_PATH,
    0x004B3088: 0x0078D44C,
}
SOURCE_ONLY = [
    "DmDevWhiteListAdd", "DmDevWhiteListRemove", "DmDevWhiteListClear",
    "dmDevSetFilterPolicy", "DmDevSetFilterPolicy", "DmDevSetExtFilterPolicy",
]


class AuditError(RuntimeError):
    """Raised when authenticated DM-device evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [LOAD_BASE + i for i in range(len(blob) - 3) if blob[i:i + 4] == packed]


def _load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_dev_thumb", path)
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
        raise AuditError("Lorelei dm_dev readiness size changed")
    if _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_dev readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_dev input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = _slice(blob, start, end)
        if _sha256(data) != expected:
            raise AuditError(f"stock dm_dev body changed: {name}")
        bodies.append(data)
    if _sha256(b"".join(bodies)) != BODY_CONCAT_SHA256:
        raise AuditError("dm_dev concatenated body digest changed")
    if _sha256(_slice(blob, *POOL)) != POOL_SHA256:
        raise AuditError("dm_dev literal pool changed")
    if _sha256(_slice(blob, *PAD)) != PAD_SHA256:
        raise AuditError("dm_dev trailing pad changed")
    if _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("dm_dev physical translation unit changed")

    path_data = _slice(blob, SOURCE_PATH, SOURCE_PATH + len(SOURCE_PATH_BYTES))
    if path_data != SOURCE_PATH_BYTES or _sha256(path_data) != SOURCE_PATH_SHA256:
        raise AuditError("retained dm_dev source path changed")
    if _occurrences(blob, SOURCE_PATH) != SOURCE_PATH_POINTER_CELLS:
        raise AuditError("dm_dev source-path pointer closure changed")

    decoder = _load_decoder()
    callers: dict[str, list[int]] = {name: [] for name in FUNCTIONS}
    direct: dict[int, list[int]] = {target: [] for target in DIRECT_CALLEES}
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            callers[starts[target]].append(address)
        if PHYSICAL[0] <= address < PHYSICAL[1] and target in direct:
            direct[target].append(address)
    if callers != CALLERS:
        raise AuditError("dm_dev direct caller closure changed")
    if direct != DIRECT_CALLEES:
        raise AuditError("dm_dev direct callee closure changed")

    stored: dict[int, list[int]] = {}
    body_addresses = set()
    for start, end, _ in FUNCTIONS.values():
        body_addresses.update(range(start, end, 2))
    strict_interiors = body_addresses - {start for start, _, _ in FUNCTIONS.values()}
    interior_pointers = []
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in starts:
            stored.setdefault(address, []).append(value)
        elif target in strict_interiors:
            interior_pointers.append((address, value))
    expected_stored = {
        0x0078A848: [0x004B2E65],
        0x0078A84C: [0x004B2E95],
        0x0078EFF4: [0x004B2DF9],
    }
    if stored != expected_stored or interior_pointers:
        raise AuditError("dm_dev stored entry/interior pointer closure changed")

    tables = {}
    for bounds, (expected_hash, expected_values) in EXPECTED_TABLES.items():
        data = _slice(blob, *bounds)
        values = list(struct.unpack(f"<{len(data) // 4}I", data))
        if _sha256(data) != expected_hash or values != expected_values:
            raise AuditError(f"dm_dev registered table changed at 0x{bounds[0]:08x}")
        tables[f"0x{bounds[0]:08x}"] = values
    for address, expected in EXPECTED_POOL_WORDS.items():
        actual = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"dm_dev pool word changed at 0x{address:08x}")
    if decoder.literal_references(blob, 0x004B3084) != SOURCE_PATH_LOAD_SITES:
        raise AuditError("dm_dev source-path load closure changed")

    # High-value message/event architecture immediates.
    expected_halfwords = {
        0x004B2E1E: 0x2815,  # DM_NUM_IDS == 21
        0x004B2E3C: 0x217B,  # vendor command complete
        0x004B2E4A: 0x217A,  # vendor-specific event
        0x004B2E58: 0x2179,  # hardware error
        0x004B300A: 0x226F,  # DM_CONN_CTE_MSG_STATE
        0x004B303E: 0x2138,  # DM_DEV_MSG_API_RESET
    }
    for address, expected in expected_halfwords.items():
        actual = struct.unpack("<H", _slice(blob, address, address + 2))[0]
        if actual != expected:
            raise AuditError(f"dm_dev architecture immediate changed at 0x{address:08x}")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "physical_sha256": PHYSICAL_SHA256,
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "body_concat_sha256": BODY_CONCAT_SHA256,
            "literal_pool_bytes": POOL[1] - POOL[0],
            "trailing_pad_bytes": PAD[1] - PAD[0],
            "direct_bl_ingress_sites": sum(len(v) for v in callers.values()),
            "registered_function_pointers": len(stored),
            "strict_interior_pointers": len(interior_pointers),
            "source_inventory_functions": 18,
            "source_only_functions": SOURCE_ONLY,
        },
        "dispatch": {
            "tables": tables,
            "dm_num_ids": 21,
            "dm_message_mask": 7,
            "dm_dev_reset_event": 0x38,
            "dm_conn_cte_state_event": 0x6F,
            "hci_inputs": [0, 18, 19, 20],
            "dm_callback_outputs": [0x20, 0x7B, 0x7A, 0x79],
            "direct_callee_relocations": sum(len(v) for v in direct.values()),
            "indirect_dispatch_sites": [0x004B2E16,0x004B2E36,0x004B2E44,0x004B2E52,0x004B2E60,0x004B2EA2,0x004B3002,0x004B3022],
        },
        "abi": {
            "dm_cb": 0x20073B78,
            "local_addr_offset": 0,
            "callback_offset": 8,
            "handler_id_offset": 0x0C,
            "resetting_offset": 0x10,
            "dm_function_interface_table": 0x20000694,
            "device_privacy_component_id": 1,
            "connection_cte_component_id": 13,
            "dm_dev_cb": 0x200744F4,
            "dm_num_adv_sets": 2,
        },
        "lineage": {
            "selected_official_source": "AmbiqSuite R4.4.1 via AmbiqAI/neuralSPOT",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "cb169ff9d07eac7dbea2f25723cc6816c5c8d48e",
            "selected_sha256": "da6094bd77961d1e42f7ccdd78d0551f9888860bcd3ba5c43fbfe4981130dc3e",
            "stock_discriminator": "separate command/vendor/error translators, trace line 214, reset-clear patch, and r20 message IDs",
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST),
            "archive_sha256": READINESS_SHA256,
            "conservative_stock_anchors": 1,
            "conservative_stock_anchor_bytes": 354,
            "compiler_profiles": 2,
            "provider_seams": 14,
            "valid_non_vacuous_closure_profiles": 2,
            "linked_unresolved_symbols": 0,
            "minimum_retained_text": 556,
            "retained_bss": 5124,
        },
        "production": {"source_owned_bytes_added": 0, "stock_bytes_replaced": 0},
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
            "Cordio dm_dev closed: "
            f"{module['linked_function_count']} functions / "
            f"{module['linked_function_bytes']} code bytes"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
