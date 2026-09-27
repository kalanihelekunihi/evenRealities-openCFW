#!/usr/bin/env python3
"""Verify the AM142 retained hot-target semantic model as a target object."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am142_semantic_model.c"
)
OUT = ROOT / "tools/manifests/g2-apollo-am142-pullthrough-candidate.json"
EXPECTED_SYMBOLS = [
    "open_cfw_am142_0x4ec718_semantic_model",
    "open_cfw_am142_0x4ec774_semantic_model",
    "open_cfw_am142_0x59aa84_semantic_model",
    "open_cfw_am142_0x59aec8_semantic_model",
    "open_cfw_am142_0x59af1e_semantic_model",
    "open_cfw_am142_0x59af42_semantic_model",
    "open_cfw_am142_0x59af54_semantic_model",
    "open_cfw_am142_0x59afa0_semantic_model",
    "open_cfw_am142_0x59a312_semantic_model",
    "open_cfw_am142_0x59a3d2_semantic_model",
    "open_cfw_am142_0x59b00e_semantic_model",
    "open_cfw_am142_0x59b272_semantic_model",
    "open_cfw_am142_0x59b2aa_semantic_model",
    "open_cfw_am142_0x59b33e_semantic_model",
    "open_cfw_am142_0x59b382_semantic_model",
    "open_cfw_am142_0x59b3de_semantic_model",
    "open_cfw_am142_0x59b454_semantic_model",
    "open_cfw_am142_0x59b52c_semantic_model",
    "open_cfw_am142_0x59b53c_semantic_model",
    "open_cfw_am142_0x59b654_semantic_model",
    "open_cfw_am142_0x59ba4a_semantic_model",
    "open_cfw_am142_0x59cb1e_semantic_model",
    "open_cfw_am142_0x59cb44_semantic_model",
    "open_cfw_am142_0x59cb6c_semantic_model",
    "open_cfw_am142_0x59cb98_semantic_model",
    "open_cfw_am142_0x59c052_semantic_model",
    "open_cfw_am142_0x59c060_semantic_model",
    "open_cfw_am142_0x59c530_semantic_model",
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
    objdump = _llvm_objdump()
    proc = subprocess.run(
        [objdump, "-r", str(object_path)],
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
    with tempfile.TemporaryDirectory(prefix="g2-am142-pullthrough-") as tmp:
        object_path = Path(tmp) / "runtime_liblc3_am142_semantic_model.o"
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
            raise RuntimeError("AM142 pull-through target symbols changed")
        undefined_symbols = _undefined_symbols(object_path)
        if undefined_symbols:
            raise RuntimeError("AM142 pull-through object gained undefined symbols")
        relocations = _relocations(object_path)
        relocation_kinds = {
            (row["section"], row["type"], row["value"])
            for row in relocations
        }
        if relocation_kinds - {
                (
                    ALLOWED_RELOCATION["section"],
                    ALLOWED_RELOCATION["type"],
                    ALLOWED_RELOCATION["value"],
                )}:
            raise RuntimeError("AM142 pull-through object gained unexpected relocations")
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
                "0x004ec718",
                "0x004ec774",
                "0x0059aa84",
                "0x0059aec8",
                "0x0059af1e",
                "0x0059af42",
                "0x0059af54",
                "0x0059afa0",
                "0x0059a312",
                "0x0059a3d2",
                "0x0059b00e",
                "0x0059b272",
                "0x0059b2aa",
                "0x0059b33e",
                "0x0059b382",
                "0x0059b3de",
                "0x0059b454",
                "0x0059b52c",
                "0x0059b53c",
                "0x0059b654",
                "0x0059ba4a",
                "0x0059cb1e",
                "0x0059cb44",
                "0x0059cb6c",
                "0x0059cb98",
                "0x0059c052",
                "0x0059c060",
                "0x0059c530",
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
