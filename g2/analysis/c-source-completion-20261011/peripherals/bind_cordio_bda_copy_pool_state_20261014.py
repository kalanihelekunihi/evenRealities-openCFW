#!/usr/bin/env python3
"""Select only pinned Cordio BdaCpy from upstream source into Main pool."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
UP = ROOT / "third-party/upstream/cordio"
SOURCE = UP / "wsf/sources/util/bda.c"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-decoders-current-receipt.json"
FULL = OUT / "cordio-bda-upstream-full.o"
TRIM = OUT / "cordio-bda-copy-rooted.o"
OBJECT = OUT / "cordio-bda-copy-rooted-stripped.o"
BOUND = OUT / "apollo-main-pool-state-cordio-bda-copy-bound.o"
RECEIPT = OUT / "pool-state-cordio-bda-copy-current-receipt.json"
NAME = "BdaCpy"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def syms(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_HCI_DECODERS_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    assert subprocess.check_output(["git", "-C", str(UP), "rev-parse", "HEAD"], text=True).strip() == "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
    assert sha(SOURCE) == "f60d668469ca1ad0d855cbbe28c6d297566a42664cad95779f9697764463ffe0"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-fno-builtin", "-O2", "-ffunction-sections",
                    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
                    "-I", str(G2 / "config-recovered/cordio/g2-compat-include"),
                    "-I", str(UP / "wsf/include"), "-c", str(SOURCE), "-o", str(FULL)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections", f"--undefined={NAME}",
                    str(FULL), "-o", str(TRIM)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "--strip-unneeded", str(TRIM), str(OBJECT)], check=True)
    with OBJECT.open("rb") as stream:
        elf = ELFFile(stream)
        symbol, = [s for s in elf.get_section_by_name(".symtab").iter_symbols() if s.name == NAME]
        assert symbol["st_size"] == 6
        assert elf.get_section(symbol["st_shndx"]).name == ".text.BdaCpy"
    assert syms(["--defined-only"], OBJECT) == {NAME}
    assert syms(["-u"], OBJECT) == {"memcpy"}
    before = syms(["-u"], prior)
    assert NAME in before and "memcpy" in syms(["--defined-only"], prior)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = syms(["-u"], BOUND)
    assert after == before - {NAME}
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_PINNED_CORDIO_BDA_COPY_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "upstream_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "rooted_object": str(OBJECT.relative_to(ROOT)), "rooted_object_sha256": sha(OBJECT),
               "imports_resolved": [NAME], "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned Cordio utility source and ABI are available; stock BdaCpy native body and full call domain remain unqualified.",
                         "Other HCI runtime imports and Main placement remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
