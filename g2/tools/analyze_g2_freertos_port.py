#!/usr/bin/env python3
"""Read-only binary audit for the G2 FreeRTOS Cortex-M55 port boundary.

The checks in this file deliberately stop short of generating, linking, or
flashing firmware.  They pin the official 2.2.6.10 application image and the
small instruction ranges used to classify the FreeRTOS portable layer.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from capstone import CS_ARCH_ARM, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
except ImportError as exc:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "capstone is required; install the openCFW analysis dependencies"
    ) from exc


OPENCFW_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
PACKAGE_PREAMBLE_SIZE = 32
APPLICATION_BASE = 0x0043_8000


@dataclass(frozen=True)
class Span:
    name: str
    start: int
    end: int
    sha256: str


SPANS = (
    Span(
        "port.restore_first_task",
        0x005F_A058,
        0x005F_A07E,
        "10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8",
    ),
    Span(
        "port.start_first_task",
        0x005F_A08C,
        0x005F_A0A4,
        "44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347",
    ),
    Span(
        "port.set_interrupt_mask",
        0x005F_A0A4,
        0x005F_A0BA,
        "f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323",
    ),
    Span(
        "port.pendsv",
        0x005F_A0C8,
        0x005F_A120,
        "d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3",
    ),
    Span(
        "port.svc_assembly",
        0x005F_A120,
        0x005F_A132,
        "d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94",
    ),
    Span(
        "port.fpu_setup",
        0x0044_20A6,
        0x0044_20BC,
        "59f9a18538c1aab61aefe1664793178c6c16cc5f1c4d79b3c8502ddda0b742c8",
    ),
    Span(
        "port.svc_c",
        0x0044_2134,
        0x0044_215A,
        "7afe568df362a8b1af03c36af654ed56bd68da6b7266ee1172eb556ae2276c19",
    ),
    Span(
        "port.initial_stack",
        0x0044_215A,
        0x0044_21E2,
        "f97bdb238b175f9e72f3f03b228ffda3b69351cbe53e0b70c65707f600372caa",
    ),
    Span(
        "port.start_scheduler",
        0x0044_21E2,
        0x0044_2210,
        "66bacaafa2fa8e76a548eb9da62c2d3e1f058a471efe0bdfa072f59bf38ae1c0",
    ),
    Span(
        "task.create_static",
        0x0045_4820,
        0x0045_48BA,
        "21c10ddaf25950d84acbcf302f2de18d3471dd5321c4cd7aa50dcc8a6f29debe",
    ),
    Span(
        "task.initialise",
        0x0045_4938,
        0x0045_49FC,
        "54a87da84dbcdf7871563962b44490d635a2a924225fed68b99ccce811b397b2",
    ),
    Span(
        "tick.stimer_dispatch",
        0x0045_63B4,
        0x0045_6426,
        "43a3151849cd96e46d45ad12bb338ea09f586e9fe734b01d485fb9b21c6775fa",
    ),
    Span(
        "tick.stimer_isr",
        0x0045_6426,
        0x0045_643E,
        "518fea2d6b0fab0ff4dce31adcaa55015c872000ee314e97987aed9459040f4a",
    ),
    Span(
        "tick.setup",
        0x0045_643E,
        0x0045_6496,
        "5a54cfc80b658ae5b645ac53b60f0e3098f0fd24fd4b5bedcfb0f822007b30ae",
    ),
    Span(
        "tick.tickless",
        0x0045_6498,
        0x0045_655C,
        "d6716a7a132b61665a401d513ce75119e5210640f69f5d16424067cb4216e8da",
    ),
    Span(
        "heap.pvPortMalloc",
        0x0045_6110,
        0x0045_6210,
        "8d86a7daf341ad836729e4abdd25b66b45f97a56d6d1077c07bf0c5718f8dc57",
    ),
    Span(
        "heap.vPortFree",
        0x0045_6210,
        0x0045_6280,
        "d754aec282080b2deafeb6756cbacc156af70a311499ee4d73eeb7497f12b032",
    ),
    Span(
        "heap.initialise_and_insert",
        0x0045_6280,
        0x0045_6338,
        "93bf57f7e3b9672cc54fcf3565327f169fbe24dca09d72205ff40b41ac931df2",
    ),
    Span(
        "timer.create_service_task",
        0x0047_E674,
        0x0047_E6DC,
        "589900974898dee81ea80021f6a946ddb353b6521df25d2a189aa3b6e5056005",
    ),
    Span(
        "timer.service_task_loop",
        0x0047_E878,
        0x0047_E88C,
        "9a7fd60775e97786baeb1ea1871423c63c5d744b5b8e1ce0c8176e8bb80d377a",
    ),
    Span(
        "timer.runtime_init",
        0x0047_EAB8,
        0x0047_EAF6,
        "e34431d020471c30b8e3d3fed60fb15e83b77f49ee2921fcdae5e3be7d589ece",
    ),
)

EXPECTED_VECTORS = {
    0: 0x2007_FB00,
    1: 0x005E_4233,
    2: 0x0043_97A7,
    3: 0x005B_0115,
    11: 0x005F_A121,
    14: 0x005F_A0C9,
    15: 0x0044_2115,
    48: 0x0045_6427,
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def application_slice(application: bytes, start: int, end: int) -> bytes:
    first = start - APPLICATION_BASE
    last = end - APPLICATION_BASE
    if first < 0 or last > len(application) or first >= last:
        raise ValueError(f"span 0x{start:08X}...0x{end - 1:08X} is outside image")
    return application[first:last]


def disassembly(application: bytes, start: int, end: int) -> tuple[str, ...]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    instructions = decoder.disasm(application_slice(application, start, end), start)
    return tuple(
        f"{instruction.mnemonic} {instruction.op_str}".strip().lower()
        for instruction in instructions
    )


def require_instruction(instructions: tuple[str, ...], fragment: str) -> None:
    if not any(fragment in instruction for instruction in instructions):
        raise AssertionError(f"missing instruction signature: {fragment}")


def check_semantics(application: bytes) -> None:
    restore = disassembly(application, 0x005F_A058, 0x005F_A07E)
    require_instruction(restore, "ldm r0!, {r1, r2}")
    require_instruction(restore, "msr psplim, r1")
    require_instruction(restore, "movs r1, #2")
    require_instruction(restore, "msr control, r1")

    start = disassembly(application, 0x005F_A08C, 0x005F_A0A4)
    require_instruction(start, "svc #2")

    mask = disassembly(application, 0x005F_A0A4, 0x005F_A0BA)
    require_instruction(mask, "mov.w r1, #0x30")
    require_instruction(mask, "msr basepri, r1")

    pendsv = disassembly(application, 0x005F_A0C8, 0x005F_A120)
    require_instruction(pendsv, "vstmdbeq r0!, {s16")
    require_instruction(pendsv, "mrs r2, psplim")
    require_instruction(pendsv, "stmdb r0!, {r2, r3, r4")
    require_instruction(pendsv, "bl #0x4551b4")
    require_instruction(pendsv, "vldmiaeq r0!, {s16")
    if sum(instruction.startswith("bl ") for instruction in pendsv) != 1:
        raise AssertionError("PendSV call shape changed; re-review TrustZone classification")
    if any("control" in instruction for instruction in pendsv):
        raise AssertionError("PendSV unexpectedly saves or restores CONTROL")

    svc_c = disassembly(application, 0x0044_2134, 0x0044_215A)
    require_instruction(svc_c, "cmp r0, #2")
    require_instruction(svc_c, "bl #0x4420a6")
    require_instruction(svc_c, "bl #0x5fa058")

    fpu = disassembly(application, 0x0044_20A6, 0x0044_20BC)
    require_instruction(fpu, "#0xf00000")
    require_instruction(fpu, "#0xc0000000")

    initial_stack = disassembly(application, 0x0044_215A, 0x0044_21E2)
    require_instruction(initial_stack, "#0x12121212")
    require_instruction(initial_stack, "mvns r2, #2")

    task_init = disassembly(application, 0x0045_4938, 0x0045_49FC)
    require_instruction(task_init, "str.w sb, [r6, #0x54]")
    require_instruction(task_init, "cmp.w sb, #0x38")
    require_instruction(task_init, "str.w sb, [r6, #0x60]")

    tick_setup = disassembly(application, 0x0045_643E, 0x0045_6496)
    require_instruction(tick_setup, "movs r0, #0x20")
    require_instruction(tick_setup, "movw r0, #0x103")

    heap = disassembly(application, 0x0045_6280, 0x0045_6338)
    require_instruction(heap, "movs.w r2, #0x2f000")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "image",
        nargs="?",
        type=Path,
        default=DEFAULT_IMAGE,
        help="official ota_s200_firmware_ota.bin package",
    )
    args = parser.parse_args()

    package = args.image.read_bytes()
    package_hash = digest(package)
    if len(package) != PACKAGE_SIZE:
        raise AssertionError(
            f"package size mismatch: expected {PACKAGE_SIZE}, got {len(package)}"
        )
    if package_hash != PACKAGE_SHA256:
        raise AssertionError(
            f"package SHA-256 mismatch: expected {PACKAGE_SHA256}, got {package_hash}"
        )

    application = package[PACKAGE_PREAMBLE_SIZE:]
    for index, expected in EXPECTED_VECTORS.items():
        actual = struct.unpack_from("<I", application, index * 4)[0]
        if actual != expected:
            raise AssertionError(
                f"vector {index} mismatch: expected 0x{expected:08X}, "
                f"got 0x{actual:08X}"
            )

    for span in SPANS:
        actual = digest(application_slice(application, span.start, span.end))
        if actual != span.sha256:
            raise AssertionError(
                f"{span.name} SHA-256 mismatch: expected {span.sha256}, got {actual}"
            )

    check_semantics(application)

    print(f"PASS package: {args.image}")
    print(f"PASS SHA-256: {package_hash}")
    print(
        "PASS vectors: SVC=0x005FA121 PendSV=0x005FA0C9 "
        "SysTick=0x00442115 IRQ32=0x00456427"
    )
    print(f"PASS reviewed spans: {len(SPANS)}")
    print("PASS port shape: IAR ARM_CM55_NTZ/non_secure, configENABLE_MPU=0")
    print("PASS context: PSPLIM + EXC_RETURN + r4-r11; conditional s16-s31")
    print("PASS FPU setup: CP10/CP11 enabled; automatic/lazy FP state enabled")
    print("PASS interrupt mask: BASEPRI=0x30")
    print("PASS tick seam: Apollo STIMER compare A, 32 counts/tick, config 0x103")
    print("PASS TCB seam: size 0x70; G2 stack-depth word at offset 0x54")
    print("PASS heap seam: heap_4 shape; configTOTAL_HEAP_SIZE=0x2F000")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
