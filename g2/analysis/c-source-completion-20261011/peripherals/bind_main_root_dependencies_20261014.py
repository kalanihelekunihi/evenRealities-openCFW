#!/usr/bin/env python3
"""Compose pinned Cordio, native ROM data, and runtime C into current Main."""
import hashlib
import json
import subprocess
from pathlib import Path

G2 = Path(__file__).resolve().parents[3]
REPO = G2.parent
HERE = Path(__file__).resolve().parent
BASE_RECEIPT = G2 / "build/c-firmware/20261014/main-root-refresh/receipt.json"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
OBJECTS = (
    "cordio-calc128-round1010/calc128.o",
    "cordio-bda-round1011/bda.o",
    "cordio-wstr-round1012/wstr.o",
    "radio-rom-literals-round1036/radio_strings.o",
    "hci-rom-tables-round1037/event_sizes.o",
    "hci-rom-tables-round1037/dm_hci_route_table.o",
    "radio-rom-tail-round1038/radio_tail.o",
)
SOURCE_PATHS = (
    "third-party/upstream/cordio/wsf/sources/util/calc128.c",
    "third-party/upstream/cordio/wsf/sources/util/bda.c",
    "third-party/upstream/cordio/wsf/sources/util/wstr.c",
    "g2/analysis/c-source-completion-20261011/peripherals/root-rom-radio-strings-round424/radio_strings.c",
    "g2/analysis/c-source-completion-20261011/peripherals/root-hci-event-sizes-round427/event_sizes.c",
    "g2/analysis/c-source-completion-20261011/peripherals/root-dm-hci-route-table-round429/dm_hci_route_table.c",
    "g2/analysis/c-source-completion-20261011/peripherals/root-rom-radio-tail-round425/radio_tail.c",
)
SOURCE_RECEIPTS = (
    "cordio-calc128-round1010/receipt.json",
    "cordio-bda-round1011/receipt.json",
    "cordio-wstr-round1012/receipt.json",
    "radio-rom-literals-round1036/receipt.json",
    "hci-rom-tables-round1037/receipt.json",
    "radio-rom-tail-round1038/receipt.json",
)
SOURCE_C = (
    G2 / "components/audio/file_sync_candidate/byte_compare.c",
    G2 / "components/main/full_formatter_native_candidate/memclr4.c",
    G2 / "analysis/c-source-completion-20261011/peripherals/root-dma-descriptors-round433/dma_descriptors.c",
)
HCI_RECEIPT = G2 / "analysis/c-source-completion-20261011/peripherals/root-hci-decoders-round434/hci-decoders-receipt.json"
HCI_NEW_IMPORTS = {
    "hciCb", "hciCmdRecvCmpl", "hciCoreCisByHandle", "hciCoreCisClose",
    "hciCoreCisOpen", "hciCoreConnClose", "hciCoreConnOpen",
    "hciCoreNumCmplPkts", "hciCoreVsCmdCmplRcvd",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines() if line.strip()}


def rom_data(path, output):
    subprocess.run(["arm-none-eabi-objcopy", "-O", "binary", "-j", ".rodata",
                    str(path), str(output)], check=True)
    return output.read_bytes()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(BASE_RECEIPT.read_text())
    image = receipt["images"]["apollo_main"]
    assert image["candidate_compilation_passed"] and not image["source_complete"]
    linked = image["relocatable_link"]
    base = REPO / linked["output"]
    assert sha(base) == linked["output_sha256"]
    before = symbols(base, "-u")
    assert before == set(linked["unresolved_symbols"])
    coherent = json.loads((G2 / "build/c-firmware/ble-coherent-dependencies-round1046/receipt.json").read_text())
    pinned = {row["path"]: row["sha256"] for row in coherent["objects"]}
    objects = []
    for relative, source_relative in zip(OBJECTS, SOURCE_PATHS, strict=True):
        old = G2 / "build/c-firmware" / relative
        assert sha(old) == pinned[str(old.relative_to(G2))], old
        source = REPO / source_relative
        obj = OUT / old.name
        subprocess.run([
            "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
            "-Wall", "-Wextra", "-Werror",
            "-I", str(G2 / "config-recovered/cordio/g2-compat-include"),
            "-I", str(REPO / "third-party/upstream/cordio/wsf/include"),
            "-c", str(source), "-o", str(obj),
        ], check=True)
        if old.name in {"radio_strings.o", "event_sizes.o", "dm_hci_route_table.o", "radio_tail.o"}:
            assert rom_data(old, OUT / (old.stem + ".old.bin")) == rom_data(
                obj, OUT / (old.stem + ".new.bin")), old.name
        objects.append(obj)
    for relative in SOURCE_RECEIPTS:
        old = json.loads((G2 / "build/c-firmware" / relative).read_text())
        sources = old.get("sources", [{"path": old["source"], "sha256": old["source_sha256"]}]
                          if "source" in old else [])
        for row in sources:
            path = G2 / row["path"]
            if not path.is_file():
                path = REPO / row["path"]
            assert sha(path) == row["sha256"], row["path"]
    assert sha(SOURCE_C[0]) == coherent["byte_compare_source_sha256"]
    for source in SOURCE_C:
        obj = OUT / (source.stem + ".o")
        subprocess.run([
            "clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
            "-std=c11", "-ffreestanding", "-fno-builtin",
            "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
            "-o", str(obj),
        ], check=True)
        if source.name == "dma_descriptors.c":
            stock = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
            assert sha(stock) == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
            native = stock.read_bytes()[32 + 0x6c0f40 - 0x438000:
                                        32 + 0x6c1120 - 0x438000]
            assert len(native) == 480
            assert rom_data(obj, OUT / "dma_descriptors.bin") == native
        objects.append(obj)
    hci = json.loads(HCI_RECEIPT.read_text())
    hci_source = REPO / hci["source_unit"]["source"]
    # The current wrapper has advanced since the round-434 receipt; compile
    # its current bytes rather than importing an older object/equality claim.
    previous_build = json.loads((REPO / hci["build_receipt"]["path"]).read_text())
    rows = [row for row in previous_build["images"]["apollo_main"]["experimental_compile"]
            if row.get("source") == hci["source_unit"]["source"]]
    assert len(rows) == 1
    command = rows[0]["argv"].copy()
    hci_object = OUT / "source_linked_decoders.o"
    command[command.index("-o") + 1] = str(hci_object)
    command[command.index("-MF") + 1] = str(OUT / "source_linked_decoders.d")
    subprocess.run(command, check=True)
    listing = subprocess.check_output(["arm-none-eabi-nm", "-S", str(hci_object)], text=True)
    assert any(line.split()[-1] == "audio_ble_hci_event_decoders_6c910c" and
               int(line.split()[1], 16) == 344 for line in listing.splitlines())
    objects.append(hci_object)
    for obj in objects:
        attributes = subprocess.check_output(
            ["arm-none-eabi-readelf", "-A", str(obj)], text=True)
        assert "Tag_ABI_enum_size: int" in attributes, obj
    provided = set()
    base_defined = symbols(base, "-g", "--defined-only")
    for obj in objects:
        defined = symbols(obj, "-g", "--defined-only")
        assert not (defined & (provided | base_defined)), sorted(defined & (provided | base_defined))
        provided |= defined
    output = OUT / "apollo-main-dependencies.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(base),
                    *map(str, objects), "-o", str(output)], check=True)
    after = symbols(output, "-u")
    bound = sorted(before - after)
    assert set(bound) == provided & before
    assert len(bound) == 43, (len(bound), bound)
    assert after - before == HCI_NEW_IMPORTS, sorted(after - before)
    result = {
        "status": "PASS_CURRENT_MAIN_DEPENDENCY_COMPOSITION",
        "base_receipt": str(BASE_RECEIPT.relative_to(REPO)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "base_object_sha256": sha(base),
        "sources": [{"path": str(source.relative_to(REPO)), "sha256": sha(source)}
                    for source in SOURCE_C],
        "pinned_dependency_sources": [
            {"path": relative, "sha256": sha(REPO / relative)}
            for relative in SOURCE_PATHS],
        "target_abi_enum_size": "int",
        "rom_data_matches_pinned_objects": True,
        "dma_descriptor_bytes_match_stock": True,
        "hci_decoder_source": {"path": str(hci_source.relative_to(REPO)),
                               "sha256": sha(hci_source)},
        "hci_decoder_prior_receipt_sha256": sha(HCI_RECEIPT),
        "hci_decoder_current_source_recompiled": True,
        "new_hci_runtime_imports": sorted(after - before),
        "objects": [{"path": str(obj.relative_to(REPO)), "sha256": sha(obj)}
                    for obj in objects],
        "bound_symbols": bound,
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "output": str(output.relative_to(REPO)),
        "output_sha256": sha(output),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": [
            "The aggregate is relocatable source evidence, not a placed Apollo image.",
            "Remaining imports include product bodies, state and data contracts.",
            "The HCI decoder cohort adds nine genuine Cordio runtime imports; table pointer equivalence is checked separately, while parser bodies lack native qualification.",
            "Native runtime and hardware behavior remain unqualified outside prior bounded oracles.",
        ],
    }
    (OUT / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(OUT / "receipt.json")


if __name__ == "__main__":
    main()
