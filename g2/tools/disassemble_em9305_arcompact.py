#!/usr/bin/env python3
"""Disassemble authenticated EM9305 stock ranges as ARCv2 EM.

GNU objcopy creates an ARC600 ELF when converting a raw binary directly.
This helper first asks the ARC GCC driver for an ARCv2 EM carrier object, then
adds the stock package as an executable section. Preserving the ELF machine
flags is required for correct long-immediate decoding.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin"
IMAGE_SIZE = 211_948
IMAGE_SHA256 = "91a38f7fc05555f86181ecb22b363e3239bfcaaa2ff6171e98524ae64821eca9"
PACKAGE_MAP_BASE = 0x0030_1FDC
PACKAGE_MAP_END = PACKAGE_MAP_BASE + IMAGE_SIZE


class DisassemblyError(RuntimeError):
    """The authenticated wrapper/disassembly workflow failed."""


def parse_range(value: str) -> tuple[int, int]:
    try:
        start_text, stop_text = value.split(":", 1)
        start = int(start_text, 0)
        stop = int(stop_text, 0)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("range must be START:STOP") from exc
    if not PACKAGE_MAP_BASE <= start < stop <= PACKAGE_MAP_END:
        raise argparse.ArgumentTypeError(
            f"range must lie within 0x{PACKAGE_MAP_BASE:X}:0x{PACKAGE_MAP_END:X}"
        )
    if start & 1 or stop & 1:
        raise argparse.ArgumentTypeError("ARCv2 EM range endpoints must be halfword-aligned")
    return start, stop


def resolve_tool(name: str, binutils_dir: Path | None = None) -> Path:
    candidate = binutils_dir / name if binutils_dir is not None else None
    if candidate is not None and candidate.is_file():
        return candidate
    prefixed_candidate = (
        binutils_dir / f"arc-linux-gnu-{name}"
        if binutils_dir is not None else None
    )
    if prefixed_candidate is not None and prefixed_candidate.is_file():
        return prefixed_candidate
    found = shutil.which(f"arc-linux-gnu-{name}" if name != "gcc" else "arc-linux-gnu-gcc")
    if found is None:
        raise DisassemblyError(f"ARC tool not found: {name}")
    return Path(found)


def run(command: Sequence[str | Path], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(item) for item in command],
        check=True,
        text=True,
        capture_output=True,
        **kwargs,
    )


def disassemble(
    image: Path,
    ranges: Sequence[tuple[int, int]],
    *,
    gcc: Path,
    binutils_dir: Path,
) -> str:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or hashlib.sha256(blob).hexdigest() != IMAGE_SHA256:
        raise DisassemblyError("official EM9305 image identity mismatch")

    objcopy = resolve_tool("objcopy", binutils_dir)
    objdump = resolve_tool("objdump", binutils_dir)
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-arcv2-") as directory:
        work = Path(directory)
        carrier = work / "arcv2-em-carrier.o"
        wrapped = work / "em9305-stock.elf"
        run(
            (
                gcc,
                "-B",
                f"{binutils_dir}/",
                "-x",
                "c",
                "-c",
                "-mcpu=em",
                "-ffreestanding",
                "-o",
                carrier,
                "-",
            ),
            input="void open_cfw_arcv2_em_carrier(void) {}\n",
        )
        run(
            (
                objcopy,
                "--remove-section",
                ".text",
                "--add-section",
                f".firmware={image.resolve()}",
                "--set-section-flags",
                ".firmware=alloc,load,readonly,code,contents",
                "--change-section-vma",
                f".firmware=0x{PACKAGE_MAP_BASE:X}",
                carrier,
                wrapped,
            )
        )
        identity = run((objdump, "-f", wrapped)).stdout
        if "architecture: ARCv2" not in identity:
            raise DisassemblyError("wrapper did not preserve ARCv2 ELF machine flags")

        outputs = []
        for start, stop in ranges:
            outputs.append(
                run(
                    (
                        objdump,
                        "-D",
                        "-j",
                        ".firmware",
                        "-M",
                        "cpu=em",
                        f"--start-address=0x{start:X}",
                        f"--stop-address=0x{stop:X}",
                        wrapped,
                    )
                ).stdout
            )
        return "\n".join(outputs)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--gcc", type=Path, default=Path("arc-linux-gnu-gcc"))
    parser.add_argument("--binutils-dir", type=Path, required=True)
    parser.add_argument(
        "--range",
        dest="ranges",
        type=parse_range,
        action="append",
        required=True,
        metavar="START:STOP",
        help="installed halfword-aligned address range; repeat as needed",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    gcc = args.gcc
    if not gcc.is_file():
        found = shutil.which(str(gcc))
        if found is None:
            raise DisassemblyError(f"ARC GCC not found: {gcc}")
        gcc = Path(found)
    print(
        disassemble(
            args.image,
            args.ranges,
            gcc=gcc,
            binutils_dir=args.binutils_dir,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
