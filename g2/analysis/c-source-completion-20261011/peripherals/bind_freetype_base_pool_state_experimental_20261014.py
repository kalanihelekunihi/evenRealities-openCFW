#!/usr/bin/env python3
"""Build pinned FreeType base/gzip support for pooled Main module classes."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-freetype-modules-current-receipt.json"
BUILDER = G2 / "build/c-firmware/20261013/peripherals-root-hci-control-layout-round437/receipt.json"
UP = ROOT / "third-party/upstream/freetype"
BOUND = OUT / "apollo-main-pool-state-freetype-base-bound.o"
RECEIPT = OUT / "pool-state-freetype-base-current-receipt.json"
RENAMES = {
    "ftgloadr.c": ("FT_GlyphLoader_CreateExtra", "FT_GlyphLoader_Rewind"),
    "ftstream.c": ("FT_Stream_Close", "FT_Stream_OpenMemory", "FT_Stream_Read",
                   "FT_Stream_ReadAt", "FT_Stream_ReadULong", "FT_Stream_ReadUShort",
                   "FT_Stream_Seek", "FT_Stream_Skip"),
    "ftobjs.c": ("FT_Get_Module", "FT_Lookup_Renderer", "FT_Stream_Free"),
    "ftutil.c": ("FT_List_Add", "FT_List_Finalize", "FT_List_Find",
                   "ft_mem_alloc", "ft_mem_free", "ft_mem_qalloc",
                   "ft_mem_qrealloc", "ft_mem_realloc"),
    "ftrfork.c": ("FT_Raccess_Get_DataOffsets", "FT_Raccess_Get_HeaderInfo", "FT_Raccess_Guess"),
}


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
    builder = json.loads(BUILDER.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_MODULES_C"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    assert subprocess.check_output(["git", "-C", str(UP), "rev-parse", "HEAD"], text=True).strip() == base["upstream_commit"]
    rows = builder["images"]["apollo_main"]["experimental_compile"][8:21]
    assert len(rows) == 13
    include = [G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include",
               G2 / "config-recovered/freetype/g2-config", UP / "include"]
    objects, units = [], []
    definitions = global_defs(prior)
    for row in rows:
        source = ROOT / row["source"]
        assert source.is_file() and row["source_sha256"] == sha(source)
        obj = OUT / f"freetype-base-{source.stem}-pool-state-abi.o"
        flags = [f"-D{name}=experimental_upstream_{name}" for name in RENAMES.get(source.name, ())]
        if source.name == "ftgzip.c":
            flags.append("-DNO_ERRNO_H")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Wno-cast-function-type-mismatch",
                        "-DFT2_BUILD_LIBRARY", *(f"-I{x}" for x in include), *flags,
                        "-c", str(source), "-o", str(obj)], check=True)
        current = global_defs(obj)
        assert current and not (current & definitions), (source.name, current & definitions)
        definitions |= current
        objects.append(obj)
        units.append({"source": row["source"], "source_sha256": sha(source),
                      "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                      "global_definitions": len(current), "source_renames": RENAMES.get(source.name, ())})
    before = symbols(["-u"], prior)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    removed, added = sorted(before - after), sorted(after - before)
    assert len(removed) >= 50 and len(added) <= 20
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_BASE_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "upstream_commit": base["upstream_commit"], "source_units": units,
               "imports_resolved": removed, "imports_added": added,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned FreeType base/gzip source is C linked; individual stock body equivalence and full provider closure remain open.",
                         "The 128-byte jump-buffer overlay is analysis-only; final ABI, placement and hardware operation remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), len(removed), len(added), sha(RECEIPT))


if __name__ == "__main__":
    main()
