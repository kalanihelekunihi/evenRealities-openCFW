#!/usr/bin/env python3
"""Audit the linked CMSIS-FreeRTOS wrapper tranche in G2 2.2.6.10.

The official image contains a compact, smart-linked subset of Arm's
``cmsis_os2.c``.  This read-only analyzer pins every admitted body, the three
literal pools that make the physical object contiguous, and all direct/stored
entry topology.  It does not modify or build firmware.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
DEFAULT_SOURCE = (
    OPENCFW_ROOT
    / "third_party"
    / "cmsis-freertos"
    / "CMSIS-FreeRTOS"
    / "CMSIS"
    / "RTOS2"
    / "FreeRTOS"
    / "Source"
    / "cmsis_os2.c"
)
FUNCTION_MAP = (
    OPENCFW_ROOT
    / "tools"
    / "manifests"
    / "cmsis-freertos-v10.5.1-linked-function-map.tsv"
)

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
PACKAGE_PREAMBLE = 32
APPLICATION_BASE = 0x0043_8000

SOURCE_SIZE = 70_106
SOURCE_SHA256 = "8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36"
SOURCE_GIT_BLOB = "88dca1d881f1a960872572a8a0efd94cde19dcea"

PHYSICAL_START = 0x0044_900E
PHYSICAL_END = 0x0044_9ED2
PHYSICAL_SHA256 = "4213db1407beb89f59deb37d585df874a0fc37939ffb8e16b0f3de2c9c22225a"
FUNCTION_BYTES = 3_758
LITERAL_BYTES = 22

TOTAL_DIRECT_BL = 872
EXTERNAL_DIRECT_BL = 831
INTERNAL_DIRECT_BL = 41
DIRECT_BL_PAIR_SHA256 = "50b0b3b198afa541b8371158f8ec9884ea858a1fe996c95588a6fbb6a31bba98"

SELECTED_TAG = "v10.5.1"
SELECTED_TAG_OBJECT = "34e6e4c403c17de35ec0acf29610e374dc938604"
SELECTED_COMMIT = "d213f261b5be6bb29a7cce8b84071706b72f4d53"
SELECTED_TREE = "d3689a816acc77a3f0b7d35439d666ad8434b6ba"
SOURCE_BLOB_INTRODUCED_COMMIT = "13acfbef7be85119fc6bc56832c455d4547d92c7"
LINKED_BEHAVIOR_LOWER_COMMIT = "600ba38a66b38105817bd7351be6f6718cd1c2be"
NEXT_EXCLUDED_LINKED_CHANGE = "bb8a350a84567e5a000020abfbd6ab45ea9f6b46"


class AuditError(RuntimeError):
    """Raised when a pinned input or topology invariant changes."""


@dataclass(frozen=True)
class Function:
    name: str
    start: int
    end: int
    size: int
    sha256: str
    external_callers: int
    classification: str


@dataclass(frozen=True)
class Gap:
    name: str
    start: int
    end: int
    sha256: str


GAPS = (
    Gap(
        "event_flags_literal_pool",
        0x0044_9694,
        0x0044_969C,
        "0b91bcd98339871a7aa4985246254aa8d919507ebf4b9af37d613eb5ed9177dd",
    ),
    Gap(
        "timer_callback_literal",
        0x0044_9DD0,
        0x0044_9DD4,
        "9d023b7228d30ccf1a0dd1ba172ac9da8af03286e4d1b3bc14696f60d03ee45d",
    ),
    Gap(
        "memory_pool_literal_pool",
        0x0044_9E8E,
        0x0044_9E98,
        "a0ed70e0edd384aa9afd59b0672e5cdf8d6d53bd8b9bba3b9335b6cc58768edb",
    ),
)

DEAD_STRIPPED_APIS = (
    "osDelayUntil",
    "osEventFlagsDelete",
    "osEventFlagsGet",
    "osKernelGetInfo",
    "osKernelGetSysTimerCount",
    "osKernelGetSysTimerFreq",
    "osKernelGetTickFreq",
    "osKernelLock",
    "osKernelRestoreLock",
    "osKernelUnlock",
    "osMemoryPoolDelete",
    "osMemoryPoolGetBlockSize",
    "osMemoryPoolGetCapacity",
    "osMemoryPoolGetCount",
    "osMemoryPoolGetName",
    "osMemoryPoolGetSpace",
    "osMessageQueueGetMsgSize",
    "osMessageQueueGetSpace",
    "osMessageQueueReset",
    "osMutexGetOwner",
    "osSemaphoreDelete",
    "osThreadEnumerate",
    "osThreadExit",
    "osThreadFlagsClear",
    "osThreadFlagsGet",
    "osThreadGetCount",
    "osThreadGetName",
    "osThreadGetPriority",
    "osThreadGetStackSpace",
    "osThreadGetState",
    "osThreadResume",
    "osThreadSuspend",
    "osTimerGetName",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def application_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or first >= last or last > len(application):
        raise AuditError(f"span [0x{start:08X},0x{end:08X}) is outside image")
    return application[first:last]


def load_function_map(path: Path = FUNCTION_MAP) -> tuple[Function, ...]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = tuple(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != 43:
        raise AuditError(f"linked function map has {len(rows)} rows, expected 43")
    functions: list[Function] = []
    for row in rows:
        start = int(row["start"], 0)
        end = int(row["end_exclusive"], 0)
        size = int(row["bytes"], 0)
        if end - start != size:
            raise AuditError(f"{row['function']} map size is inconsistent")
        functions.append(
            Function(
                row["function"],
                start,
                end,
                size,
                row["sha256"],
                int(row["external_bl_callers"], 0),
                row["classification"],
            )
        )
    if len({item.name for item in functions}) != len(functions):
        raise AuditError("linked function map contains duplicate names")
    if len({item.start for item in functions}) != len(functions):
        raise AuditError("linked function map contains duplicate starts")
    return tuple(functions)


def thumb_wide_branch_target(
    address: int, first: int, second: int, *, link: bool
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return (address + 4 + immediate * 2,)
    return ()


def verify_partition(functions: tuple[Function, ...]) -> None:
    regions = sorted(
        [(item.start, item.end, item.name) for item in functions]
        + [(item.start, item.end, item.name) for item in GAPS]
    )
    cursor = PHYSICAL_START
    for start, end, name in regions:
        if start != cursor:
            raise AuditError(
                f"physical partition changed before {name}: "
                f"0x{cursor:08X} != 0x{start:08X}"
            )
        cursor = end
    if cursor != PHYSICAL_END:
        raise AuditError(f"physical partition ends at 0x{cursor:08X}")
    if sum(item.size for item in functions) != FUNCTION_BYTES:
        raise AuditError("linked function byte total changed")
    if sum(item.end - item.start for item in GAPS) != LITERAL_BYTES:
        raise AuditError("linked literal byte total changed")


def verify_source(source: bytes, functions: tuple[Function, ...]) -> None:
    if len(source) != SOURCE_SIZE or digest(source) != SOURCE_SHA256:
        raise AuditError("authenticated CMSIS-FreeRTOS source identity changed")
    text = source.decode("utf-8")
    for item in functions:
        if item.name not in text:
            raise AuditError(f"upstream source no longer contains {item.name}")
    for name in DEAD_STRIPPED_APIS:
        if name not in text:
            raise AuditError(f"dead-stripped upstream API marker missing: {name}")

    # These three changes first landed together in upstream commit 600ba38a.
    # They distinguish the linked G2 behavior from release v10.4.6.
    required = (
        "else if ((hTimer == NULL) || (ticks == 0U))",
        "rflags  = xEventGroupGetBitsFromISR (hEventGroup);",
        "rflags = (uint32_t)osFlagsErrorParameter;",
    )
    for marker in required:
        if marker not in text:
            raise AuditError(f"v10.5.1 source discriminator missing: {marker}")


def verify_function_bytes(
    application: bytes, functions: tuple[Function, ...]
) -> None:
    for item in functions:
        body = application_slice(application, item.start, item.end)
        if len(body) != item.size or digest(body) != item.sha256:
            raise AuditError(f"stock body changed: {item.name}")
    for gap in GAPS:
        if digest(application_slice(application, gap.start, gap.end)) != gap.sha256:
            raise AuditError(f"stock literal pool changed: {gap.name}")
    physical = application_slice(application, PHYSICAL_START, PHYSICAL_END)
    if len(physical) != FUNCTION_BYTES + LITERAL_BYTES:
        raise AuditError("physical CMSIS-FreeRTOS object size changed")
    if digest(physical) != PHYSICAL_SHA256:
        raise AuditError("physical CMSIS-FreeRTOS object identity changed")

    if application_slice(application, 0x0044_94B0, 0x0044_94B2) != b"\x00\x2c":
        raise AuditError("osTimerStart no longer rejects zero ticks")
    first, second = struct.unpack(
        "<HH", application_slice(application, 0x0044_961C, 0x0044_9620)
    )
    if thumb_wide_branch_target(0x0044_961C, first, second, link=True) != 0x0047_ED64:
        raise AuditError("osEventFlagsSet lost the ISR get-bits call")
    if application_slice(application, 0x0044_9620, 0x0044_9622) != b"\x05\x43":
        raise AuditError("osEventFlagsSet lost the ISR existing-bits OR")
    if application_slice(application, 0x0044_96BE, 0x0044_96CE) != bytes.fromhex(
        "002c02d17ff0050028e07ff0030025e0"
    ):
        raise AuditError("osEventFlagsWait ISR timeout discriminator changed")


def scan_references(
    application: bytes, functions: tuple[Function, ...]
) -> dict[str, object]:
    starts = {item.start: item for item in functions}
    calls: dict[int, list[int]] = {start: [] for start in starts}
    external_interior_wide: list[tuple[int, int, str]] = []
    external_interior_narrow: list[tuple[int, int]] = []

    for offset in range(0, len(application) - 3, 2):
        address = APPLICATION_BASE + offset
        first, second = struct.unpack_from("<HH", application, offset)
        for link, kind in ((True, "BL"), (False, "B.W")):
            target = thumb_wide_branch_target(address, first, second, link=link)
            if target is None:
                continue
            if link and target in starts:
                calls[target].append(address)
            if (
                PHYSICAL_START <= target < PHYSICAL_END
                and target not in starts
                and not PHYSICAL_START <= address < PHYSICAL_END
            ):
                external_interior_wide.append((address, target, kind))

    for offset in range(0, len(application) - 1, 2):
        address = APPLICATION_BASE + offset
        if PHYSICAL_START <= address < PHYSICAL_END:
            continue
        halfword = struct.unpack_from("<H", application, offset)[0]
        for target in narrow_branch_targets(address, halfword):
            if PHYSICAL_START <= target < PHYSICAL_END and target not in starts:
                external_interior_narrow.append((address, target))

    pairs = sorted((target, site) for target, sites in calls.items() for site in sites)
    pair_bytes = "".join(
        f"{target:08x}:{site:08x}\n" for target, site in pairs
    ).encode("ascii")
    if len(pairs) != TOTAL_DIRECT_BL or digest(pair_bytes) != DIRECT_BL_PAIR_SHA256:
        raise AuditError("CMSIS-FreeRTOS direct-BL topology changed")

    external_count = 0
    internal_count = 0
    for item in functions:
        external = [
            site
            for site in calls[item.start]
            if not PHYSICAL_START <= site < PHYSICAL_END
        ]
        internal = [
            site for site in calls[item.start] if PHYSICAL_START <= site < PHYSICAL_END
        ]
        if len(external) != item.external_callers:
            raise AuditError(f"external caller count changed: {item.name}")
        external_count += len(external)
        internal_count += len(internal)
    if external_count != EXTERNAL_DIRECT_BL or internal_count != INTERNAL_DIRECT_BL:
        raise AuditError("CMSIS-FreeRTOS external/internal call totals changed")
    if external_interior_wide or external_interior_narrow:
        raise AuditError("external control flow enters a CMSIS function interior")

    aligned_stored: list[tuple[int, int]] = []
    for offset in range(0, len(application) - 3, 4):
        value = struct.unpack_from("<I", application, offset)[0]
        canonical = value & ~1
        if value & 1 and canonical in starts:
            aligned_stored.append((APPLICATION_BASE + offset, canonical))
    if aligned_stored != [(0x0044_9DD0, 0x0044_9398)]:
        raise AuditError("aligned CMSIS-FreeRTOS stored-entry topology changed")

    return {
        "direct_bl_total": len(pairs),
        "external_direct_bl": external_count,
        "internal_direct_bl": internal_count,
        "direct_bl_pair_sha256": digest(pair_bytes),
        "external_interior_wide": [],
        "external_interior_narrow": [],
        "aligned_stored_entries": [
            {"word_address": f"0x{site:08X}", "target": f"0x{target:08X}"}
            for site, target in aligned_stored
        ],
    }


def audit(image_path: Path = DEFAULT_IMAGE, source_path: Path = DEFAULT_SOURCE) -> dict:
    package = image_path.read_bytes()
    if len(package) != PACKAGE_SIZE or digest(package) != PACKAGE_SHA256:
        raise AuditError("official G2 package identity changed")
    application = package[PACKAGE_PREAMBLE:]
    source = source_path.read_bytes()
    functions = load_function_map()

    verify_partition(functions)
    verify_source(source, functions)
    verify_function_bytes(application, functions)
    references = scan_references(application, functions)

    return {
        "package": {
            "path": str(image_path),
            "bytes": len(package),
            "sha256": digest(package),
        },
        "upstream": {
            "repository": "https://github.com/ARM-software/CMSIS-FreeRTOS",
            "selected_tag": SELECTED_TAG,
            "selected_tag_object": SELECTED_TAG_OBJECT,
            "selected_commit": SELECTED_COMMIT,
            "selected_tree": SELECTED_TREE,
            "cmsis_os2_git_blob": SOURCE_GIT_BLOB,
            "cmsis_os2_sha256": SOURCE_SHA256,
            "source_blob_introduced_commit": SOURCE_BLOB_INTRODUCED_COMMIT,
            "linked_behavior_lower_commit": LINKED_BEHAVIOR_LOWER_COMMIT,
            "next_excluded_linked_change": NEXT_EXCLUDED_LINKED_CHANGE,
            "historical_checkout_status": (
                "v10.5.1 is the selected exact release and joint FreeRTOS/CMSIS "
                "fit; linked behavior alone proves a bounded source interval, "
                "not Even's exact checkout"
            ),
        },
        "linked_object": {
            "start": f"0x{PHYSICAL_START:08X}",
            "end_exclusive": f"0x{PHYSICAL_END:08X}",
            "bytes": PHYSICAL_END - PHYSICAL_START,
            "sha256": PHYSICAL_SHA256,
            "function_count": len(functions),
            "public_api_count": sum(
                item.classification == "public CMSIS-RTOS2 API" for item in functions
            ),
            "function_bytes": FUNCTION_BYTES,
            "literal_pool_bytes": LITERAL_BYTES,
            "functions": [
                {
                    "name": item.name,
                    "start": f"0x{item.start:08X}",
                    "end_exclusive": f"0x{item.end:08X}",
                    "bytes": item.size,
                    "sha256": item.sha256,
                    "external_bl_callers": item.external_callers,
                    "classification": item.classification,
                }
                for item in functions
            ],
            "literal_pools": [
                {
                    "name": gap.name,
                    "start": f"0x{gap.start:08X}",
                    "end_exclusive": f"0x{gap.end:08X}",
                    "bytes": gap.end - gap.start,
                    "sha256": gap.sha256,
                }
                for gap in GAPS
            ],
        },
        "topology": references,
        "dead_stripped": {
            "public_api_count": len(DEAD_STRIPPED_APIS),
            "public_apis": list(DEAD_STRIPPED_APIS),
        },
        "version_discriminators": {
            "v10_4_6_excluded": [
                "osTimerStart rejects ticks == 0",
                "osEventFlagsSet ISR path retrieves and ORs existing bits",
                "osEventFlagsWait distinguishes zero/nonzero ISR timeout",
            ],
            "post_bb8a350_excluded": (
                "stock osThreadFlagsWait lacks the later re-notification repair"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = audit(args.image, args.source)
    except (AuditError, OSError, ValueError, KeyError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        linked = report["linked_object"]
        topology = report["topology"]
        print(
            "PASS CMSIS-FreeRTOS linked census: "
            f"{linked['function_count']} functions / {linked['function_bytes']} code bytes, "
            f"{linked['literal_pool_bytes']} literal bytes, "
            f"{topology['external_direct_bl']} external BL callers"
        )
        print(
            "PASS selected upstream: v10.5.1 commit "
            f"{SELECTED_COMMIT}; exact source blob introduced by "
            f"{SOURCE_BLOB_INTRODUCED_COMMIT}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
