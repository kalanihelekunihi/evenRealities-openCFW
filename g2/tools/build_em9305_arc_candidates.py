#!/usr/bin/env python3
"""Compile the maintained EM9305 candidates for ARCv2 EM and fail closed."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "components/shared/em9305"
SOURCES = tuple(sorted(SOURCE_DIR.glob("*.c")))
FORBIDDEN_IMPORTS = frozenset({
    "__ashldi3", "__ashrdi3", "__divdi3", "__divsi3", "__lshrdi3",
    "__moddi3", "__modsi3", "__muldi3", "__mulsi3", "__udivdi3",
    "__udivsi3", "__umoddi3", "__umodsi3", "memcpy", "memmove", "memset",
})
FLAGS = (
    "-mcpu=em", "-Os", "-std=c99", "-ffreestanding", "-fno-builtin",
    "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror",
)


class BuildError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command: list[str]) -> str:
    completed = subprocess.run(
        command, check=False, capture_output=True, text=True, cwd=ROOT,
    )
    if completed.returncode != 0:
        raise BuildError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stdout}{completed.stderr}"
        )
    return completed.stdout


def build(gcc: str, nm: str, output_dir: Path) -> dict[str, object]:
    if not SOURCES:
        raise BuildError("no EM9305 candidate translation units found")
    output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    all_undefined: set[str] = set()
    for source in SOURCES:
        output = output_dir / f"{source.stem}.o"
        run([gcc, *FLAGS, "-c", str(source), "-o", str(output)])
        undefined = set()
        for line in run([nm, "-u", str(output)]).splitlines():
            fields = line.split()
            if fields:
                undefined.add(fields[-1])
        forbidden = sorted(undefined & FORBIDDEN_IMPORTS)
        if forbidden:
            raise BuildError(f"{source.name}: forbidden runtime imports: {forbidden}")
        if undefined:
            raise BuildError(f"{source.name}: undefined symbols: {sorted(undefined)}")
        all_undefined.update(undefined)
        records.append({
            "source": str(source.relative_to(ROOT)),
            "source_size": source.stat().st_size,
            "source_sha256": sha256(source),
            "object": str(output.relative_to(ROOT)),
            "object_size": output.stat().st_size,
            "object_sha256": sha256(output),
            "undefined_symbols": [],
        })
    version = run([gcc, "--version"]).splitlines()[0]
    return {
        "schema_version": 1,
        "status": "arcv2-em-candidates-target-compiled",
        "target": "ARCv2 EM",
        "compiler": version,
        "flags": list(FLAGS),
        "translation_units": records,
        "translation_unit_count": len(records),
        "undefined_symbols": sorted(all_undefined),
        "forbidden_runtime_imports": [],
        "production_routed": False,
        "hardware_operations": [],
        "hardware_validation": "blocked by unavailable physical evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcc", default=os.environ.get("OPENCFW_ARC_GCC", "arc-linux-gnu-gcc"))
    parser.add_argument("--nm", default=os.environ.get("OPENCFW_ARC_NM", "arc-linux-gnu-nm"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-summary", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="opencfw-em9305-arc-") as temporary:
        output_dir = args.output_dir or Path(temporary)
        report = build(args.gcc, args.nm, output_dir.resolve())
        payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.write_summary is not None:
            args.write_summary.resolve().write_text(payload, encoding="utf-8")
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
