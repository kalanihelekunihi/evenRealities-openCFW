#!/usr/bin/env python3
"""Bind pinned Cordio HCI decoder table and parser bodies to pooled Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-hci-event-sizes-current-receipt.json"
PROVIDER = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-decoders-round434/hci-decoders-receipt.json"
OBJECT = OUT / "hci-decoders-current-source-abi.o"
BOUND = OUT / "apollo-main-pool-state-hci-decoders-bound.o"
RECEIPT = OUT / "pool-state-hci-decoders-current-receipt.json"
NAME = "audio_ble_hci_event_decoders_6c910c"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def symbols(flags, p):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(p)], text=True).splitlines()}


def main():
    base = json.loads(BASE.read_text())
    provider = json.loads(PROVIDER.read_text())
    assert base["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_HCI_EVENT_SIZE_C"
    assert provider["import_delta"]["removed"] == [NAME]
    evidence = provider["native_evidence"]
    assert evidence["source_entries"] == 85 and evidence["native_index_85_word"] == "0x00000000"
    prior = ROOT / base["linked_object"]
    source = ROOT / provider["source_unit"]["source"]
    assert sha(prior) == base["linked_sha256"]
    # The historical provider receipt describes an older source revision.
    # Recompile the current source instead of linking that stale object.
    cordio = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
    include = [ROOT,
               G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"]
    include += [cordio / subdir for subdir in (
        "ble-host/include", "ble-host/sources/hci/ambiq", "ble-host/sources/stack/hci",
        "ble-host/sources/stack/cfg", "wsf/include", "wsf/sources",
        "wsf/sources/port/freertos", "wsf/sources/util")]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-fshort-enums", "-std=c11",
                    "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra",
                    "-Wno-unused-parameter", *(f"-I{x}" for x in include),
                    "-c", str(source), "-o", str(OBJECT)], check=True)
    before = symbols(["-u"], prior)
    olddefs = symbols(["--defined-only"], prior)
    newdefs = symbols(["--defined-only"], OBJECT)
    assert NAME in before and NAME in newdefs
    assert not (olddefs & newdefs)
    subprocess.run(["arm-none-eabi-ld", "-r", str(prior), str(OBJECT), "-o", str(BOUND)], check=True)
    after = symbols(["-u"], BOUND)
    added = sorted(after - before)
    removed = sorted(before - after)
    assert removed == [NAME]
    assert added == sorted(set(provider["import_delta"]["added"]) | {"BdaCpy"})
    receipt = {"status": "PASS_EXPERIMENTAL_POOLED_MAIN_CORDIO_HCI_DECODERS_C",
               "base_receipt": str(BASE.relative_to(ROOT)), "base_receipt_sha256": sha(BASE),
               "provider_receipt": str(PROVIDER.relative_to(ROOT)), "provider_receipt_sha256": sha(PROVIDER),
               "source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
               "current_object": str(OBJECT.relative_to(ROOT)), "current_object_sha256": sha(OBJECT),
               "historical_source_sha256": provider["source_unit"]["source_sha256"],
               "source_definitions": len(newdefs), "imports_resolved": removed, "imports_added": added,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "linked_object": str(BOUND.relative_to(ROOT)), "linked_sha256": sha(BOUND),
               "whole_image_complete": False, "hardware_proof": False,
               "gates": ["Pinned Cordio parser bodies are source-linked but not yet native body or ABI equivalents.",
                         "Index-85 sentinel has exact ROM zero but original table allocation extent remains unproved.",
                         "New Cordio imports, final placement, and controller behavior remain open."]}
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(newdefs), len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
