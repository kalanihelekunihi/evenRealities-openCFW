#!/usr/bin/env python3
"""Audit constant-materialized Thumb interworking branches for a missing Thumb bit.

Injected firmware code frequently returns to, or tail-calls, a stock function by
materializing its address into a scratch register and interworking to it:

    movw ip, #:lower16:target
    movt ip, #:upper16:target
    bx   ip

`BX`/`BLX` select the instruction set from bit 0 of the destination. A Thumb
destination must therefore be encoded odd. The Apollo510 (Cortex-M55) targeted
here implements no ARM state at all, so an even destination does not silently
mis-execute: it raises a UsageFault with INVSTATE set. When the configurable
fault handlers are not installed -- as in the stock G2 vector table, where the
MemManage, BusFault and UsageFault vectors are all zero -- that escalates
directly to HardFault.

The failure is invisible in C review because the address is spelled as a bare
number in inline assembly rather than as a function pointer, so neither the
compiler nor the linker ever sees a symbol whose Thumb bit it could set. It is
also invisible to a patch-level review that only checks the *entry* addresses of
injected code: those are reached by `BL`/`B.W`, which stay in Thumb state and
need no Thumb bit. Only the interworking branches inside the injected code do.

This analyzer reads a raw Thumb-2 code blob and reports every adjacent
`movw/movt -> bx|blx` triple through the same register whose materialized
destination has bit 0 clear.

Scope, stated precisely so a clean report is not over-read:

  * Only the exact adjacent three-instruction idiom is recognized. A sequence
    with anything in between -- including a deliberate `orr rN, #1` -- is not
    reported, because the intervening instruction may legitimately set the bit
    and this analyzer performs no dataflow analysis. That keeps false positives
    at zero at the cost of not being a completeness proof.
  * A destination held in a register loaded any other way (literal pool, `adr`,
    a C function pointer) is out of scope. Function pointers formed in C are not
    at risk here: the compiler sets the Thumb bit for them.

Usage:

    python3 thumb_branch_audit.py <blob.bin> [--base 0x00794324] [--json]

Exits 1 when any defective branch is found, 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import NamedTuple, Sequence


# Thumb-2 MOVW (T3) / MOVT (T1) share an encoding shape:
#   hw1: 1111 0 i 10 x100 imm4      (x selects MOVW=0 / MOVT=1)
#   hw2: 0 imm3 Rd imm8
_WIDE_MASK = 0xFBF0
_MOVW_BITS = 0xF240
_MOVT_BITS = 0xF2C0

# Thumb BX (T1) / BLX (T1):
#   0100 0111 L Rm 000
_INTERWORK_MASK = 0xFF87
_BX_BITS = 0x4700
_BLX_BITS = 0x4780

_MOVW_LENGTH = 4
_MOVT_LENGTH = 4
_BRANCH_LENGTH = 2
_SEQUENCE_LENGTH = _MOVW_LENGTH + _MOVT_LENGTH + _BRANCH_LENGTH


class ConstantBranch(NamedTuple):
    """One `movw/movt -> bx|blx` triple found in a blob."""

    offset: int
    """Byte offset of the `movw` within the scanned blob."""

    address: int
    """`offset` biased by the blob's load address."""

    register: int
    """Register the destination is materialized into and branched through."""

    target: int
    """Destination exactly as encoded, including bit 0."""

    mnemonic: str
    """Either `bx` or `blx`."""

    @property
    def is_thumb(self) -> bool:
        """Whether the destination selects Thumb state, as it must here."""
        return bool(self.target & 1)

    def describe(self) -> str:
        state = "Thumb" if self.is_thumb else "ARM (INVSTATE UsageFault)"
        return (
            f"{self.address:#010x}  movw/movt r{self.register} = {self.target:#010x}"
            f"  {self.mnemonic} r{self.register}  -> {state}"
        )


def _halfword(blob: bytes, offset: int) -> int:
    return blob[offset] | (blob[offset + 1] << 8)


def decode_movw_movt_immediate(first: int, second: int) -> int:
    """Return the 16-bit immediate encoded in a Thumb-2 MOVW/MOVT halfword pair."""
    imm4 = first & 0xF
    i = (first >> 10) & 1
    imm3 = (second >> 12) & 7
    imm8 = second & 0xFF
    return (imm4 << 12) | (i << 11) | (imm3 << 8) | imm8


def _register(second: int) -> int:
    return (second >> 8) & 0xF


def _is_wide(first: int, second: int, bits: int) -> bool:
    # Bit 15 of the second halfword distinguishes the data-processing
    # encodings from the branch/miscellaneous ones sharing the same prefix.
    return (first & _WIDE_MASK) == bits and (second & 0x8000) == 0


def _interwork(halfword: int) -> tuple[str, int] | None:
    if (halfword & _INTERWORK_MASK) == _BX_BITS:
        return "bx", (halfword >> 3) & 0xF
    if (halfword & _INTERWORK_MASK) == _BLX_BITS:
        return "blx", (halfword >> 3) & 0xF
    return None


def find_constant_branches(
    blob: bytes, base_address: int = 0
) -> list[ConstantBranch]:
    """Return every adjacent `movw/movt -> bx|blx` triple through one register."""
    branches: list[ConstantBranch] = []
    for offset in range(0, max(len(blob) - _SEQUENCE_LENGTH + 1, 0), 2):
        movw_first = _halfword(blob, offset)
        movw_second = _halfword(blob, offset + 2)
        if not _is_wide(movw_first, movw_second, _MOVW_BITS):
            continue

        movt_first = _halfword(blob, offset + 4)
        movt_second = _halfword(blob, offset + 6)
        if not _is_wide(movt_first, movt_second, _MOVT_BITS):
            continue

        register = _register(movw_second)
        if register != _register(movt_second):
            continue

        interwork = _interwork(_halfword(blob, offset + 8))
        if interwork is None:
            continue
        mnemonic, branch_register = interwork
        if branch_register != register:
            continue

        low = decode_movw_movt_immediate(movw_first, movw_second)
        high = decode_movw_movt_immediate(movt_first, movt_second)
        branches.append(
            ConstantBranch(
                offset=offset,
                address=base_address + offset,
                register=register,
                target=(high << 16) | low,
                mnemonic=mnemonic,
            )
        )
    return branches


def audit(blob: bytes, base_address: int = 0) -> list[ConstantBranch]:
    """Return only the constant branches that would fault on an ARMv8-M core."""
    return [
        branch
        for branch in find_constant_branches(blob, base_address)
        if not branch.is_thumb
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("blob", help="raw Thumb-2 code blob to audit")
    parser.add_argument(
        "--base",
        default="0",
        help="load address of the blob, for absolute reporting (default 0)",
    )
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable findings"
    )
    arguments = parser.parse_args(argv)

    try:
        base_address = int(arguments.base, 0)
    except ValueError:
        parser.error(f"invalid --base value: {arguments.base!r}")

    with open(arguments.blob, "rb") as handle:
        blob = handle.read()

    branches = find_constant_branches(blob, base_address)
    findings = [branch for branch in branches if not branch.is_thumb]

    if arguments.json:
        print(
            json.dumps(
                {
                    "blob": arguments.blob,
                    "base_address": base_address,
                    "scanned_bytes": len(blob),
                    "constant_branches": len(branches),
                    "findings": [
                        {
                            "offset": branch.offset,
                            "address": branch.address,
                            "register": branch.register,
                            "target": branch.target,
                            "mnemonic": branch.mnemonic,
                        }
                        for branch in findings
                    ],
                },
                indent=2,
            )
        )
    else:
        print(
            f"scanned {len(blob)} bytes at {base_address:#010x}: "
            f"{len(branches)} constant interworking branches"
        )
        for branch in branches:
            marker = "    " if branch.is_thumb else "!!! "
            print(f"  {marker}{branch.describe()}")
        if findings:
            print(
                f"\n{len(findings)} branch(es) request ARM state on a core that "
                "has none; each is a HardFault at run time."
            )

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
