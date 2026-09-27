#!/usr/bin/env python3
"""Verify the AM145 semantic model as a target pull-through object."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am145_semantic_model.c"
)
OUT = ROOT / "tools/manifests/g2-apollo-am145-pullthrough-candidate.json"
EXPECTED_SYMBOLS = [
    "open_cfw_am145_0x5a340c_semantic_model",
    "open_cfw_am145_0x5a34ca_semantic_model",
    "open_cfw_am145_0x5a35a4_semantic_model",
    "open_cfw_am145_0x5a36ac_semantic_model",
    "open_cfw_am145_0x5a3798_semantic_model",
    "open_cfw_am145_0x5a3980_semantic_model",
    "open_cfw_am145_0x5a3a10_semantic_model",
    "open_cfw_am145_0x5a3ab0_semantic_model",
    "open_cfw_am145_0x5a3bcc_semantic_model",
    "open_cfw_am145_0x5a3cc6_semantic_model",
    "open_cfw_am145_0x5a3e24_semantic_model",
    "open_cfw_am145_0x5a3fe8_semantic_model",
    "open_cfw_am145_0x5a40ca_semantic_model",
    "open_cfw_am145_0x5a4a66_semantic_model",
    "open_cfw_am145_0x5a4b36_semantic_model",
    "open_cfw_am145_0x5a4802_semantic_model",
    "open_cfw_am145_0x5a487a_semantic_model",
    "open_cfw_am145_0x5a490c_semantic_model",
    "open_cfw_am145_0x5a63c8_semantic_model",
    "open_cfw_am145_0x5a6596_semantic_model",
    "open_cfw_am145_0x5a659a_semantic_model",
    "open_cfw_am145_0x5a65a2_semantic_model",
    "open_cfw_am145_0x5a65b0_semantic_model",
    "open_cfw_am145_0x5a66cc_semantic_model",
    "open_cfw_am145_0x5a674a_semantic_model",
    "open_cfw_am145_0x5a6c52_semantic_model",
    "open_cfw_am145_0x5a6c5e_semantic_model",
    "open_cfw_am145_0x5a6c7c_semantic_model",
    "open_cfw_am145_0x5a6c94_semantic_model",
    "open_cfw_am145_0x5a6ca2_semantic_model",
    "open_cfw_am145_0x5a6cb0_semantic_model",
    "open_cfw_am145_0x5a6d10_semantic_model",
    "open_cfw_am145_0x5a67d2_semantic_model",
    "open_cfw_am145_0x5a6822_semantic_model",
    "open_cfw_am145_0x5a6e34_semantic_model",
    "open_cfw_am145_0x5a6e4a_semantic_model",
    "open_cfw_am145_0x5a6eb6_semantic_model",
    "open_cfw_am145_0x5a6f5c_semantic_model",
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
    with tempfile.TemporaryDirectory(prefix="g2-am145-pullthrough-") as tmp:
        object_path = Path(tmp) / "runtime_liblc3_am145_semantic_model.o"
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
            raise RuntimeError("AM145 pull-through target symbols changed")
        undefined_symbols = _undefined_symbols(object_path)
        if undefined_symbols:
            raise RuntimeError("AM145 pull-through object gained undefined symbols")
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
            raise RuntimeError("AM145 pull-through object gained unexpected relocations")
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
                "0x005a340c",
                "0x005a34ca",
                "0x005a35a4",
                "0x005a36ac",
                "0x005a3798",
                "0x005a3980",
                "0x005a3a10",
                "0x005a3ab0",
                "0x005a3bcc",
                "0x005a3cc6",
                "0x005a3e24",
                "0x005a3fe8",
                "0x005a40ca",
                "0x005a4a66",
                "0x005a4b36",
                "0x005a4802",
                "0x005a487a",
                "0x005a490c",
                "0x005a63c8",
                "0x005a6596",
                "0x005a659a",
                "0x005a65a2",
                "0x005a65b0",
                "0x005a66cc",
                "0x005a674a",
                "0x005a6c52",
                "0x005a6c5e",
                "0x005a6c7c",
                "0x005a6c94",
                "0x005a6ca2",
                "0x005a6cb0",
                "0x005a6d10",
                "0x005a67d2",
                "0x005a6822",
                "0x005a6e34",
                "0x005a6e4a",
                "0x005a6eb6",
                "0x005a6f5c",
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
