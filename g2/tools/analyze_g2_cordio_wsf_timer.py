#!/usr/bin/env python3
"""Fail-closed G2 Cordio/Ambiq FreeRTOS WSF timer recovery audit.

The official image and authenticated Ghidra corpus are read only.  The report
separates public Packetcraft semantic lineage from the official proprietary
AmbiqSuite source-family pin, pins the recovered target ABI and caller
topology, and authenticates the bounded production-excluded clean-room
candidate.
"""

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
RECOVERY_ANALYZER = ROOT / "tools" / "recover_apollo_embedded_source_paths.py"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
CANDIDATE_SOURCE = ROOT / "components" / "shared" / "cordio" / "runtime_cordio_wsf_timer_candidate.c"
CANDIDATE_HEADER = ROOT / "components" / "shared" / "cordio" / "runtime_cordio_wsf_timer_candidate.h"
TIMER_MATRIX = ROOT / "tools" / "manifests" / "readiness-cordio-wsf-timer-matrix.tsv"
AMBIQ_PROVENANCE = ROOT / "tools" / "manifests" / "ambiqsuite-cordio-wsf-timer-provenance.tsv"
AMBIQ_FUNCTION_MAP = ROOT / "tools" / "manifests" / "ambiqsuite-cordio-wsf-timer-function-map.tsv"
CURRENT11_CONFIG_SUMMARY = ROOT / "tools" / "manifests" / "readiness-cordio-wsf-timer-current11-config-summary.tsv"
CURRENT11_BEST_SIZE = ROOT / "tools" / "manifests" / "readiness-cordio-wsf-timer-current11-best-size.tsv"

RELATIVE_PATH = r"third_party\cordio\wsf\sources\port\freertos\wsf_timer.c"
PATH_RUN = 0x006DF034
PATH_CELL = 0x0052A630
MODULE_START = 0x0052A3FC
MODULE_END = 0x0052A614
MODULE_SHA256 = "e410a5b1c5e5d7a475ba75fcefecd99015c4a3e77e2fdec841ec124167cd0458"
DISPATCHER_START = 0x0052B9D0
DISPATCHER_END = 0x0052BAB8
DISPATCHER_SHA256 = "49ba08ce0c35eb58c098babd1ad0e4d68c303c67bf8e2543be552511732474d8"
CANDIDATE_SOURCE_SHA256 = "def199a7179981092894a10627a243c121c7cf221fd35b6ecd9423e1cf600223"
CANDIDATE_HEADER_SHA256 = "86ff13950babe599ee73e5cb9d6eea133179ee1c0c2c8499205eb5e452b3e0b9"
LORELEI_MATRIX_SHA256 = "5609187015274a97cb734c6f47106e3fa9f65d05ee0873c10f4eebab60054323"
AMBIQ_PROVENANCE_SHA256 = "e5bd4f8800b3e1045ac4f9219adc7fa3281093b47263f72b3305704f508bea9a"
AMBIQ_FUNCTION_MAP_SHA256 = "e06c07aeb4766d4c6c4ac0168572f96c21957d2f85365a700f977e57e77e265e"
CURRENT11_CONFIG_SUMMARY_SHA256 = "8b051054e4f6869eec0298f787f15ee0a8313dfa3ad06a019980a718f82e1345"
CURRENT11_BEST_SIZE_SHA256 = "f490ebaba0de30c981b3702014e5921b362c8829e05f7832e87af0862bdc0b42"

FUNCTIONS = [
    (0x0052A3FC, 0x0052A424, "wsfTimerRemove", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A424, 0x0052A468, "wsfTimerInsert", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A468, 0x0052A474, "WsfTimer_handler", "AmbiqSuite 2.5.1 exact source identity"),
    (0x0052A474, 0x0052A4B8, "WsfTimerInit", "AmbiqSuite 2.5.1 source discriminator"),
    (0x0052A4B8, 0x0052A4C4, "WsfTimerStartSec", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A4C4, 0x0052A4D2, "WsfTimerStartMs", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A4D2, 0x0052A4E6, "WsfTimerStop", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A4E6, 0x0052A51A, "WsfTimerUpdate", "AmbiqSuite 2.5.1 exact source mapping"),
    (0x0052A51A, 0x0052A542, "WsfTimerNextExpiration", "AmbiqSuite 2.5.1 exact mapping plus Packetcraft r19.02 oracle"),
    (0x0052A542, 0x0052A574, "WsfTimerServiceExpired", "AmbiqSuite 2.5.1 exact mapping plus Packetcraft oracle"),
    (0x0052A574, 0x0052A614, "WsfTimerUpdateTicks", "AmbiqSuite 2.5.1 exact source mapping"),
]

EXPECTED_CALLERS = {
    0x0052A3FC: [0x0052A438, 0x0052A4DC],
    0x0052A424: [0x0052A4BE, 0x0052A4CC],
    0x0052A468: [],
    0x0052A474: [0x004B7F6A],
    0x0052A4B8: [
        0x0052AE9C, 0x00530E52, 0x00530EF6, 0x0053112E,
        0x005339F0, 0x00534D40, 0x00536ECA, 0x0056E5D8,
    ],
    0x0052A4C4: [
        0x004B2A56, 0x004B2AF8, 0x004B2B60, 0x004B2B82,
        0x004B4AD6, 0x004B4B32, 0x004B4B7E, 0x004BA61C,
        0x004BB38E, 0x00536986, 0x005374FC, 0x00541E4A,
        0x0056EDCA,
    ],
    0x0052A4D2: [
        0x004B2B34, 0x004B3600, 0x004B49D4, 0x004B4B28,
        0x004B4B74, 0x004B548A, 0x004BA472, 0x004BA656,
        0x004BAADE, 0x004BAC0E, 0x0052AF00, 0x00531412,
        0x005317C8, 0x00533A8E, 0x00533DE4, 0x00534AFA,
        0x0053692A, 0x005369A2, 0x00536CFA, 0x0054229A,
        0x0056E5F6, 0x0056E5FE,
    ],
    0x0052A4E6: [0x0052A592],
    0x0052A51A: [0x0052A59A],
    0x0052A542: [0x0052BA32],
    0x0052A574: [0x0052B9D4, 0x0052BA96],
}

RECOVERED_ENTRIES = {0x0052A474, 0x0052A51A, 0x0052A542, 0x0052A574}

EXPECTED_CALLEES = {
    0x0052A3FC: [(0x0052A41A, 0x00538CC8)],
    0x0052A424: [
        (0x0052A42C, 0x0052B8C8),
        (0x0052A438, 0x0052A3FC),
        (0x0052A45E, 0x00538C8C),
        (0x0052A462, 0x0052B8D0),
    ],
    0x0052A468: [(0x0052A46E, 0x0052B95E)],
    0x0052A474: [
        (0x0052A494, 0x0047E6DC),
        (0x0052A4A0, 0x005FA0A4),
        (0x0052A4AE, 0x00454EFE),
    ],
    0x0052A4B8: [(0x0052A4BE, 0x0052A424)],
    0x0052A4C4: [(0x0052A4CC, 0x0052A424)],
    0x0052A4D2: [
        (0x0052A4D6, 0x0052B8C8),
        (0x0052A4DC, 0x0052A3FC),
        (0x0052A4E0, 0x0052B8D0),
    ],
    0x0052A4E6: [
        (0x0052A4EA, 0x0052B8C8),
        (0x0052A4FC, 0x0052B95E),
        (0x0052A514, 0x0052B8D0),
    ],
    0x0052A51A: [
        (0x0052A51E, 0x0052B8C8),
        (0x0052A53A, 0x0052B8D0),
    ],
    0x0052A542: [
        (0x0052A546, 0x0052B8C8),
        (0x0052A55C, 0x00538CC8),
        (0x0052A564, 0x0052B8D0),
        (0x0052A56C, 0x0052B8D0),
    ],
    0x0052A574: [
        (0x0052A576, 0x00454EFE),
        (0x0052A592, 0x0052A4E6),
        (0x0052A59A, 0x0052A51A),
        (0x0052A5BC, 0x0047E7B0),
        (0x0052A5C6, 0x0043D0CE),
        (0x0052A5E0, 0x0043D574),
        (0x0052A5E4, 0x0043D0CE),
        (0x0052A5EC, 0x0043D0CE),
        (0x0052A5FC, 0x0043CE9E),
        (0x0052A604, 0x005FA0A4),
    ],
}


class AuditError(RuntimeError):
    """Raised when any closed WSF timer evidence changes."""


def _load_recovery():
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location("g2_wsf_recovery", RECOVERY_ANALYZER)
    if spec is None or spec.loader is None:
        raise AuditError("cannot load source-path recovery analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _u32(blob: bytes, base: int, address: int) -> int:
    offset = address - base
    if offset < 0 or offset + 4 > len(blob):
        raise AuditError(f"word outside image at 0x{address:08x}")
    return struct.unpack_from("<I", blob, offset)[0]


def _cstring(blob: bytes, base: int, address: int) -> str:
    offset = address - base
    if offset < 0 or offset >= len(blob):
        raise AuditError(f"string outside image at 0x{address:08x}")
    end = blob.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _direct_bl_callers(blob: bytes, recovery: Any, targets: set[int]) -> dict[int, list[int]]:
    base = recovery.baseline.LOAD_BASE
    callers = {target: [] for target in targets}
    for address in range(base, base + len(blob) - 3, 2):
        target = recovery._thumb_bl_target(blob, address)
        if target in callers:
            callers[target].append(address)
    return callers


def analyze(corpus_root: Path, image: Path = IMAGE) -> dict[str, Any]:
    recovery = _load_recovery()
    recovered = recovery.recover(image, corpus_root)
    if recovered["recovery"]["recovered_functions"] != 8:
        raise AuditError("reviewed recovered-function census changed")
    matches = [item for item in recovered["paths"] if item["relative"] == RELATIVE_PATH]
    if len(matches) != 1:
        raise AuditError("retained FreeRTOS WSF timer path changed")
    path = matches[0]
    if path["path_run"] != PATH_RUN or path["path_pointer_cells"] != [PATH_CELL]:
        raise AuditError("retained WSF timer path anchor changed")
    if [item["entry"] for item in path["recovered_functions"]] != sorted(RECOVERED_ENTRIES):
        raise AuditError("recovered WSF timer entry set changed")

    blob = image.read_bytes()
    base = recovery.baseline.LOAD_BASE
    module = blob[MODULE_START - base : MODULE_END - base]
    dispatcher = blob[DISPATCHER_START - base : DISPATCHER_END - base]
    if len(module) != 536 or _sha256(module) != MODULE_SHA256:
        raise AuditError("complete WSF timer module span changed")
    if len(dispatcher) != 232 or _sha256(dispatcher) != DISPATCHER_SHA256:
        raise AuditError("WSF dispatcher span changed")

    direct_callers = _direct_bl_callers(
        blob,
        recovery,
        {entry for entry, _end, _name, _identity in FUNCTIONS},
    )
    functions = []
    for entry, end, name, identity in FUNCTIONS:
        body = blob[entry - base : end - base]
        callees = EXPECTED_CALLEES[entry]
        for callsite, target in callees:
            if not entry <= callsite < end:
                raise AuditError(f"callee site outside {name}")
            if recovery._thumb_bl_target(blob, callsite) != target:
                raise AuditError(f"callee topology changed for {name}")
        functions.append({
            "entry": entry,
            "end_exclusive": end,
            "size": end - entry,
            "sha256": _sha256(body),
            "name": name,
            "identity": identity,
            "direct_bl_callers": direct_callers[entry],
            "direct_bl_callees": [
                {"callsite": callsite, "target": target}
                for callsite, target in callees
            ],
            "ghidra_discovered": entry not in RECOVERED_ENTRIES,
        })
    for item in functions:
        expected = EXPECTED_CALLERS.get(item["entry"])
        if expected is not None and item["direct_bl_callers"] != expected:
            raise AuditError(f"caller topology changed for {item['name']}")

    literal_words = {
        "timer_queue": _u32(blob, base, 0x0052A614),
        "freertos_timer_handle": _u32(blob, base, 0x0052A618),
        "callback_thumb": _u32(blob, base, 0x0052A61C),
        "timer_name": _u32(blob, base, 0x0052A620),
        "last_tick": _u32(blob, base, 0x0052A624),
        "failure_text": _u32(blob, base, 0x0052A628),
        "update_name": _u32(blob, base, 0x0052A62C),
        "source_path": _u32(blob, base, 0x0052A630),
        "log_tag": _u32(blob, base, 0x0052A634),
    }
    expected_words = {
        "timer_queue": 0x200741B0,
        "freertos_timer_handle": 0x20074EF4,
        "callback_thumb": 0x0052A469,
        "timer_name": 0x0078C95C,
        "last_tick": 0x20074EF8,
        "failure_text": 0x00768250,
        "update_name": 0x00784B6C,
        "source_path": PATH_RUN,
        "log_tag": 0x0078C968,
    }
    if literal_words != expected_words:
        raise AuditError("WSF timer literal/global table changed")
    strings = {
        "timer_name": _cstring(blob, base, literal_words["timer_name"]),
        "failure_text": _cstring(blob, base, literal_words["failure_text"]),
        "update_name": _cstring(blob, base, literal_words["update_name"]),
        "source_path": _cstring(blob, base, literal_words["source_path"]),
        "log_tag": _cstring(blob, base, literal_words["log_tag"]),
    }
    if strings != {
        "timer_name": "WSF Timer",
        "failure_text": "--->xTimerChangePeriod failed",
        "update_name": "WsfTimerUpdateTicks",
        "source_path": r"D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\wsf\sources\port\freertos\wsf_timer.c",
        "log_tag": "wsf_timer",
    }:
        raise AuditError("WSF timer retained strings changed")

    source_data = CANDIDATE_SOURCE.read_bytes()
    header_data = CANDIDATE_HEADER.read_bytes()
    if _sha256(source_data) != CANDIDATE_SOURCE_SHA256:
        raise AuditError("clean-room WSF timer candidate source changed")
    if _sha256(header_data) != CANDIDATE_HEADER_SHA256:
        raise AuditError("clean-room WSF timer candidate header changed")
    matrix_data = TIMER_MATRIX.read_bytes()
    if _sha256(matrix_data) != LORELEI_MATRIX_SHA256:
        raise AuditError("Lorelei WSF candidate matrix changed")
    matrix_lines = [
        line for line in matrix_data.decode("utf-8").splitlines()
        if not line.startswith("#")
    ]
    matrix_rows = list(csv.DictReader(matrix_lines, delimiter="\t"))
    if len(matrix_rows) != 8 or any(
        row["raw_match"] != "no" or row["normalized_match"] != "no"
        for row in matrix_rows
    ):
        raise AuditError("Lorelei WSF matrix result census changed")
    size_exact = [
        row for row in matrix_rows
        if row["candidate_size"] == row["stock_size"]
    ]
    if [(row["release"], row["config"], row["symbol"]) for row in size_exact] != [
        ("r19.02", "Os_noinline", "WsfTimerNextExpiration")
    ]:
        raise AuditError("Lorelei WSF size discriminator changed")
    ambiq_data = AMBIQ_PROVENANCE.read_bytes()
    if _sha256(ambiq_data) != AMBIQ_PROVENANCE_SHA256:
        raise AuditError("AmbiqSuite WSF provenance ledger changed")
    ambiq_lines = [
        line for line in ambiq_data.decode("utf-8").splitlines()
        if not line.startswith("#")
    ]
    ambiq_rows = list(csv.DictReader(ambiq_lines, delimiter="\t"))
    if [row["release"] for row in ambiq_rows] != ["2.4.2", "2.5.1"]:
        raise AuditError("AmbiqSuite WSF provenance release interval changed")
    if ambiq_rows[1]["source_git_blob"] != "91ae7bb7d9883587822914c2586e95e4d08f165c":
        raise AuditError("AmbiqSuite 2.5.1 WSF source identity changed")
    function_map_data = AMBIQ_FUNCTION_MAP.read_bytes()
    if _sha256(function_map_data) != AMBIQ_FUNCTION_MAP_SHA256:
        raise AuditError("AmbiqSuite WSF function map changed")
    function_map_lines = [
        line for line in function_map_data.decode("utf-8").splitlines()
        if not line.startswith("#")
    ]
    function_map_rows = list(csv.DictReader(function_map_lines, delimiter="\t"))
    if len(function_map_rows) != len(functions):
        raise AuditError("AmbiqSuite WSF function map count changed")
    for function, mapped in zip(functions, function_map_rows):
        if (
            mapped["stock_name"] != function["name"]
            or int(mapped["stock_start"], 0) != function["entry"]
            or int(mapped["stock_end_exclusive"], 0) != function["end_exclusive"]
            or mapped["stock_sha256"] != function["sha256"]
        ):
            raise AuditError(f"AmbiqSuite mapping changed for {function['name']}")
    current_config_data = CURRENT11_CONFIG_SUMMARY.read_bytes()
    if _sha256(current_config_data) != CURRENT11_CONFIG_SUMMARY_SHA256:
        raise AuditError("Lorelei current-11 config summary changed")
    current_config_rows = list(csv.DictReader(
        [
            line for line in current_config_data.decode("utf-8").splitlines()
            if not line.startswith("#")
        ],
        delimiter="\t",
    ))
    if len(current_config_rows) != 13 or any(
        row["functions"] != "11"
        or row["raw_matches"] != "0"
        or row["normalized_matches"] != "0"
        for row in current_config_rows
    ):
        raise AuditError("Lorelei current-11 config result changed")
    current_best_data = CURRENT11_BEST_SIZE.read_bytes()
    if _sha256(current_best_data) != CURRENT11_BEST_SIZE_SHA256:
        raise AuditError("Lorelei current-11 best-size summary changed")
    current_best_rows = list(csv.DictReader(
        [
            line for line in current_best_data.decode("utf-8").splitlines()
            if not line.startswith("#")
        ],
        delimiter="\t",
    ))
    if len(current_best_rows) != 11:
        raise AuditError("Lorelei current-11 function count changed")
    remaining_size_gaps = {
        row["function"]: int(row["best_abs_delta"])
        for row in current_best_rows
        if row["best_abs_delta"] != "0"
    }
    if remaining_size_gaps != {
        "WsfTimerInit": 4,
        "WsfTimerServiceExpired": 2,
        "WsfTimerUpdateTicks": 12,
    }:
        raise AuditError("Lorelei current-11 best-size gaps changed")

    return {
        "schema_version": 2,
        "analysis_mode": "read-only target audit; production-excluded source candidate; no hardware or flash operation",
        "module": {
            "start": MODULE_START,
            "end_exclusive": MODULE_END,
            "size": len(module),
            "sha256": MODULE_SHA256,
            "functions": functions,
            "retained_path_run": PATH_RUN,
            "retained_path_pointer_cell": PATH_CELL,
            "callback_pointer_cell": 0x0052A61C,
            "callback_thumb_entry": literal_words["callback_thumb"],
        },
        "abi": {
            "timer_size": 16,
            "timer_offsets": {
                "next": 0,
                "ticks": 4,
                "msg": 8,
                "handler_id": 12,
                "is_started": 13,
            },
            "queue_size": 8,
            "globals": {
                "queue": literal_words["timer_queue"],
                "freertos_timer_handle": literal_words["freertos_timer_handle"],
                "last_tick": literal_words["last_tick"],
            },
            "lock": {
                "WsfCsEnter": [0x0052B8A4, 0x0052B8B6, "e0ff3f4fa338e939616823c70ae7fc13df075b7de32178db2810cf9eb39edb87"],
                "WsfCsExit": [0x0052B8B6, 0x0052B8C8, "8685a9a54cba4040bb297f58f5bc9e0d5beed1f46a7159363edc8f80648e824c"],
                "WsfTaskLock": [0x0052B8C8, 0x0052B8D0, "4ae68a8cc15e75c482171f6fdd1e56d9bf7a9a787f56a9761e89af9833911f02"],
                "WsfTaskUnlock": [0x0052B8D0, 0x0052B8D8, "19785a8c5eb6c2e10cd274c554a5d7d1b649a94433f558511c02cdb5405397a1"],
            },
        },
        "lineage": {
            "classification": "official AmbiqSuite 2.5.1 exact implementation/source family with Packetcraft lineage",
            "ambiqsuite": {
                "selected_release": "2.5.1",
                "release_date": "2020-09",
                "archive_url": ambiq_rows[1]["official_archive_url"],
                "archive_sha256": ambiq_rows[1]["archive_sha256"],
                "archive_bytes": int(ambiq_rows[1]["archive_bytes"]),
                "s3_version_id": ambiq_rows[1]["s3_version_id"],
                "path": ambiq_rows[1]["source_path"],
                "source_bytes": int(ambiq_rows[1]["source_bytes"]),
                "source_sha256": ambiq_rows[1]["source_sha256"],
                "git_blob": ambiq_rows[1]["source_git_blob"],
                "header_path": ambiq_rows[1]["header_path"],
                "header_sha256": ambiq_rows[1]["header_sha256"],
                "license_path": ambiq_rows[1]["license_path"],
                "license_sha256": ambiq_rows[1]["license_sha256"],
                "provenance_manifest": str(AMBIQ_PROVENANCE.relative_to(ROOT)),
                "provenance_manifest_sha256": AMBIQ_PROVENANCE_SHA256,
                "function_map": str(AMBIQ_FUNCTION_MAP.relative_to(ROOT)),
                "function_map_sha256": AMBIQ_FUNCTION_MAP_SHA256,
                "mapped_functions": len(function_map_rows),
                "stock_discriminator": "2.5.1 adds the saved xTaskGetTickCount value after timer creation; stock contains that call/store and excludes unmodified 2.4.2",
                "qualification": "exact implementation/source family, not proof of byte-identical local source text or IAR output",
                "license": "proprietary ARM license in official source; identity recorded without redistributing source",
                "later_official_git_corroboration": {
                    "repository": "AmbiqAI/nsx-ambiq-sdk",
                    "commit": "9f36432d875060ca301675131b40452ecf8377ca",
                    "git_blob": "91ae7bb7d9883587822914c2586e95e4d08f165c",
                },
            },
            "packetcraft_r19_02": {
                "commit": "86372d84ef0386d8834ed036e613c8f2ded1ff16",
                "path": "wsf/sources/port/baremetal/wsf_timer.c",
                "git_blob": "d2cced51a06a87f7ca26369b01e4a8b0ec325346",
                "sha256": "1dd5bb6aab28031793227a152686d692b2c04878de4bf6d2d8bef187081a0a4e",
                "matched_functions": ["WsfTimerNextExpiration", "WsfTimerServiceExpired"],
            },
            "packetcraft_r20_05_to_r20_05c": {
                "commits": [
                    "eeb34839755da1c19cc85b8795cc863483c16ef0",
                    "5e21ee596a80a3dc75ae5ef0938712a6042b2ac3",
                    "eb4282c7abe78dad8fb3984791b9c193fe904052",
                    "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
                ],
                "path": "wsf/sources/targets/baremetal/wsf_timer.c",
                "git_blob": "df2c9dd1e94b26e2e989f01dcc82a1cf418b58d2",
                "sha256": "35fd98d54047480071df7c8475a822bceec2f27e13c2960b063991e4100d673b",
                "qualification": "byte-identical public comparator, not the retained FreeRTOS translation unit",
            },
        },
        "strings": strings,
        "dispatcher": {
            "start": DISPATCHER_START,
            "end_exclusive": DISPATCHER_END,
            "size": len(dispatcher),
            "sha256": DISPATCHER_SHA256,
            "entry_calls": [0x0052B9D4, 0x0052BA32, 0x0052BA96],
        },
        "candidate": {
            "source": str(CANDIDATE_SOURCE.relative_to(ROOT)),
            "source_sha256": CANDIDATE_SOURCE_SHA256,
            "header": str(CANDIDATE_HEADER.relative_to(ROOT)),
            "header_sha256": CANDIDATE_HEADER_SHA256,
            "functions": [
                "open_cfw_cordio_wsf_timer_remove_candidate",
                "open_cfw_cordio_wsf_timer_insert_candidate",
                "open_cfw_cordio_wsf_timer_callback_candidate",
                "open_cfw_cordio_wsf_timer_init_candidate",
                "open_cfw_cordio_wsf_timer_start_sec_candidate",
                "open_cfw_cordio_wsf_timer_start_ms_candidate",
                "open_cfw_cordio_wsf_timer_stop_candidate",
                "open_cfw_cordio_wsf_timer_update_candidate",
                "open_cfw_cordio_wsf_timer_next_expiration_candidate",
                "open_cfw_cordio_wsf_timer_service_expired_candidate",
                "open_cfw_cordio_wsf_timer_update_ticks_candidate",
            ],
            "behaviorally_recreated_stock_function_bytes": 536,
            "production": "excluded",
        },
        "compiler_matrix": {
            "manifest": str(TIMER_MATRIX.relative_to(ROOT)),
            "manifest_sha256": LORELEI_MATRIX_SHA256,
            "returned_artifact_sha256": "59a67b7a29bf00aae45692f2beb745a96e27ca1dcb20c65b5733680d289d63d1",
            "container_id": "sha256:4bf18d22a8e9e1dffa4c21ea1ba44decf7a88a4a2e9c766e47c523f4bef26db0",
            "matrix_elapsed_ns": 800405321,
            "rows": len(matrix_rows),
            "raw_matches": 0,
            "strict_normalized_matches": 0,
            "exact_size_rows": [
                {
                    "release": "r19.02",
                    "config": "Os_noinline",
                    "function": "WsfTimerNextExpiration",
                    "bytes": 40,
                }
            ],
            "verdict": "r19.02 is a semantic/ABI discriminator; no GCC row proves exact IAR output",
        },
        "current11_matrix": {
            "config_summary": str(CURRENT11_CONFIG_SUMMARY.relative_to(ROOT)),
            "config_summary_sha256": CURRENT11_CONFIG_SUMMARY_SHA256,
            "best_size_summary": str(CURRENT11_BEST_SIZE.relative_to(ROOT)),
            "best_size_summary_sha256": CURRENT11_BEST_SIZE_SHA256,
            "returned_artifact_sha256": "b0c5614157d33fbeddbdfdaa88bcdd6927f58af64ce73cd274de45342c807fa6",
            "full_143_row_ledger_sha256": "2da0db026a5235e3d5f61e5d59ea1bd390d0249d41b710f2a0606318a02381f1",
            "matrix_elapsed_ns": 2448108512,
            "configs": len(current_config_rows),
            "function_rows": len(current_config_rows) * len(current_best_rows),
            "raw_matches": 0,
            "strict_normalized_matches": 0,
            "exact_size_functions": sum(
                row["best_abs_delta"] == "0" for row in current_best_rows
            ),
            "remaining_best_size_gaps": remaining_size_gaps,
            "undefined_provider_and_global_seams": 13,
            "linked_unresolved_symbols": 0,
            "comment_only_predecessor_objects_identical": 13,
            "comment_only_predecessor_elfs_identical": 13,
            "verdict": "all eleven functions compile/link in isolation; no GCC row proves exact IAR output",
        },
        "limitations": [
            "the historical source pin is an official versioned AmbiqSuite 2.5.1 archive/S3 object rather than a historical public Git commit",
            "the archived source is the exact implementation family, but retained assertion line metadata indicates minor local text/config drift, so byte-identical original source text is not claimed",
            "the stock timer structure places ticks at +4 and msg at +8, opposite the selected r20.05c public header",
            "the r19.02 commit is a public semantic oracle for two functions; the separate official AmbiqSuite archive supplies the vendor implementation-family pin",
            "all eleven bounded functions have clean-room behavioral source, but the candidate remains absent from every production overlay and package manifest",
            "stock logging, assertion internals, IAR code generation, placement, and relocation closure remain outside the clean-room behavioral recreation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ghidra-corpus", type=Path, required=True)
    parser.add_argument("--image", type=Path, default=IMAGE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = analyze(args.ghidra_corpus, args.image)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 Cordio/Ambiq WSF timer recovery")
        print(f"  module: 0x{MODULE_START:08x}..0x{MODULE_END:08x} ({MODULE_END - MODULE_START} bytes)")
        print("  recovered: WsfTimerInit, WsfTimerNextExpiration, WsfTimerServiceExpired, WsfTimerUpdateTicks")
        print("  lineage: official AmbiqSuite 2.5.1 implementation/source family")
        print("  source candidate: eleven functions behaviorally recreated; production-excluded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
