#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 ICM45608 IMU driver object."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-imu-icm45608-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-imu-icm45608-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-imu-icm45608-provenance.tsv"
SOURCE_PATH = "components/apollo_main/core_overlay/imu_icm45608.c"
TDK_PORT_PATH = "components/apollo_main/core_overlay/imu_icm45608_tdk_port.c"
TDK_SNAPSHOT = ROOT / "third_party/invensense-icm45608"
TDK_PROVENANCE = TDK_SNAPSHOT / "PROVENANCE.json"
TDK_VERIFY = TDK_SNAPSHOT / "verify_snapshot.py"
TDK_LICENSE = TDK_SNAPSHOT / "LICENSE"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
COMPONENT_BUILDER = (
    ROOT / "components/apollo_main/core_overlay/build_component.py"
)
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "111409c72081337d19c6cc62e501bfd39011c4bff92de02928abdb18b0941f5b",
    CLOSURE: "ba9bdb509da95a8a30c286632376123e97401541fbd9ddf347fc2de593bd07f8",
    PROVENANCE: "68b400c84fafeece9d61b0bda22a741456bde6d4263e00c52d953f5a9785561e",
    TDK_PROVENANCE: "be486672038868ef86a4365b388f86746883d4ca771c504e8b63a9d4b80c733e",
    TDK_VERIFY: "d22531aae24e5eb4ceb9c3ae81aa6b61fe5998cef1a39bdb2f84fd6546f84073",
    TDK_LICENSE: "68bed9c72222b77b8744add292f524000661c6537d960adeaf740722b0b2637f",
}
TDK_TAG = "1.1.2"
TDK_COMMIT = "b79ae575f7f310e5ae2e1164096d1a858bb74662"
TDK_AGGREGATE = "cc6088eed9f14a02af419a29856064ab62e4b79e2860a135e1d84ba22e1c9570"
PHYSICAL = (0x004A35B0, 0x004A6644)
PHYSICAL_SHA256 = "d4946b892b0fcb6e45a3cb2f4dadd452e737712815577d6780c26ff7e1185e22"
CALLER_ROWS_SHA256 = "e8cad0ba615a9a793e8f31f21c81db34ec749c9682be8d2236940030fbb3f9b0"
BODY_SHA256 = "9a2ab101ce16b0bbb2c08a8338249ca8eb97ecece2fb331fe0595a3cb628e21e"
GAP_SHA256 = "f715282f60d047a6a9aa7942b9396eabe3ad99cebafbd7a705178ba10b0da912"
ENTRY_SHA256 = "6fc6c004909b2109de41e379b3f119f55075c78506a8943a0112505c34dfba4c"
EXTERNAL_ENTRY_SHA256 = "3f7058f2ad43c18f16b3e5fe63ddb88405808a5098b7ac31d6bd2e3042df8903"
BODY_CALL_SHA256 = "b0847bd244f673ce4cc130c18148b81d05f28da0f1eda494d917cc6f65531994"
RAW_WINDOW_SHA256 = "00d68e6d145635c2a14f325a09a5724af2229964bca734c935871fbad544cef1"
STORED_ENTRY_SHA256 = "6b6d7bc15efec56ac7dd557bb6f2d5af022098b0f205ab2e35edac3146631a47"
BW_SHA256 = "eb0d42d179a43b6eba6a611c8c79b4bf84f5a103c755c19e9d30bfeb145ced5b"
RETAINED_PATH_ADDRESS = 0x006FADE4
RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\driver\sensor\imu\imu_icm45608.c"
)
PATH_CELLS = (0x004A4588, 0x004A5374, 0x004A6264, 0x004A65E4)
EXACT_SYMBOLS = (
    (0x0076BDF8, "DRV_IMUSetSensorParameters"),
    (0x0077F7AC, "IMU_AIDStatePrint"),
    (0x0077F7C0, "IMU_AIDStateUpdate"),
    (0x007860E0, "DRV_IMUReadData"),
    (0x00777B34, "DRV_IMUCheckHeadUpEvent"),
    (0x0076BE4C, "DRV_IMUCheckCompassEvent"),
    (0x0077F7D4, "DRV_IMUAccelConfig"),
    (0x0076BE68, "DRV_IMUDataParserCallback"),
    (0x00777B4C, "DRV_IMUWriteCSVHeader"),
    (0x00777B64, "DRV_IMUWriteCSVDataLine"),
    (0x007603B0, "DRV_IMUStartRawDataCollection"),
    (0x007603D0, "DRV_IMUStopRawDataCollection"),
    (0x00777B94, "DRV_IMUSaveRawDataToCSV"),
    (0x0077F7E8, "DRV_IMUReadWhoAmI"),
    (0x0077F7FC, "DRV_MAGReadWhoAmI"),
)
GAPS = (
    (0x004A37E0, 0x004A3820, "ab56bb2d1a0a2e6b854f855340b9aee0c642a945b0001d55e005fa7db6dd05c8"),
    (0x004A457C, 0x004A4590, "565b74f76a382a5386e5544caf54874a77040c62bb2f7c3156048b08560bee3d"),
    (0x004A45FC, 0x004A460C, "f372da1ea4dda47e1691e21ecafb9417c08ef898fc28190d4bc024c875f2d34a"),
    (0x004A496A, 0x004A499C, "0bbfb9376fee573c1459f7b259ed591e393f5ab76e0660054bd18450e0027e7f"),
    (0x004A4ED0, 0x004A4ED4, "e2a3fb2cf7962608f49ddd4435a6ceea3cf362389c6d59faf3c84daf90ef0b48"),
    (0x004A50CE, 0x004A50FC, "0a6d7e88b4e3d4c3ced2098bc0149cb6acb9ca0d2db00b2c544afc84d9b23b4c"),
    (0x004A528E, 0x004A52A0, "700026f3e557fd36496e94427359e60e245affc9ea5d665ee7d6822ed0cd8642"),
    (0x004A5374, 0x004A538C, "2220a12b63566f4cc1b4d268f905d123d939af9e884983e7f0783eedd98e1fe0"),
    (0x004A5480, 0x004A54A0, "a3602c2d30cde490a679fd723930586707d3d079e436240c9a320419024012fe"),
    (0x004A5576, 0x004A5578, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x004A5698, 0x004A56D4, "3d671ded769d5a57a35e69d97fbc853a804a81c4b1ac12e7393f1046bf9d46af"),
    (0x004A5B66, 0x004A5B90, "b2397d5953d5cea485d02a469afd70a258b9b6772a0db701facaee2305f066ed"),
    (0x004A5CFE, 0x004A5D04, "fe449bc4eb4bbd56dd374d27da592996cff9bf2163edf0e3038c18bb38cd752f"),
    (0x004A5D26, 0x004A5D38, "d04c89d17bf4eb83f84bca8d39152855b9fc9e27837d19526a2483ddedf82e37"),
    (0x004A5E12, 0x004A5E1C, "f45b3b27352e92c8b9c901f542b9f81b306707c28dbc6b6d5f8c04c52dfcc943"),
    (0x004A5E44, 0x004A5E4C, "ce92919148a1ad812a6c8df873733cbbe052f63d008422b743dffcdd34d4dc68"),
    (0x004A5EC2, 0x004A5EF4, "489eeb5a21e1a08aae3e8a543e93746bfb580cc75ca0c4ff2727679040b6bc27"),
    (0x004A60D0, 0x004A60E8, "49db338e27ea5350b0644654d54223ed1deccd5a6372572557a0a97976e8f17d"),
    (0x004A625A, 0x004A6270, "8b69554104d4ac6497591a5028be10a7d385d24a3cf08a6d0d200715804f6cfb"),
    (0x004A6364, 0x004A6384, "0f5ee3f711a129cef1c29b25aff73f7fc1fa0c83416f1f01292207c8a8d61ed4"),
    (0x004A656E, 0x004A6644, "d3adab623b287e27c598c00db6efdfcff8a90ebad671dfa892ca0b06dd215aee"),
)
STORED_ENTRIES = (
    (0x004A3804, 0x004A35B1),
    (0x004A3808, 0x004A35EB),
    (0x004A3810, 0x004A56D5),
)
RETIRED_WRAPPER_FUNCTIONS = (
    "open_cfw_imu_bus_read", "open_cfw_imu_bus_write",
    "open_cfw_imu_filter_init", "open_cfw_imu_filter_update",
    "open_cfw_imu_device_context_init", "open_cfw_imu_apply_odr_config",
    "open_cfw_imu_set_sensor_parameters", "open_cfw_imu_sensor_power_cycle",
    "open_cfw_imu_sensor_reset_line", "open_cfw_imu_initialize",
    "open_cfw_imu_set_orientation_matrix", "open_cfw_imu_aid_state_print",
    "open_cfw_imu_get_aid_enabled", "open_cfw_imu_aid_state_update",
    "open_cfw_imu_read_data", "open_cfw_imu_set_motion_threshold",
    "open_cfw_imu_set_motion_period", "open_cfw_imu_emit_event",
    "open_cfw_imu_check_head_up_event", "open_cfw_imu_normalize_heading",
    "open_cfw_imu_check_compass_event", "open_cfw_imu_noop_sample_callback",
    "open_cfw_imu_accel_config", "open_cfw_imu_forward_periodic_sample",
    "open_cfw_imu_postprocess_samples", "open_cfw_imu_transform_vector",
    "open_cfw_imu_fixed_vector_to_float", "open_cfw_imu_quaternion_to_euler",
    "open_cfw_imu_data_parser_callback",
    "open_cfw_imu_get_latest_complete_sample", "open_cfw_imu_set_heading",
    "open_cfw_imu_set_magnetic_vector", "open_cfw_imu_get_heading_degrees",
    "open_cfw_imu_get_heading_float", "open_cfw_imu_get_magnetic_vector",
    "open_cfw_imu_get_orientation_vector", "open_cfw_imu_build_raw_csv_path",
    "open_cfw_imu_write_csv_header", "open_cfw_imu_write_csv_data_line",
    "open_cfw_imu_start_raw_data_collection",
    "open_cfw_imu_stop_raw_data_collection",
    "open_cfw_imu_save_raw_data_to_csv", "open_cfw_imu_read_who_am_i",
    "open_cfw_mag_read_who_am_i", "open_cfw_imu_get_state_zero",
    "open_cfw_imu_get_state_one", "open_cfw_imu_get_state_two",
    "open_cfw_imu_get_state_three", "open_cfw_imu_set_state_zero",
    "open_cfw_imu_set_state_one", "open_cfw_imu_set_state_two",
    "open_cfw_imu_get_compass_ready", "open_cfw_imu_set_state_three",
    "open_cfw_imu_delay_callback",
)

RESTRICTED_NOTICE_PATHS = (
    "third_party/invensense-icm45608/src/imu/inv_imu_edmp_defs.h",
    "third_party/invensense-icm45608/src/imu/inv_imu_edmp_patches_defs.h",
    "third_party/invensense-icm45608/src/imu/inv_imu_edmp_patch_key_offsets.h",
    "third_party/invensense-icm45608/src/imu/inv_imu_edmp_calmag_defs.h",
    "third_party/invensense-icm45608/src/imu/"
    "inv_imu_edmp_all_quat_patch_key_offsets.h",
)
DENSE_PAYLOAD_PATHS = (
    "third_party/invensense-icm45608/src/imu/edmp_prgm_ram_dispatch.h",
    "third_party/invensense-icm45608/src/imu/"
    "edmp_prgm_ram_dispatch_over_gaf.h",
    "third_party/invensense-icm45608/src/imu/edmp_prgm_ram_patch_calmag.h",
    "third_party/invensense-icm45608/src/imu/edmp_prgm_ram_selftest.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_aid_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_aid_over_gaf_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_all_quat_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_b2s_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_b2s_over_gaf_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_mrm_image.h",
)
RISKY_PATHS = frozenset(RESTRICTED_NOTICE_PATHS + DENSE_PAYLOAD_PATHS)
SELECTED_PAYLOAD_PATHS = (
    "third_party/invensense-icm45608/src/imu/edmp_ram_mrm_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_prgm_ram_dispatch.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_b2s_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_ram_aid_image.h",
    "third_party/invensense-icm45608/src/imu/edmp_prgm_ram_patch_calmag.h",
)
SELECTED_PAYLOAD_IDENTITIES = (
    (674, "6436679c2bb3d34da51a19ad9afb941fb4c5cc807149eb38c90f022492776799"),
    (25, "86e12e2483301114273ba809c1de6dbe11491c97e121f60ac6e8ef69472f98f8"),
    (1310, "f9a6d7db4e1f2511b228845d391cf0fcb4e5269cfcfea445a9b2ee80c9274230"),
    (375, "16e4e9a482563c57ff82bec369464e0094d4a92140840edcaee738e201615ba7"),
    (125, "80eb396ba1b365d332aabebed514cccb19f5d5a8eba1d6543be61ceda4fa8b2f"),
)
BW_HITS = tuple((site, 0x004A4576) for site in (
    0x004A38E0, 0x004A3958, 0x004A39CE, 0x004A3A90, 0x004A3B18,
    0x004A3B96, 0x004A3C06, 0x004A3C7E, 0x004A3CF6, 0x004A3D5A,
))
RAW_WINDOWS = (
    (0x004449C9, 0x004A64F8), (0x0047530D, 0x004A60F8),
    (0x00489877, 0x004A60F0), *STORED_ENTRIES,
    (0x004AEE2B, 0x004A54F8), (0x004C4BE9, 0x004A3D20),
    (0x0058F32F, 0x004A6301), (0x0058F72D, 0x004A5FFB),
    (0x005B346D, 0x004A3F00), (0x005B3DFB, 0x004A3D00),
    (0x006313AD, 0x004A50B2), (0x00643147, 0x004A3600),
    (0x006448A7, 0x004A4300), (0x0064A5A3, 0x004A4900),
    (0x0064CF1B, 0x004A52FF), (0x00677FEA, 0x004A3F80),
    (0x006781CA, 0x004A3F80), (0x006C0B1D, 0x004A408A),
    (0x0077FD5C, 0x004A424F),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE:end - BASE]


def pair_digest(values: list[tuple[int, int]] | tuple[tuple[int, int], ...]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    first, second = struct.unpack_from("<HH", data, address - BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = (~(j1 ^ sign)) & 1, (~(j2 ^ sign)) & 1
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load required audit module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _selected_payloads() -> tuple[bytes, ...]:
    payloads = tuple(bytes(
        int(value, 16)
        for value in re.findall(r"0x([0-9a-fA-F]{2})", (ROOT / path).read_text())
    ) for path in SELECTED_PAYLOAD_PATHS)
    identities = tuple((len(payload), sha256(payload)) for payload in payloads)
    if identities != SELECTED_PAYLOAD_IDENTITIES:
        raise AuditError("selected EDMP payload identity changed")
    return payloads


def _caller_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for leaf in config.get("relocated_leaves", []):
        source = leaf.get("source", {}).get("path")
        function = leaf.get("function")
        for relocation in leaf.get("relocations", []):
            target = relocation.get("target_address")
            if (isinstance(target, int) and not isinstance(target, bool)
                    and PHYSICAL[0] <= (target & ~1) < PHYSICAL[1]):
                rows.append({
                    "function": function,
                    "offset": relocation.get("offset"),
                    "source": source,
                    "target_address": target,
                })
    return sorted(rows, key=lambda row: (
        row["source"], row["function"], row["offset"], row["target_address"]
    ))


def _caller_digest(rows: list[dict[str, Any]]) -> str:
    return sha256((json.dumps(
        rows, sort_keys=True, separators=(",", ":")
    ) + "\n").encode())


def _patch_interval(site: dict[str, Any]) -> tuple[int, int]:
    start = site.get("runtime_address")
    size = site.get("expected_size")
    expected_hex = site.get("expected_hex")
    if size is None and isinstance(expected_hex, str):
        if re.fullmatch(r"(?:[0-9a-fA-F]{2})+", expected_hex) is None:
            raise AuditError("overlay patch expected_hex is invalid")
        size = len(expected_hex) // 2
    if (not isinstance(start, int) or isinstance(start, bool)
            or not isinstance(size, int) or isinstance(size, bool) or size < 1):
        raise AuditError("overlay patch interval is not a positive integer range")
    return start, start + size


def audit_overlay_boundary(
    config: dict[str, Any], function_starts: set[int]
) -> dict[str, Any]:
    selected_sources = {
        item.get("path") for item in config.get("sources", [])
        if isinstance(item, dict)
    }
    forbidden_sources = {
        SOURCE_PATH, TDK_PORT_PATH,
        *(path for path in selected_sources
          if isinstance(path, str)
          and path.startswith("third_party/invensense-icm45608/")),
    }
    if selected_sources & forbidden_sources:
        raise AuditError("retired ICM45608 source route reappeared")

    leaf_sources = {
        item.get("source", {}).get("path")
        for item in config.get("relocated_leaves", [])
        if isinstance(item, dict)
    }
    if SOURCE_PATH in leaf_sources or TDK_PORT_PATH in leaf_sources:
        raise AuditError("retired ICM45608 source leaf reappeared")
    if set(RETIRED_WRAPPER_FUNCTIONS) & set(config.get("functions", [])):
        raise AuditError("retired ICM45608 wrapper function reappeared")

    overlaps = []
    for site in config.get("patch_sites", []):
        start, end = _patch_interval(site)
        if start < PHYSICAL[1] and PHYSICAL[0] < end:
            overlaps.append(site.get("name"))
    if overlaps:
        raise AuditError("a patch overlaps the retained stock ICM45608 object")

    include_dirs = list(config.get("toolchain", {}).get("include_dirs", []))
    for profile in config.get("toolchain_profiles", {}).values():
        include_dirs.extend(profile.get("include_dirs", []))
    if any(path == "third_party/invensense-icm45608/src"
           or path.startswith("third_party/invensense-icm45608/src/")
           for path in include_dirs if isinstance(path, str)):
        raise AuditError("retired InvenSense compiler include route reappeared")

    callers = _caller_rows(config)
    if (len(callers) != 29 or len({row["function"] for row in callers}) != 11
            or len({row["target_address"] & ~1 for row in callers}) != 20
            or _caller_digest(callers) != CALLER_ROWS_SHA256):
        raise AuditError("stock ICM45608 external caller topology changed")
    if any((row["target_address"] & ~1) not in function_starts
           for row in callers):
        raise AuditError("stock ICM45608 caller does not target a known entry")
    return {
        "external_callers": len(callers),
        "external_caller_functions": len({row["function"] for row in callers}),
        "external_caller_targets": len({
            row["target_address"] & ~1 for row in callers
        }),
        "redirect_overlap_bytes": 0,
        "caller_rows_sha256": CALLER_ROWS_SHA256,
    }


def audit_public_closure(config: dict[str, Any]) -> dict[str, Any]:
    builder = _load_module("g2_imu_core_builder_audit", COMPONENT_BUILDER)
    inputs = builder._canonical_input_paths(ROOT, OVERLAY, config)
    relative_inputs = {
        path.relative_to(ROOT.resolve()).as_posix() for path in inputs
    }
    selected_risky = sorted(relative_inputs & RISKY_PATHS)
    if selected_risky:
        raise AuditError(
            f"restricted InvenSense input entered compiler closure: {selected_risky[0]}"
        )
    if any(path == SOURCE_PATH or path == TDK_PORT_PATH
           or path.startswith("third_party/invensense-icm45608/src/")
           for path in relative_inputs):
        raise AuditError("retired ICM45608 implementation entered compiler closure")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import community_distribution

    records = community_distribution._selected_records()
    destinations = {destination for _source, destination in records}
    risky_destinations = {
        f"g2/{path}" for path in RISKY_PATHS
    }
    selected_bundle_risky = sorted(destinations & risky_destinations)
    if selected_bundle_risky:
        raise AuditError(
            f"restricted InvenSense input entered community bundle: "
            f"{selected_bundle_risky[0]}"
        )
    retired_destinations = {f"g2/{SOURCE_PATH}", f"g2/{TDK_PORT_PATH}"}
    if destinations & retired_destinations:
        raise AuditError("retired ICM45608 source entered community bundle")
    return {
        "compiler_inputs": len(relative_inputs),
        "community_bundle_records": len(records),
        "restricted_notice_files_selected": 0,
        "dense_payload_files_selected": 0,
        "retired_implementation_files_selected": 0,
    }


def audit_built_boundary(
    report_path: Path, donor_data: bytes, caller_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    report = json.loads(report_path.read_text())
    component_record = report.get("component", {})
    component_path = ROOT / component_record.get("artifact", "")
    component = component_path.read_bytes()
    if (len(component), sha256(component)) != (
            component_record.get("size"), component_record.get("sha256")):
        raise AuditError("canonical component artifact/report identity changed")
    donor_object = image_slice(donor_data, *PHYSICAL)
    component_object = image_slice(component, *PHYSICAL)
    if component_object != donor_object or sha256(component_object) != PHYSICAL_SHA256:
        raise AuditError("canonical component changed retained donor ICM45608 bytes")

    source_paths = {
        item.get("path") for item in report.get("sources", [])
        if isinstance(item, dict)
    }
    if (SOURCE_PATH in source_paths or TDK_PORT_PATH in source_paths
            or any(isinstance(path, str) and
                   path.startswith("third_party/invensense-icm45608/src/")
                   for path in source_paths)):
        raise AuditError("retired ICM45608 source entered built component")

    for site in report.get("overlay", {}).get("patched_sites", []):
        start = site.get("runtime_address")
        size = site.get("expected_size") or site.get("size")
        if (isinstance(start, int) and isinstance(size, int)
                and start < PHYSICAL[1] and PHYSICAL[0] < start + size):
            raise AuditError("built patch overlaps retained stock ICM45608 object")

    built_callers: list[dict[str, Any]] = []
    for leaf in report.get("relocated_leaves", []):
        for relocation in leaf.get("extraction", {}).get("relocations", []):
            target = relocation.get("target_address")
            if (isinstance(target, int) and not isinstance(target, bool)
                    and PHYSICAL[0] <= (target & ~1) < PHYSICAL[1]):
                built_callers.append({
                    "function": leaf.get("extraction", {}).get("function"),
                    "offset": relocation.get("offset"),
                    "source": leaf.get("source", {}).get("path"),
                    "target_address": target,
                })
    built_callers.sort(key=lambda row: (
        row["source"], row["function"], row["offset"], row["target_address"]
    ))
    if built_callers != caller_rows:
        raise AuditError("built stock ICM45608 caller topology changed")

    overlay_record = report.get("overlay", {})
    overlay_path = ROOT / overlay_record.get("artifact", "")
    overlay_data = overlay_path.read_bytes()
    if (len(overlay_data), sha256(overlay_data)) != (
            overlay_record.get("size"), overlay_record.get("sha256")):
        raise AuditError("canonical overlay artifact/report identity changed")
    payload_hits = [overlay_data.count(payload) for payload in _selected_payloads()]
    if any(payload_hits):
        raise AuditError("retired EDMP payload sequence entered canonical overlay")
    return {
        "component_stock_object_sha256": PHYSICAL_SHA256,
        "component_stock_object_bytes": len(donor_object),
        "built_external_callers": len(built_callers),
        "selected_payload_sequence_hits": payload_hits,
    }


def analyze(
    image_path: Path = IMAGE,
    build_report_path: Path | None = BUILD_REPORT,
) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start, end = int(row["entry"], 0), int(row["end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["size"]) or sha256(raw) != row["sha256"]:
            raise AuditError(f"body changed: {row['name']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 53 or sum(map(len, bodies)) != 11_674:
        raise AuditError("function inventory changed")
    if sum(row["path_anchor"] == "true" for row in rows) != 11:
        raise AuditError("retained-path anchor inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = [image_slice(data, start, end) for start, end, _ in GAPS]
    if any(sha256(raw) != expected for raw, (*_, expected) in zip(gaps, GAPS)):
        raise AuditError("owned gap/pool changed")
    if sum(map(len, gaps)) != 762 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, 0x004A35A0, PHYSICAL[0])) != \
            "bae62192a0b6a1914df47a51cbdc20fa873a69dc54cec2838cd2142079d3ce54":
        raise AuditError("previous-object pool boundary changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 16) != bytes.fromhex(
            "1fb5dff88448dff8842800210ff21520"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained IMU symbol changed")

    literal_contract = {
        0x004A3800: 0x20073020,
        0x004A3804: 0x004A35B1,
        0x004A3808: 0x004A35EB,
        0x004A3810: 0x004A56D5,
        0x004A3814: 0x20073170,
        0x004A5698: 0x200640A0,
        0x004A658C: 0x20074684,
        0x004A65B4: 0x20074688,
        0x004A65B8: 0x20074FDD,
        0x004A65D0: 0x2007468C,
        0x004A6630: 0x20074674,
        0x004A6634: 0x20074678,
        0x004A6638: 0x2007467C,
        0x004A663C: 0x20074680,
        0x004A6640: 0x20074FDC,
    }
    if any(struct.unpack_from("<I", data, site - BASE)[0] != value
           for site, value in literal_contract.items()):
        raise AuditError("IMU callback/state literal contract changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior_bl: list[tuple[int, int]] = []
    bw_hits: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw_hits.append((site, target))
    if len(entries) != 72 or pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct BL entry closure changed")
    external = [pair for pair in entries
                if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if len(external) != 35 or pair_digest(external) != EXTERNAL_ENTRY_SHA256:
        raise AuditError("external direct-entry closure changed")
    if interior_bl:
        raise AuditError("direct BL strict-interior ingress changed")
    if bw_hits != list(BW_HITS) or pair_digest(bw_hits) != BW_SHA256:
        raise AuditError("B.W epilogue-branch closure changed")
    if any(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in bw_hits):
        raise AuditError("external B.W ingress appeared")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 464 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    raw_windows: list[tuple[int, int]] = []
    stored_entries: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        target = value & ~1 if value & 1 else value
        if target in starts or target in interiors:
            raw_windows.append((BASE + offset, value))
            if target in starts:
                stored_entries.append((BASE + offset, value))
    if raw_windows != list(RAW_WINDOWS) or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if stored_entries != list(STORED_ENTRIES) or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored callback-entry closure changed")
    if any(site % 4 == 0 for site, value in raw_windows
           if (site, value) not in STORED_ENTRIES and site != 0x0077FD5C):
        raise AuditError("an accidental raw window became aligned")

    tdk = json.loads(TDK_PROVENANCE.read_text())
    if (tdk.get("license"), tdk.get("upstream", {}).get("tag"),
            tdk.get("upstream", {}).get("commit"),
            tdk.get("upstream", {}).get("driver_version"),
            tdk.get("selection", {}).get("file_count"),
            tdk.get("selection", {}).get("total_bytes"),
            tdk.get("selection", {}).get("aggregate_sha256"),
            tdk.get("g2_delta", {}).get("transport_bytes"),
            tdk.get("g2_delta", {}).get("fifo_callback_offset")) != (
                "mixed-file-specific", TDK_TAG, TDK_COMMIT, "1.1.0", 52,
                594_177, TDK_AGGREGATE, 16, 24):
        raise AuditError("TDK research snapshot provenance changed")
    restricted_notices = tuple(
        "strictly prohibited" in (ROOT / path).read_text(errors="replace")
        for path in RESTRICTED_NOTICE_PATHS
    )
    if restricted_notices != (True,) * 5:
        raise AuditError("restricted InvenSense notice inventory changed")
    payloads = _selected_payloads()
    donor_payload_hits = [data.count(payload) for payload in payloads]
    if donor_payload_hits != [0, 0, 0, 0, 1]:
        raise AuditError("official donor EDMP payload occurrence contract changed")

    overlay = json.loads(OVERLAY.read_text())
    boundary = audit_overlay_boundary(overlay, starts)
    public_closure = audit_public_closure(overlay)
    callers = _caller_rows(overlay)
    built = None
    if build_report_path is not None:
        built = audit_built_boundary(build_report_path, data, callers)

    return {
        "surface": {
            "retained_path_anchors": 11,
            "restored_non_anchor_functions": 42,
            "linked_functions": 53,
            "body_bytes": 11_674,
            "owned_gap_pool_bytes": 762,
            "physical_bytes": 12_436,
            "direct_bl_entry_sites": 72,
            "external_direct_bl_entry_sites": 35,
            "direct_body_calls": 464,
            "stored_exact_entry_pointers": 3,
            "strict_interior_bl_ingress": 0,
            "internal_b_w_epilogue_branches": 10,
            "external_b_w_ingress": 0,
            "raw_entry_or_interior_windows": 21,
        },
        "contracts": {
            "driver_context_address": "0x20073020",
            "sample_ring_address": "0x200640a0",
            "sample_ring_header_bytes": 12,
            "sample_slots": 20,
            "sample_stride": 0x70,
            "bus_read_callback_entry": "0x004a35b1",
            "bus_write_callback_entry": "0x004a35eb",
            "fifo_callback_entry": "0x004a56d5",
            "raw_file_handle_address": "0x20074684",
            "raw_sample_count_address": "0x20074688",
            "raw_collection_active_address": "0x20074fdd",
            "raw_collection_start_time_address": "0x2007468c",
            "raw_collection_limit_ms": 120_000,
            "accel_config_min_interval": 100,
            "accel_config_max_interval": 4_999,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS],
            "source_inventory": "unavailable",
            "license": "unknown",
            "tdk_exact_abi_tag": TDK_TAG,
            "tdk_exact_abi_commit": TDK_COMMIT,
            "tdk_snapshot_license": (
                "mixed: root BSD-3-Clause plus five restrictive file notices"
            ),
            "tdk_snapshot_files": 52,
            "tdk_snapshot_bytes": 594_177,
            "tdk_snapshot_aggregate": TDK_AGGREGATE,
            "tdk_snapshot_status": (
                "repository-local research evidence; not a public/compiler input"
            ),
            "restricted_notice_files": len(RESTRICTED_NOTICE_PATHS),
            "dense_payload_files": len(DENSE_PAYLOAD_PATHS),
            "selected_payloads_in_official_donor": donor_payload_hits,
        },
        "production": {
            "candidate": SOURCE_PATH,
            "source_inventory_available": False,
            "production_routed": False,
            "retained_donor": True,
            "stock_functionality_preserved": True,
            "source_functions": 0,
            "tdk_primary_functions": 0,
            "total_source_functions": 0,
            "recovered_functions": 53,
            "compiled_text_bytes": 0,
            "tdk_compiled_function_bytes": 0,
            "tdk_build_source_files": 0,
            "tdk_build_source_bytes": 0,
            "generated_alignment_bytes": 0,
            "guarded_redirects": 0,
            "authenticated_relocations": boundary["external_callers"],
            "ownership_bytes": 0,
            "retained_stock_bytes": PHYSICAL[1] - PHYSICAL[0],
            "redirect_overlap_bytes": boundary["redirect_overlap_bytes"],
            "external_callers": boundary["external_callers"],
            "external_caller_functions": boundary["external_caller_functions"],
            "external_caller_targets": boundary["external_caller_targets"],
            "external_caller_rows_sha256": boundary["caller_rows_sha256"],
            "restricted_compiler_or_bundle_files": 0,
            "public_closure": public_closure,
            "built_boundary": built,
            "remaining_software_gap": None,
            "hardware_validation": "blocked by unavailable physical evidence",
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 ICM45608 IMU audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 ICM45608 IMU audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
