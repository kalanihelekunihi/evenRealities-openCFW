#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare one compiled function against its stock bytes.

    compare_function.py --image <raw image> --base <load address> \
        --address <stock entry> --size <bytes> --object <file.o> \
        --section <.text.symbol> [--objcopy <arm-none-eabi-objcopy>] [--objdump ...]

Prints MATCH, or a side-by-side disassembly of the stock and built bytes.
Relocations in the built object are not applied. Compile with
-ffunction-sections and compare only functions whose bytes carry no
unresolved literal-pool or branch relocations, or read the diff with that
in mind.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def disasm(objdump: str, data: bytes, vma: int, thumb: bool) -> list[str]:
    with tempfile.NamedTemporaryFile(suffix=".bin") as tmp:
        tmp.write(data)
        tmp.flush()
        args = [objdump, "-D", "-b", "binary", "-m", "arm", f"--adjust-vma={vma:#x}"]
        if thumb:
            args += ["-M", "force-thumb"]
        out = subprocess.run(args + [tmp.name], capture_output=True, text=True, check=True).stdout
    return [l for l in out.splitlines() if l[:1] == " " and ":" in l]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--base", type=lambda v: int(v, 0), required=True)
    p.add_argument("--address", type=lambda v: int(v, 0), required=True)
    p.add_argument("--size", type=lambda v: int(v, 0), required=True)
    p.add_argument("--object", type=Path, required=True)
    p.add_argument("--section", required=True)
    p.add_argument("--objcopy", default="arm-none-eabi-objcopy")
    p.add_argument("--objdump", default="arm-none-eabi-objdump")
    p.add_argument("--arm", action="store_true", help="A32 instead of Thumb")
    a = p.parse_args()

    image = a.image.read_bytes()
    offset = (a.address & ~1) - a.base
    stock = image[offset:offset + a.size]
    with tempfile.NamedTemporaryFile(suffix=".bin") as tmp:
        subprocess.run([a.objcopy, "-O", "binary", f"--only-section={a.section}", str(a.object), tmp.name], check=True)
        built = Path(tmp.name).read_bytes()
    if built == stock:
        print(f"MATCH {a.section} {len(built)} bytes at {a.address:#x}")
        return 0
    print(f"DIFF {a.section}: stock {len(stock)} bytes, built {len(built)} bytes")
    left = disasm(a.objdump, stock, a.address & ~1, not a.arm)
    right = disasm(a.objdump, built, a.address & ~1, not a.arm)
    for i in range(max(len(left), len(right))):
        l = left[i].split("\t", 1)[-1] if i < len(left) else ""
        r = right[i].split("\t", 1)[-1] if i < len(right) else ""
        mark = " " if l == r else "|"
        print(f"{l[:44]:<44} {mark} {r[:44]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
