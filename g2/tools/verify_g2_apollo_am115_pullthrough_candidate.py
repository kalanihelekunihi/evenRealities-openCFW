#!/usr/bin/env python3
"""Verify the AM115 semantic model as a target pull-through object."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am115_semantic_model.c"
)
OUT = ROOT / "tools/manifests/g2-apollo-am115-pullthrough-candidate.json"
EXPECTED_SYMBOLS = [
    "open_cfw_am115_0x5455c6_semantic_model",
    "open_cfw_am115_0x545ec4_semantic_model",
    "open_cfw_am115_0x546e02_semantic_model",
]
CLANG = "/usr/bin/clang"
NM = "/usr/bin/nm"
XCRUN = "/usr/bin/xcrun"
FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-builtin",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-Wall",
    "-Wextra",
    "-Werror",
]
ALLOWED_RELOCATION = {
    "section": ".ARM.exidx",
    "type": "R_ARM_PREL31",
    "value": ".text",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _global_text_symbols(object_path: Path) -> list[str]:
    proc = subprocess.run(
        [NM, "-g", str(object_path)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    symbols = []
    for line in proc.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1] == "T":
            symbols.append(fields[2])
    return sorted(symbols)


def _undefined_symbols(object_path: Path) -> list[str]:
    proc = subprocess.run(
        [NM, "-u", str(object_path)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip())


def _llvm_objdump() -> str:
    proc = subprocess.run(
        [XCRUN, "--find", "llvm-objdump"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.strip()


def _relocations(object_path: Path) -> list[dict[str, object]]:
    proc = subprocess.run(
        [_llvm_objdump(), "-r", str(object_path)],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    rows = []
    section = None
    for line in proc.stdout.splitlines():
        if line.startswith("RELOCATION RECORDS FOR [") and line.endswith("]:"):
            section = line.removeprefix("RELOCATION RECORDS FOR [").removesuffix("]:")
            continue
        fields = line.split()
        if len(fields) == 3 and section is not None and fields[0] != "OFFSET":
            rows.append({
                "section": section,
                "offset": int(fields[0], 16),
                "type": fields[1],
                "value": fields[2],
            })
    return rows


def analyze() -> dict:
    with tempfile.TemporaryDirectory(prefix="g2-am115-pullthrough-") as tmp:
        object_path = Path(tmp) / "runtime_liblc3_am115_semantic_model.o"
        subprocess.run(
            [CLANG, *FLAGS, "-c", str(SOURCE), "-o", str(object_path)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        symbols = _global_text_symbols(object_path)
        if symbols != sorted(EXPECTED_SYMBOLS):
            raise RuntimeError("AM115 pull-through target symbols changed")
        undefined_symbols = _undefined_symbols(object_path)
        if undefined_symbols:
            raise RuntimeError("AM115 pull-through object gained undefined symbols")
        relocations = _relocations(object_path)
        relocation_kinds = {
            (row["section"], row["type"], row["value"])
            for row in relocations
        }
        expected_relocation = (
            ALLOWED_RELOCATION["section"],
            ALLOWED_RELOCATION["type"],
            ALLOWED_RELOCATION["value"],
        )
        if relocation_kinds - {expected_relocation}:
            raise RuntimeError("AM115 pull-through object gained unexpected relocations")
        object_bytes = object_path.read_bytes()
        return {
            "schema_version": 1,
            "source": str(SOURCE.relative_to(ROOT)),
            "source_sha256": _sha256(SOURCE),
            "toolchain_profile": "apple-clang",
            "compiler": CLANG,
            "target": "thumbv7em-none-eabi",
            "flags": FLAGS,
            "object_size": len(object_bytes),
            "object_sha256": hashlib.sha256(object_bytes).hexdigest(),
            "exported_text_symbols": symbols,
            "symbol_count": len(symbols),
            "undefined_symbols": undefined_symbols,
            "relocation_count": len(relocations),
            "allowed_relocation": ALLOWED_RELOCATION,
            "relocation_summary": [
                {
                    "section": section,
                    "type": rel_type,
                    "value": value,
                    "count": sum(
                        1 for row in relocations
                        if (
                            row["section"],
                            row["type"],
                            row["value"],
                        ) == (section, rel_type, value)
                    ),
                }
                for section, rel_type, value in sorted(relocation_kinds)
            ],
            "candidate_addresses": [
                "0x005455c6",
                "0x00545ec4",
                "0x00546e02",
            ],
            "firmware_routing_status": "not_yet_routed_into_overlay",
            "target_compile_verified": True,
        }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source": report["source"],
        "target_compile_verified": report["target_compile_verified"],
        "symbol_count": report["symbol_count"],
        "undefined_symbol_count": len(report["undefined_symbols"]),
        "relocation_count": report["relocation_count"],
        "object_sha256": report["object_sha256"],
        "firmware_routing_status": report["firmware_routing_status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
