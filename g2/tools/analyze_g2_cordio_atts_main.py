#!/usr/bin/env python3
"""Fail-closed audit for the linked Cordio ATT server owner/dispatcher unit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-main-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-main-provenance.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_main.c": "07ba6daa2635d20250e531637f39044899f80b56aa86d9aa92fafda867a85c6a",
    ROOT / "components/shared/cordio/runtime_cordio_atts_main.h": "242da5dfcfb938bee915c6787832b79b9521578a3f1ca6c911edf5ec54e1efa3",
    MAP: "78fed1c571e8ad9f255cf1b16eecbb0a4e82cfd9a94ec206f8e51c211f20663a",
    PROVENANCE: "7dff7d41421a53887b134e77ced701224682686fa16fa1d5a1a108d5515cc014",
}

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_main.c"
CANDIDATE_PREVIOUS_OVERLAY_SIZE = 344484
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_data_callback",
    "open_cfw_cordio_atts_connection_callback",
    "open_cfw_cordio_atts_message_callback",
    "open_cfw_cordio_atts_l2c_control_callback",
    "open_cfw_cordio_atts_error_response",
    "open_cfw_cordio_atts_clear_prepared_writes",
    "open_cfw_cordio_atts_discovery_busy",
    "open_cfw_cordio_atts_process_database_hash_update",
    "open_cfw_cordio_atts_check_pending_database_hash_read_response",
    "open_cfw_cordio_atts_is_hashable_attribute",
    "open_cfw_cordio_atts_ind_connection_by_id",
    "open_cfw_cordio_atts_ind_connection_by_handle",
    "open_cfw_cordio_atts_initialize",
    "open_cfw_cordio_atts_hash_database_string",
    "open_cfw_cordio_atts_calculate_database_hash",
    "open_cfw_cordio_atts_add_group",
    "open_cfw_cordio_atts_remove_group",
]
CANDIDATE_LEAF_METRICS = [
    (344484, 230, 3), (344716, 146, 9), (344864, 60, 2),
    (344924, 14, 0), (344940, 62, 2), (345004, 38, 2),
    (345044, 82, 2), (345128, 276, 3), (345404, 234, 5),
    (345640, 128, 0), (345768, 38, 1), (345808, 36, 1),
    (345844, 182, 0), (346028, 38, 1), (346076, 848, 5),
    (346924, 110, 4), (347036, 100, 4),
]

FUNCTIONS = {
    "attsDataCback": (0x0053498C, 0x00534ABA, "85eb30f34c90e44920ec79112f060fb6559d06713d818574490fbe66131d452c"),
    "attsConnCback": (0x00534ABA, 0x00534C42, "3bcc8d463d6bd5735159748fea85120a9b5b90c3cca9fbd9b3dd2c9c91eba35e"),
    "attsMsgCback": (0x00534C42, 0x00534C8A, "d3739f3d89c3f36a7bbc0e3b11df247f5c9d123c1af80e9efecc1b99541ce01c"),
    "attsL2cCtrlCback": (0x00534C8A, 0x00534C9A, "24e59a1ce28c2ca2248182f4cd2dd3b698cfac0517f68af7bdcddc4dee5b4730"),
    "attsErrRsp": (0x00534C9A, 0x00534CDE, "3c5485f56cb488f166da84e2ba3f6d71ad35063569e9a33491c6cf83da207647"),
    "attsClearPrepWrites": (0x00534CDE, 0x00534D06, "399cd6fc237964f7ba288253833dac995b66561a8136ec0636ed1d8c198e9b35"),
    "attsDiscBusy": (0x00534D06, 0x00534D46, "c099daf28a9ba578e3c58e8d07da98a114b365913d7a62522b566cc5f3314acf"),
    "attsProcessDatabaseHashUpdate": (0x00534D46, 0x00534DD0, "f00596a27efc58f97df9598ca744d22211f9b796659e6c5b178d1b6a0e1869e8"),
    "attsCheckPendDbHashReadRsp": (0x00534DD8, 0x00534EA8, "bfd372d7c50bacfe0ae7a1f3f9f1a92cce5dc501561bc72119046b1c4a8753c6"),
    "attsIsHashableAttr": (0x00534EA8, 0x00534F0E, "1cc3c52accd3a7a922aa78f7279356d68bd0c81b8d02d222e21aa9e32ecf6623"),
    "attsCcbByConnId": (0x00534F14, 0x005351A8, "09e5d20039fbd32a49e9423b709d0612703ef7a0aa562674c4488068ec2340c1"),
    "attsCcbByHandle": (0x005351A8, 0x005351D6, "50d366d5ffee2e81102410f129066aa9c9b0e054be4e72134bb14087c17db90b"),
    "AttsInit": (0x005351DC, 0x00535258, "e95331e3a4690f7f3b6fe71c099316a36971c554d3d629601db19f7414e856b6"),
    "AttsHashDatabaseString": (0x0053525C, 0x00535276, "fff983cc67c7ee5e7c3c6f6fdd0c01d2dbd5a8fbe6209ec106a290098dc3a137"),
    "AttsCalculateDbHash": (0x0053527C, 0x005353AE, "53f50e7ed0ec6a7be0c78c20a72db17c7f3710f59c3f8d56dabc13c68cdb991a"),
    "AttsAddGroup": (0x005353AE, 0x005353E8, "04ac25c324a223a80d8db282e91a0f6f4d1acf7fd1949393a541a786526d5ff6"),
    "AttsRemoveGroup": (0x005353E8, 0x00535440, "846d4a4b25d6a39464e50ba164b9242ee332f0dc758c2422002e85d1257df7b6"),
}
SOURCE_ONLY = ["AttsAuthorRegister", "AttsSetAttr", "AttsGetAttr", "AttsErrorTest"]
BODY_CONCAT_SHA = "8fd2f55f88f2c162a1278917a5aa0318846d22e59cb8c62700bc4ed5a4a9fd46"
PHYSICAL = (0x0053498C, 0x00535488)
PHYSICAL_SHA = "bbb2af59b583526d4e63a1e2f18fb8dbeec790518b694922061565cc9b511deb"
GAPS = [
    (0x00534DD0, 0x00534DD8, "ba8e7926516ae3369715ddbe1f29bb87840ecbafbf721eb3b8304ffe1553f46e"),
    (0x00534F0E, 0x00534F14, "a09591f721837cb325df3b73b468bb33b75f20cd2ff47067c196ce64a3eace3d"),
    (0x005351D6, 0x005351DC, "2c63161bef9b35aa71cbc37025db3d9c2a2f8a62b9bfc564af6b13e959cfddd6"),
    (0x00535258, 0x0053525C, "a48171e6ce630083872846df4f1a31a16a115f2d98450a911a0e5731afa392de"),
    (0x00535276, 0x0053527C, "a09591f721837cb325df3b73b468bb33b75f20cd2ff47067c196ce64a3eace3d"),
    (0x00535440, 0x00535488, "1e1471ed53e065f846eb914e1678404a0e2d3dad25c9aa477f3bbd92c5b0a5b7"),
]
NONCODE_CONCAT_SHA = "197e22bfadbe05c41285842de4f5f66f47acb1fddfc802690ab38d814cbcceea"
POOL_WORDS = [
    0x2000045C, 0x0077E2D0, 0x2006E5F0, 0x0078CCBC, 0x0073C694,
    0x007852D0, 0x006DC9F4, 0x0078CCC4, 0x200004B4, 0x200610AC,
    0x0078F54E, 0x20074F95, 0x00731C34, 0x007852E0, 0x007756BC,
    0x007851E0, 0x004B4EE7, 0x007852F0,
]

CALLERS = {
    "attsDataCback": [], "attsConnCback": [], "attsMsgCback": [], "attsL2cCtrlCback": [],
    "attsErrRsp": [0x00534AB2, 0x00534DEE, 0x00534E02, 0x0056C846, 0x0056CAA0, 0x0056CBC2, 0x0056CD8C, 0x0056DBFC, 0x0056DD92, 0x0056DF10, 0x0056E0D4, 0x0056E262, 0x0056E4DA, 0x005A5FBA, 0x005A6166, 0x005A622E],
    "attsClearPrepWrites": [0x00534AE8, 0x005A6182, 0x005A61D6, 0x005A620A],
    "attsDiscBusy": [0x0056CA66, 0x0056DD58, 0x0056E4A4],
    "attsProcessDatabaseHashUpdate": [0x00534C84],
    "attsCheckPendDbHashReadRsp": [0x0052C7E0],
    "attsIsHashableAttr": [0x00535290, 0x00535324],
    "attsCcbByConnId": [0x00533BDC, 0x00533C40, 0x00533C56, 0x00533C88],
    "attsCcbByHandle": [0x00534998],
    "AttsInit": [0x004B8062],
    "AttsHashDatabaseString": [0x005353A0],
    "AttsCalculateDbHash": [0x004B7712, 0x004B7C28],
    "AttsAddGroup": [0x0052DC10, 0x0052DC16, 0x005361A8, 0x005361C0, 0x005361D8, 0x005361F0, 0x00536208, 0x00536220],
    "AttsRemoveGroup": [0x00534DB8],
}
CALLER_DIGESTS = {
    "attsDataCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsConnCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsMsgCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsL2cCtrlCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsErrRsp": "feef44ac7884b437652959a36d74c7aa99c5058c59b67188f5599797adc8dccc",
    "attsClearPrepWrites": "2395e0d69a622f4a2eeade7e1c9f05ab162e91bbf2bdda2b4a9859530afb8546",
    "attsDiscBusy": "4df411ef35c40017eccda7ee6394a14575ae98dda0c6a90e3c0d4bdfbfdad8a0",
    "attsProcessDatabaseHashUpdate": "f8dd6749c74e898158658dbd0b3f1295c86f96b15d076be9b8ba9995940b7e99",
    "attsCheckPendDbHashReadRsp": "2d1046ffcc79d6b1e881beda3f2d6f2697f145720fbb7706ae61ae6be7eb12c9",
    "attsIsHashableAttr": "41939cc9d27ac64ff213d3f28694069c8eb18318223707d2277c492bccf66936",
    "attsCcbByConnId": "65df52cbb1ac6140011a1e774243936355c2fe322b60e14c91d07ad1165524f1",
    "attsCcbByHandle": "dad169376be4b5eaf9b3b371e7d349ae479f52db7b8d4eec939d13a3456ea3b7",
    "AttsInit": "0af8f1800d9b56f9aecad56677af573d4d67e863d29221b7a732ed9320638553",
    "AttsHashDatabaseString": "7a9285e56d587bfe756821109604bdfbca9e1f531013109e11e5be5eb11a88ef",
    "AttsCalculateDbHash": "eb91d295630d298d5cb31ec8a11b293ec337f78bf8ebf769027e0dc9568220ba",
    "AttsAddGroup": "7848034d5cf02e0f9060ff0c026c78ab73c9f0f41039893bad49d30e1b0f4142",
    "AttsRemoveGroup": "21970ef46178a982e087961efef57f278ee3b67ab78893a8681f19666b74e136",
}

ATTS_FCN_IF = (0x007852F0, 0x00785300)
ATTS_FCN_IF_SHA = "ac310299eb7761edbb967813e18c633dc21604da0b705b47ff0551656e928e6a"
ATTS_FCN_IF_WORDS = [0x0053498D, 0x00534C8B, 0x00534C43, 0x00534ABB]
STORED_ENTRIES = [(0x007852F0, 0x0053498D), (0x007852F4, 0x00534C8B), (0x007852F8, 0x00534C43), (0x007852FC, 0x00534ABB)]
RAW_INTERIOR_WINDOWS = 40
RAW_INTERIOR_WINDOWS_SHA = "19d26199279274308807e891b3c510dee63b2b0e2a1c2a210b0fcd98493c8dc1"

ATTS_MIN_PDU_LEN = (0x0077E2D0, 0x0077E2E2)
ATTS_MIN_PDU_LEN_BYTES = bytes.fromhex("00030507050305050503030502000001000f")
ATTS_MIN_PDU_LEN_SHA = "927697413fa714628e6101c45f23d8a766fecef0384f552deb28b667bab03810"
ATTS_PROC_FCN_TBL = 0x2000045C
ATTS_PROC_FCN_TBL_BYTES = bytes.fromhex(
    "00000000fdc6560031c9560005dc56009ddd5600a9ca56009fda5600dfe05600"
    "6de256003b5e5a003b5e5a00c35f5a0071615a000000000000000000d93d5300"
    "cbcb560000000000"
)
ATTS_PROC_FCN_TBL_SHA = "e468091048ea8d3f4b301a8eaf3edce9085c7a136fb33d1407cbe6696209828e"
ATTS_PROC_FCN_NAMES = [
    None, "attsProcMtuReq", "attsProcFindInfoReq", "attsProcFindTypeReq",
    "attsProcReadTypeReq", "attsProcReadReq", "attsProcReadBlobReq",
    "attsProcReadMultReq", "attsProcReadGroupTypeReq", "attsProcWrite",
    "attsProcWrite", "attsProcPrepWriteReq", "attsProcExecWriteReq",
    None, None, "attsProcValueCnf", "attsProcReadMultiVarReq", None,
]
INITIALIZER_STREAM_VALUE_CELL = 0x00791AD0
INITIALIZER_STREAM_VALUE_SHA = "e5f37d38718806b2e6fd9c36ec23f097a99e98d4df5217e8902ace213cc453ee"

ATTS_CB = 0x2006E5F0
ATT_CB = 0x200610AC
P_ATT_CFG = 0x200004B4
SOURCE_PATH = b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_main.c"
SOURCE_PATH_ADDRESS = 0x006DC9F4
SOURCE_PATH_CELL = 0x00535458

# The compiler folds the three R4 ATT_CHECK_DATA_LENGTH calls into these two
# stock guard sites: one len>0 gate and one shared len>=3 gate before handle use.
R44_GUARDS = [
    (0x005349A4, bytes.fromhex("200080b2002800f084802f7a")),
    (0x00534A2A, bytes.fromhex("210089b2032941db697aaa7a")),
]


class AuditError(RuntimeError):
    """Raised when authenticated ATT server-owner evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3) if blob[offset:offset + 4] == packed]


def load_tool(name: str, filename: str):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_inventory() -> tuple[list[str], list[str]]:
    linked, source_only = [], []
    with MAP.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["stock_status"] == "linked":
                linked.append(row["function"])
            elif row["stock_status"] == "source_only":
                source_only.append(row["function"])
            else:
                raise AuditError("unexpected atts_main source-map status")
    return linked, source_only


def direct_calls(blob: bytes, decoder, targets: set[int]) -> dict[int, list[int]]:
    result = {target: [] for target in targets}
    for address in range(BASE, BASE + len(blob) - 3, 2):
        target = decoder._thumb_bl_target(blob, address)
        if target in result:
            result[target].append(address)
    return result


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != IMAGE_BYTES or sha(blob) != IMAGE_SHA:
        raise AuditError("official image changed")
    for path, digest in PINS.items():
        if not path.is_file() or sha(path.read_bytes()) != digest:
            raise AuditError(f"pinned input changed: {path}")

    linked, source_only = source_inventory()
    if linked != list(FUNCTIONS) or source_only != SOURCE_ONLY:
        raise AuditError("atts_main source inventory changed")
    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_main body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA:
        raise AuditError("atts_main body concatenation changed")
    if sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_main physical interval changed")
    noncode = []
    for start, end, expected in GAPS:
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError("atts_main owned gap changed")
        noncode.append(data)
    if sha(b"".join(noncode)) != NONCODE_CONCAT_SHA:
        raise AuditError("atts_main non-code concatenation changed")
    if list(struct.unpack("<18I", noncode[-1])) != POOL_WORDS:
        raise AuditError("atts_main literal pool changed")

    interface = image_slice(blob, *ATTS_FCN_IF)
    if sha(interface) != ATTS_FCN_IF_SHA or list(struct.unpack("<4I", interface)) != ATTS_FCN_IF_WORDS:
        raise AuditError("attsFcnIf changed")
    min_lengths = image_slice(blob, *ATTS_MIN_PDU_LEN)
    if min_lengths != ATTS_MIN_PDU_LEN_BYTES or sha(min_lengths) != ATTS_MIN_PDU_LEN_SHA:
        raise AuditError("attsMinPduLen changed")

    flashdb = load_tool("atts_main_flashdb", "analyze_g2_flashdb.py")
    initialized = flashdb._decode_initialized_sram(blob)
    proc_table = flashdb._sram_slice(initialized, ATTS_PROC_FCN_TBL, len(ATTS_PROC_FCN_TBL_BYTES))
    if proc_table != ATTS_PROC_FCN_TBL_BYTES or sha(proc_table) != ATTS_PROC_FCN_TBL_SHA:
        raise AuditError("initialized attsProcFcnTbl changed")
    stream_value = image_slice(blob, INITIALIZER_STREAM_VALUE_CELL, INITIALIZER_STREAM_VALUE_CELL + 4)
    if sha(stream_value) != INITIALIZER_STREAM_VALUE_SHA or struct.unpack("<I", stream_value)[0] != 0x00533DD9:
        raise AuditError("attsProcValueCnf initializer-stream word changed")

    for address, expected in R44_GUARDS:
        if image_slice(blob, address, address + len(expected)) != expected:
            raise AuditError("R4 ATT data-length guard changed")
    if occurrences(blob, ATTS_PROC_FCN_TBL) != [0x00535440]:
        raise AuditError("attsProcFcnTbl literal closure changed")
    if occurrences(blob, ATTS_FCN_IF[0]) != [0x00535484]:
        raise AuditError("attsFcnIf literal closure changed")
    if occurrences(blob, SOURCE_PATH_ADDRESS) != [SOURCE_PATH_CELL]:
        raise AuditError("atts_main path-cell closure changed")
    if image_slice(blob, SOURCE_PATH_ADDRESS, SOURCE_PATH_ADDRESS + len(SOURCE_PATH) + 1) != SOURCE_PATH + b"\0":
        raise AuditError("retained atts_main source path changed")

    decoder = load_tool("atts_main_thumb", "recover_apollo_embedded_source_paths.py")
    targets = {start for start, _, _ in FUNCTIONS.values()}
    calls = direct_calls(blob, decoder, targets)
    for name, (start, _, _) in FUNCTIONS.items():
        sites = calls[start]
        if sites != CALLERS[name]:
            raise AuditError(f"direct caller closure changed: {name}")
        if sha(b"".join(struct.pack("<I", site) for site in sites)) != CALLER_DIGESTS[name]:
            raise AuditError(f"direct caller digest changed: {name}")

    entries = {start for start, _, _ in FUNCTIONS.values()}
    interiors = {address for start, end, _ in FUNCTIONS.values() for address in range(start + 1, end)}
    stored_entries, raw_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            raw_interiors.append((BASE + offset, value))
    if stored_entries != STORED_ENTRIES:
        raise AuditError("atts_main stored-entry closure changed")
    raw_digest = sha(b"".join(struct.pack("<II", address, value) for address, value in raw_interiors))
    if len(raw_interiors) != RAW_INTERIOR_WINDOWS or raw_digest != RAW_INTERIOR_WINDOWS_SHA:
        raise AuditError("atts_main raw interior-window census changed")
    for address in range(BASE, BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) in interiors:
            raise AuditError("unexpected direct BL into atts_main interior")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATTS main production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATTS main production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, (start, end, expected))) in enumerate(
        zip(CANDIDATE_FUNCTIONS, FUNCTIONS.items()), 1
    ):
        site = sites.get(f"replace_cordio_atts_main_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATTS main production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = leaves[0]["expected"]["offset"] - CANDIDATE_PREVIOUS_OVERLAY_SIZE
    alignment += sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (2622, 30, 44):
        raise AuditError("ATTS main production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    if (
        build["overlay"]["size"] != 404796
        or build["overlay"]["sha256"]
        != "a55b20ca90792f195ef8de456a6cb7d90c831575b9aff147676a716844bfc73d"
        or build["component"]["size"] != 3928192
        or build["component"]["sha256"]
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or override["provider"].get("size") != 3928192
        or override["provider"].get("sha256")
        != "5979e515c76aa1601701a01e9c0aa1050a7cc0708d0b7470b94c3d6aac0c9a73"
        or len([
            row for row in override["regions"]
            if row["name"].startswith("cordio_atts_main_")
        ]) != 45
    ):
        raise AuditError("ATTS main component/manifest ownership changed")
    if (
        PACKAGE.stat().st_size != 4706686
        or sha(PACKAGE.read_bytes())
        != "30afcda8c32cc34fb1a1c12df13aff2f97223e12d74425690e67a6e4d81bfddf"
    ):
        raise AuditError("ATTS main package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != 4071097
        or sha(FLASH_PLAN.read_bytes())
        != "cf46c2b6e6ed099ce9ef240520be8d81847ae219d52479286a373c326d22da6d"
        or (
            len(flash["flash_regions"]), len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]), len(flash["protected_regions"]),
        ) != (5863, 2, 5, 6)
    ):
        raise AuditError("ATTS main flash plan changed")

    proc_words = list(struct.unpack("<18I", proc_table))
    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_eatt_server_owner_dispatcher",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": sum(end - start for start, end, _ in GAPS),
            "source_inventory_functions": len(linked) + len(source_only),
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "registered_function_pointers": len(STORED_ENTRIES),
            "accepted_strict_interior_pointers": 0,
            "raw_accidental_interior_windows": len(raw_interiors),
        },
        "architecture": {
            "eatt_aware": True, "dm_conn_max": 3, "att_bearer_max": 3,
            "server_ccb_count": 9, "server_ccb_stride": 64,
            "connection_ccb_stride": 0xC0,
            "r44_data_length_guards": True,
            "public_r20_missing_stock_guards": True,
        },
        "abi": {
            "atts_cb": ATTS_CB, "att_cb": ATT_CB, "p_att_cfg": P_ATT_CFG,
            "group_queue_offset": 0x258, "p_ind_offset": 0x260,
            "sign_msg_callback_offset": 0x264,
            "main_ccb_offset": 0x10, "conn_id_offset": 0x24, "slot_offset": 0x25,
            "att_cb_server_interface_offset": 0x40,
        },
        "dispatch": {
            "server_interface": ATTS_FCN_IF[0],
            "server_interface_entries": ATTS_FCN_IF_WORDS,
            "minimum_pdu_lengths": list(min_lengths),
            "processor_table_live_sram": ATTS_PROC_FCN_TBL,
            "processor_table_entries": proc_words,
            "processor_table_names": ATTS_PROC_FCN_NAMES,
            "value_confirmation_method": 15,
            "signed_write_method": 17,
            "signed_write_processor_linked": False,
            "initializer_stream_value_cell": INITIALIZER_STREAM_VALUE_CELL,
            "initializer_stream_is_not_runtime_table": True,
        },
        "lineage": {
            "selected_source": "AmbiqSuite R4.4.1 later official import",
            "selected_commit": "4264b9309e03064ffad13a0468d5d0c1110c5288",
            "selected_blob": "bb99817115ce4da49ce26b5c52c4dd3418baaf88",
            "selected_sha256": "f28ba51cfb47d360508d5d8eac5187da34f84ac29180e712bcd1591f861eeff1",
            "public_r20_base_blob": "998e6300d08ddcb18b2c91c17ca4b90da2b6e04b",
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
        },
        "production": {
            "status": "routed", "linked_functions": 17,
            "source_functions": 21,
            "stock_bytes_replaced": 2710,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 17,
            "source_only_public_helpers": SOURCE_ONLY,
            "r44_data_length_guards_preserved": True,
            "hardware_validation": (
                "blocked by unavailable authorized responsive G2/ATT peer evidence"
            ),
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
        print("Cordio atts_main closed: 17 linked functions / 18-method initialized dispatch table")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
