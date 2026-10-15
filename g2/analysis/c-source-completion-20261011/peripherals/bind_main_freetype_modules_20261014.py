#!/usr/bin/env python3
"""Rebuild pinned FreeType modules and bind their native-matched classes to Main."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
PRIOR = OUT / "nema-mode-current-receipt.json"
BASE = OUT / "apollo-main-nema-mode-bound.o"
PINNED = G2 / "build/c-firmware/20261013/peripherals-root-freetype-upstream-modules-round411/receipt.json"
INVENTORY = G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-new-library-round370/default-module-inventory.json"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OBJECTS = OUT / "freetype-modules-current"
BOUND = OUT / "apollo-main-freetype-modules-bound.o"
RECEIPT = OUT / "freetype-modules-current-receipt.json"
MODULES = ("autofit/autofit", "truetype/truetype", "cff/cff", "psaux/psaux",
           "psnames/psnames", "pshinter/pshinter", "sfnt/sfnt", "smooth/smooth")
CLASSES = ("autofit_module_class", "tt_driver_class", "cff_driver_class",
           "psaux_module_class", "psnames_module_class", "pshinter_module_class",
           "sfnt_module_class", "ft_smooth_renderer_class",
           "ft_smooth_lcd_renderer_class", "ft_smooth_lcdv_renderer_class")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    output = subprocess.check_output(["arm-none-eabi-nm", *flags, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def validate_class_words(obj, native, expected, found):
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symtab = elf.get_section_by_name(".symtab")
        for symbol in symtab.iter_symbols():
            if symbol.name not in CLASSES:
                continue
            size = symbol["st_size"]
            assert size >= 32 and size % 4 == 0
            offset = symbol["st_value"]
            section = elf.get_section(symbol["st_shndx"])
            words = struct.unpack("<" + "I" * (size // 4),
                                  section.data()[offset:offset + size])
            address = int(expected[symbol.name]["address"], 16)
            native_offset = address - 0x438000
            assert 0 <= native_offset <= len(native) - size
            stock_words = struct.unpack_from("<" + "I" * (size // 4), native,
                                             native_offset)
            relocated = set()
            for reloc_section in elf.iter_sections():
                if reloc_section["sh_type"] not in ("SHT_REL", "SHT_RELA") or \
                        reloc_section["sh_info"] != symbol["st_shndx"]:
                    continue
                for reloc in reloc_section.iter_relocations():
                    if offset <= reloc["r_offset"] < offset + size:
                        assert (reloc["r_offset"] - offset) % 4 == 0
                        relocated.add((reloc["r_offset"] - offset) // 4)
            for index, word in enumerate(words):
                if index in relocated:
                    pointer = stock_words[index] & ~1
                    assert stock_words[index] != 0 and 0x438000 <= pointer < 0x438000 + len(native)
                else:
                    assert word == stock_words[index], (symbol.name, index, word, stock_words[index])
            assert symbol.name not in found
            found[symbol.name] = {"object": str(obj.relative_to(ROOT)),
                                  "words": len(words), "relocation_slots": len(relocated)}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_NEMA_MODE_C"
    assert sha(BASE) == prior["output_sha256"]
    before = names(BASE, "-u")
    assert len(before) == 562 and set(CLASSES) <= before
    assert sha(STOCK) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
    assert subprocess.check_output(
        ["git", "-C", str(ROOT / "third-party/upstream/freetype"), "rev-parse", "HEAD"],
        text=True).strip() == "86bc8a95056c97a810986434a3f268cbe67f2902"
    pinned = json.loads(PINNED.read_text())
    rows = pinned["images"]["apollo_main"]["experimental_compile"][:8]
    inventory = json.loads(INVENTORY.read_text())
    expected = {name: inventory["classes"][index] for index, name in enumerate(CLASSES)}
    native = STOCK.read_bytes()[32:]
    OBJECTS.mkdir(parents=True, exist_ok=True)
    objects = []
    source_rows = []
    found = {}
    for index, (row, module) in enumerate(zip(rows, MODULES)):
        source = ROOT / "third-party/upstream/freetype/src" / (module + ".c")
        obj = OBJECTS / (f"module-{index:02d}.o")
        deps = OBJECTS / (f"module-{index:02d}.d")
        assert row["returncode"] == 0 and row["source"] == str(source.relative_to(ROOT))
        assert row["source_sha256"] == sha(source)
        argv = list(row["argv"])
        assert argv[0] == "clang" and argv[argv.index("-c") + 1] == str(source)
        argv[argv.index("-MF") + 1] = str(deps)
        argv[argv.index("-o") + 1] = str(obj)
        subprocess.run(argv, cwd=ROOT, check=True, capture_output=True)
        validate_class_words(obj, native, expected, found)
        objects.append(obj)
        source_rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                            "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
    assert set(found) == set(CLASSES)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(BOUND)], cwd=ROOT, check=True, capture_output=True)
    after = names(BOUND, "-u")
    resolved = before - after
    added = after - before
    assert set(CLASSES) <= resolved and not set(CLASSES) & after
    assert len(after) == 645 and len(added) == 93 and len(resolved) == 10
    receipt = {
        "status": "PASS_CURRENT_MAIN_FREETYPE_MODULE_C_LINK",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "pinned_build_receipt": str(PINNED.relative_to(ROOT)),
        "pinned_build_receipt_sha256": sha(PINNED),
        "inventory": str(INVENTORY.relative_to(ROOT)), "inventory_sha256": sha(INVENTORY),
        "stock_sha256": sha(STOCK),
        "freetype_submodule_commit": "86bc8a95056c97a810986434a3f268cbe67f2902",
        "source_units": source_rows, "class_words": found,
        "class_word_count": sum(v["words"] for v in found.values()),
        "class_pointer_slots": sum(v["relocation_slots"] for v in found.values()),
        "imports_resolved": sorted(resolved), "imports_added": sorted(added),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native class fixed words and pointer slots verified; callback behavior not verified",
                   "93 upstream lower-level imports remain newly exposed for source closure",
                   "Whole-image layout and physical device behavior remain unverified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "unresolved_after": len(after),
                      "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
