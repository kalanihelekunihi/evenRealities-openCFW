#!/usr/bin/env python3
"""Compose source-linked Cordio HCI decoders, joins, event child and state."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-source-refresh2"
BUILD = OUT / "apollo_main"
BASE_RECEIPT = OUT / "main-tlsf-runtime-receipt.json"
BASE = BUILD / "candidate-tlsf-runtime.o"
DECODER = BUILD / "refresh-hci-decoders.o"
DECODER_LINK = BUILD / "candidate-hci-decoders.o"
JOINS = BUILD / "candidate-hci-joins.o"
VENDOR_SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-vendor-complete-round436/vendor_complete.c"
VENDOR = BUILD / "refresh-hci-vendor-complete.o"
CLOSURE = BUILD / "candidate-hci-closure.o"
CB_FULL = BUILD / "refresh-hci-main-full.o"
CB_ROOTED = BUILD / "refresh-hci-cb-rooted.o"
CB = BUILD / "refresh-hci-cb.o"
FINAL = BUILD / "candidate-hci-composed.o"
RECEIPT = OUT / "main-hci-decoder-composition-receipt.json"
CORDIO = ROOT / "third-party/local-vendor/sources/AmbiqSuite_R3.2.0/third_party/cordio"
DECODER_SOURCE = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-decoders-round434/source_linked_decoders.c"
CB_SOURCE = CORDIO / "ble-host/sources/stack/hci/hci_main.c"
ALIASES = {
    "hciCmdRecvCmpl": "audio_ble_hci_cmd_receive_complete",
    "hciCoreNumCmplPkts": "audio_ble_hci_num_complete_packets",
    "hciCoreCisByHandle": "audio_ble_hci_cis_by_handle",
    "hciCoreCisClose": "audio_ble_hci_cis_close",
    "hciCoreCisOpen": "audio_ble_hci_cis_open",
    "hciCoreConnClose": "audio_ble_hci_conn_close",
    "hciCoreConnOpen": "audio_ble_hci_conn_open",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(*args):
    return subprocess.check_output(args, text=True)


def imports(path):
    return {line.split()[-1] for line in output("arm-none-eabi-nm", "-u", str(path)).splitlines()}


def rodata(path, label):
    target = BUILD / f"hci-decoder-{label}.rodata"
    subprocess.run(["arm-none-eabi-objcopy", "--dump-section",
                    ".rodata=" + str(target), str(path)], check=True)
    return target.read_bytes()


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_MAIN_TLSF_RUNTIME_SOURCE_RELOCATABLE"
    assert sha(BASE) == base["linked_object_sha256"]
    decoder_receipt = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-decoders-round434/hci-decoders-receipt.json"
    decoder_evidence = json.loads(decoder_receipt.read_text())
    assert decoder_evidence["native_evidence"]["source_entries"] == 85
    assert decoder_evidence["native_evidence"]["native_index_85_word"] == "0x00000000"
    include = [ROOT, G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"]
    include += [CORDIO / p for p in ("ble-host/include", "ble-host/sources/hci/ambiq",
                "ble-host/sources/stack/hci", "ble-host/sources/stack/cfg", "wsf/include",
                "wsf/sources", "wsf/sources/port/freertos", "wsf/sources/util")]
    cmd = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
           "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-std=c11",
           "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra",
           "-Wno-unused-parameter"]
    subprocess.run(cmd + [*("-I" + str(p) for p in include),
                          "-c", str(DECODER_SOURCE), "-o", str(DECODER)], check=True)
    old = G2 / "build/c-firmware/20261014/main-root-dependencies/hci-decoders-current-source-abi.o"
    assert rodata(old, "old") == rodata(DECODER, "new")
    def reloc(path):
        return output("arm-none-eabi-objdump", "-r", "-j", ".rodata",
                      str(path)).split("RELOCATION RECORDS", 1)[-1]
    assert reloc(old) == reloc(DECODER)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(DECODER),
                    "-o", str(DECODER_LINK)], check=True)
    join_receipt = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-joins-round435/hci-joins-receipt.json"
    joins = json.loads(join_receipt.read_text())
    for alias, provider in ALIASES.items():
        assert joins["bindings"][alias] == provider
    for source, digest in joins["source_hashes"].items():
        assert sha(ROOT / source) == digest
    args = ["arm-none-eabi-ld", "-r"]
    for alias, provider in ALIASES.items():
        args.append("--defsym=" + alias + "=" + provider)
    subprocess.run(args + [str(DECODER_LINK), "-o", str(JOINS)], check=True)
    vendor_receipt = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-vendor-complete-round436/vendor-complete-receipt.json"
    vendor_evidence = json.loads(vendor_receipt.read_text())
    assert vendor_evidence["status"] == "completed"
    assert sha(VENDOR_SOURCE) == vendor_evidence["source_unit"]["source_sha256"]
    native = ROOT / vendor_evidence["native_branch_evidence"]["path"]
    assert sha(native) == vendor_evidence["native_branch_evidence"]["sha256"]
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(VENDOR_SOURCE),
                    "-o", str(VENDOR)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(JOINS), str(VENDOR),
                    "-o", str(CLOSURE)], check=True)
    subprocess.run(cmd + ["-ffunction-sections", "-fdata-sections",
                          *("-I" + str(p) for p in include),
                          "-c", str(CB_SOURCE), "-o", str(CB_FULL)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections", "--undefined=hciCb",
                    str(CB_FULL), "-o", str(CB_ROOTED)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "--strip-unneeded", str(CB_ROOTED),
                    str(CB)], check=True)
    assert output("arm-none-eabi-nm", "-S", "-g", str(CB)).strip() == \
        "00000000 00000024 B hciCb"
    subprocess.run(["arm-none-eabi-ld", "-r", str(CLOSURE), str(CB),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    assert len(before) == 561 and len(after) == 560
    assert before - after == {"audio_ble_hci_event_decoders_6c910c"}
    assert not after - before
    receipt = {
        "status": "PASS_MAIN_HCI_DECODER_SOURCE_COMPOSITION",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "source_files": {str(p.relative_to(ROOT)): sha(p)
                         for p in (DECODER_SOURCE, VENDOR_SOURCE, CB_SOURCE)},
        "prior_evidence": {str(p.relative_to(ROOT)): sha(p)
                           for p in (decoder_receipt, join_receipt, vendor_receipt)},
        "decoder_rodata_bytes_matched": len(rodata(DECODER, "new")),
        "decoder_rodata_relocations_identical": True,
        "hci_aliases": ALIASES,
        "hci_cb_size": 36,
        "hci_cb_native_ram_address_proven": False,
        "objects": {str(p.relative_to(ROOT)): sha(p)
                    for p in (DECODER, VENDOR, CB)},
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Decoder table bytes and relocations match the earlier source object; parser body and ABI equivalence remain incomplete.",
                  "hciCb has source-owned 36-byte storage but no verified native RAM address or overlap proof.",
                  "Other Main imports, final placement, controller behavior, and hardware remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
