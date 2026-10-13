#!/usr/bin/env python3
"""Compile the pinned FreeType class sources and audit an analysis-only Main link."""
from pathlib import Path
import hashlib
import json
import shlex
import struct
import subprocess

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
UPSTREAM = ROOT / "third-party/upstream/freetype"
CONFIG = ROOT / "g2/config-recovered/freetype/g2-config"
OVERLAY = HERE / "freestanding_include"
OUT = HERE / "objects"
MAIN = ROOT / "g2/build/c-firmware/20261013/peripherals-root-freetype-qalloc-round410/apollo_main/candidate.o"
MODULES = ["autofit/autofit", "truetype/truetype", "cff/cff", "psaux/psaux",
           "psnames/psnames", "pshinter/pshinter", "sfnt/sfnt", "smooth/smooth"]
CLASSES = ["autofit_module_class", "tt_driver_class", "cff_driver_class",
           "psaux_module_class", "psnames_module_class", "pshinter_module_class",
           "sfnt_module_class", "ft_smooth_renderer_class",
           "ft_smooth_lcd_renderer_class", "ft_smooth_lcdv_renderer_class"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def census(path):
    text = subprocess.check_output(["arm-none-eabi-nm", "-g", str(path)], text=True)
    definitions, unresolved, duplicates = set(), set(), set()
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        kind, name = parts[-2:]
        if kind == "U":
            unresolved.add(name)
        elif kind in "TDRBSCWVA":
            if name in definitions and kind not in "WV":
                duplicates.add(name)
            definitions.add(name)
    return definitions, unresolved - definitions, duplicates


def main():
    OUT.mkdir(exist_ok=True)
    flags = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
             "-O2", "-ffreestanding", "-fno-builtin", "-DFT2_BUILD_LIBRARY",
             "-I", str(OVERLAY), "-I", str(CONFIG), "-I", str(UPSTREAM / "include")]
    objects, sources, headers = [], [], {}
    for module in MODULES:
        source = UPSTREAM / "src" / (module + ".c")
        obj = OUT / (module.split("/")[0] + ".o")
        dep = obj.with_suffix(".d")
        cmd = flags + ["-MD", "-MF", str(dep), "-c", str(source), "-o", str(obj)]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if proc.returncode:
            raise RuntimeError(f"{module}: {proc.stderr[:1200]}")
        objects.append(obj)
        sources.append({"path": str(source.relative_to(ROOT)), "sha256": sha(source),
                        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj)})
        deptext = dep.read_text().replace("\\\n", " ").split(":", 1)[1]
        for name in shlex.split(deptext):
            path = Path(name)
            if not path.is_absolute():
                path = ROOT / path
            if path.is_file() and path.is_relative_to(ROOT):
                headers[str(path.relative_to(ROOT))] = sha(path)

    inventory = json.loads((ROOT / "g2/analysis/c-source-completion-20261011/peripherals"
                            "/root-freetype-new-library-round370/default-module-inventory.json").read_text())
    native_path = Path("/tmp/opencfw-main-native.bin")
    native = native_path.read_bytes()
    native_sha = sha(native_path)
    assert native_sha == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    found = {}
    for obj in objects:
        with obj.open("rb") as handle:
            elf = ELFFile(handle)
            symtab = elf.get_section_by_name(".symtab")
            for symbol in symtab.iter_symbols():
                if symbol.name not in CLASSES:
                    continue
                section = elf.get_section(symbol["st_shndx"])
                size = symbol["st_size"]
                assert size % 4 == 0 and size >= 32
                offset = symbol["st_value"]
                words = struct.unpack("<" + "I" * (size // 4),
                                      section.data()[offset:offset + size])
                expected = inventory["classes"][CLASSES.index(symbol.name)]
                scalar_positions = (0, 1, 3, 4)
                assert all(words[i] == int(expected["class_words"][i], 16)
                           for i in scalar_positions), symbol.name
                native_offset = int(expected["address"], 16) - 0x438000
                assert 0 <= native_offset <= len(native) - size
                native_words = struct.unpack_from("<" + "I" * (size // 4),
                                                  native, native_offset)
                relocations = {}
                for reloc_section in elf.iter_sections():
                    if reloc_section["sh_type"] not in ("SHT_REL", "SHT_RELA") or reloc_section["sh_info"] != symbol["st_shndx"]:
                        continue
                    for reloc in reloc_section.iter_relocations():
                        if offset <= reloc["r_offset"] < offset + size:
                            assert (reloc["r_offset"] - offset) % 4 == 0
                            index = (reloc["r_offset"] - offset) // 4
                            relocations[index] = symtab.get_symbol(reloc["r_info_sym"]).name
                mismatches = [index for index, (source_word, native_word)
                              in enumerate(zip(words, native_words))
                              if (index in relocations and native_word == 0)
                              or (index not in relocations and source_word != native_word)]
                assert not mismatches, (symbol.name, mismatches)
                assert all(0x438000 <= (native_words[i] & ~1) < 0x438000 + len(native)
                           for i in relocations), symbol.name
                found[symbol.name] = {"object": str(obj.relative_to(ROOT)),
                                      "size": size,
                                      "scalar_words_match": list(scalar_positions),
                                      "native_address": expected["address"],
                                      "full_word_shape_match": size // 4,
                                      "relocation_slots": {str(i): relocations[i]
                                                           for i in sorted(relocations)},
                                      "native_pointer_values": {str(i): hex(native_words[i])
                                                                for i in sorted(relocations)}}
    assert set(found) == set(CLASSES)

    combined = HERE / "main-plus-upstream-classes.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(MAIN), *map(str, objects),
                    "-o", str(combined)], cwd=ROOT, check=True)
    before_defs, before_imports, _ = census(MAIN)
    after_defs, after_imports, duplicates = census(combined)
    assert not duplicates
    assert set(CLASSES).issubset(before_imports) and not set(CLASSES) & after_imports
    runtime = sorted({name for obj in objects for name in census(obj)[1]
                      if name in {"setjmp", "longjmp"}})
    receipt = {
        "status": "PASS_ANALYSIS_ONLY_UPSTREAM_CLASS_COMPILE_AND_SIDE_LINK",
        "freetype_submodule_commit": subprocess.check_output(
            ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True).strip(),
        "compiler": subprocess.check_output(["clang", "--version"], text=True).splitlines()[0],
        "main_candidate": {"path": str(MAIN.relative_to(ROOT)), "sha256": sha(MAIN)},
        "native_oracle": {"path": str(native_path), "sha256": native_sha,
                          "load_address": "0x438000"},
        "modules": sources,
        "header_sha256": dict(sorted(headers.items())),
        "class_objects": {name: found[name] for name in CLASSES},
        "combined": {"path": str(combined.relative_to(ROOT)), "sha256": sha(combined),
                     "definitions": len(after_defs), "imports": len(after_imports),
                     "duplicate_strong_symbols": sorted(duplicates),
                     "class_imports_removed": CLASSES,
                     "new_import_count": len(after_imports - before_imports),
                     "new_imports": sorted(after_imports - before_imports)},
        "runtime_abi_unverified": runtime,
        "newlib_arm_candidate": {
            "provenance": str((HERE / "newlib-source/provenance.json").relative_to(ROOT)),
            "provenance_sha256": sha(HERE / "newlib-source/provenance.json"),
            "jmp_buf_bytes": 160,
            "status": "rejected_for_native_gray_worker_layout"},
        "native_jump_buffer_compile_layout": {
            "bytes": 128,
            "basis": "native gray_TWorker first following field at offset 0x80 and native setjmp saves 104 bytes",
            "status": "analysis_only_runtime_provider_unqualified"},
        "limits": ["Compile-only 128-byte jump buffer based on native field offsets; runtime setjmp/longjmp provider and callbacks unqualified",
                   "Scalar class fields match native inventory; pointer relocations and runtime behavior do not",
                   "Side link is not selected production Main build or a complete firmware image"],
    }
    (HERE / "source-link-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "classes": len(found),
                      "definitions": len(after_defs), "imports": len(after_imports),
                      "runtime_abi_unverified": runtime}))


if __name__ == "__main__":
    main()
