#!/usr/bin/env python3
"""Compose pinned FreeType and portable libc C into the current Main graph.

setjmp/longjmp remain explicit ARM ABI contracts; no host stdio provider is used.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-freetype-source-closure"
BASE = G2 / "build/c-firmware/20261014/main-logger-provider-closure/apollo-main-logger-providers.o"
PRIOR = G2 / "build/c-firmware/20261014/main-root-dependencies"
MANIFEST = G2 / "firmware_c/experimental-link-aliases.json"
SDK = ROOT / "third-party/upstream/nationalchip-lvp-kws/utility/libc"
LIBC = ("memchr", "memmove", "strcmp", "strcpy", "memmem", "strstr",
        "strtol", "strntoumax")
ALIASES = ("FT_Stream_Open", "__aeabi_memcpy4", "qsort", "strcat",
           "strlen", "strncmp", "strncpy", "strrchr")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, option):
    output = subprocess.check_output(["arm-none-eabi-nm", option, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def link(name, *parts):
    path = OUT / name
    subprocess.run(["arm-none-eabi-ld", "-r", *map(str, parts), "-o", str(path)],
                   check=True)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    objects = []
    upstream = {}
    receipts = {}
    for name in ("freetype-modules-current-receipt.json",
                 "freetype-base-current-receipt.json"):
        path = PRIOR / name
        old = json.loads(path.read_text())
        if old["freetype_submodule_commit"] != "86bc8a95056c97a810986434a3f268cbe67f2902":
            raise RuntimeError("FreeType source revision changed")
        receipts[str(path.relative_to(ROOT))] = sha(path)
        for unit in old["source_units"]:
            source, obj = ROOT / unit["source"], ROOT / unit["object"]
            if sha(source) != unit["source_sha256"] or sha(obj) != unit["object_sha256"]:
                raise RuntimeError(f"FreeType source/object drift: {source}")
            upstream[unit["source"]] = unit["source_sha256"]
            objects.append(obj)
    gzip_receipt = PRIOR / "freetype-gzip-current-receipt.json"
    gzip_old = json.loads(gzip_receipt.read_text())
    gzip_source, gzip_obj = ROOT / gzip_old["source"], ROOT / gzip_old["object"]
    if sha(gzip_source) != gzip_old["source_sha256"] or sha(gzip_obj) != gzip_old["object_sha256"]:
        raise RuntimeError("FreeType gzip source/object drift")
    receipts[str(gzip_receipt.relative_to(ROOT))] = sha(gzip_receipt)
    upstream[gzip_old["source"]] = gzip_old["source_sha256"]
    objects.append(gzip_obj)
    mapping = json.loads(MANIFEST.read_text())["apollo_main"]
    defined = symbols(BASE, "--defined-only")
    for alias in ALIASES:
        if mapping[alias] not in defined:
            raise RuntimeError(f"native-derived alias provider absent: {alias}")
    stages = [BASE, *objects]
    stages.extend(f"--defsym={name}={mapping[name]}" for name in ALIASES)
    combined = link("apollo-main-freetype-alias-bound.o", *stages)
    libc_objects = []
    libc_sources = {}
    for name in LIBC:
        source = SDK / f"{name}.c"
        obj = OUT / f"{name}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror",
                        "-I" + str(ROOT / "third-party/upstream/nationalchip-lvp-kws/include/utility/libc"),
                        "-I" + str(SDK / "templates"), "-c", str(source),
                        "-o", str(obj)], check=True)
        libc_sources[str(source.relative_to(ROOT))] = sha(source)
        libc_objects.append(obj)
    template = SDK / "templates/strtox.c"
    libc_sources[str(template.relative_to(ROOT))] = sha(template)
    final = link("apollo-main-freetype-libc-complete.o", combined, *libc_objects)
    before, after = symbols(BASE, "-u"), symbols(final, "-u")
    expected_added = {"setjmp", "longjmp"}
    if len(before) != 518 or len(after) != 510 or after - before != expected_added:
        raise RuntimeError(f"unexpected FreeType closure: {len(before)}->{len(after)}, {sorted(after-before)}")
    classes = {"autofit_module_class", "cff_driver_class", "psaux_module_class",
               "pshinter_module_class", "psnames_module_class", "sfnt_module_class",
               "tt_driver_class"}
    if not classes <= before - after:
        raise RuntimeError("pinned FreeType classes not bound")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_FREETYPE_LIBC_C_COMPOSITION",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "upstream_receipts": receipts, "upstream_sources": upstream,
        "alias_manifest": str(MANIFEST.relative_to(ROOT)),
        "alias_manifest_sha256": sha(MANIFEST),
        "aliases": {name: mapping[name] for name in ALIASES},
        "portable_libc_sources": libc_sources,
        "portable_libc_objects": {str(p.relative_to(ROOT)): sha(p) for p in libc_objects},
        "linked_object": str(final.relative_to(ROOT)),
        "linked_object_sha256": sha(final),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["setjmp/longjmp require ARM ABI source or runtime binding.",
                   "Portable libc and FreeType runtime behavior are not native or device qualified.",
                   "Other Main imports and final placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
