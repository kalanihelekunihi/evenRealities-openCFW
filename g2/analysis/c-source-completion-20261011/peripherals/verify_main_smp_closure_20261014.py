#!/usr/bin/env python3
"""Rebuild the source-backed SMP table/action/ECC closure for refreshed Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-source-refresh2"
BASE_RECEIPT = OUT / "main-source-refresh-receipt.json"
BUILD = OUT / "apollo_main"
SMP = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/smp_tables"
OLD = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
CORDIO = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
UP = ROOT / "third-party/upstream/cordio"
NAMES = ("smpi_sm", "smpi_sc_sm", "smpr_sm", "smpr_sc_sm",
         "smp_act", "smp_sc_act", "smpi_act", "smpi_sc_act", "smpr_act", "smpr_sc_act")
TABLES = NAMES[:4]
BASE = BUILD / "candidate-power-smp-rows.o"
TABLE_LINK = BUILD / "candidate-smp-tables-actions.o"
FINAL = BUILD / "candidate-smp-closure.o"
RECEIPT = OUT / "main-smp-closure-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args):
    return subprocess.check_output(args, text=True)


def imports(path):
    return {line.split()[-1] for line in run("arm-none-eabi-nm", "-u", str(path)).splitlines()}


def compile_source(source, obj, includes=(), extra=()):
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-std=c11",
                    "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra",
                    "-Wno-unused-parameter", *extra,
                    *("-I" + str(path) for path in includes),
                    "-c", str(source), "-o", str(obj)], check=True)


def main():
    baseline = json.loads(BASE_RECEIPT.read_text())
    assert baseline["status"] == "PASS_SOURCE_ARCHIVE_RELOCATABLE_LINK"
    assert sha(BASE) == baseline["smp_rows_linked_object_sha256"]
    include = [CORDIO / p for p in ("ble-host/include", "ble-host/sources/stack/smp",
               "ble-host/sources/stack/cfg", "wsf/include", "wsf/sources",
               "wsf/sources/port/freertos", "ble-host/sources/stack/dm")]
    include.append(ROOT / "g2/components/bootloader/filesystem/freestanding_include")
    objects = []
    table_matches = {}
    for name in NAMES:
        source = SMP / f"candidate_{name}.c"
        obj = BUILD / f"refresh-smp-{name}.o"
        compile_source(source, obj, include)
        objects.append(obj)
        if name in TABLES:
            prior = OLD / f"smp-{name}-pool-state-abi.o"
            old_data = BUILD / f"{name}-old.rodata"
            new_data = BUILD / f"{name}-new.rodata"
            for item, data in ((prior, old_data), (obj, new_data)):
                subprocess.run(["arm-none-eabi-objcopy", "--dump-section",
                                ".rodata=" + str(data), str(item)], check=True)
            assert old_data.read_bytes() == new_data.read_bytes(), name
            def reloc(path):
                return run("arm-none-eabi-objdump", "-r", "-j", ".rodata",
                           str(path)).split("RELOCATION RECORDS", 1)[-1]
            assert reloc(prior) == reloc(obj), name
            table_matches[name] = {"rodata_bytes": len(new_data.read_bytes()),
                                   "rodata_sha256": sha(new_data),
                                   "prior_object_sha256": sha(prior),
                                   "current_object_sha256": sha(obj),
                                   "relocations_identical": True}
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(TABLE_LINK)], check=True)
    ecc_include = [ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-cordio-ecc-round422/freestanding_include",
                   ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"]
    ecc_include += [CORDIO / p for p in ("ble-host/include", "ble-host/sources/sec/common",
                    "ble-host/sources/sec/uecc", "ble-host/sources/stack/smp",
                    "ble-host/sources/stack/cfg", "ble-host/sources/stack/dm",
                    "wsf/include", "wsf/sources", "wsf/sources/util",
                    "wsf/sources/port/freertos")]
    ecc_include.append(CORDIO.parent / "uecc")
    ecc_sources = [CORDIO / "ble-host/sources/sec/uecc/sec_ecc.c",
                   CORDIO.parent / "uecc/uECC.c"]
    ecc_objects = [BUILD / "refresh-sec-ecc.o", BUILD / "refresh-uecc.o"]
    for source, obj in zip(ecc_sources, ecc_objects):
        compile_source(source, obj, ecc_include)
    bda_source = UP / "wsf/sources/util/bda.c"
    bda_full = BUILD / "refresh-bda-full.o"
    bda_trim = BUILD / "refresh-bda-copy-trim.o"
    bda_copy = BUILD / "refresh-bda-copy.o"
    compile_source(bda_source, bda_full,
                   [ROOT / "g2/config-recovered/cordio/g2-compat-include", UP / "wsf/include"],
                   ["-ffunction-sections", "-fdata-sections", "-Werror"])
    subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections", "--undefined=BdaCpy",
                    str(bda_full), "-o", str(bda_trim)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "--strip-unneeded", str(bda_trim),
                    str(bda_copy)], check=True)
    assert {line.split()[-1] for line in run("arm-none-eabi-nm", "-g", "--defined-only",
                                            str(bda_copy)).splitlines()} == {"BdaCpy"}
    memcmp_source = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-memcmp-binding-round142/candidate.c"
    memcmp_obj = BUILD / "refresh-memcmp.o"
    compile_source(memcmp_source, memcmp_obj)
    memcmp_receipt = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-memcmp-binding-round142/receipt.json"
    memcmp_evidence = json.loads(memcmp_receipt.read_text())
    assert memcmp_evidence["status"] == "PASS_PUBLIC_MEMCMP_NATIVE_EXACT_RETURN"
    assert memcmp_evidence["source_sha256"] == sha(memcmp_source)
    subprocess.run(["arm-none-eabi-ld", "-r", str(TABLE_LINK),
                    *map(str, ecc_objects), str(bda_copy), str(memcmp_obj),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    resolved = sorted(before - after)
    assert len(before) == 624 and len(after) == 618
    assert resolved == ["audio_ble_smpi_legacy_table", "audio_ble_smpi_sc_table",
                        "audio_ble_smpr_legacy_table", "audio_ble_smpr_sc_table",
                        "g2_lfs_memcmp", "smpStartRspTimer"]
    assert not after - before
    prior_receipts = [OLD / f"pool-state-{name}-current-receipt.json"
                      for name in ("smp-tables", "smp-actions", "cordio-ecc", "cordio-bda-copy")]
    assert all(path.exists() for path in prior_receipts)
    receipt = {
        "status": "PASS_MAIN_SMP_SOURCE_CLOSURE_RELOCATABLE",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "table_action_sources": {str((SMP / f"candidate_{n}.c").relative_to(ROOT)):
                                 sha(SMP / f"candidate_{n}.c") for n in NAMES},
        "table_action_objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "table_object_matches": table_matches,
        "ecc_sources": {str(p.relative_to(ROOT)): sha(p) for p in ecc_sources},
        "ecc_objects": {str(p.relative_to(ROOT)): sha(p) for p in ecc_objects},
        "bda_source": str(bda_source.relative_to(ROOT)),
        "bda_source_sha256": sha(bda_source),
        "bda_copy_object": str(bda_copy.relative_to(ROOT)),
        "bda_copy_object_sha256": sha(bda_copy),
        "memcmp_source": str(memcmp_source.relative_to(ROOT)),
        "memcmp_source_sha256": sha(memcmp_source),
        "memcmp_native_receipt": str(memcmp_receipt.relative_to(ROOT)),
        "memcmp_native_receipt_sha256": sha(memcmp_receipt),
        "prior_receipts": {str(p.relative_to(ROOT)): sha(p) for p in prior_receipts},
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": resolved, "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Table read-only bytes and relocations match the earlier native-checked objects; action body equivalence and pairing runtime remain unproved.",
                  "ECC variant and key/RNG behavior, final placement, other Main imports, and physical hardware remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
