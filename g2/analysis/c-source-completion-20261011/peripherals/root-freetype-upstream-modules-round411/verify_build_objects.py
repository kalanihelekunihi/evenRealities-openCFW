#!/usr/bin/env python3
"""Audit the coordinated builder's eight pinned FreeType objects against native class data."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
BUILD = ROOT / "g2/build/c-firmware/20261013/peripherals-root-freetype-upstream-modules-round411"
NATIVE = Path("/tmp/opencfw-main-native.bin")
INVENTORY = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-freetype-new-library-round370/default-module-inventory.json"
MODULES = ["autofit/autofit", "truetype/truetype", "cff/cff", "psaux/psaux",
           "psnames/psnames", "pshinter/pshinter", "sfnt/sfnt", "smooth/smooth"]
CLASSES = ["autofit_module_class", "tt_driver_class", "cff_driver_class",
           "psaux_module_class", "psnames_module_class", "pshinter_module_class",
           "sfnt_module_class", "ft_smooth_renderer_class",
           "ft_smooth_lcd_renderer_class", "ft_smooth_lcdv_renderer_class"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


receipt = json.loads((BUILD / "receipt.json").read_text())
rows = receipt["images"]["apollo_main"]["experimental_compile"][:8]
assert len(rows) == 8 and sha(NATIVE) == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
inventory = json.loads(INVENTORY.read_text())
native = NATIVE.read_bytes()
found = {}
for row, module in zip(rows, MODULES):
    source = ROOT / "third-party/upstream/freetype/src" / (module + ".c")
    obj = ROOT / row["object"]
    assert row["source"] == str(source.relative_to(ROOT))
    assert row["returncode"] == 0 and row["source_sha256"] == sha(source)
    assert row["object_sha256"] == sha(obj)
    assert row["compile_source_snapshot"]["stable_during_command"]
    assert any(name.endswith("freestanding_include/setjmp.h") for name in row["header_inputs"])
    with obj.open("rb") as handle:
        elf = ELFFile(handle)
        symtab = elf.get_section_by_name(".symtab")
        for symbol in symtab.iter_symbols():
            if symbol.name not in CLASSES:
                continue
            size = symbol["st_size"]
            assert size >= 32 and size % 4 == 0
            offset = symbol["st_value"]
            section = elf.get_section(symbol["st_shndx"])
            words = struct.unpack("<" + "I" * (size // 4), section.data()[offset:offset + size])
            expected = inventory["classes"][CLASSES.index(symbol.name)]
            native_offset = int(expected["address"], 16) - 0x438000
            assert 0 <= native_offset <= len(native) - size
            native_words = struct.unpack_from("<" + "I" * (size // 4), native, native_offset)
            relocated = set()
            for reloc_section in elf.iter_sections():
                if reloc_section["sh_type"] not in ("SHT_REL", "SHT_RELA") or reloc_section["sh_info"] != symbol["st_shndx"]:
                    continue
                for reloc in reloc_section.iter_relocations():
                    if offset <= reloc["r_offset"] < offset + size:
                        assert (reloc["r_offset"] - offset) % 4 == 0
                        relocated.add((reloc["r_offset"] - offset) // 4)
            assert all((native_words[i] != 0 and 0x438000 <= (native_words[i] & ~1) < 0x438000 + len(native))
                       if i in relocated else words[i] == native_words[i]
                       for i in range(len(words))), symbol.name
            found[symbol.name] = {"object": row["object"], "words": len(words),
                                  "relocation_slots": len(relocated)}
assert set(found) == set(CLASSES)
link = receipt["images"]["apollo_main"]["relocatable_link"]
assert link["returncode"] == 0 and not link["duplicate_strong_symbols"]
assert not set(CLASSES) & set(link["unresolved_symbols"])
names = subprocess.check_output(["arm-none-eabi-nm", "-g", str(ROOT / link["output"])], text=True)
assert all(any(line.endswith(" " + name) and " U " not in line for line in names.splitlines())
           for name in CLASSES)
out = {"status": "PASS_COORDINATED_EXPERIMENTAL_FREETYPE_CLASS_OBJECT_BUILD",
       "build_receipt_sha256": sha(BUILD / "receipt.json"),
       "native_oracle_sha256": sha(NATIVE),
       "freetype_submodule_commit": subprocess.check_output(
           ["git", "-C", str(ROOT / "third-party/upstream/freetype"), "rev-parse", "HEAD"], text=True).strip(),
       "module_source_count": len(rows), "class_objects": found,
       "class_word_count": sum(item["words"] for item in found.values()),
       "class_pointer_slots": sum(item["relocation_slots"] for item in found.values()),
       "definitions": len(link["defined_symbols"]), "imports": len(link["unresolved_symbols"]),
       "duplicate_strong_symbols": 0,
       "limits": ["Experimental builder path only; callback behavior and provider closure unverified",
                  "128-byte jump buffer overlay is native-layout analysis, not a production libc header",
                  "Full image layout, byte identity and hardware operation unverified"]}
(HERE / "builder-class-receipt.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({"status": out["status"], "classes": len(found),
                  "words": out["class_word_count"], "imports": out["imports"]}))
