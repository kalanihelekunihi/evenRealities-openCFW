#!/usr/bin/env python3
"""Fail closed on drift in the durable R1 whole-image decompilation corpus."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS = REPO_ROOT / "research" / "decompilation"
EXPECTED = {
    "application": {
        "functions": 2687,
        "decompile_succeeded": 2686,
        "decompile_failed": 1,
        "minimum_address": 0x00027000,
        "maximum_address": 0x000C4D07,
    },
    "bootloader": {
        "functions": 285,
        "decompile_succeeded": 285,
        "decompile_failed": 0,
        "minimum_address": 0x000F8000,
        "maximum_address": 0x000FDFFF,
    },
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_image(label: str, expectation: dict[str, int]) -> None:
    image_root = CORPUS / label
    summary = json.loads((image_root / "analysis-summary.json").read_text())
    assert summary["function_count"] == expectation["functions"]
    assert summary["decompile_succeeded"] == expectation["decompile_succeeded"]
    assert summary["decompile_failed"] == expectation["decompile_failed"]
    assert int(summary["minimum_address"], 16) == expectation["minimum_address"]
    assert int(summary["maximum_address"], 16) == expectation["maximum_address"]

    with (image_root / "functions.csv").open(newline="", encoding="utf-8") as handle:
        functions = list(csv.DictReader(handle))
    assert len(functions) == expectation["functions"]
    entries = [int(row["entry"], 16) for row in functions]
    assert entries == sorted(entries)
    assert len(entries) == len(set(entries))
    for row in functions:
        entry = int(row["entry"], 16)
        end = int(row["end"], 16)
        assert expectation["minimum_address"] <= entry <= end <= expectation["maximum_address"]
        assert int(row["size"]) > 0

    output = (image_root / "decompiler-output.c").read_text(encoding="utf-8")
    for row in functions:
        entry = row["entry"]
        if entry == "0x000979dc":
            manual = image_root / "manual-recovery" / f"{entry}.c"
            assert manual.is_file()
        else:
            assert f"entry: {entry}" in output

    with (image_root / "decompiler-failures.csv").open(newline="", encoding="utf-8") as handle:
        failures = list(csv.DictReader(handle))
    assert len(failures) == expectation["decompile_failed"]
    if label == "application":
        assert [row["entry"] for row in failures] == ["0x000979dc"]

    required = (
        "analysis-summary.json",
        "call-graph.csv",
        "decompiler-failures.csv",
        "decompiler-output.c",
        "disassembly.s",
        "functions.csv",
        "memory-blocks.csv",
        "symbols.csv",
    )
    for name in required:
        path = image_root / name
        assert path.is_file() and path.stat().st_size > 0


def verify_rebuild() -> None:
    rebuild = CORPUS / "rebuild"
    manifest = json.loads((rebuild / "manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="r1-decomp-verify-") as temporary:
        temporary_root = Path(temporary)
        executable = temporary_root / "emit_image"
        subprocess.run(
            [
                "cc",
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(rebuild / "emit_image.c"),
                "-I",
                str(rebuild),
                "-o",
                str(executable),
            ],
            check=True,
        )
        for label, metadata in manifest["images"].items():
            output = temporary_root / f"{label}.bin"
            subprocess.run([str(executable), label, str(output)], check=True)
            assert output.stat().st_size == metadata["bytes"]
            assert sha256(output) == metadata["sha256"]

    manual = CORPUS / "application" / "manual-recovery" / "0x000979dc.c"
    with tempfile.TemporaryDirectory(prefix="r1-manual-c-") as temporary:
        subprocess.run(
            [
                "clang",
                "--target=arm-none-eabi",
                "-mcpu=cortex-m4",
                "-mthumb",
                "-std=c11",
                "-ffreestanding",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-c",
                str(manual),
                "-o",
                str(Path(temporary) / "manual.o"),
            ],
            check=True,
        )


def main() -> int:
    for label, expectation in EXPECTED.items():
        verify_image(label, expectation)
    verify_rebuild()
    print("R1 decompilation corpus verified: 2,972 functions and four exact-byte artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
