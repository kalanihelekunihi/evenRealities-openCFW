#!/usr/bin/env python3
"""Audit the next G2 FreeRTOS queue-creation wrapper tranche.

This tool is deliberately read-only.  It authenticates the official
2.2.6.10 Apollo-main image and the pinned FreeRTOS-Kernel V10.5.1 queue
source, verifies three complete public wrapper bodies, scans the full
application for branch and stored-pointer references, and confirms that
their queue dependencies are already source-owned by the production
overlay.  It has no device, serial, signing, or flash-programming path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
PACKAGE_PREAMBLE_SIZE = 32
APPLICATION_BASE = 0x0043_8000
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_QUEUE_SIZE = 125_614
UPSTREAM_QUEUE_SHA256 = (
    "5cdf4fa35fe059446effff5bf20deaf83"
    "ddffb08921bc198fda106b1d17dd894"
)
UPSTREAM_QUEUE_GIT_BLOB = "5c872e0302839d96aab90919788fdc2b0be1c09e"

ASSERT_FAIL = 0x005F_A0A4
GENERIC_CREATE_STATIC = 0x0044_15CA
GENERIC_CREATE_DYNAMIC = 0x0044_1636
INITIALISE_MUTEX = 0x0044_16B8

FUNCTIONS: dict[str, dict[str, Any]] = {
    "xQueueCreateMutexStatic": {
        "start": 0x0044_16F0,
        "end": 0x0044_1710,
        "bytes": bytes.fromhex(
            "1cb50b0001240021c0b2009000222000"
            "fff763ff04002000fff7d6ff200016bd"
        ),
        "sha256": (
            "2977000da7aab5b87abce1270dca651"
            "8785de04a1e72d08082802713d478fd28"
        ),
        "callers": [0x0043_C7DE, 0x0044_9778, 0x0044_9784],
        "caller_sha256": (
            "18956e929d4db6cfb12a062fedc6d049"
            "16549fe51dcca21ff4aca45ba1c72784"
        ),
        "outgoing_calls": [
            {"address": 0x0044_1700, "target": GENERIC_CREATE_STATIC},
            {"address": 0x0044_1708, "target": INITIALISE_MUTEX},
        ],
        "source_block_size": 643,
        "source_block_sha256": (
            "790cfc1e7f21e0f961b35020ea6f47ce"
            "0d9d147b2370be4c1620787b2a3d4c0f"
        ),
    },
    "xQueueCreateCountingSemaphoreStatic": {
        "start": 0x0044_1790,
        "end": 0x0044_17C2,
        "bytes": bytes.fromhex(
            "1cb50c001300002100280bd0a04209d3"
            "0221009100220021fff70fff002800d0"
            "846316bdb8f176fc00205ff0ff310860"
            "fee7"
        ),
        "sha256": (
            "a46100f23dd51b8276a4c2ebafa1ba96"
            "c6813114810ae0f5297764c20368eb62"
        ),
        "callers": [0x0044_9938, 0x0044_9CCA],
        "caller_sha256": (
            "5002b370782bf8b3f503055d7c11af76"
            "30622fe21b3858cd9cbe74b42f9d2873"
        ),
        "outgoing_calls": [
            {"address": 0x0044_17A8, "target": GENERIC_CREATE_STATIC},
            {"address": 0x0044_17B4, "target": ASSERT_FAIL},
        ],
        "source_block_size": 1_024,
        "source_block_sha256": (
            "47ec21550eaab3b4f847f2e803ec67fd"
            "8804bacb02cfdeb3d2e0fc0421c94f36"
        ),
    },
    "xQueueCreateCountingSemaphore": {
        "start": 0x0044_17C2,
        "end": 0x0044_17EE,
        "bytes": bytes.fromhex(
            "10b50c000021002809d0a04207d30222"
            "0021fff72fff002800d0846310bdb8f1"
            "60fc00205ff0ff310860fee7"
        ),
        "sha256": (
            "ed30ebca04b655b1ec31e60296d977382"
            "d0712057db88f99b205a555b374120f"
        ),
        "callers": [0x0044_9944],
        "caller_sha256": (
            "2a96b89cb1e27e8aa093eafe45e2990e"
            "706084ea8d179689b1c61c66ed925bad"
        ),
        "outgoing_calls": [
            {"address": 0x0044_17D4, "target": GENERIC_CREATE_DYNAMIC},
            {"address": 0x0044_17E0, "target": ASSERT_FAIL},
        ],
        "source_block_size": 898,
        "source_block_sha256": (
            "c20b22c99a49745040aa25673f39b1ee"
            "e8831b790011b8ae18f47fce674e1802"
        ),
    },
}

ORDERED_TRANCHE_SHA256 = (
    "1d305cd5e6313c35b3489f26b310b416"
    "1252543b882bc6c62e9c55d567523460"
)

BOUNDARIES = {
    "predecessor_dynamic_mutex": {
        "start": 0x0044_16D6,
        "end": 0x0044_16F0,
        "sha256": (
            "fd3801ca9d39f700a0c4dc5598707c4"
            "dd9c6efd75ec8c25d432e7ef29c15eddf"
        ),
    },
    "recursive_mutex_give": {
        "start": 0x0044_1710,
        "end": 0x0044_1750,
        "sha256": (
            "ba48b7e573af0899510fa67e97d7127b"
            "06f55015f5aeb951fb834f94d44ec1c9"
        ),
    },
    "recursive_mutex_take": {
        "start": 0x0044_1750,
        "end": 0x0044_1790,
        "sha256": (
            "08842b983b428e0e38c484385f62d27b"
            "6c50719ce1028019a36c343b4ccdc726"
        ),
    },
    "successor_generic_send_prefix": {
        "start": 0x0044_17EE,
        "end": 0x0044_1810,
        "sha256": (
            "ea3a9434f23c3dadb07815859e3ebe84"
            "fe83b99e51c40f64d9832729e8a819b5"
        ),
    },
}

SOURCE_OWNED_DEPENDENCIES = {
    GENERIC_CREATE_STATIC: {
        "function": "open_cfw_freertos_queue_generic_create_static",
        "redirect_name": "replace_freertos_queue_generic_create_static",
        "size": 108,
    },
    GENERIC_CREATE_DYNAMIC: {
        "function": "open_cfw_freertos_queue_generic_create",
        "redirect_name": "replace_freertos_queue_generic_create",
        "size": 96,
    },
    INITIALISE_MUTEX: {
        "function": "open_cfw_freertos_queue_initialise_mutex",
        "redirect_name": "replace_freertos_queue_initialise_mutex",
        "size": 30,
    },
}


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data, usedforsecurity=False).hexdigest()


def image_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or first >= last or last > len(application):
        raise AuditError(
            f"span [0x{start:08X},0x{end:08X}) is outside the application"
        )
    return application[first:last]


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    """Decode a Thumb-2 BL or unconditional B.W immediate target."""

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
    """Return targets for narrow B/Bcc/CBZ/CBNZ encodings."""

    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


def extract_source_function(text: str, function_name: str) -> bytes:
    marker = f"    QueueHandle_t {function_name}("
    try:
        start = text.index(marker)
        opening = text.index("{", start)
    except ValueError as error:
        raise AuditError(
            f"upstream queue.c is missing {function_name}"
        ) from error
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1].encode("utf-8")
    raise AuditError(f"upstream {function_name} has an unterminated body")


def verify_upstream_source() -> dict[str, Any]:
    data = UPSTREAM_QUEUE.read_bytes()
    if len(data) != UPSTREAM_QUEUE_SIZE:
        raise AuditError("FreeRTOS queue.c size drift")
    if sha256(data) != UPSTREAM_QUEUE_SHA256:
        raise AuditError("FreeRTOS queue.c SHA-256 drift")
    if git_blob_sha1(data) != UPSTREAM_QUEUE_GIT_BLOB:
        raise AuditError("FreeRTOS queue.c Git blob drift")

    text = data.decode("utf-8")
    blocks: dict[str, dict[str, Any]] = {}
    for name, expected in FUNCTIONS.items():
        block = extract_source_function(text, name)
        if len(block) != expected["source_block_size"]:
            raise AuditError(f"upstream {name} source-block size drift")
        if sha256(block) != expected["source_block_sha256"]:
            raise AuditError(f"upstream {name} source-block SHA-256 drift")
        blocks[name] = {
            "size": len(block),
            "sha256": sha256(block),
        }

    required = (
        "#define queueSEMAPHORE_QUEUE_ITEM_LENGTH",
        "xQueueGenericCreateStatic( uxMutexLength, uxMutexSize, NULL, pxStaticQueue, ucQueueType )",
        "xQueueGenericCreateStatic( uxMaxCount, queueSEMAPHORE_QUEUE_ITEM_LENGTH, NULL, pxStaticQueue, queueQUEUE_TYPE_COUNTING_SEMAPHORE )",
        "xQueueGenericCreate( uxMaxCount, queueSEMAPHORE_QUEUE_ITEM_LENGTH, queueQUEUE_TYPE_COUNTING_SEMAPHORE )",
        "( ( Queue_t * ) xHandle )->uxMessagesWaiting = uxInitialCount;",
        "configASSERT( xHandle );",
    )
    for fragment in required:
        if fragment not in text:
            raise AuditError(
                f"FreeRTOS queue.c is missing released fragment {fragment!r}"
            )

    return {
        "version": "FreeRTOS-Kernel V10.5.1",
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
        "file": str(UPSTREAM_QUEUE.relative_to(ROOT)),
        "size": len(data),
        "sha256": sha256(data),
        "git_blob": git_blob_sha1(data),
        "license": "MIT",
        "function_blocks": blocks,
    }


def verify_source_owned_dependencies() -> dict[str, Any]:
    try:
        config = json.loads(OVERLAY_CONFIG.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise AuditError("could not read Apollo-main overlay config") from error

    functions = set(config.get("functions", []))
    redirects = {
        redirect.get("runtime_address"): redirect
        for redirect in config.get("patch_sites", [])
    }
    result: list[dict[str, Any]] = []
    for address, expected in SOURCE_OWNED_DEPENDENCIES.items():
        if expected["function"] not in functions:
            raise AuditError(
                f"source-owned function {expected['function']} is absent"
            )
        redirect = redirects.get(address)
        if redirect is None:
            raise AuditError(
                f"source redirect for 0x{address:08X} is absent"
            )
        for key, wanted in (
            ("name", expected["redirect_name"]),
            ("target_function", expected["function"]),
            ("expected_size", expected["size"]),
            ("branch", "b_w"),
        ):
            if redirect.get(key) != wanted:
                raise AuditError(
                    f"source redirect for 0x{address:08X} has {key} drift"
                )
        result.append(
            {
                "official_entry": address,
                "function": expected["function"],
                "redirect_name": expected["redirect_name"],
                "redirect_branch": "b_w",
                "status": "source-owned",
            }
        )

    return {
        "config": str(OVERLAY_CONFIG.relative_to(ROOT)),
        "queue_dependencies": result,
        "all_queue_dependencies_source_owned": True,
        "remaining_non_queue_dependency": {
            "entry": ASSERT_FAIL,
            "role": "reviewed configASSERT fail-stop port seam",
            "used_by": [
                "xQueueCreateCountingSemaphoreStatic",
                "xQueueCreateCountingSemaphore",
            ],
        },
    }


def scan_references(
    application: bytes,
    function_name: str,
    start: int,
    end: int,
) -> dict[str, Any]:
    direct_bl: list[dict[str, int | str]] = []
    direct_bw: list[dict[str, int | str]] = []
    external_interior_wide: list[dict[str, int | str]] = []
    external_entry_or_interior_narrow: list[dict[str, int | str]] = []
    stored: list[dict[str, int | str]] = []

    for offset in range(0, len(application) - 3, 2):
        address = APPLICATION_BASE + offset
        first, second = struct.unpack_from("<HH", application, offset)
        encoding = application[offset : offset + 4].hex()
        for link, collection, kind in (
            (True, direct_bl, "BL"),
            (False, direct_bw, "B.W"),
        ):
            target = thumb_wide_branch_target(
                address,
                first,
                second,
                link=link,
            )
            if target is None:
                continue
            if target == start and not start <= address < end:
                collection.append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": encoding,
                    }
                )
            if start < target < end and not start <= address < end:
                external_interior_wide.append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": encoding,
                        "kind": kind,
                    }
                )

    for offset in range(0, len(application) - 1, 2):
        address = APPLICATION_BASE + offset
        halfword = struct.unpack_from("<H", application, offset)[0]
        for target in narrow_branch_targets(address, halfword):
            if start <= target < end and not start <= address < end:
                external_entry_or_interior_narrow.append(
                    {
                        "address": address,
                        "target": target,
                        "encoding": f"{halfword:04x}",
                    }
                )

    for offset in range(0, len(application) - 3):
        value = struct.unpack_from("<I", application, offset)[0]
        canonical = value & ~1
        if start <= canonical < end:
            stored.append(
                {
                    "address": APPLICATION_BASE + offset,
                    "value": value,
                    "canonical": canonical,
                    "kind": "entry" if canonical == start else "interior",
                }
            )

    expected = FUNCTIONS[function_name]
    caller_addresses = [int(item["address"]) for item in direct_bl]
    packed = b"".join(
        struct.pack("<I", address) for address in caller_addresses
    )
    if caller_addresses != expected["callers"]:
        raise AuditError(f"{function_name} direct caller topology drift")
    if sha256(packed) != expected["caller_sha256"]:
        raise AuditError(f"{function_name} caller-list SHA-256 drift")
    if (
        direct_bw
        or external_interior_wide
        or external_entry_or_interior_narrow
        or stored
    ):
        raise AuditError(f"{function_name} non-BL reference topology drift")

    return {
        "direct_bl_count": len(direct_bl),
        "direct_bl": direct_bl,
        "direct_bl_callsite_sha256": sha256(packed),
        "direct_bw": direct_bw,
        "external_interior_wide": external_interior_wide,
        "external_entry_or_interior_narrow": (
            external_entry_or_interior_narrow
        ),
        "stored_entry_or_interior": stored,
    }


def verify_outgoing_calls(
    application: bytes,
    function_name: str,
    start: int,
    end: int,
) -> list[dict[str, int | str]]:
    calls: list[dict[str, int | str]] = []
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    for offset in range(first, last - 3, 2):
        address = APPLICATION_BASE + offset
        halfword_a, halfword_b = struct.unpack_from(
            "<HH",
            application,
            offset,
        )
        target = thumb_wide_branch_target(
            address,
            halfword_a,
            halfword_b,
            link=True,
        )
        if target is not None:
            calls.append(
                {
                    "address": address,
                    "target": target,
                    "encoding": application[offset : offset + 4].hex(),
                }
            )
    expected = FUNCTIONS[function_name]["outgoing_calls"]
    observed_pairs = [
        {"address": item["address"], "target": item["target"]}
        for item in calls
    ]
    if observed_pairs != expected:
        raise AuditError(f"{function_name} outgoing call topology drift")
    return calls


def verify_boundaries(application: bytes) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, expected in BOUNDARIES.items():
        data = image_slice(
            application,
            expected["start"],
            expected["end"],
        )
        if sha256(data) != expected["sha256"]:
            raise AuditError(f"{name} boundary SHA-256 drift")
        result[name] = {
            "start": expected["start"],
            "end_exclusive": expected["end"],
            "size": len(data),
            "sha256": sha256(data),
        }
    return result


def verify_application(package: bytes) -> bytes:
    if len(package) != PACKAGE_SIZE:
        raise AuditError("package size drift")
    if sha256(package) != PACKAGE_SHA256:
        raise AuditError("package SHA-256 drift")
    application = package[PACKAGE_PREAMBLE_SIZE:]
    if sha256(application) != APPLICATION_SHA256:
        raise AuditError("installed application SHA-256 drift")
    return application


def run_audit(image_path: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    package = image_path.read_bytes()
    application = verify_application(package)
    upstream = verify_upstream_source()
    dependency_closure = verify_source_owned_dependencies()
    boundaries = verify_boundaries(application)

    functions: dict[str, Any] = {}
    tranche = bytearray()
    for name, expected in FUNCTIONS.items():
        data = image_slice(application, expected["start"], expected["end"])
        if data != expected["bytes"]:
            raise AuditError(f"{name} exact bytes drift")
        if sha256(data) != expected["sha256"]:
            raise AuditError(f"{name} SHA-256 drift")
        tranche.extend(data)
        functions[name] = {
            "start": expected["start"],
            "end_exclusive": expected["end"],
            "size": len(data),
            "sha256": sha256(data),
            "abi": (
                {
                    "r0": "uint8_t mutex type (low eight bits)",
                    "r1": "StaticQueue_t *",
                    "return_r0": "QueueHandle_t or null",
                }
                if name == "xQueueCreateMutexStatic"
                else {
                    "r0": "UBaseType_t maximum count",
                    "r1": "UBaseType_t initial count",
                    **(
                        {"r2": "StaticQueue_t *"}
                        if name.endswith("Static")
                        else {}
                    ),
                    "return_r0": "QueueHandle_t or null",
                }
            ),
            "semantics": (
                [
                    "create length-one, zero-item queue with caller mutex type",
                    "initialise mutex ownership and available-token state",
                    "return the static control block handle",
                ]
                if name == "xQueueCreateMutexStatic"
                else [
                    "require maximum count nonzero",
                    "require initial count <= maximum count (unsigned)",
                    (
                        "create static zero-item queue with type 2"
                        if name.endswith("Static")
                        else "create dynamic zero-item queue with type 2"
                    ),
                    "write initial count to Queue_t + 0x38 on success",
                    "return null unchanged if creator returns null",
                ]
            ),
            "outgoing_calls": verify_outgoing_calls(
                application,
                name,
                expected["start"],
                expected["end"],
            ),
            "references": scan_references(
                application,
                name,
                expected["start"],
                expected["end"],
            ),
        }

    if len(tranche) != 126:
        raise AuditError("ordered wrapper tranche size drift")
    if sha256(bytes(tranche)) != ORDERED_TRANCHE_SHA256:
        raise AuditError("ordered wrapper tranche SHA-256 drift")

    return {
        "status": "ok",
        "read_only": True,
        "scope": "official G2 Apollo-main 2.2.6.10",
        "image": {
            "path": str(image_path),
            "package_size": len(package),
            "package_sha256": sha256(package),
            "preamble_size": PACKAGE_PREAMBLE_SIZE,
            "application_base": APPLICATION_BASE,
            "application_size": len(application),
            "application_sha256": sha256(application),
        },
        "upstream": upstream,
        "functions": functions,
        "ordered_tranche": {
            "functions": list(FUNCTIONS),
            "total_size": len(tranche),
            "sha256": sha256(bytes(tranche)),
        },
        "boundaries": boundaries,
        "configuration": {
            "configUSE_MUTEXES": 1,
            "configUSE_COUNTING_SEMAPHORES": 1,
            "configSUPPORT_STATIC_ALLOCATION": 1,
            "configSUPPORT_DYNAMIC_ALLOCATION": 1,
            "configASSERT": "enabled; invalid counting dimensions fail-stop",
            "configUSE_TRACE_FACILITY": 1,
            "trace_wrapper_hooks": "empty in the official build",
            "mtCOVERAGE_TEST_MARKER": "empty in the official build",
            "queueSEMAPHORE_QUEUE_ITEM_LENGTH": 0,
            "queueQUEUE_TYPE_COUNTING_SEMAPHORE": 2,
            "Queue_t.messages_waiting_offset": 0x38,
            "StaticQueue_t_size": 0x50,
            "UBaseType_t_bits": 32,
            "pointer_bits": 32,
        },
        "dependency_closure": dependency_closure,
        "ownership_assessment": {
            "unequivocal_public_source": True,
            "source": "FreeRTOS-Kernel V10.5.1 queue.c",
            "mutex_wrapper_queue_dependencies_source_owned": True,
            "counting_wrapper_queue_dependencies_source_owned": True,
            "source_ownable": True,
            "remaining_port_seam": ASSERT_FAIL,
            "atomic_recommendation": [
                (
                    "promote xQueueCreateMutexStatic first as a zero-new-seam "
                    "wrapper over source-owned dependencies"
                ),
                (
                    "promote both counting-semaphore wrappers together; they "
                    "share validation, type, count-field, and assertion ABI"
                ),
                (
                    "a single three-wrapper promotion is safe if the existing "
                    "assertion seam is retained and package gates pass"
                ),
            ],
        },
        "limitations": [
            "offline static audit only",
            "no hardware, serial, signing, or flash operation",
            "the assertion port entry remains a reviewed official seam",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image",
        type=Path,
        default=DEFAULT_IMAGE,
        help="official G2 Apollo-main OTA image",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable audit",
    )
    arguments = parser.parse_args()

    result = run_audit(arguments.image)
    if arguments.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("FreeRTOS queue wrapper tranche audit: ok")
        print(
            "  wrappers: "
            f"{result['ordered_tranche']['total_size']} authenticated bytes"
        )
        print(
            "  queue dependencies: source-owned; retained assertion seam: "
            f"0x{ASSERT_FAIL:08X}"
        )
        print("  mode: read-only/offline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
