#!/usr/bin/env python3
"""Fail-closed Cordio/Packetcraft source-version audit for the G2 main image.

This tool is deliberately read-only.  It authenticates the official image,
pins several independently useful Cordio function bodies, and reports only
the source-equivalence claims supported by those bytes.  It does not flash a
device and it does not claim that the complete vendor tree equals an upstream
Packetcraft release.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
MAIN_SIZE = 3_523_396
MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0

PACKETCRAFT_REPOSITORY = "https://github.com/packetcraft-inc/cordio.git"
PACKETCRAFT_LICENSE = "Apache-2.0"
PACKETCRAFT_LICENSE_BLOB = "5fe50d5491f1166292380f46c8beae44ca83cadb"
PACKETCRAFT_LICENSE_SHA256 = (
    "682ae5978019e4ee9d439b300efb125525b2e4cc4181ebd1e676dd60dc69d7cd"
)

# The relevant source blobs are unchanged through all four official releases.
PACKETCRAFT_RELEASES = {
    "r20.05": {
        "commit": "eeb34839755da1c19cc85b8795cc863483c16ef0",
        "tree": "906eb9beaf5e8c3b39ab445f6522f7febeda38b5",
    },
    "r20.05a": {
        "commit": "5e21ee596a80a3dc75ae5ef0938712a6042b2ac3",
        "tree": "5001d075e93220d66ae1340208046c0526b0dc3a",
    },
    "r20.05b": {
        "commit": "eb4282c7abe78dad8fb3984791b9c193fe904052",
        "tree": "c8204fcb39847aa6d3cae3ec49772a70f6097765",
    },
    "r20.05c": {
        "commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
        "tree": "0a76c7dde46d3b94bb9185a4a5327d0e3f38ec97",
    },
}

PACKETCRAFT_SOURCE_BLOBS = {
    "ble-host/sources/stack/att/atts_csf.c": {
        "git_blob": "ed4f051194b77827ec991f0d5c0c38969ea7548a",
        "sha256": "1464bff0dbb063ce0e69c5781b73fd7b95656afcd8f710084449298189f2f747",
    },
    "ble-host/sources/stack/dm/dm_conn_sm.c": {
        "git_blob": "58c5c6e1e4df5744c9a41902634cdd23a1aef906",
        "sha256": "cdab18be5711866031487f164d39ea1806bd7f75032992c3050a75bdd0a85de8",
    },
    "ble-host/sources/stack/smp/smp_db.c": {
        "git_blob": "cbd056aaab32eab0838b2bd9bbaac872012ca06b",
        "sha256": "d73d33be7c3d64476b8edb763bb0f32f4a49b54e07a65d44cbfbc4b2deb76645",
    },
    "ble-profiles/sources/af/common/app_db.c": {
        "git_blob": "789f4c9bac29a5b7eb92c2cb22a221cdd720fe83",
        "sha256": "9d96742d3dcb100f9156bdc339cee04e34a2ef5ca4bc5ee3b9971d1d7876f3df",
    },
    "wsf/sources/targets/baremetal/wsf_buf.c": {
        "git_blob": "be2ab9cfc03b65390ba25d8d97321fa2d304fc64",
        "sha256": "d50d374e87b8bed25a0afd50156abac8abad0ae395a7b3db6671decfb50c701d",
    },
}

AMBIQ_HAL_510 = {
    "repository": "https://github.com/AmbiqMicro/ambiqhal_ambiq.git",
    "commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
    "tree": "02b79dbf428a8cded053c65c92cc58fa5fdb8e78",
    "license": "BSD-3-Clause",
    "scope": "Apollo510 HAL dependency closure only; no Cordio source",
}


class AnalysisError(RuntimeError):
    """Raised when an authenticated firmware invariant does not hold."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_offset(runtime_address: int) -> int:
    offset = runtime_address - LOAD_BASE
    if offset < 0:
        raise AnalysisError(f"runtime address 0x{runtime_address:08x} precedes image")
    return offset


def image_slice(data: bytes, start: int, end: int) -> bytes:
    offset = image_offset(start)
    length = end - start
    if length < 0 or offset + length > len(data):
        raise AnalysisError(f"run range 0x{start:08x}--0x{end:08x} is outside image")
    return data[offset : offset + length]


PATH_RECORDS = {
    "app_db": {
        "file_offset": 0x002A04DC,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-profiles\sources\apps\app\common\app_db.c",
        "xrefs": [0x409A0, 0x41590, 0x42300, 0x42DEC, 0x43714, 0x43C40, 0x44564, 0x44B68],
    },
    "att_main": {
        "file_offset": 0x002A4774,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\att\att_main.c",
        "xrefs": [0x7D1F8],
    },
    "atts_csf": {
        "file_offset": 0x002A4954,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\att\atts_csf.c",
        "xrefs": [0xF50A8, 0xF5A4C],
    },
    "dm_conn_sm": {
        "file_offset": 0x002A5134,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\dm\dm_conn_sm.c",
        "xrefs": [0xFC56C],
    },
    "l2c_main": {
        "file_offset": 0x002A54F4,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\l2c\l2c_main.c",
        "xrefs": [0xF8BA0],
    },
    "smp_main": {
        "file_offset": 0x002A6874,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\smp\smp_main.c",
        "xrefs": [0xFFECC],
    },
    "smp_sc_main": {
        "file_offset": 0x002A68D4,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\smp\smp_sc_main.c",
        "xrefs": [0x135858],
    },
    "dm_conn": {
        "file_offset": 0x002A7FD4,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\dm\dm_conn.c",
        "xrefs": [0x7E54C, 0x7E808, 0x7F480],
    },
    "hci_evt": {
        "file_offset": 0x002A8538,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\hci\ambiq\hci_evt.c",
        "xrefs": [0x13339C, 0x133804],
    },
    "smp_act": {
        "file_offset": 0x002A99B4,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\smp\smp_act.c",
        "xrefs": [0x137184],
    },
    "smp_db": {
        "file_offset": 0x002A9A10,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\smp\smp_db.c",
        "xrefs": [0x10A978],
    },
    "wsf_buf": {
        "file_offset": 0x002AA0E4,
        "path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_buf.c",
        "xrefs": [0xF8548],
    },
}


CODE_SPANS = {
    "WsfBufAlloc": {
        "range": [0x00530446, 0x005304D4],
        "sha256": "307ff7ddc2830031087eff4c703949a9974deb2e81efe9cd4334b06c35d57d48",
    },
    "WsfBufFree": {
        "range": [0x005304D4, 0x00530512],
        "sha256": "6148f827458d86f257dc4ac8eab53f4eeb9372912249d1181fc835861b5a058f",
    },
    "AttsCsfSetClientChangeAwareState": {
        "range": [0x0052D090, 0x0052D0DC],
        "sha256": "3d8ce46d70a13f0a62d6693355310733d09cf623fa61018f825956a8feb56070",
    },
    "AttsCsfWriteFeatures_core": {
        "range": [0x0052D628, 0x0052D674],
        "sha256": "2e11f9d1dfa9b76ebfd7d92902439df111292ba781151196eca08280184d5bd9",
    },
    "AttsCsfWriteFeatures_callback_tail": {
        "range": [0x0052D79E, 0x0052D7B6],
        "sha256": "27aa2fb64353776ed629c906e6c6466d6fdcf0ae9d5f02efa1a5650229afa124",
    },
    "dmConnSmExecute_event_table_core": {
        "range": [0x00534024, 0x005340A0],
        "sha256": "decb00baeedd9291a19c1746fb58d8114c979e3f622c78567143f19b515d89b1",
    },
    "dmConnSmExecute_dispatch_tail": {
        "range": [0x005344FA, 0x00534532],
        "sha256": "80294c9e8e8462f412813b8fb7711f795d654d9dd6344b2cda45e8c88e145dd1",
    },
}

WSF_FREE_MAGIC_ADDRESS = 0x00530534
WSF_FREE_MAGIC = 0xFAABD00D
WSF_TRACE_LINE_ADDRESS = 0x0053049C
WSF_TRACE_LINE_INSTRUCTION = bytes.fromhex("40f24110")  # movw r0, #321


def _pointer_offsets(data: bytes, runtime_address: int) -> list[int]:
    needle = struct.pack("<I", runtime_address)
    result: list[int] = []
    cursor = 0
    while True:
        offset = data.find(needle, cursor)
        if offset < 0:
            return result
        result.append(offset)
        cursor = offset + 1


def _validate_paths(data: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label, record in PATH_RECORDS.items():
        offset = record["file_offset"]
        encoded = record["path"].encode("ascii") + b"\0"
        if data[offset : offset + len(encoded)] != encoded:
            raise AnalysisError(f"{label}: source path drift at file offset 0x{offset:x}")
        runtime_address = LOAD_BASE + offset
        found_xrefs = _pointer_offsets(data, runtime_address)
        if found_xrefs != record["xrefs"]:
            raise AnalysisError(
                f"{label}: source-path xrefs drift: {found_xrefs!r} != {record['xrefs']!r}"
            )
        result[label] = {
            "file_offset": offset,
            "runtime_address": runtime_address,
            "path": record["path"],
            "pointer_xrefs_file_offsets": found_xrefs,
        }
    return result


def _validate_code(data: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for label, record in CODE_SPANS.items():
        start, end = record["range"]
        digest = sha256(image_slice(data, start, end))
        if digest != record["sha256"]:
            raise AnalysisError(f"{label}: code fingerprint drift: {digest}")
        result[label] = {
            "range": [start, end],
            "size": end - start,
            "sha256": digest,
        }

    magic = struct.unpack("<I", image_slice(data, WSF_FREE_MAGIC_ADDRESS, WSF_FREE_MAGIC_ADDRESS + 4))[0]
    if magic != WSF_FREE_MAGIC:
        raise AnalysisError(f"WsfBufFree: free marker drift: 0x{magic:08x}")
    trace_line = image_slice(data, WSF_TRACE_LINE_ADDRESS, WSF_TRACE_LINE_ADDRESS + 4)
    if trace_line != WSF_TRACE_LINE_INSTRUCTION:
        raise AnalysisError("WsfBufAlloc: source-line instruction drift")
    return result


def analyze_bytes(data: bytes, *, enforce_image_identity: bool = True) -> dict[str, Any]:
    """Analyze an image; the public CLI always enforces the official identity."""

    if len(data) != MAIN_SIZE:
        raise AnalysisError(f"official image size mismatch: {len(data)} != {MAIN_SIZE}")
    digest = sha256(data)
    if enforce_image_identity and digest != MAIN_SHA256:
        raise AnalysisError(f"official image SHA-256 mismatch: {digest}")

    paths = _validate_paths(data)
    code = _validate_code(data)

    return {
        "status": "whole-stack exact version unresolved",
        "exact_upstream_commit": None,
        "whole_stack_lower_bound": "Packetcraft Cordio r20.05-or-later semantics",
        "bounded_equivalence_interval": {
            "releases": list(PACKETCRAFT_RELEASES),
            "scope": [
                "AttsCsfWriteFeatures behavior",
                "dmConnSmExecute eight-event state-machine shape",
                "individually pinned source blobs unchanged across the interval",
            ],
            "not_an_upper_bound_for": "the complete G2 Cordio vendor tree",
        },
        "qualification": (
            "G2 contains an Ambiq FreeRTOS WSF port and local trace changes; "
            "an exact Packetcraft tree or AmbiqSuite 5.1.0 Cordio archive was not proven"
        ),
        "image": {
            "path": str(MAIN),
            "size": len(data),
            "sha256": digest,
            "load_base": LOAD_BASE,
            "identity_enforced": enforce_image_identity,
        },
        "source_paths": paths,
        "code_fingerprints": code,
        "discriminators": {
            "atts_csf_write_features": {
                "meaning": (
                    "mask 0x07, forbid nonzero-to-zero with ATT error 0x13, "
                    "and OR new bits into the stored features"
                ),
                "excludes": "public r19.02 implementation",
                "supports": "r20.05-or-later behavior",
            },
            "dm_conn_sm_execute": {
                "event_mask": 0x07,
                "events_per_state": 8,
                "table_row_bytes": 16,
                "action_sets": 3,
                "excludes": "public r19.02 thirteen-event table",
                "supports": "r20.05-or-later behavior",
            },
            "wsf_buffer_configuration": {
                "pool_descriptor_bytes": 12,
                "free_list_pointer_offset": 8,
                "free_marker": f"0x{WSF_FREE_MAGIC:08x}",
                "trace_source_line": 321,
                "inferred_flags": {
                    "WSF_BUF_FREE_CHECK": True,
                    "WSF_BUF_STATS": False,
                    "WSF_BUF_STATS_HIST": False,
                    "WSF_OS_DIAG": False,
                },
                "source_port": "Ambiq/FreeRTOS derivative, not upstream baremetal file text",
            },
            "atts_client_state": {
                "DM_CONN_ID_NONE": 0,
                "DM_CONN_MAX": 3,
                "record_stride": 2,
                "DB_READ_PENDING": 2,
                "PENDING_AWARE": 1,
            },
        },
        "upstream": {
            "repository": PACKETCRAFT_REPOSITORY,
            "license": PACKETCRAFT_LICENSE,
            "license_git_blob": PACKETCRAFT_LICENSE_BLOB,
            "license_sha256": PACKETCRAFT_LICENSE_SHA256,
            "releases": PACKETCRAFT_RELEASES,
            "source_blobs": PACKETCRAFT_SOURCE_BLOBS,
        },
        "ambiqsuite_5_1_0_authenticated_local_scope": AMBIQ_HAL_510,
        "ownership_boundary": {
            "upstream_packetcraft": ["WSF core", "BLE host ATT/DM/L2CAP/SMP", "profile framework core"],
            "ambiq_port": ["ble-host/sources/hci/ambiq", "wsf/sources/port/freertos"],
            "even_platform_glue": [
                "platform/ble",
                "custom services and profiles",
                "MRAM record persistence",
                "application database wrappers or extensions",
            ],
            "separate_controller": "EM9305 controller firmware blob",
        },
        "reuse_decision": (
            "Use Apache-2.0 Packetcraft r20.05c only as a pinned source oracle and "
            "promote functions after individual ABI/configuration/call-closure proof; "
            "do not treat the full G2 stack as an exact upstream import"
        ),
    }


def analyze(path: Path) -> dict[str, Any]:
    return analyze_bytes(path.read_bytes(), enforce_image_identity=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=MAIN, help="official G2 main image")
    args = parser.parse_args()
    try:
        report = analyze(args.image)
    except (OSError, AnalysisError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
