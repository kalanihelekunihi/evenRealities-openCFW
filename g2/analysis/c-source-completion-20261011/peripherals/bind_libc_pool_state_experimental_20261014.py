#!/usr/bin/env python3
"""Compile pinned portable libc C bodies needed by pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-memmove-current-receipt.json"
UP = ROOT / "third-party/upstream/nationalchip-lvp-kws"
LIBC = UP / "utility/libc"
STRSTR = G2 / "analysis/c-source-completion-20261011/peripherals/root-strstr-round432/candidate_strstr.c"
STRSTR_RECEIPT = STRSTR.with_name("strstr-receipt.json")
STRTOL_RECEIPT = G2 / "analysis/c-source-completion-20261011/peripherals/root-strtol-round431/strtol-receipt.json"
SOURCES = (LIBC / "memchr.c", LIBC / "strcmp.c", LIBC / "strcpy.c",
           LIBC / "strtol.c", LIBC / "strntoumax.c", LIBC / "memmem.c", STRSTR)
NAMES = {"memchr", "strcmp", "strcpy", "strtol", "strstr"}
BOUND = OUT / "apollo-main-pool-state-portable-libc-bound.o"
RECEIPT = OUT / "pool-state-portable-libc-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def global_defs(p):
    return {parts[2] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(p)], text=True).splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def main():
    base = json.loads(BASE.read_text())
    strstr = json.loads(STRSTR_RECEIPT.read_text())
    strtol = json.loads(STRTOL_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_BOUNDED_NATIVE_MEMMOVE_C_JOIN"
    assert strstr["status"] == "completed" and strtol["status"] == "completed"
    assert strstr["host_edge_test"]["result"] == "pass"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    include_common = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"
    include_conversion = [UP / "include/utility/libc",
                          ROOT / "third-party/reference/ambiq-zephyr/lib/libc/minimal/include",
                          LIBC / "templates"]
    definitions = global_defs(prior)
    objects, units = [], []
    for source in SOURCES:
        obj = OUT / f"portable-libc-{source.stem}-pool-state-abi.o"
        include = include_conversion if source.stem in ("strtol", "strntoumax") else [include_common]
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", *(f"-I{x}" for x in include),
                        "-c", str(source), "-o", str(obj)], check=True)
        current = global_defs(obj)
        assert current and not (current & definitions), (source.name, current & definitions)
        definitions |= current
        objects.append(obj)
        units.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                      "global_definitions": len(current)})
    assert NAMES <= definitions
    before = symbols(["-u"], prior)
    assert NAMES <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert after == before - NAMES
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_PORTABLE_LIBC_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "strstr_evidence": str(STRSTR_RECEIPT.relative_to(ROOT)), "strstr_evidence_sha256": sha(STRSTR_RECEIPT),
               "strtol_evidence": str(STRTOL_RECEIPT.relative_to(ROOT)), "strtol_evidence_sha256": sha(STRTOL_RECEIPT),
               "source_units": units, "imports_resolved": sorted(NAMES), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Portable libc source implements C semantics; stock Main implementation identity and full input-domain equivalence are unproved.",
                         "The strstr host edge matrix is bounded; final placement and hardware behavior remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
