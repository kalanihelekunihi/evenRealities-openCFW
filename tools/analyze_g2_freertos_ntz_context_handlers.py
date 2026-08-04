#!/usr/bin/env python3
"""Read-only audit of the G2 FreeRTOS NTZ context/exception assembly.

This analyzer authenticates the local official 2.2.6.10 Apollo-main package
and the vendored FreeRTOS-Kernel V10.5.1 snapshot.  It then pins the exact
stock bodies, instruction mode, branch topology, literal dependencies, vector
references, and recovered configuration seams for:

* vRestoreContextOfFirstTask
* vRaisePrivilege
* vStartFirstTask
* PendSV_Handler
* SVC_Handler

It never builds, signs, connects to hardware, or writes firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "capstone is required; install the openCFW analysis dependencies"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
UPSTREAM_ROOT = ROOT / "third_party" / "freertos-kernel"
UPSTREAM_PORTASM = (
    UPSTREAM_ROOT
    / "portable"
    / "IAR"
    / "ARM_CM55_NTZ"
    / "non_secure"
    / "portasm.s"
)
UPSTREAM_PORTASM_H = UPSTREAM_PORTASM.with_name("portasm.h")
UPSTREAM_PORT_C = UPSTREAM_PORTASM.with_name("port.c")
UPSTREAM_PROVENANCE = UPSTREAM_ROOT / "PROVENANCE.json"

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

UPSTREAM_RELEASE = "FreeRTOS-Kernel V10.5.1"
UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_PORTASM_SIZE = 11_686
UPSTREAM_PORTASM_SHA256 = (
    "eaa83b3867edec5560c69f2a21facd7a"
    "ff3c0f3bfcdfc5751722375ae328ee8f"
)
UPSTREAM_PORTASM_GIT_BLOB = (
    "4d02a431e1d759f12f50e70fc55a7b0b4d368e89"
)
UPSTREAM_PORTASM_H_SHA256 = (
    "61af2aed89b618689b69c2e80f75a7cf"
    "8c9a46d0eaf1951f4454b775ee6fda0e"
)
UPSTREAM_PORT_C_SHA256 = (
    "c2762e124d700d26ceb0dc737af706f36"
    "1dd45c9e40bf683b916f1e430e37a08"
)

PX_CURRENT_TCB_ADDRESS = 0x2007_4A20
VTOR_ADDRESS = 0xE000_ED08
V_TASK_SWITCH_CONTEXT = 0x0045_51B4
V_PORT_SVC_HANDLER_C = 0x0044_2134
PRV_SETUP_FPU = 0x0044_20A6
X_PORT_START_SCHEDULER = 0x0044_21E2


class AuditError(RuntimeError):
    """Raised when an authenticated input or recovered invariant drifts."""


@dataclass(frozen=True)
class FunctionSpec:
    name: str
    start: int
    end: int
    sha256: str
    body_hex: str
    source_lines: tuple[int, int]
    source_sha256: str
    signatures: tuple[str, ...]


FUNCTIONS = (
    FunctionSpec(
        "vRestoreContextOfFirstTask",
        0x005F_A058,
        0x005F_A07E,
        "10edd4871b5f0c829e38618f1003ef0c"
        "45ec3629219317e23c62a2e255b0f4f8",
        (
            "364a1168086806c881f30b88022181f31488"
            "203080f30988bff36f8f4ff0000080f311881047"
        ),
        (82, 134),
        "117988195a20a6173b75d012cc5b36a8"
        "fc186685ebdd387e1074ce268d9bdfbd",
        (
            "ldr r2, [pc, #0xd8]",
            "ldm r0!, {r1, r2}",
            "msr psplim, r1",
            "msr control, r1",
            "msr psp, r0",
            "msr basepri, r0",
            "bx r2",
        ),
    ),
    FunctionSpec(
        "vRaisePrivilege",
        0x005F_A07E,
        0x005F_A08C,
        "29bceedf776515c291813e4eecd9a836"
        "378b81550c42d08aee35cf15df3bd8db",
        "eff3148020f0010080f314887047",
        (137, 141),
        "73109ec741c185e9a831a98656a1ad6b"
        "b1fbafdc0138aff2a2f809b76c7c7ebf",
        (
            "mrs r0, control",
            "bic r0, r0, #1",
            "msr control, r0",
            "bx lr",
        ),
    ),
    FunctionSpec(
        "vStartFirstTask",
        0x005F_A08C,
        0x005F_A0A4,
        "44ba0097fbbc1d0691837d5c51bee83e"
        "6b61509c9d89efffee9c202d930e6347",
        (
            "2a480068006880f3088862b661b6"
            "bff34f8fbff36f8f02df"
        ),
        (144, 153),
        "d6000ef7822e3b5a9ec14d07b6b401a"
        "bb6858a60ce0405d5a736f4cf95c2d5ed",
        (
            "ldr r0, [pc, #0xa8]",
            "msr msp, r0",
            "cpsie i",
            "cpsie f",
            "dsb sy",
            "isb sy",
            "svc #2",
        ),
    ),
    FunctionSpec(
        "PendSV_Handler",
        0x005F_A0C8,
        0x005F_A120,
        "d8e234bfa34805ad160e41ef54801973"
        "c9c871b36cf7ac0f365b56fe503253e3",
        (
            "eff309801ef0100f08bf20ed108aeff30b82734620e9fc0f"
            "144a116808604ff0300080f31188bff34f8fbff36f8f5bf6"
            "5df84ff0000080f311880c4a11680868b0e8fc0f13f0100f"
            "08bfb0ec108a82f30b8880f309881847"
        ),
        (172, 251),
        "ea3746fb4f92a56c1fcba4ec96107539"
        "b6a74e3d7bb3d910bb6554de6478a683",
        (
            "mrs r0, psp",
            "vstmdbeq r0!, {s16",
            "mrs r2, psplim",
            "stmdb r0!, {r2, r3, r4",
            "mov.w r0, #0x30",
            "bl #0x4551b4",
            "vldmiaeq r0!, {s16",
            "msr psplim, r2",
            "msr psp, r0",
            "bx r3",
        ),
    ),
    FunctionSpec(
        "SVC_Handler",
        0x005F_A120,
        0x005F_A132,
        "d0fac197473b52d6ed466462d237ddb20"
        "dd8096a6507ea559e75d4bd9d88da94",
        "1ef0040f0cbfeff30880eff3098048f601b8",
        (254, 259),
        "dbac230cb37c6e0c21cc139dfe97d4ec"
        "f74c44e3edfe7c9fe5a5c623546f3aaa",
        (
            "tst.w lr, #4",
            "ite eq",
            "mrseq r0, msp",
            "mrsne r0, psp",
            "b.w #0x442134",
        ),
    ),
)

FUNCTION_BY_NAME = {spec.name: spec for spec in FUNCTIONS}

EXPECTED_LITERAL_DEPENDENCIES = (
    {
        "function": "vRestoreContextOfFirstTask",
        "instruction": 0x005F_A058,
        "literal_address": 0x005F_A134,
        "value": PX_CURRENT_TCB_ADDRESS,
        "classification": "pxCurrentTCB",
    },
    {
        "function": "vStartFirstTask",
        "instruction": 0x005F_A08C,
        "literal_address": 0x005F_A138,
        "value": VTOR_ADDRESS,
        "classification": "SCB_VTOR",
    },
    {
        "function": "PendSV_Handler",
        "instruction": 0x005F_A0E0,
        "literal_address": 0x005F_A134,
        "value": PX_CURRENT_TCB_ADDRESS,
        "classification": "pxCurrentTCB",
    },
    {
        "function": "PendSV_Handler",
        "instruction": 0x005F_A102,
        "literal_address": 0x005F_A134,
        "value": PX_CURRENT_TCB_ADDRESS,
        "classification": "pxCurrentTCB",
    },
)

EXPECTED_INCOMING_BRANCHES = {
    "vRestoreContextOfFirstTask": (
        {
            "address": 0x0044_2146,
            "kind": "BL",
            "target": 0x005F_A058,
            "encoding": "b7f187ff",
        },
    ),
    "vRaisePrivilege": (),
    "vStartFirstTask": (
        {
            "address": 0x0044_2200,
            "kind": "BL",
            "target": 0x005F_A08C,
            "encoding": "b7f144ff",
        },
    ),
    "PendSV_Handler": (),
    "SVC_Handler": (),
}

EXPECTED_STORED_REFERENCES = {
    "vRestoreContextOfFirstTask": (),
    "vRaisePrivilege": (),
    "vStartFirstTask": (),
    "PendSV_Handler": (
        {
            "address": 0x0043_8038,
            "value": 0x005F_A0C9,
            "canonical": 0x005F_A0C8,
            "alignment": 0,
        },
    ),
    "SVC_Handler": (
        {
            "address": 0x0043_802C,
            "value": 0x005F_A121,
            "canonical": 0x005F_A120,
            "alignment": 0,
        },
    ),
}

SUPPORT_SPANS = {
    "prvSetupFPU": (
        0x0044_20A6,
        0x0044_20BC,
        "59f9a18538c1aab61aefe1664793178c"
        "6c16cc5f1c4d79b3c8502ddda0b742c8",
    ),
    "vPortSVCHandler_C": (
        0x0044_2134,
        0x0044_215A,
        "7afe568df362a8b1af03c36af654ed56"
        "bd68da6b7266ee1172eb556ae2276c19",
    ),
    "xPortStartScheduler": (
        0x0044_21E2,
        0x0044_2210,
        "66bacaafa2fa8e76a548eb9da62c2d3e"
        "1f058a471efe0bdfa072f59bf38ae1c0",
    ),
}


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


def decode_thumb_wide_branch(
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
    """Return possible narrow B/Bcc/CBZ/CBNZ targets."""

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


def function_for_address(address: int) -> FunctionSpec | None:
    for spec in FUNCTIONS:
        if spec.start <= address < spec.end:
            return spec
    return None


def disassemble(body: bytes, start: int) -> list[dict[str, Any]]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    instructions = list(decoder.disasm(body, start))
    if sum(instruction.size for instruction in instructions) != len(body):
        raise AuditError(f"incomplete Thumb decode at 0x{start:08X}")
    return [
        {
            "address": instruction.address,
            "size": instruction.size,
            "encoding": instruction.bytes.hex(),
            "mnemonic": instruction.mnemonic.lower(),
            "operands": instruction.op_str.lower(),
        }
        for instruction in instructions
    ]


def instruction_text(instruction: dict[str, Any]) -> str:
    operands = str(instruction["operands"])
    return (
        f"{instruction['mnemonic']} {operands}".strip()
    )


def scan_incoming_references(
    application: bytes,
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    incoming = {spec.name: [] for spec in FUNCTIONS}
    external_interior = {spec.name: [] for spec in FUNCTIONS}
    narrow = {spec.name: [] for spec in FUNCTIONS}

    for offset in range(0, len(application) - 3, 2):
        address = APPLICATION_BASE + offset
        first, second = struct.unpack_from("<HH", application, offset)
        for link, kind in ((True, "BL"), (False, "B.W")):
            target = decode_thumb_wide_branch(
                address,
                first,
                second,
                link=link,
            )
            if target is None:
                continue
            spec = function_for_address(target)
            if spec is None or spec.start <= address < spec.end:
                continue
            item = {
                "address": address,
                "kind": kind,
                "target": target,
                "encoding": application[offset : offset + 4].hex(),
            }
            if target == spec.start:
                incoming[spec.name].append(item)
            else:
                external_interior[spec.name].append(item)

    for offset in range(0, len(application) - 1, 2):
        address = APPLICATION_BASE + offset
        halfword = struct.unpack_from("<H", application, offset)[0]
        for target in narrow_branch_targets(address, halfword):
            spec = function_for_address(target)
            if spec is None or spec.start <= address < spec.end:
                continue
            narrow[spec.name].append(
                {
                    "address": address,
                    "target": target,
                    "encoding": application[offset : offset + 2].hex(),
                }
            )

    return incoming, external_interior, narrow


def scan_stored_references(
    application: bytes,
) -> dict[str, list[dict[str, Any]]]:
    references = {spec.name: [] for spec in FUNCTIONS}
    for offset in range(0, len(application) - 3):
        value = struct.unpack_from("<I", application, offset)[0]
        spec = function_for_address(value & ~1)
        if spec is None:
            continue
        references[spec.name].append(
            {
                "address": APPLICATION_BASE + offset,
                "value": value,
                "canonical": value & ~1,
                "alignment": offset % 4,
            }
        )
    return references


def verify_literal_dependencies(application: bytes) -> list[dict[str, Any]]:
    dependencies: list[dict[str, Any]] = []
    for expected in EXPECTED_LITERAL_DEPENDENCIES:
        instruction = int(expected["instruction"])
        halfword = struct.unpack_from(
            "<H",
            application,
            instruction - APPLICATION_BASE,
        )[0]
        if halfword & 0xF800 != 0x4800:
            raise AuditError(
                f"literal load at 0x{instruction:08X} is not Thumb LDR"
            )
        register = (halfword >> 8) & 0x7
        literal_address = (
            ((instruction + 4) & ~3)
            + ((halfword & 0xFF) << 2)
        )
        value = struct.unpack_from(
            "<I",
            application,
            literal_address - APPLICATION_BASE,
        )[0]
        if literal_address != expected["literal_address"]:
            raise AuditError(
                f"literal address drift at 0x{instruction:08X}"
            )
        if value != expected["value"]:
            raise AuditError(f"literal value drift at 0x{literal_address:08X}")
        item = dict(expected)
        item["destination_register"] = f"r{register}"
        dependencies.append(item)
    return dependencies


def verify_upstream() -> dict[str, Any]:
    portasm = UPSTREAM_PORTASM.read_bytes()
    portasm_h = UPSTREAM_PORTASM_H.read_bytes()
    port_c = UPSTREAM_PORT_C.read_bytes()
    provenance = json.loads(UPSTREAM_PROVENANCE.read_text())
    upstream = provenance["upstream"]
    files = provenance["files"]
    relative_portasm = (
        "portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s"
    )
    relative_portasm_h = (
        "portable/IAR/ARM_CM55_NTZ/non_secure/portasm.h"
    )
    relative_port_c = "portable/IAR/ARM_CM55_NTZ/non_secure/port.c"

    if len(portasm) != UPSTREAM_PORTASM_SIZE:
        raise AuditError("FreeRTOS portasm.s size drift")
    if sha256(portasm) != UPSTREAM_PORTASM_SHA256:
        raise AuditError("FreeRTOS portasm.s SHA-256 drift")
    if git_blob_sha1(portasm) != UPSTREAM_PORTASM_GIT_BLOB:
        raise AuditError("FreeRTOS portasm.s Git blob drift")
    if sha256(portasm_h) != UPSTREAM_PORTASM_H_SHA256:
        raise AuditError("FreeRTOS portasm.h SHA-256 drift")
    if sha256(port_c) != UPSTREAM_PORT_C_SHA256:
        raise AuditError("FreeRTOS port.c SHA-256 drift")
    if (
        upstream["selected_commit"] != UPSTREAM_COMMIT
        or upstream["selected_tree"] != UPSTREAM_TREE
        or upstream["selected_tag"] != "V10.5.1"
    ):
        raise AuditError("FreeRTOS provenance release identity drift")
    for path, data in (
        (relative_portasm, portasm),
        (relative_portasm_h, portasm_h),
        (relative_port_c, port_c),
    ):
        if files[path]["sha256"] != sha256(data):
            raise AuditError(f"provenance SHA-256 drift for {path}")
        if files[path]["git_blob_sha1"] != git_blob_sha1(data):
            raise AuditError(f"provenance Git blob drift for {path}")

    source_lines = portasm.splitlines(keepends=True)
    blocks: dict[str, dict[str, Any]] = {}
    for spec in FUNCTIONS:
        first, last = spec.source_lines
        block = b"".join(source_lines[first - 1 : last])
        if sha256(block) != spec.source_sha256:
            raise AuditError(f"upstream source block drift for {spec.name}")
        if block.count((spec.name + ":").encode()) != 1:
            raise AuditError(f"upstream label drift for {spec.name}")
        blocks[spec.name] = {
            "line_start": first,
            "line_end_inclusive": last,
            "size": len(block),
            "sha256": spec.source_sha256,
        }

    header_text = portasm_h.decode("utf-8")
    for spec in FUNCTIONS:
        expected = (
            f"void {spec.name}( void ) "
            "__attribute__( ( naked ) ) PRIVILEGED_FUNCTION;"
        )
        if expected not in header_text:
            raise AuditError(f"upstream ABI declaration drift for {spec.name}")

    return {
        "release": UPSTREAM_RELEASE,
        "tag": "V10.5.1",
        "commit": UPSTREAM_COMMIT,
        "tree": UPSTREAM_TREE,
        "license": "MIT",
        "portable_layer": "IAR/ARM_CM55_NTZ/non_secure",
        "portasm": {
            "path": relative_portasm,
            "size": len(portasm),
            "sha256": UPSTREAM_PORTASM_SHA256,
            "git_blob_sha1": UPSTREAM_PORTASM_GIT_BLOB,
        },
        "portasm_header": {
            "path": relative_portasm_h,
            "sha256": UPSTREAM_PORTASM_H_SHA256,
        },
        "port_c": {
            "path": relative_port_c,
            "sha256": UPSTREAM_PORT_C_SHA256,
        },
        "source_blocks": blocks,
        "abi_declaration": "naked PRIVILEGED_FUNCTION",
        "authentication_qualification": (
            "official annotated tag is unsigned; tag, peeled commit, tree, "
            "Git blobs, and local SHA-256 values are pinned"
        ),
    }


def verify_support_spans(application: bytes) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected_hash) in SUPPORT_SPANS.items():
        data = image_slice(application, start, end)
        if sha256(data) != expected_hash:
            raise AuditError(f"support span drift for {name}")
        result[name] = {
            "start": start,
            "end_exclusive": end,
            "size": len(data),
            "sha256": expected_hash,
        }

    handler = image_slice(
        application,
        SUPPORT_SPANS["vPortSVCHandler_C"][0],
        SUPPORT_SPANS["vPortSVCHandler_C"][1],
    )
    handler_start = SUPPORT_SPANS["vPortSVCHandler_C"][0]
    handler_calls = []
    for offset in range(0, len(handler) - 3, 2):
        first, second = struct.unpack_from("<HH", handler, offset)
        target = decode_thumb_wide_branch(
            handler_start + offset,
            first,
            second,
            link=True,
        )
        if target is not None:
            handler_calls.append((handler_start + offset, target))
    if handler_calls != [
        (0x0044_2142, PRV_SETUP_FPU),
        (0x0044_2146, FUNCTION_BY_NAME["vRestoreContextOfFirstTask"].start),
        (0x0044_214C, 0x005F_A0A4),
    ]:
        raise AuditError("vPortSVCHandler_C call shape drift")
    result["vPortSVCHandler_C"]["direct_bl"] = [
        {"address": address, "target": target}
        for address, target in handler_calls
    ]
    return result


def run_audit(image_path: Path = DEFAULT_IMAGE) -> dict[str, Any]:
    package = image_path.read_bytes()
    if len(package) != PACKAGE_SIZE:
        raise AuditError(
            f"official package size drift: {len(package)} != {PACKAGE_SIZE}"
        )
    if sha256(package) != PACKAGE_SHA256:
        raise AuditError("official package SHA-256 drift")
    application = package[PACKAGE_PREAMBLE_SIZE:]
    if sha256(application) != APPLICATION_SHA256:
        raise AuditError("installed application SHA-256 drift")

    functions: dict[str, dict[str, Any]] = {}
    for spec in FUNCTIONS:
        body = image_slice(application, spec.start, spec.end)
        if body != bytes.fromhex(spec.body_hex):
            raise AuditError(f"stock bytes drift for {spec.name}")
        if sha256(body) != spec.sha256:
            raise AuditError(f"stock SHA-256 drift for {spec.name}")
        instructions = disassemble(body, spec.start)
        text = tuple(instruction_text(item) for item in instructions)
        for signature in spec.signatures:
            if not any(signature in item for item in text):
                raise AuditError(
                    f"instruction signature drift for {spec.name}: "
                    f"{signature}"
                )
        functions[spec.name] = {
            "start": spec.start,
            "end_exclusive": spec.end,
            "size": len(body),
            "sha256": spec.sha256,
            "instruction_set": (
                "Armv8.1-M Mainline Thumb/Thumb-2, little-endian"
            ),
            "entry_state": "Thumb",
            "instructions": instructions,
        }

    literals = verify_literal_dependencies(application)
    incoming, external_interior, narrow = scan_incoming_references(application)
    stored = scan_stored_references(application)
    for spec in FUNCTIONS:
        name = spec.name
        if incoming[name] != list(EXPECTED_INCOMING_BRANCHES[name]):
            raise AuditError(f"incoming branch topology drift for {name}")
        if external_interior[name]:
            raise AuditError(f"external interior branch drift for {name}")
        if narrow[name]:
            raise AuditError(f"external narrow branch drift for {name}")
        if stored[name] != list(EXPECTED_STORED_REFERENCES[name]):
            raise AuditError(f"stored reference topology drift for {name}")

    pend_body = image_slice(
        application,
        FUNCTION_BY_NAME["PendSV_Handler"].start,
        FUNCTION_BY_NAME["PendSV_Handler"].end,
    )
    first, second = struct.unpack_from(
        "<HH",
        pend_body,
        0x005F_A0F6 - FUNCTION_BY_NAME["PendSV_Handler"].start,
    )
    if (
        decode_thumb_wide_branch(
            0x005F_A0F6,
            first,
            second,
            link=True,
        )
        != V_TASK_SWITCH_CONTEXT
    ):
        raise AuditError("PendSV vTaskSwitchContext call drift")

    svc_body = image_slice(
        application,
        FUNCTION_BY_NAME["SVC_Handler"].start,
        FUNCTION_BY_NAME["SVC_Handler"].end,
    )
    first, second = struct.unpack_from(
        "<HH",
        svc_body,
        0x005F_A12E - FUNCTION_BY_NAME["SVC_Handler"].start,
    )
    if (
        decode_thumb_wide_branch(
            0x005F_A12E,
            first,
            second,
            link=False,
        )
        != V_PORT_SVC_HANDLER_C
    ):
        raise AuditError("SVC handler tail branch drift")

    support = verify_support_spans(application)
    upstream = verify_upstream()
    return {
        "status": "ok",
        "read_only": True,
        "hardware_access": False,
        "flash_writes": False,
        "image": {
            "path": str(image_path),
            "package_size": len(package),
            "package_sha256": PACKAGE_SHA256,
            "application_size": len(application),
            "application_sha256": APPLICATION_SHA256,
            "application_base": APPLICATION_BASE,
        },
        "functions": functions,
        "literal_dependencies": literals,
        "references": {
            name: {
                "incoming_wide": incoming[name],
                "external_interior_wide": external_interior[name],
                "external_entry_or_interior_narrow": narrow[name],
                "stored_entry_or_interior": stored[name],
            }
            for name in FUNCTION_BY_NAME
        },
        "outgoing_dependencies": {
            "vRestoreContextOfFirstTask": {
                "direct_calls": [],
                "indirect_exit": (
                    "BX r2 to stacked EXC_RETURN; does not return by AAPCS"
                ),
            },
            "vRaisePrivilege": {
                "direct_calls": [],
                "return": "BX lr",
            },
            "vStartFirstTask": {
                "direct_calls": [],
                "exception": "SVC #2 through vector 11",
            },
            "PendSV_Handler": {
                "direct_calls": [
                    {
                        "address": 0x005F_A0F6,
                        "kind": "BL",
                        "target": V_TASK_SWITCH_CONTEXT,
                        "classification": "vTaskSwitchContext",
                    }
                ],
                "indirect_exit": "BX r3 to saved EXC_RETURN",
            },
            "SVC_Handler": {
                "direct_calls": [],
                "tail_branch": {
                    "address": 0x005F_A12E,
                    "kind": "B.W",
                    "target": V_PORT_SVC_HANDLER_C,
                    "classification": "vPortSVCHandler_C",
                },
            },
        },
        "vectors": {
            "SVC": {
                "index": 11,
                "address": 0x0043_802C,
                "value": 0x005F_A121,
                "canonical_target": 0x005F_A120,
                "thumb_bit": 1,
            },
            "PendSV": {
                "index": 14,
                "address": 0x0043_8038,
                "value": 0x005F_A0C9,
                "canonical_target": 0x005F_A0C8,
                "thumb_bit": 1,
            },
        },
        "support_spans": support,
        "recovered_configuration": {
            "portable_layer": {
                "value": "IAR/ARM_CM55_NTZ/non_secure",
                "binary_determined": True,
            },
            "configENABLE_MPU": {
                "value": 0,
                "binary_determined": True,
                "evidence": (
                    "two-word first restore; PendSV saves PSPLIM/EXC_RETURN "
                    "without CONTROL or MPU register programming"
                ),
            },
            "configENABLE_TRUSTZONE": {
                "value": 0,
                "binary_determined": True,
                "evidence": (
                    "NTZ context shape and compact SVC C dispatcher omit "
                    "secure-context allocate/free/init paths"
                ),
            },
            "configENABLE_FPU": {
                "value": 1,
                "binary_determined": True,
                "evidence": (
                    "SVC #2 dispatcher calls authenticated prvSetupFPU and "
                    "PendSV conditionally saves/restores s16-s31"
                ),
            },
            "configENABLE_MVE": {
                "value": None,
                "binary_determined": False,
                "upstream_default": 0,
                "emission_relevance": (
                    "none for these five bodies once configENABLE_FPU=1; "
                    "the PendSV conditional is FPU || MVE"
                ),
            },
            "configMAX_SYSCALL_INTERRUPT_PRIORITY": {
                "value": 0x30,
                "binary_determined": True,
            },
            "portSVC_START_SCHEDULER": {
                "value": 2,
                "binary_determined": True,
            },
        },
        "upstream": upstream,
        "promotion_assessment": {
            "source_identity": "unequivocal public MIT source",
            "safest_atomic_order": [
                {
                    "order": 1,
                    "functions": ["vRaisePrivilege"],
                    "qualification": (
                        "relocation-free leaf with no active call, vector, "
                        "literal, or stored reference in the MPU-disabled image"
                    ),
                },
                {
                    "order": 2,
                    "functions": ["vRestoreContextOfFirstTask"],
                    "qualification": (
                        "one active BL and one pxCurrentTCB relocation; retain "
                        "official vPortSVCHandler_C during promotion"
                    ),
                },
                {
                    "order": 3,
                    "functions": ["vStartFirstTask", "SVC_Handler"],
                    "qualification": (
                        "promote as one scheduler-start transaction because "
                        "SVC #2 immediately depends on vector 11 dispatch"
                    ),
                },
                {
                    "order": 4,
                    "functions": ["PendSV_Handler"],
                    "qualification": (
                        "promote last: live vector 14 context switch with "
                        "pxCurrentTCB, FP context, BASEPRI, and "
                        "vTaskSwitchContext dependencies"
                    ),
                },
            ],
            "hardware_validation_required_before_flash": True,
            "this_audit_authorizes_flash": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE,
        help="authenticated official ota_s200_firmware_ota.bin package",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the complete machine-readable audit",
    )
    args = parser.parse_args()
    result = run_audit(args.image)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PASS package: {args.image}")
        print("PASS NTZ functions: 5 exact stock bodies and Thumb decode")
        print(
            "PASS vectors: SVC[11]=0x005FA121, "
            "PendSV[14]=0x005FA0C9"
        )
        print(
            "PASS topology: 2 direct BL callers, 2 vector references, "
            "no external interior or narrow references"
        )
        print(
            "PASS configuration: MPU=0, TrustZone=0, FPU=1, "
            "BASEPRI=0x30, SVC-start=2; MVE remains emission-equivalent"
        )
        print(
            "PASS upstream: FreeRTOS-Kernel V10.5.1 "
            "IAR/ARM_CM55_NTZ/non_secure, MIT"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuditError, OSError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
