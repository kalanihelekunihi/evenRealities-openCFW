#!/usr/bin/env python3
"""Find stock EM9305 functions from a relocation-bearing SDK ARC archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
IMAGE_SIZE = 211_948
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
PACKAGE_MAP_BASE = 0x0030_1FDC
APP_FILE_OFFSET = 0x424
APP_BASE = 0x0030_2400
APP_END = 0x0033_5BC8
SDK_ARCHIVES = {
    "qpc": {
        "path": "libs/third_party/QPC/lib_QPC.a",
        "git_blob": "26fc11bf0144caab77608fa5794e544d4d1d8a38",
        "sha256": "c8b5834ca8c3b42fde7e2f8447772800561ddd5897123918e8353807242f8db5",
    },
    "pml": {
        "path": "libs/pml/lib_pml.a",
        "git_blob": "45c88f15bc6367dc15e3cdcabb9a23be74bb9934",
        "sha256": "e57be8e7fd4352e99c3437bbea0563e1b1add61228781925f7212a07f0a04ce2",
    },
    "sleep_manager": {
        "path": "libs/sleep_manager/lib_sleep_manager.a",
        "git_blob": "05af021ac9132dc8c727913c4382eba9019aebdb",
        "sha256": "82968846c25b2a6685aa357386ad1dcb6bbe33bb138359de66ce91d10d600856",
    },
    "sleep_timer": {
        "path": "libs/sleep_timer/lib_sleep_timer.a",
        "git_blob": "3713f176b7f1614920a3043c4dcb41ba730e3fe0",
        "sha256": "cbf143b6d90832b349925bc1cfdd0963c2a7102b66c11b6aee9277739dcbe1b9",
    },
    "prot_timer": {
        "path": "libs/prot_timer/lib_prot_timer.a",
        "git_blob": "cf8f1f22ea840568c83c6a2662c86e7d95b6581a",
        "sha256": "8ea99f2afa095f90d1c9555d748908bb6e03805db87d38a80a51f640f11788c7",
    },
    "unitimer": {
        "path": "libs/unitimer/lib_unitimer.a",
        "git_blob": "07ed4df5a464637adf024d383bc89d2fd0b57bb0",
        "sha256": "8699c09a59e65fec8f349a67fc445b8ab931a9e736d4bfabe01ebd773c005bd4",
    },
}
SUPPORTED_RELOCATIONS = {
    "R_ARC_32": 4,
    "R_ARC_32_ME": 4,
    "R_ARC_S25H_PCREL": 4,
    "R_ARC_S25W_PCREL": 4,
}
COMPILER_COMMENT_ANCHORS = (
    "LLVM 14.0.6/T-2022.09. (build 004)",
    "(EM-Micro)",
    "-arcv2em",
    "-Os",
)

# Expected locations already established independently from stock topology.
KNOWN_STOCK_FUNCTIONS = {
    "qkPortDummy": 0x0030_2518,
    "IRQHandler_SWI0": 0x0030_251C,
    "QK_noPreemption": 0x0030_25D0,
    "QK_restoreContext": 0x0030_25DC,
    "SWI1WaitForInterrupt": 0x0030_25EA,
    "IRQHandler_SWI1": 0x0030_25F8,
    "BSP_Init": 0x0030_2E80,
    "QActive_ctor": 0x0031_0D18,
    "QActive_get_": 0x0031_0D38,
    "QActive_postLIFO_": 0x0031_0DA0,
    "QActive_post_": 0x0031_0E28,
    "QActive_start_": 0x0031_0EE4,
    "QEQueue_init": 0x0031_0F5C,
    "QF_add_": 0x0031_0F74,
    "QF_bzero": 0x0031_0FAC,
    "QF_gc": 0x0031_0FB8,
    "QF_init": 0x0031_1014,
    "QF_newX_": 0x0031_1060,
    "QF_onResume": 0x0031_10F4,
    "QF_onResumeExt": 0x0031_114C,
    "QF_onResumeInternalHook": 0x0031_1150,
    "QF_onStartup": 0x0031_1154,
    "QF_onStartupExt": 0x0031_11A0,
    "QF_onStartupInternalHook": 0x0031_11A4,
    "QF_poolInit": 0x0031_11A8,
    "QF_run": 0x0031_1230,
    "QHsm_ctor": 0x0031_1260,
    "QHsm_dispatch_": 0x0031_1274,
    "QHsm_init_": 0x0031_1490,
    "QHsm_top": 0x0031_1550,
    "QK_activate_": 0x0031_1554,
    "QK_onIdle": 0x0031_15E4,
    "QK_onIdleExt": 0x0031_161C,
    "QK_onIdleInternalHook": 0x0031_1620,
    "QK_sched_": 0x0031_1634,
    "QMPool_get": 0x0031_166C,
    "QMPool_init": 0x0031_16F4,
    "QMPool_put": 0x0031_1798,
    "Q_onAssert": 0x0031_17D8,
    "Q_onAssertExt": 0x0031_17E8,
}
EXPECTED_EXACT_MATCHES = {
    "qpc": {
        name: address for name, address in KNOWN_STOCK_FUNCTIONS.items()
        if name not in {
            "SWI1WaitForInterrupt",
            "QF_onResumeInternalHook",
            "QF_onStartupInternalHook",
            "QK_onIdleInternalHook",
        }
    },
    "pml": {
        "IRQHandler_PmlSvld": 0x00305E68,
        "PML_AutomaticSleepModeDisable": 0x0030F1CC,
        "PML_ConfigWakeByStInHfClk": 0x0030F218,
        "PML_ConfigWakeByStInSysClkWithBootTimeComp": 0x0030F250,
        "PML_ConfigureSleepRcCalibBeforeSleep": 0x0030F288,
        "PML_ConvertHf2LfClk": 0x0030F2B8,
        "PML_ConvertLf2HfClk": 0x0030F2D8,
        "PML_Dbm2PmlRfPower": 0x0030F2F0,
        "PML_GetMaximumRfOutputPower": 0x0030F31C,
        "PML_GoToSleep": 0x0030F374,
        "PML_GoToSleepWithoutChecks": 0x0030F468,
        "PML_Init": 0x0030F4B0,
        "PML_IsCPUSleepAllowed": 0x0030F568,
        "PML_IsItOkToGoToSleep": 0x0030F57C,
        "PML_IsVendorSleepAutomatic": 0x0030F60C,
        "PML_PmlRfPower2Dbm": 0x0030F65C,
        "PML_PowerInit": 0x0030F668,
        "PML_PowerPreInit": 0x0030F67C,
        "PML_RegisterWakeUpAction": 0x0030F6EC,
        "PML_SetDcdcTimingConst": 0x0030F730,
        "PML_SetLfClkSource": 0x0030F768,
        "PML_SetRfOutputPower": 0x0030F794,
        "PML_SetRfOutputPowerRegisters": 0x0030F864,
        "PML_UpdateDCDC": 0x0030F944,
        "PML_UpdateDcdcParameters": 0x0030F970,
        "PML_UpdateResumeTime": 0x0030F998,
        "PML_UpdateScDbMode": 0x0030F9BC,
        "PML_UpdateWakeUpTime": 0x0030F9D0,
        "PML_UseLfXtalClk": 0x0030FA08,
        "PML_VoltMonitorInit": 0x0030FA40,
        "PML_VoltMonitorPreInit": 0x0030FA78,
        "PML_VoltMonitorReStoreConfig": 0x0030FA9C,
        "VoltMon_ConfigureAppModeLimits": 0x00313A0C,
        "VoltMon_DoMeasurement": 0x00313AE4,
        "VoltMon_GetFlagLimitRf0dBm": 0x00313B4C,
        "VoltMon_GetFlagLimitRf10dBm": 0x00313B60,
        "VoltMon_GetFlagLimitRf3dBm": 0x00313B70,
        "VoltMon_GetFlagLimitRf4dBm": 0x00313B84,
        "VoltMon_GetFlagLimitRf5dBm": 0x00313B98,
        "VoltMon_GetFlagLimitRf6dBm": 0x00313BAC,
        "VoltMon_GetVoltage": 0x00313C18,
        "VoltMon_SetVoltageMonitorEnable": 0x00313C4C,
        "VoltMon_SetVoltageMonitorLevel": 0x00313C74,
        "VoltMon_UpdateFlags": 0x00313C9C,
    },
    "sleep_manager": {
        "SLEEP_MANAGER_RCCAL_Callback": 0x003128E4,
    },
    "sleep_timer": {
        "SleepTimer_Init": 0x0031376C,
        "SleepTimer_SetCompareValue": 0x0031377C,
        "SleepTimer_SetWakeupTime": 0x003137B4,
    },
    "prot_timer": {
        "ProtTimer_GetCompareEnable": 0x003108D0,
        "ProtTimer_GetDivider": 0x003108E8,
        "ProtTimer_GetSystemTime": 0x00310900,
        "ProtTimer_Init": 0x00310914,
        "ProtTimer_RegisterEventTimeCallback": 0x00310944,
        "ProtTimer_RestartAfterSleep": 0x00310990,
        "ProtTimer_RestoreAdjust": 0x00310A4C,
        "ProtTimer_RestoreConfig": 0x00310AA8,
        "ProtTimer_RestoreStart": 0x00310B08,
        "ProtTimer_SetConfiguration": 0x00310B84,
        "ProtTimer_SetDivider": 0x00310B94,
        "ProtTimer_StoreConfig": 0x00310C08,
        "ProtTimer_UpdateRestartTime": 0x00310CEC,
    },
    "unitimer": {
        "Timer_RegisterModule": 0x00311EE0,
    },
}
EXPECTED_VENDOR_MODIFIED = {
    "qpc": {
        "QF_onResumeInternalHook": 0x00311150,
        "QF_onStartupInternalHook": 0x003111A4,
        "QK_onIdleInternalHook": 0x00311620,
    },
}


class ComparisonError(RuntimeError):
    """Raised when an authenticated input or comparison invariant changes."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(command: Sequence[str], *, cwd: Path | None = None) -> str:
    return subprocess.run(
        command,
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse_functions(symbol_table: str) -> list[dict[str, Any]]:
    functions = []
    for line in symbol_table.splitlines():
        fields = line.split()
        if len(fields) != 6 or fields[2] != "F":
            continue
        address, binding, _kind, section, size, name = fields
        if name.startswith("$") or section == "*UND*":
            continue
        functions.append({
            "name": name,
            "binding": binding,
            "section": section,
            "offset": int(address, 16),
            "size": int(size, 16),
        })
    return functions


def parse_relocations(relocation_table: str) -> dict[str, list[tuple[int, str]]]:
    result: dict[str, list[tuple[int, str]]] = {}
    current: str | None = None
    heading = re.compile(r"^RELOCATION RECORDS FOR \[(.+)\]:$")
    record = re.compile(r"^([0-9A-Fa-f]+)\s+(R_ARC_\S+)\s+")
    for line in relocation_table.splitlines():
        match = heading.match(line)
        if match:
            current = match.group(1)
            result.setdefault(current, [])
            continue
        match = record.match(line)
        if match and current is not None:
            relocation = match.group(2)
            if relocation not in SUPPORTED_RELOCATIONS:
                raise ComparisonError(f"unsupported ARC relocation: {relocation}")
            result[current].append((int(match.group(1), 16), relocation))
    return result


def normalized_body(
    section_body: bytes,
    function_offset: int,
    function_size: int,
    relocations: Sequence[tuple[int, str]],
) -> tuple[bytes, tuple[int, ...]]:
    body = bytearray(section_body[function_offset:function_offset + function_size])
    if len(body) != function_size:
        raise ComparisonError("function extends beyond extracted ELF section")
    masked = set()
    for offset, relocation in relocations:
        width = SUPPORTED_RELOCATIONS[relocation]
        if not (function_offset <= offset < function_offset + function_size):
            continue
        relative = offset - function_offset
        if relative + width > function_size:
            raise ComparisonError("relocation crosses function boundary")
        for index in range(relative, relative + width):
            body[index] = 0
            masked.add(index)
    return bytes(body), tuple(sorted(masked))


def find_normalized_matches(
    app: bytes,
    candidate: bytes,
    masked: Sequence[int],
    *,
    minimum_compared_bytes: int,
) -> tuple[int, ...]:
    masked_set = set(masked)
    compared = tuple(index for index in range(len(candidate)) if index not in masked_set)
    if len(compared) < minimum_compared_bytes:
        return ()

    # Every real match must contain any contiguous run of unmasked candidate
    # bytes. Use the longest run as a C-optimized bytes.find() anchor, then
    # perform the complete masked comparison only at anchor hits. This is
    # equivalent to scanning every halfword but scales to multi-megabyte SDK
    # archives without multiplying Python work by the whole application size.
    runs: list[tuple[int, int]] = []
    run_start: int | None = None
    for index in range(len(candidate) + 1):
        is_compared = index < len(candidate) and index not in masked_set
        if is_compared and run_start is None:
            run_start = index
        elif not is_compared and run_start is not None:
            runs.append((run_start, index))
            run_start = None
    anchor_start, anchor_end = max(runs, key=lambda item: item[1] - item[0])
    anchor = candidate[anchor_start:anchor_end]
    matches = []
    search_from = 0
    while True:
        position = app.find(anchor, search_from)
        if position < 0:
            break
        offset = position - anchor_start
        search_from = position + 1
        if (
            offset >= 0
            and offset % 2 == 0
            and offset + len(candidate) <= len(app)
            and all(app[offset + index] == candidate[index] for index in compared)
        ):
            matches.append(APP_BASE + offset)
    return tuple(matches)


def normalized_matches_at(
    app: bytes,
    candidate: bytes,
    masked: Sequence[int],
    address: int,
) -> bool:
    offset = address - APP_BASE
    if offset < 0 or offset + len(candidate) > len(app):
        return False
    masked_set = set(masked)
    return all(
        app[offset + index] == value
        for index, value in enumerate(candidate)
        if index not in masked_set
    )


def compare(
    image: Path,
    archive: Path,
    binutils_dir: Path,
    *,
    archive_kind: str = "qpc",
    minimum_compared_bytes: int = 8,
    archive_identity_override: dict[str, str] | None = None,
) -> dict[str, Any]:
    image = image.resolve()
    archive = archive.resolve()
    binutils_dir = binutils_dir.resolve()
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or sha256(blob) != IMAGE_SHA256:
        raise ComparisonError("official EM9305 image identity mismatch")
    if archive_kind in SDK_ARCHIVES:
        if archive_identity_override is not None:
            raise ComparisonError("known archive kind cannot use an identity override")
        archive_identity = SDK_ARCHIVES[archive_kind]
        enforce_known = True
    else:
        if archive_identity_override is None:
            raise ComparisonError(
                "discovery archive requires path, Git blob, and SHA-256 identity"
            )
        archive_identity = archive_identity_override
        enforce_known = False
        if not re.fullmatch(r"[0-9a-f]{40}", archive_identity.get("git_blob", "")):
            raise ComparisonError("discovery archive Git blob must be 40 lowercase hex digits")
        if not re.fullmatch(r"[0-9a-f]{64}", archive_identity.get("sha256", "")):
            raise ComparisonError("discovery archive SHA-256 must be 64 lowercase hex digits")
        if not archive_identity.get("path"):
            raise ComparisonError("discovery archive source path is required")
    archive_body = archive.read_bytes()
    if sha256(archive_body) != archive_identity["sha256"]:
        raise ComparisonError(f"EM9305 SDK {archive_kind} archive identity mismatch")
    app = blob[APP_FILE_OFFSET:]
    if len(app) != APP_END - APP_BASE:
        raise ComparisonError("EM9305 application record length changed")

    tools = {
        name: binutils_dir / f"arc-linux-gnu-{name}"
        for name in ("ar", "objcopy", "objdump", "readelf")
    }
    for name, executable in tools.items():
        if not executable.is_file():
            raise ComparisonError(f"ARC binutils {name} missing: {executable}")

    records = []
    compiler_comments = set()
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-sdk-qpc-") as temp_name:
        temp = Path(temp_name)
        run((str(tools["ar"]), "x", str(archive)), cwd=temp)
        objects = sorted(temp.glob("*.obj"))
        if not objects:
            raise ComparisonError("QP/C archive contains no extracted objects")
        section_cache: dict[tuple[Path, str], bytes] = {}
        for object_path in objects:
            symbol_table = run((str(tools["objdump"]), "-t", str(object_path)))
            relocation_table = run((str(tools["objdump"]), "-r", str(object_path)))
            relocations = parse_relocations(relocation_table)
            comment = subprocess.run(
                (str(tools["readelf"]), "-p", ".comment", str(object_path)),
                check=False,
                capture_output=True,
                text=True,
            ).stdout
            if comment:
                compiler_comments.add(comment.strip())

            for function in parse_functions(symbol_table):
                size = function["size"]
                if size == 0:
                    continue
                section = function["section"]
                key = (object_path, section)
                if key not in section_cache:
                    section_path = temp / (
                        f"section-{object_path.stem}-{sha256(section.encode())[:12]}.bin"
                    )
                    run((
                        str(tools["objcopy"]),
                        "--dump-section",
                        f"{section}={section_path}",
                        str(object_path),
                    ))
                    section_cache[key] = section_path.read_bytes()
                candidate, masked = normalized_body(
                    section_cache[key],
                    function["offset"],
                    size,
                    relocations.get(section, ()),
                )
                matches = find_normalized_matches(
                    app,
                    candidate,
                    masked,
                    minimum_compared_bytes=minimum_compared_bytes,
                )
                expected = EXPECTED_EXACT_MATCHES.get(archive_kind, {}).get(function["name"])
                expected_kind = "exact"
                if expected is None:
                    expected = EXPECTED_VENDOR_MODIFIED.get(archive_kind, {}).get(function["name"])
                    expected_kind = "vendor_modified" if expected is not None else None
                expected_matched = (
                    normalized_matches_at(app, candidate, masked, expected)
                    if expected is not None else None
                )
                records.append({
                    **function,
                    "object": object_path.name,
                    "relocation_count": sum(
                        1 for offset, _kind in relocations.get(section, ())
                        if function["offset"] <= offset < function["offset"] + size
                    ),
                    "masked_byte_count": len(masked),
                    "compared_byte_count": size - len(masked),
                    "normalized_sha256": sha256(candidate),
                    "matches": matches,
                    "expected_stock_address": expected,
                    "expected_match_kind": expected_kind,
                    "expected_address_matched": expected_matched,
                })

    comments = "\n".join(sorted(compiler_comments))
    compiler_anchors_matched = all(anchor in comments for anchor in COMPILER_COMMENT_ANCHORS)
    if enforce_known and not compiler_anchors_matched:
        raise ComparisonError("QP/C archive compiler identity anchors changed")
    records_by_name: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        records_by_name.setdefault(record["name"], []).append(record)
    for name, address in EXPECTED_EXACT_MATCHES.get(archive_kind, {}).items():
        candidates = records_by_name.get(name, ())
        if not any(
            record["expected_stock_address"] == address
            and record["expected_address_matched"]
            for record in candidates
        ):
            raise ComparisonError(
                f"expected exact {archive_kind} match missing: {name}@0x{address:08X}"
            )
    for name, address in EXPECTED_VENDOR_MODIFIED.get(archive_kind, {}).items():
        candidates = records_by_name.get(name, ())
        if not candidates or any(record["expected_address_matched"] for record in candidates):
            raise ComparisonError(
                f"expected vendor-modified {archive_kind} body changed: {name}@0x{address:08X}"
            )

    known = [record for record in records if record["expected_stock_address"] is not None]
    return {
        "identity": {
            "archive_kind": archive_kind,
            "archive_path": archive_identity["path"],
            "archive_git_blob": archive_identity["git_blob"],
            "archive_sha256": archive_identity["sha256"],
            "compiler": (
                "Synopsys MetaWare ARC Compiler T-2022.09 build 004 / LLVM 14.0.6 (EM-Micro)"
                if compiler_anchors_matched else "unresolved_from_required_anchors"
            ),
            "optimization": "-Os" if compiler_anchors_matched else "unresolved",
            "architecture": "ARCv2 EM",
            "compiler_comment_sha256": sha256(comments.encode()),
            "compiler_anchors_matched": compiler_anchors_matched,
        },
        "function_count": len(records),
        "known_function_count": len(known),
        "known_expected_address_match_count": sum(
            1 for record in known if record["expected_address_matched"]
        ),
        "expected_exact_match_count": len(EXPECTED_EXACT_MATCHES.get(archive_kind, {})),
        "expected_vendor_modified_count": len(EXPECTED_VENDOR_MODIFIED.get(archive_kind, {})),
        "unique_discovered_matches": [
            record for record in records
            if len(record["matches"]) == 1
        ],
        "functions": records,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument(
        "--archive-kind",
        default="qpc",
        help="known enforced kind or a discovery label paired with explicit identity options",
    )
    parser.add_argument("--archive-sha256")
    parser.add_argument("--archive-git-blob")
    parser.add_argument("--archive-source-path")
    parser.add_argument("--binutils-dir", type=Path, required=True)
    parser.add_argument("--minimum-compared-bytes", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.minimum_compared_bytes < 1:
        raise ComparisonError("minimum compared bytes must be positive")
    identity_override = None
    if args.archive_kind not in SDK_ARCHIVES:
        identity_override = {
            "path": args.archive_source_path or "",
            "git_blob": args.archive_git_blob or "",
            "sha256": args.archive_sha256 or "",
        }
    elif any((args.archive_sha256, args.archive_git_blob, args.archive_source_path)):
        raise ComparisonError("identity override options require a discovery archive kind")
    report = compare(
        args.image,
        args.archive,
        args.binutils_dir,
        archive_kind=args.archive_kind,
        minimum_compared_bytes=args.minimum_compared_bytes,
        archive_identity_override=identity_override,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"EM9305 SDK {args.archive_kind} archive comparison: PASS")
        print(json.dumps({
            "function_count": report["function_count"],
            "known_function_count": report["known_function_count"],
            "known_expected_address_match_count": report["known_expected_address_match_count"],
            "unique_discovered_match_count": len(report["unique_discovered_matches"]),
        }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
