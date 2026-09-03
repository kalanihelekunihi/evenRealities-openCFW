#!/usr/bin/env python3
"""Fail-closed audit for the stock G2 Cordio device-manager router."""

from __future__ import annotations

import argparse
import hashlib
import importlib
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
READINESS_MANIFEST = ROOT / "research/readiness/dm-main/SHA256SUMS"
READINESS_BYTES = 1_302
READINESS_SHA256 = "402cf2c7901b343bef43c6cb1acca540acc9b9a3800c2e503e6e5afb6c127d55"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE = ROOT / "components/shared/cordio/runtime_cordio_dm_main.c"
HEADER = ROOT / "components/shared/cordio/runtime_cordio_dm_main.h"
TEST = ROOT / "tests/test_runtime_cordio_dm_main.py"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
SOURCE_PIN = (10_852, "5152a1727b61f74af21bbee81ca062536bc9ca970a3e60f16145f3e039c41aaf")
HEADER_PIN = (2_252, "f168ba398d10500f1d5864569228787564b044a33b7541733efbd18c89f26f64")
TEST_PIN = (12_041, "f87d3046ca7fdf1179091c6ea8396a439d4e57cca6f2a1b4cc01b3b261d1d189")
PRODUCTION_OVERLAY = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
PRODUCTION_COMPONENT = (3_956_672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef")
PRODUCTION_PACKAGE = (4_750_780, "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27")
PRODUCTION_FLASH_PLAN = (4_961_300, "f2625775d8a7b3c81c8862db00979cdcf4965eeb003e4b6b84e8cb2d8c1293b9")
PINNED_INPUTS = {
    ROOT / "tools/manifests/packetcraft-cordio-dm-main-function-map.tsv":
        "52bd88e68310d813b191cf53be8177ad0ed33ed83d9698175a7340e988b75363",
    ROOT / "tools/manifests/packetcraft-cordio-dm-main-provenance.tsv":
        "a4d25277fd8fe980ea5d2cfc53e085baa4ae66fe0cd55a6485ae9fad86e123a6",
    ROOT / "tools/manifests/readiness-cordio-dm-main-build-results.tsv":
        "b703725571bd2658177d530bde5a622d6e8931efc35dd39bc68610c82e91dc52",
    ROOT / "tools/manifests/readiness-cordio-dm-main-candidate-discriminator.tsv":
        "df7a4efb28c879403fe6e0928ac546b9fae3ff87a405e8a1035bb7f409e7bf36",
    ROOT / "tools/manifests/readiness-cordio-dm-main-closure-results.tsv":
        "4f3ee1df9dafcb4912048cf17319e7f4edca0bdb23a8a1cef1888d1c387cd3ce",
    ROOT / "tools/manifests/readiness-cordio-dm-main-include-closure.tsv":
        "53c50e90772e7b3947b28b9182b566250acf0a1c07d246aae904253d2cb320e0",
    ROOT / "tools/manifests/readiness-cordio-dm-main-r441-input-identities.tsv":
        "5b9d514945dfb659e3fee2f9ad610feff3b70f4e05e69cacdec0dc40c621182d",
    ROOT / "tools/manifests/readiness-cordio-dm-main-source-identities.tsv":
        "642187bf52a9fa22d7069d74bd20c65577f6db0259d882fa5eed4704e9680cd0",
    ROOT / "tools/manifests/readiness-cordio-dm-main-undefined-providers.tsv":
        "0759c09b5af17a1d65c81d298aacdb2bad2a849a12c85ef81eb475199cabb79c",
}

FUNCTIONS = {
    "dmHciEvtCback": (0x004D299C, 0x004D29BE, "b17c7de7f07989946aa573f9d526bf3608519abd6d60337e66c6ab22f34c80fd"),
    "dmEmptyReset": (0x004D29BE, 0x004D29C0, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "dmEmptyHandler": (0x004D29C0, 0x004D29C2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "dmDevPassHciEvtToConn": (0x004D29C2, 0x004D29CE, "b3431bf41015550f59f3a5e019a14d26255aca075f5e5850515abac5370130ac"),
    "DmRegister": (0x004D29CE, 0x004D2A06, "ba349e8e5645eff35022b2ea6c68675455d3aed3fe5e5ad65dc3293cb484bda9"),
    "DmFindAdType": (0x004D2A06, 0x004D2A46, "47788f8d1b0247eaa47865cf2159dc71aa039b526032a36c85d7a50fe8427f51"),
    "DmHandlerInit": (0x004D2A46, 0x004D2A5C, "a8b518e0a5b7e05027f077c6dd6a7b4a6ffc427be537a9f0b04b47b70581cb97"),
    "DmHandler": (0x004D2A5C, 0x004D2A7E, "ee6f3c27ec1b668ccea4a9e3d04e2a8168fc02cee71ffcf2f2065377b751c7b5"),
    "DmLlPrivEnabled": (0x004D2A7E, 0x004D2A84, "3452a2e9f881d8a5a0e734eb442674b16b63b931fcd7119abe34c705115fe1e2"),
    "DmLlAddrType": (0x004D2A84, 0x004D2AA8, "4a20ec96c74e5fa5bf3188c3a2c0b600d853ceaff000cf64b7a00089cc093056"),
    "DmHostAddrType": (0x004D2AA8, 0x004D2ACC, "62b5170c4d157293ef923f947116d25e1d0d27bcd6f229bfa34e84f6e5c6bdf0"),
    "DmSizeOfEvt": (0x004D2ACC, 0x004D2AE8, "6d837a89649b3b1eb8b9314d0add5754e787e5159cf75efa145684e3e86fe11a"),
    "dmScanPhyToIdx": (0x004D2B00, 0x004D2B3E, "d505d6ee7f4f5a2dc7afe547118dfa5bad6af9461a319a28814183ab4372a8aa"),
    "DmScanPhyToIdx": (0x004D2B3E, 0x004D2B4C, "53e4628f2d5336fde56bf2acb22e0f2cf78270a7eed3c2b77fb0a22b573625d7"),
    "dmInitPhyToIdx": (0x004D2B4C, 0x004D2B8A, "d505d6ee7f4f5a2dc7afe547118dfa5bad6af9461a319a28814183ab4372a8aa"),
    "DmInitPhyToIdx": (0x004D2B8A, 0x004D2B98, "53e4628f2d5336fde56bf2acb22e0f2cf78270a7eed3c2b77fb0a22b573625d7"),
}
BODY_CONCAT_SHA256 = "b205ad08e7f2f8046ac507d588f7f51ad87fc17444d67412254e08021bb18f25"
PHYSICAL = (0x004D299C, 0x004D2B98)
PHYSICAL_SHA256 = "b45dd5bb498ca7f31fc5c60b4eea5571d0a3a76b279d93831641302c463674de"
LITERAL_GAP = (0x004D2AE8, 0x004D2B00)
LITERAL_GAP_SHA256 = "10ef058b1cf51e6492e342a86269d0a4c668187dea6ae19d7a54972a06da6b8f"
LITERAL_WORDS = [0x20073B78, 0x20000694, 0x006E006C, 0x0078A850, 0x004D299D, 0x006D1904]

HCI_ROUTE = (0x006E006C, 0x006E00C6)
HCI_ROUTE_SHA256 = "6a01e464d577fb127d88ad65cc81002de6041494b34f3a3784abb6fc716e528f"
HCI_ROUTE_VALUES = [7,3,3,3,3,3,2,4,4,4,4,4,5,5,5,5,5,7,7,7,7,6,6,6,6,6,6,5,5,4,4,7,7,4,7,4,4,5,5,4,4,9,9,9,2,2,0,0,11,11,11,7,2,0,2,0,10,1,11,12,12,13,13,13,13,13,13,13,16,16,22,13,16,16,16,4,17,17,20,20,20,20,20,20,18,18,19,19,19,19]
EVENT_LENGTHS = (0x006D1904, 0x006D19BC)
EVENT_LENGTHS_SHA256 = "e2d84537496c845a86cfb034cdb743e8528a1e87c146aab5399239709a1b4935"
EVENT_LENGTH_VALUES = [4,4,4,12,4,4,28,36,10,14,6,4,6,4,6,34,16,8,6,36,100,20,6,4,10,10,6,6,6,12,12,6,14,14,8,6,10,6,10,8,10,12,4,4,36,6,6,22,22,6,26,26,8,8,16,16,14,28,28,8,8,8,8,8,8,8,8,10,40,6,10,40,10,10,6,6,6,44,32,16,60,6,56,56,6,6,28,8,4,6,6,136]

DM_FCN_IF_TABLE = 0x20000694
DM_NUM_IDS = 21
DM_DEFAULT_IF = (0x0078A850, 0x0078A85C)
DM_DEFAULT_IF_SHA256 = "203372a811e7881325fe55a1ef19871303192cfda3e2d76d8d08db14afb459ef"
DM_FCN_IF_BOOT_SHA256 = "590f6b5e0e6e2075ecf65176a09eed976c145138f6d486d69e808165c06bdeac"
DM_FCN_IF_BOOT_VALUES = [0x0078A850] * DM_NUM_IDS
DM_FCN_IF_BOOT_VALUES[7] = 0x0078A844

CALLERS = {
    "dmHciEvtCback": [], "dmEmptyReset": [], "dmEmptyHandler": [],
    "dmDevPassHciEvtToConn": [0x004B315E], "DmRegister": [0x004B7ECA],
    "DmFindAdType": [0x0049FD00,0x0049FD20,0x005368E6],
    "DmHandlerInit": [0x004B8036], "DmHandler": [],
    "DmLlPrivEnabled": [0x004B3BA8,0x00503874],
    "DmLlAddrType": [0x004B9A90,0x00536838,0x00536A3A],
    "DmHostAddrType": [0x0047A7E4,0x0047AA78,0x0047AD7C,0x0049FD4A,0x0049FDA4,0x0049FE0A,0x0049FE64,0x004A01D0,0x004B63EE,0x00541FD0],
    "DmSizeOfEvt": [0x004B7494], "dmScanPhyToIdx": [0x004D2B46],
    "DmScanPhyToIdx": [0x00536826,0x00536A30,0x0055BB4A],
    "dmInitPhyToIdx": [0x004D2B92], "DmInitPhyToIdx": [0x004B6D76,0x004B6DA6],
}
EXPECTED_STORED = {
    0x004B8780: 0x004D2A5D, 0x004D2AF8: 0x004D299D,
    0x0078A82C: 0x004D29BF, 0x0078A838: 0x004D29BF,
    0x0078A83C: 0x004D29C1, 0x0078A844: 0x004D29BF,
    0x0078A850: 0x004D29BF, 0x0078A854: 0x004D29C1,
    0x0078A858: 0x004D29C1, 0x0078A85C: 0x004D29BF,
    0x0078A864: 0x004D29C1, 0x0078A874: 0x004D29BF,
    0x0078A878: 0x004D29C1, 0x0078A8A4: 0x004D29BF,
    0x0078A8A8: 0x004D29C1,
}

PRODUCTION_FUNCTIONS = [
    "open_cfw_cordio_dm_hci_event_callback",
    "open_cfw_cordio_dm_empty_reset",
    "open_cfw_cordio_dm_empty_handler",
    "open_cfw_cordio_dm_pass_hci_event_to_connection",
    "open_cfw_cordio_dm_register_callback",
    "open_cfw_cordio_dm_find_advertising_type",
    "open_cfw_cordio_dm_handler_initialize",
    "open_cfw_cordio_dm_handler",
    "open_cfw_cordio_dm_link_layer_privacy_enabled",
    "open_cfw_cordio_dm_link_layer_address_type",
    "open_cfw_cordio_dm_host_address_type",
    "open_cfw_cordio_dm_size_of_event",
    "open_cfw_cordio_dm_scan_phy_to_index_internal",
    "open_cfw_cordio_dm_scan_phy_to_index",
    "open_cfw_cordio_dm_initiator_phy_to_index_internal",
    "open_cfw_cordio_dm_initiator_phy_to_index",
]
PRODUCTION_LEAVES = [
    (288916,60,0,"3785e004053871bb0ed72e9089944998c172e8d48b09ec0df6f4a8be3d5038a4"),
    (288976,2,0,"c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    (288980,2,0,"c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    (288984,26,0,"c7e6d84d4336b6ecb2be68c06429552409ff2e5448b10e1c76ed2561176c444a"),
    (289012,62,1,"550fb103aa8dcd3d5897f9e0d5fc9a11933b37c488abf8c027c8685ae6ae8667"),
    (289076,76,0,"958ef8e09deba5426d9c5a82f9b57de315e085a6c62b4dbcaab454c191ebe10f"),
    (289152,28,1,"de979419925cf0441b0376d0e1e7b4603c2828ee27a37328ee5b3e2731e6968b"),
    (289180,52,0,"5ac9825ab14376d5b1f6861a149d3467c0dc91d263091c6bc03712b4fbf8ac41"),
    (289232,18,0,"8c08e97619be32f6af33eab2042a65135f48acf7906f7c6e10b874e696fa1b26"),
    (289252,32,0,"a1ddd33b581943dcf2bab69b7ed3fcd0c2c5bc9315d200214718e7c366183d4a"),
    (289284,32,0,"6ceae194edf1d250ecb1ae8b7fb4d8620043cecbf669c3c0feb9aafeda1821ba"),
    (289316,30,0,"05e345c48461ac138fdf0a009b4fb41a6979b8570251012ee9667944e0fbbdf8"),
    (289348,38,0,"e8deb0ffb4d3b89bf3c9bcda6ba258733e4a58194afa099bce8c1cd67e52f565"),
    (289388,14,0,"812bc7d588788d323e2342b344eea99b449be1bd5b079ba1ccc0254e4bdc7ad0"),
    (289404,38,0,"e8deb0ffb4d3b89bf3c9bcda6ba258733e4a58194afa099bce8c1cd67e52f565"),
    (289444,14,0,"defa3db371a7663e7388fcc45e8d35c88bff9e266a4c86dd63d8b8133e616d20"),
]


class AuditError(RuntimeError):
    """Raised when authenticated DM-main evidence changes."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - LOAD_BASE:end - LOAD_BASE]


def _verify_file(path: Path, expected: tuple[int, str], label: str) -> None:
    data = path.read_bytes()
    if (len(data), _sha256(data)) != expected:
        raise AuditError(f"{label} changed")


def _verify_production() -> dict[str, Any]:
    _verify_file(SOURCE, SOURCE_PIN, "DM main source")
    _verify_file(HEADER, HEADER_PIN, "DM main header")
    _verify_file(TEST, TEST_PIN, "DM main test")
    report = json.loads(REPORT.read_text())
    config = json.loads(CONFIG.read_text())
    manifest = json.loads(MANIFEST.read_text())
    leaves = [
        row for row in report["relocated_leaves"]
        if row.get("source", {}).get("path", "").endswith(SOURCE.name)
    ]
    leaves.sort(key=lambda row: row["pins"]["offset"])
    if len(leaves) != len(PRODUCTION_FUNCTIONS):
        raise AuditError("DM main production leaf count changed")
    for row, function, expected in zip(
        leaves, PRODUCTION_FUNCTIONS, PRODUCTION_LEAVES
    ):
        observed = (
            row["pins"]["offset"], row["extraction"]["size"],
            row["extraction"]["relocation_count"],
            row["extraction"]["sha256"],
        )
        if row["extraction"]["function"] != function or observed != expected:
            raise AuditError(f"DM main production leaf changed: {function}")
    sites = {
        row["name"]: row for row in config["patch_sites"]
        if row["name"].startswith("replace_cordio_dm_main_")
    }
    if len(sites) != len(PRODUCTION_FUNCTIONS):
        raise AuditError("DM main production route count changed")
    copy_indices = {2, 3}
    for index, ((name, (start, end, digest)), function) in enumerate(
        zip(FUNCTIONS.items(), PRODUCTION_FUNCTIONS), 1
    ):
        site = sites.get(f"replace_cordio_dm_main_{index:02d}")
        expected_branch = "copy" if index in copy_indices else "b_w"
        if (
            site is None or site["runtime_address"] != start
            or site["expected_size"] != end - start
            or site["expected_sha256"] != digest
            or site["target_function"] != function
            or site["branch"] != expected_branch
        ):
            raise AuditError(f"DM main route changed: {name}")
    override = manifest["component_overrides"]["apollo_main"]
    regions = [
        row for row in override["regions"]
        if row["name"].startswith("cordio_dm_main_")
    ]
    if (
        (report["overlay"]["size"], report["overlay"]["sha256"])
            != PRODUCTION_OVERLAY
        or (report["component"]["size"], report["component"]["sha256"])
            != PRODUCTION_COMPONENT
        or (override["provider"].get("size"),
            override["provider"].get("sha256")) != PRODUCTION_COMPONENT
        or len(regions) != 42
    ):
        raise AuditError("DM main component ownership changed")
    _verify_file(PACKAGE, PRODUCTION_PACKAGE, "DM main package")
    _verify_file(FLASH_PLAN, PRODUCTION_FLASH_PLAN, "DM main flash plan")
    flash = json.loads(FLASH_PLAN.read_text())
    counts = tuple(len(flash[key]) for key in (
        "flash_regions", "unresolved_flash_regions",
        "container_only_regions", "protected_regions",
    ))
    if counts != (7104, 0, 8, 6):
        raise AuditError("DM main flash counts changed")
    return {
        "status": "production-routed",
        "redirected_stock_functions": 14,
        "exact_copy_functions": 2,
        "covered_stock_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
        "source_owned_bytes_added": sum(row[1] for row in PRODUCTION_LEAVES),
        "alignment_bytes_added": sum(row["placement"]["padding_before"] for row in leaves),
        "strict_relocations": sum(row[2] for row in PRODUCTION_LEAVES),
        "manifest_regions": len(regions),
        "flash_plan_counts": counts,
    }


def _load_thumb_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("dm_main_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _initialized_sram(blob: bytes) -> bytes:
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    return importlib.import_module("analyze_g2_flashdb")._decode_initialized_sram(blob)


def analyze(image: Path = IMAGE) -> dict[str, Any]:
    if image.stat().st_size != IMAGE_BYTES:
        raise AuditError("official G2 image size changed")
    blob = image.read_bytes()
    if _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official G2 image SHA-256 changed")
    if READINESS_MANIFEST.stat().st_size != READINESS_BYTES or _sha256(READINESS_MANIFEST.read_bytes()) != READINESS_SHA256:
        raise AuditError("Lorelei dm_main readiness artifact changed")
    for path, expected in PINNED_INPUTS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned dm_main input changed: {path}")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = _slice(blob, start, end)
        if _sha256(data) != expected:
            raise AuditError(f"stock dm_main body changed: {name}")
        bodies.append(data)
    if _sha256(b"".join(bodies)) != BODY_CONCAT_SHA256:
        raise AuditError("dm_main body concatenation changed")
    if _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("dm_main physical interval changed")
    gap = _slice(blob, *LITERAL_GAP)
    if _sha256(gap) != LITERAL_GAP_SHA256 or list(struct.unpack("<6I", gap)) != LITERAL_WORDS:
        raise AuditError("dm_main literal gap changed")

    routes = _slice(blob, *HCI_ROUTE)
    lengths = _slice(blob, *EVENT_LENGTHS)
    if _sha256(routes) != HCI_ROUTE_SHA256 or list(routes) != HCI_ROUTE_VALUES:
        raise AuditError("dm_main HCI routing table changed")
    if _sha256(lengths) != EVENT_LENGTHS_SHA256 or list(struct.unpack("<92H", lengths)) != EVENT_LENGTH_VALUES:
        raise AuditError("dm_main event-length table changed")
    if _sha256(_slice(blob, *DM_DEFAULT_IF)) != DM_DEFAULT_IF_SHA256:
        raise AuditError("dmFcnDefault changed")

    sram = _initialized_sram(blob)
    offset = DM_FCN_IF_TABLE - 0x20000000
    boot = sram[offset:offset + DM_NUM_IDS * 4]
    if _sha256(boot) != DM_FCN_IF_BOOT_SHA256 or list(struct.unpack("<21I", boot)) != DM_FCN_IF_BOOT_VALUES:
        raise AuditError("boot dmFcnIfTbl changed")

    decoder = _load_thumb_decoder()
    starts = {start: name for name, (start, _, _) in FUNCTIONS.items()}
    callers = {name: [] for name in FUNCTIONS}
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in starts:
            callers[starts[target]].append(address)
    if callers != CALLERS:
        raise AuditError("dm_main direct caller closure changed")

    entries = set(starts)
    interiors = set()
    for start, end, _ in FUNCTIONS.values():
        interiors.update(range(start + 2, end, 2))
    stored: dict[int, int] = {}
    interior_pointers = []
    for address in range(LOAD_BASE, LOAD_BASE + len(blob) - 3, 4):
        value = struct.unpack("<I", _slice(blob, address, address + 4))[0]
        target = value & ~1
        if target in entries:
            stored[address] = value
        elif target in interiors:
            interior_pointers.append((address, value))
    if stored != EXPECTED_STORED or interior_pointers:
        raise AuditError("dm_main stored entry/interior pointer closure changed")

    return {
        "schema_version": 1,
        "image": {"path": str(image), "sha256": IMAGE_SHA256},
        "module": {
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "source_inventory_functions": 16, "source_only_functions": [],
            "direct_bl_ingress_sites": sum(len(v) for v in callers.values()),
            "registered_function_pointers": len(stored),
            "strict_interior_pointers": len(interior_pointers),
        },
        "routing": {
            "hci_route_entries": len(routes),
            "event_length_entries": len(lengths) // 2,
            "component_interface_slots": DM_NUM_IDS,
            "message_component_shift": 3,
            "message_ordinal_mask": 7,
            "request_peer_sca_route_value": routes[70],
            "default_routed_boot_slots": DM_FCN_IF_BOOT_VALUES.count(DM_DEFAULT_IF[0]),
        },
        "abi": {
            "dm_cb": 0x20073B78, "dm_cb_bytes": 0x18,
            "dm_num_adv_sets": 2, "dm_num_phys": 2,
            "dm_conn_max": 3, "dm_sync_max": 1,
        },
        "lineage": {
            "selected_source_family": "official AmbiqSuite R4.4.1",
            "corroborating_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "6ffb4e76585b685582fc2c3dd01049a477b06481",
            "selected_sha256": "ff9424decca9109d2aa3718ef8521f8eacc083031ff6085791cb77546bc4e3b6",
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
        },
        "readiness": {
            "archive": str(READINESS_MANIFEST), "archive_sha256": READINESS_SHA256,
            "lanes": 2, "compiler_profiles_per_lane": 2,
            "provider_seams": 4, "valid_non_vacuous_closure_profiles": 4,
            "linked_unresolved_symbols": 0, "r441_build_is_hybrid": True,
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
        module = report["module"]
        print(f"Cordio dm_main closed: {module['linked_function_count']} functions / {module['linked_function_bytes']} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
