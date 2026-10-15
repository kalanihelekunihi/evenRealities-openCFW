#!/usr/bin/env python3
"""Bind eight current pinned FreeType module objects to pooled Main."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-power-vendor-current-receipt.json"
BUILDER = G2 / "build/c-firmware/20261013/peripherals-root-freetype-upstream-modules-round411/receipt.json"
EVIDENCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-upstream-modules-round411/builder-class-receipt.json"
INVENTORY = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-new-library-round370/default-module-inventory.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOUND = OUT / "apollo-main-pool-state-freetype-modules-bound.o"
RECEIPT = OUT / "pool-state-freetype-modules-current-receipt.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def global_defs(p):
    return {parts[2] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", "--defined-only", str(p)], text=True).splitlines()
            if len(parts := line.split()) == 3 and parts[1].isupper()}


def check_class(obj, name, address, native):
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        symbol, = [s for s in symtab.iter_symbols() if s.name == name]
        size, offset = symbol["st_size"], symbol["st_value"]
        assert size >= 32 and size % 4 == 0
        section = elf.get_section(symbol["st_shndx"])
        words = struct.unpack("<" + "I" * (size // 4), section.data()[offset:offset + size])
        stock_offset = address - 0x438000
        native_words = struct.unpack_from("<" + "I" * (size // 4), native, stock_offset)
        relocated = set()
        for reloc_sec in elf.iter_sections():
            if reloc_sec["sh_type"] not in ("SHT_REL", "SHT_RELA") or reloc_sec["sh_info"] != symbol["st_shndx"]:
                continue
            for reloc in reloc_sec.iter_relocations():
                if offset <= reloc["r_offset"] < offset + size:
                    assert (reloc["r_offset"] - offset) % 4 == 0
                    relocated.add((reloc["r_offset"] - offset) // 4)
        for i, (actual, original) in enumerate(zip(words, native_words)):
            if i in relocated:
                assert 0x438000 <= (original & ~1) < 0x438000 + len(native)
            else:
                assert actual == original, (name, i)
        return {"words": len(words), "pointer_relocations": len(relocated)}


def main():
    base = json.loads(BASE.read_text())
    builder = json.loads(BUILDER.read_text())
    evidence = json.loads(EVIDENCE.read_text())
    inventory = json.loads(INVENTORY.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_APOLLO_POWER_C"
    assert evidence["status"] == "PASS_COORDINATED_EXPERIMENTAL_FREETYPE_CLASS_OBJECT_BUILD"
    prior = ROOT / base["linked_object"]
    assert sha(prior) == base["linked_sha256"]
    upstream = ROOT / "third-party/upstream/freetype"
    pin = subprocess.check_output(["git", "-C", str(upstream), "rev-parse", "HEAD"], text=True).strip()
    assert pin == evidence["freetype_submodule_commit"]
    native = STOCK.read_bytes()[32:]
    assert hashlib.sha256(native).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    rows = builder["images"]["apollo_main"]["experimental_compile"][:8]
    objects, units = [], []
    definitions = global_defs(prior)
    checked = {}
    include = [G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include",
               G2 / "config-recovered/freetype/g2-config", upstream / "include"]
    for row in rows:
        source, historical = ROOT / row["source"], ROOT / row["object"]
        assert row["returncode"] == 0 and row["source_sha256"] == sha(source)
        assert row["object_sha256"] == sha(historical)
        obj = OUT / f"freetype-module-{source.parent.name}-pool-state-abi.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Wno-cast-function-type-mismatch", "-DFT2_BUILD_LIBRARY",
                        *(f"-I{x}" for x in include), "-c", str(source), "-o", str(obj)], check=True)
        current = global_defs(obj)
        assert not (current & definitions), current & definitions
        definitions |= current
        objects.append(obj)
        units.append({"source": row["source"], "source_sha256": sha(source),
                      "historical_object": row["object"], "historical_object_sha256": sha(historical),
                      "pool_abi_object": str(obj.relative_to(ROOT)), "pool_abi_object_sha256": sha(obj),
                      "global_definitions": len(current)})
        for name, item in zip(evidence["class_objects"], inventory["classes"]):
            if name in current:
                checked[name] = check_class(obj, name, int(item["address"], 16), native)
    assert set(checked) == set(evidence["class_objects"]), set(evidence["class_objects"]) - set(checked)
    assert sum(x["words"] for x in checked.values()) == evidence["class_word_count"]
    assert sum(x["pointer_relocations"] for x in checked.values()) == evidence["class_pointer_slots"]
    before = symbols(["-u"], prior)
    assert set(checked) <= before
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), *(str(p) for p in objects),
                    "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    assert set(checked) <= before - after
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_FREETYPE_MODULES_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "builder_receipt": str(BUILDER.relative_to(ROOT)), "builder_receipt_sha256": sha(BUILDER),
               "class_evidence": str(EVIDENCE.relative_to(ROOT)), "class_evidence_sha256": sha(EVIDENCE),
               "upstream_commit": pin, "source_units": units, "stock_payload_sha256": hashlib.sha256(native).hexdigest(),
               "native_class_checks": checked, "imports_resolved": sorted(before - after),
               "imports_added": sorted(after - before),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Class data fields and pointer slots match native records, but callback body behavior and full FreeType provider closure remain open.",
                         "The 128-byte jump-buffer overlay is analysis-only; final ABI, placement and hardware operation remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), len(before - after), len(after - before), sha(RECEIPT))


if __name__ == "__main__":
    main()
