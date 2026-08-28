#!/usr/bin/env python3
"""Fail-closed audit for the linked Cordio ATT server indication unit."""

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
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_BYTES = 3_523_396
IMAGE_SHA = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
MAP = ROOT / "tools/manifests/packetcraft-cordio-atts-ind-function-map.tsv"
PROVENANCE = ROOT / "tools/manifests/packetcraft-cordio-atts-ind-provenance.tsv"
PINS = {
    ROOT / "components/shared/cordio/runtime_cordio_atts_ind.c": "932b9148e13f6edcc0935bd46db5e2352b5041cfa4fb3b6f95426006ef01fb21",
    ROOT / "components/shared/cordio/runtime_cordio_atts_ind.h": "60c93293c3b777c90318b2c31915c2654ffdbaf9d001a9c6f37802ced5d8438a",
    MAP: "fdda9360f5a4f4194634c087f55ba61fcff7ff2badbe3b952101b698d6e16282",
    PROVENANCE: "ec381fa2a080c9be95a5ff6ed95d9a8d3a30ccd7a52e2b45c5637cb4d865f51e",
}

OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
CANDIDATE_SOURCE_PATH = "components/shared/cordio/runtime_cordio_atts_ind.c"
CANDIDATE_FUNCTIONS = [
    "open_cfw_cordio_atts_ind_pending",
    "open_cfw_cordio_atts_ind_set_pending_notification",
    "open_cfw_cordio_atts_ind_execute_callback",
    "open_cfw_cordio_atts_ind_notification_callback",
    "open_cfw_cordio_atts_ind_setup_message",
    "open_cfw_cordio_atts_ind_connection_callback",
    "open_cfw_cordio_atts_ind_message_callback",
    "open_cfw_cordio_atts_ind_control_callback",
    "open_cfw_cordio_atts_handle_value_indication_notification",
    "open_cfw_cordio_atts_process_value_confirmation",
    "open_cfw_cordio_atts_ind_initialize",
    "open_cfw_cordio_atts_handle_value_indication",
    "open_cfw_cordio_atts_handle_value_notification",
]
CANDIDATE_LEAF_METRICS = [
    (340072, 182, 0), (340256, 128, 0), (340384, 26, 1),
    (340412, 190, 11), (340604, 154, 6), (340760, 164, 6),
    (340924, 116, 7), (341040, 32, 2), (341072, 318, 11),
    (341392, 110, 5), (341504, 122, 0), (341628, 30, 1),
    (341660, 30, 1),
]

FUNCTIONS = {
    "attsPendIndNtfHandle": (0x005338AC, 0x0053390E, "8c2b18ca9e905e66f5af163b215e1d376f851085e01046489194f03d86b305a5"),
    "attsSetPendNtfHandle": (0x0053390E, 0x00533934, "d6d3e17516514b6369adb2bf87d2e3241e4d38583a4215f2fef95c38f630e141"),
    "attsExecCallback": (0x00533934, 0x0053394C, "deb8cf478b9427a577bae4d10c773d3bb21b04532bf5d2496e3f7cb84ec430ec"),
    "attsIndNtfCallback": (0x0053394C, 0x005339AC, "277bd0011ebd688dfbfb103b7dacd17fc947417b241391c1f10a572650dad8b3"),
    "attsSetupMsg": (0x005339AC, 0x00533A40, "f82214ac2888411b5f23b01673f9a06fc7c1e85d4d6b7b28ff262c79762895b0"),
    "attsIndConnCback": (0x00533A40, 0x00533BC6, "137a7fd756c4b2bb9635bff4992bce71447095953168123d22603b583f9fbdba"),
    "attsIndMsgCback": (0x00533BCC, 0x00533C4C, "fedf7f9dbb82d4a55423d4c2ea0c8222e7ca2df38aa2969fdc9d3942130f5899"),
    "attsIndCtrlCback": (0x00533C4C, 0x00533C6C, "da4227cd1029c20e31e1f72649795dee1ce7f304d4235e6aaefa779298b5ecb4"),
    "attsHandleValueIndNtf": (0x00533C6C, 0x00533DD2, "559111e534923a1074c0158b103e1fffea9a26a34377f04ae149fbe382f60cf1"),
    "attsProcValueCnf": (0x00533DD8, 0x00533E40, "47cc9e8b338acea9bf2a1fcb044f97affcaa5b5954f8985417f3caac40502b65"),
    "AttsIndInit": (0x00533E40, 0x00533E90, "a526a5a852710ed4a74dae43ef1e902775bf38f7eab1c0f7a8b1a440881dba9e"),
    "AttsHandleValueInd": (0x00533EBC, 0x00533ED8, "9c730837b4a55e9d76eafe6870229e847e5ac20d384181a41564c5dfcb7d09bc"),
    "AttsHandleValueNtf": (0x00533ED8, 0x00533EF4, "e4d397bf7f80221f55892fd15b2c68d1dc985c453a8002bca27407edbbfe7ca7"),
}
SOURCE_ONLY = ["AttsHandleValueIndZeroCpy", "AttsHandleValueNtfZeroCpy"]
BODY_CONCAT_SHA = "d52b3d12ae2978a4589b75f52e5d937aed7929c61ad42a2c376f8efa27a7bb13"
PHYSICAL = (0x005338AC, 0x00533EF4)
PHYSICAL_SHA = "2d446a918ca02515e09115b012395e9a74edee087101a4c7d95cd8846e3ce669"
GAPS = [
    (0x00533BC6, 0x00533BCC, "2c63161bef9b35aa71cbc37025db3d9c2a2f8a62b9bfc564af6b13e959cfddd6"),
    (0x00533DD2, 0x00533DD8, "0589b6037e4d1d238bf39b685cca6350a975d2f763efe27e97c6445588923adb"),
    (0x00533E90, 0x00533EBC, "a5051b9866584ceeea13f2009ac508a41312c1fc70e5abd261b16367a150371f"),
]
NONCODE_CONCAT_SHA = "095be8adefe58ba46c9cf9784174cba7052e126c7a041be53011f4006d4bb9a7"
POOL_WORDS = [
    0x00494348, 0x200004B4, 0x2006E5F0, 0x0078CCAC, 0x0073C668,
    0x0077E2BC, 0x006DC994, 0x0078CCB4, 0x200610AC, 0x0078F546,
    0x007852C0,
]

CALLERS = {
    "attsPendIndNtfHandle": [0x00533BF2],
    "attsSetPendNtfHandle": [0x00533A38],
    "attsExecCallback": [0x00533964, 0x00533990, 0x00533A2C, 0x00533C04, 0x00533DA0, 0x00533DB0, 0x00533E36],
    "attsIndNtfCallback": [0x00533A9E, 0x00533C66],
    "attsSetupMsg": [0x00533C1A],
    "attsIndConnCback": [],
    "attsIndMsgCback": [],
    "attsIndCtrlCback": [],
    "attsHandleValueIndNtf": [0x00533ED2, 0x00533EEE],
    "attsProcValueCnf": [],
    "AttsIndInit": [0x004B8066],
    "AttsHandleValueInd": [0x004B5A94, 0x004B5AB4],
    "AttsHandleValueNtf": [0x004BDC60, 0x004BDF18, 0x004BE290, 0x004BE462, 0x004BE7AE],
}
CALLER_DIGESTS = {
    "attsPendIndNtfHandle": "8c2e504a7816c0a08b97c5f0a1e5cea554d4dbf49b5715ff31899ec9db32ea64",
    "attsSetPendNtfHandle": "ce598aac99d0efc1c90220760baa05ff51e66465b890e6c92c1c218e37a89036",
    "attsExecCallback": "93bc46f03a41c5c5fe3485c36b73d8706ca20caeabdd74eac09d622e62f7d231",
    "attsIndNtfCallback": "bdf764b66ac1153e8a3ca79d81a1529b0168caa34755477aeed0a3f83ffbcf3e",
    "attsSetupMsg": "f1809c814e6a3734a064240ef569eadb892fbf116cf8b3d169fb75417170c745",
    "attsIndConnCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsIndMsgCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsIndCtrlCback": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "attsHandleValueIndNtf": "e15a11848141cee0403f638aaecdabbd67221de1b6acaad096be770724f855ee",
    "attsProcValueCnf": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "AttsIndInit": "15cac75e7775bf51314d2d94883ae885942215c4d06205f04cd635b1be9c0593",
    "AttsHandleValueInd": "dfcf859f76183578eb722bd0c2f6feb1d5de50823fa46d76ee0b720742e70403",
    "AttsHandleValueNtf": "c4b9e15400f5c1a37c2ddeb46d91e5cb0edd4830d9361fc60c335d5dd82ef531",
}

ATTS_IND_FCN_IF = (0x007852C0, 0x007852D0)
ATTS_IND_FCN_IF_SHA = "ed91ad349eae91a91c25376f92691628507d111b23ecbf1dc620ad520137279f"
ATTS_IND_FCN_IF_WORDS = [0x004B4EED, 0x00533C4D, 0x00533BCD, 0x00533A41]
ATTS_PROC_VALUE_CNF_INITIALIZER_WORD = 0x00791AD0
ATTS_PROC_VALUE_CNF_INITIALIZER_WORD_SHA = "e5f37d38718806b2e6fd9c36ec23f097a99e98d4df5217e8902ace213cc453ee"
ATTS_PROC_FCN_TBL = 0x2000045C
ATTS_PROC_VALUE_CNF_LIVE_CELL = ATTS_PROC_FCN_TBL + (15 * 4)
STORED_ENTRIES = [
    (0x007852C4, 0x00533C4D),
    (0x007852C8, 0x00533BCD),
    (0x007852CC, 0x00533A41),
    (0x00791AD0, 0x00533DD9),
]

ATTS_CB = 0x2006E5F0
ATTS_CB_LITERAL_CELLS = [0x0052C6A8, 0x00533E98, 0x00535448, 0x0056CD98, 0x0056E4E4, 0x005A6258]
ATTS_CB_P_IND = ATTS_CB + 0x260
ATT_CB = 0x200610AC
P_ATT_CFG = 0x200004B4
SOURCE_PATH = b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\att\\atts_ind.c"
SOURCE_PATH_ADDRESS = 0x006DC994
SOURCE_PATH_CELL = 0x00533EA8


class AuditError(RuntimeError):
    """Raised when authenticated indication evidence changes."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE:end - BASE]


def occurrences(blob: bytes, value: int) -> list[int]:
    packed = struct.pack("<I", value)
    return [BASE + offset for offset in range(len(blob) - 3) if blob[offset:offset + 4] == packed]


def load_decoder():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    path = ROOT / "tools/recover_apollo_embedded_source_paths.py"
    spec = importlib.util.spec_from_file_location("atts_ind_thumb", path)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load Thumb decoder")
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
                raise AuditError("unexpected atts_ind source-map status")
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
        raise AuditError("atts_ind source inventory changed")

    bodies = []
    for name, (start, end, expected) in FUNCTIONS.items():
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError(f"stock atts_ind body changed: {name}")
        bodies.append(data)
    if sha(b"".join(bodies)) != BODY_CONCAT_SHA:
        raise AuditError("atts_ind body concatenation changed")
    if sha(image_slice(blob, *PHYSICAL)) != PHYSICAL_SHA:
        raise AuditError("atts_ind physical interval changed")
    noncode = []
    for start, end, expected in GAPS:
        data = image_slice(blob, start, end)
        if sha(data) != expected:
            raise AuditError("atts_ind owned gap changed")
        noncode.append(data)
    if sha(b"".join(noncode)) != NONCODE_CONCAT_SHA:
        raise AuditError("atts_ind non-code concatenation changed")
    if list(struct.unpack("<11I", noncode[-1])) != POOL_WORDS:
        raise AuditError("atts_ind literal pool changed")

    interface = image_slice(blob, *ATTS_IND_FCN_IF)
    if sha(interface) != ATTS_IND_FCN_IF_SHA or list(struct.unpack("<4I", interface)) != ATTS_IND_FCN_IF_WORDS:
        raise AuditError("attsIndFcnIf changed")
    proc_cell = image_slice(blob, ATTS_PROC_VALUE_CNF_INITIALIZER_WORD, ATTS_PROC_VALUE_CNF_INITIALIZER_WORD + 4)
    if sha(proc_cell) != ATTS_PROC_VALUE_CNF_INITIALIZER_WORD_SHA or struct.unpack("<I", proc_cell)[0] != 0x00533DD9:
        raise AuditError("attsProcValueCnf initializer-stream word changed")

    if occurrences(blob, ATTS_CB) != ATTS_CB_LITERAL_CELLS:
        raise AuditError("attsCb literal closure changed")
    if occurrences(blob, ATTS_CB_P_IND):
        raise AuditError("unexpected direct pInd-slot literal")
    if occurrences(blob, ATTS_IND_FCN_IF[0]) != [0x00533EB8]:
        raise AuditError("attsIndFcnIf literal closure changed")
    if occurrences(blob, SOURCE_PATH_ADDRESS) != [SOURCE_PATH_CELL]:
        raise AuditError("atts_ind path-cell closure changed")
    if image_slice(blob, SOURCE_PATH_ADDRESS, SOURCE_PATH_ADDRESS + len(SOURCE_PATH) + 1) != SOURCE_PATH + b"\0":
        raise AuditError("retained atts_ind source path changed")

    decoder = load_decoder()
    targets = {start for start, _, _ in FUNCTIONS.values()}
    calls = direct_calls(blob, decoder, targets)
    for name, (start, _, _) in FUNCTIONS.items():
        sites = calls[start]
        if sites != CALLERS[name]:
            raise AuditError(f"direct caller closure changed: {name}")
        raw = b"".join(struct.pack("<I", site) for site in sites)
        if sha(raw) != CALLER_DIGESTS[name]:
            raise AuditError(f"direct caller digest changed: {name}")

    entries = {start for start, _, _ in FUNCTIONS.values()}
    interiors = {
        address for start, end, _ in FUNCTIONS.values()
        for address in range(start + 1, end)
    }
    stored_entries, stored_interiors = [], []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in entries:
            stored_entries.append((BASE + offset, value))
        elif target in interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != STORED_ENTRIES or stored_interiors:
        raise AuditError("atts_ind stored entry/interior closure changed")
    for address in range(BASE, BASE + len(blob) - 3, 2):
        if decoder._thumb_bl_target(blob, address) in interiors:
            raise AuditError("unexpected direct branch into atts_ind interior")

    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves_by_function = {
        row["function"]: row for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == CANDIDATE_SOURCE_PATH
    }
    if set(leaves_by_function) != set(CANDIDATE_FUNCTIONS):
        raise AuditError("ATTS indication production leaf inventory changed")
    source_hash = PINS[ROOT / CANDIDATE_SOURCE_PATH]
    leaves = []
    for function, metrics in zip(CANDIDATE_FUNCTIONS, CANDIDATE_LEAF_METRICS):
        leaf = leaves_by_function[function]
        actual = (
            leaf["expected"]["offset"], leaf["expected"]["size"],
            len(leaf["relocations"]),
        )
        if actual != metrics or leaf["source"].get("sha256") != source_hash:
            raise AuditError(f"ATTS indication production leaf changed: {function}")
        leaves.append(leaf)
    sites = {row["name"]: row for row in overlay["patch_sites"]}
    for index, (function, (name, (start, end, expected))) in enumerate(
        zip(CANDIDATE_FUNCTIONS, FUNCTIONS.items()), 1
    ):
        site = sites.get(f"replace_cordio_atts_ind_{index:02d}")
        if (
            site is None or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != expected
            or function not in overlay["functions"]
        ):
            raise AuditError(f"ATTS indication production route changed: {name}")
    compiled = sum(row["expected"]["size"] for row in leaves)
    alignment = sum(
        right["expected"]["offset"]
        - left["expected"]["offset"] - left["expected"]["size"]
        for left, right in zip(leaves, leaves[1:])
    )
    relocations = sum(len(row["relocations"]) for row in leaves)
    if (compiled, alignment, relocations) != (1602, 16, 51):
        raise AuditError("ATTS indication production metrics changed")

    build = json.loads(BUILD_REPORT.read_text())
    manifest = json.loads(SOURCE_MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    validate_apollo_main_artifacts(ROOT, AuditError, "ATT server indication")
    if len([
        row for row in override["regions"]
        if row["name"].startswith("cordio_atts_ind_")
    ]) != 34:
        raise AuditError("ATTS indication component/manifest ownership changed")

    return {
        "schema_version": 1,
        "module": {
            "classification": "linked_eatt_indication_core",
            "start": PHYSICAL[0], "end_exclusive": PHYSICAL[1],
            "physical_bytes": PHYSICAL[1] - PHYSICAL[0],
            "linked_function_count": len(FUNCTIONS),
            "linked_function_bytes": sum(end - start for start, end, _ in FUNCTIONS.values()),
            "owned_noncode_bytes": sum(end - start for start, end, _ in GAPS),
            "source_inventory_functions": len(linked) + len(source_only),
            "source_only_functions": source_only,
            "direct_bl_ingress_sites": sum(len(sites) for sites in CALLERS.values()),
            "registered_function_pointers": 3,
            "initializer_stream_entry_windows": 1,
            "strict_interior_pointers": 0,
        },
        "architecture": {
            "eatt_aware": True, "dm_conn_max": 3, "att_bearer_max": 3,
            "server_ccb_count": 9, "server_ccb_stride": 64,
            "connection_ccb_stride": 0xC0, "simultaneous_notifications": 10,
            "zero_copy_indication_linked": False, "zero_copy_notification_linked": False,
            "ordinary_indication_linked": True, "ordinary_notification_linked": True,
        },
        "abi": {
            "atts_cb": ATTS_CB, "p_ind_offset": 0x260,
            "att_cb": ATT_CB, "p_att_cfg": P_ATT_CFG,
            "timer_offset": 0, "main_ccb_offset": 0x10,
            "conn_id_offset": 0x24, "slot_offset": 0x25,
            "outstanding_indication_offset": 0x26,
            "pending_indication_offset": 0x28,
            "pending_notification_array_offset": 0x2A,
        },
        "dispatch": {
            "interface": ATTS_IND_FCN_IF[0],
            "interface_entries": ATTS_IND_FCN_IF_WORDS,
            "processor_table_live_sram": ATTS_PROC_FCN_TBL,
            "value_confirmation_live_cell": ATTS_PROC_VALUE_CNF_LIVE_CELL,
            "value_confirmation_initializer_stream_word": ATTS_PROC_VALUE_CNF_INITIALIZER_WORD,
            "initializer_stream_is_not_runtime_table": True,
            "value_confirmation_method": 15,
        },
        "lineage": {
            "selected_source": "Packetcraft r20.05c",
            "selected_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
            "selected_blob": "803f1fefb245314a8332d6fbc210306afd2ff3ec",
            "selected_sha256": "d79922dbfcc00e4b8b68c13c7bfc604f88b173fc431daba89c70c24331495567",
            "r20_through_r20c_invariant": True,
            "later_r44_byte_identical": True,
            "historical_generating_commit_resolved": False,
            "license": "Apache-2.0",
        },
        "production": {
            "status": "routed", "functions": 13,
            "stock_bytes_replaced": 1552,
            "source_owned_bytes_added": compiled,
            "compiled_text_bytes": compiled,
            "alignment_bytes": alignment,
            "strict_relocations": relocations,
            "guarded_redirects": 13,
            "source_only_zero_copy_wrappers": 2,
            "g2_behavior_deltas": [
                "invalid zero connection guard on close",
                "disconnect status maps through authenticated 0xA0 base",
                "timeout message decodes and looks up without a retained transition",
            ],
            "hardware_validation": (
                "deferred by project direction; future qualification requires authorized responsive G2/ATT peer evidence"
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
        print("Cordio atts_ind closed: 13 linked EATT-aware functions / 2 zero-copy wrappers stripped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
