#!/usr/bin/env python3
"""Record the current Apollo Main source archive composition, without image claims."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-source-refresh2"
AUDIO = OUT / "apollo_main/audio/libaudio-source-candidates.a"
MAIN = ROOT / "g2/build/c-firmware/20261014/main-root-refresh/apollo_main/main/main-candidates.a"
COMBINED = OUT / "apollo_main/candidate.o"
CORDIO_LINK = OUT / "apollo_main/candidate-cordio-util.o"
DELAY_LINK = OUT / "apollo_main/candidate-cordio-delay.o"
EVENT_SOURCE = ROOT / "g2/analysis/c-source-completion-20261011/peripherals/root-hci-event-sizes-round427/event_sizes.c"
EVENT_OBJECT = OUT / "apollo_main/hci-event-sizes.o"
EVENT_LINK = OUT / "apollo_main/candidate-cordio-delay-event.o"
POWER_SOURCE = ROOT / "g2/components/audio/power_vendor_candidate"
POWER_NAMES = ("power.c", "power_descriptor_native.c", "power_product_native.c",
               "power_callbacks_native.c", "power_gpu_transition_native.c")
POWER_OBJECTS = [OUT / ("apollo_main/refresh-" + name[:-2] + ".o")
                 for name in POWER_NAMES]
POWER_LINK = OUT / "apollo_main/candidate-power.o"
SMP_ROWS_SOURCE = ROOT / "g2/components/main/smp_sc_rows_candidate_20261014/smp_sc_rows.c"
SMP_ROWS_OBJECT = OUT / "apollo_main/smp-sc-rows.o"
SMP_ROWS_LINK = OUT / "apollo_main/candidate-power-smp-rows.o"
CORDIO_OBJECTS = [OUT / "apollo_main/bda-is-zeros.o",
                  OUT / "apollo_main/cordio-wstr.o",
                  OUT / "apollo_main/cordio-calc128.o"]
LOG = OUT.parent / "main-root-source-refresh2-build.log"
RECEIPT = OUT / "main-source-refresh-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(*args):
    return subprocess.check_output(args, text=True)


def main():
    cordio_sources = [ROOT / "g2/components/main/cordio_bda_candidate_20261014/bda_is_zeros.c",
                      ROOT / "third-party/upstream/cordio/wsf/sources/util/wstr.c",
                      ROOT / "third-party/upstream/cordio/wsf/sources/util/calc128.c"]
    for source, obj in zip(cordio_sources, CORDIO_OBJECTS):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror",
                        "-I" + str(ROOT / "g2/config-recovered/cordio/g2-compat-include"),
                        "-I" + str(ROOT / "third-party/upstream/cordio/wsf/include"),
                        "-I" + str(ROOT / "third-party/upstream/cordio/platform/include"),
                        "-c", str(source), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(COMBINED),
                    *map(str, CORDIO_OBJECTS), "-o", str(CORDIO_LINK)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r",
                    "--defsym=actual_itcm_delay=audio_itcm_delay_iterations",
                    str(CORDIO_LINK), "-o", str(DELAY_LINK)], check=True)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(EVENT_SOURCE),
                    "-o", str(EVENT_OBJECT)], check=True)
    assert "00000000 00000056 R audio_ble_hci_event_sizes_6e3720" in output(
        "arm-none-eabi-nm", "-S", "-g", "--defined-only", str(EVENT_OBJECT))
    event_bytes = OUT / "apollo_main/hci-event-sizes.rodata"
    subprocess.run(["arm-none-eabi-objcopy", "--dump-section",
                    ".rodata=" + str(event_bytes), str(EVENT_OBJECT)], check=True)
    actual = event_bytes.read_bytes()
    assert len(actual) == 86
    stock = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
    payload = stock.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == \
        "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
    assert actual == payload[0x6e3720 - 0x438000:0x6e3720 - 0x438000 + 86]
    subprocess.run(["arm-none-eabi-ld", "-r", str(DELAY_LINK), str(EVENT_OBJECT),
                    "-o", str(EVENT_LINK)], check=True)
    for name, obj in zip(POWER_NAMES, POWER_OBJECTS):
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-mfpu=fpv5-sp-d16", "-mfloat-abi=softfp", "-std=c11",
                        "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra",
                        "-Werror", "-c", str(POWER_SOURCE / name), "-o", str(obj)],
                       check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", str(EVENT_LINK),
                    *map(str, POWER_OBJECTS), "-o", str(POWER_LINK)], check=True)
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SMP_ROWS_SOURCE), "-o",
                    str(SMP_ROWS_OBJECT)], check=True)
    assert "00000000 00000054 B audio_ble_smp_sc_rows" in output(
        "arm-none-eabi-nm", "-S", "-g", "--defined-only", str(SMP_ROWS_OBJECT))
    subprocess.run(["arm-none-eabi-ld", "-r", str(POWER_LINK), str(SMP_ROWS_OBJECT),
                    "-o", str(SMP_ROWS_LINK)], check=True)
    log = LOG.read_text()
    assert "archive: 1342 source-built objects" in log
    assert len(re.findall(r"^\d+/1295 .*: 0$", log, re.M)) == 1295
    assert len(re.findall(r"^provider .*: 0$", log, re.M)) == 94
    nm = output("arm-none-eabi-nm", "-g", str(COMBINED))
    symbols = {}
    unresolved = []
    for line in nm.splitlines():
        fields = line.split()
        if len(fields) == 2 and fields[0] == "U":
            unresolved.append(fields[1])
        elif len(fields) == 3:
            symbols[fields[2]] = (fields[0], fields[1])
    assert len(unresolved) == len(set(unresolved)) == 640
    assert symbols["g2_audio_log_transport_bits"] == symbols["audio_ota_packed_status"]
    sections = output("arm-none-eabi-objdump", "-h", str(COMBINED))
    for name, size in [("20075043", "00000001"), ("20074630", "00000004"),
                       ("20074954", "00000004")]:
        assert re.search(r"^\s*\d+\s+\.g2_ram_" + name + r"\s+" + size + r"\s", sections, re.M)
    cordio_unresolved = {line.split()[-1] for line in output(
        "arm-none-eabi-nm", "-u", str(CORDIO_LINK)).splitlines()}
    assert len(cordio_unresolved) == 634
    assert set(unresolved) - cordio_unresolved == {
        "BdaIsZeros", "Calc128Cpy", "Calc128Cpy64", "WStrReverse",
        "WStrReverseCpy", "calc128Zeros"}
    assert not cordio_unresolved - set(unresolved)
    cordio = ROOT / "third-party/upstream/cordio"
    assert output("git", "-C", str(cordio), "rev-parse", "HEAD").strip() == \
        "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"
    native_receipts = [ROOT / "g2/build/c-firmware/cordio-bda-native-round1014/receipt.json",
                       ROOT / "g2/build/c-firmware/cordio-wstr-native-round1013/receipt.json",
                       ROOT / "g2/build/c-firmware/cordio-calc128-native-round1015/receipt.json"]
    assert all(p.exists() for p in native_receipts)
    delay_unresolved = {line.split()[-1] for line in output(
        "arm-none-eabi-nm", "-u", str(DELAY_LINK)).splitlines()}
    assert len(delay_unresolved) == 633
    assert cordio_unresolved - delay_unresolved == {"actual_itcm_delay"}
    assert not delay_unresolved - cordio_unresolved
    delay_native = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies/itcm-delay-native-comparison.json"
    assert json.loads(delay_native.read_text())["status"] == "PASS_BOUNDED_NATIVE_ITCM_DELAY_C"
    event_unresolved = {line.split()[-1] for line in output(
        "arm-none-eabi-nm", "-u", str(EVENT_LINK)).splitlines()}
    assert len(event_unresolved) == 632
    assert delay_unresolved - event_unresolved == {"audio_ble_hci_event_sizes_6e3720"}
    assert not event_unresolved - delay_unresolved
    power_unresolved = {line.split()[-1] for line in output(
        "arm-none-eabi-nm", "-u", str(POWER_LINK)).splitlines()}
    expected_power = {"am_hal_pwrctrl_periph_disable", "am_hal_pwrctrl_periph_enable",
                      "audio_power_peripheral_off", "audio_power_peripheral_on",
                      "stock_disable", "stock_enable", "stock_peripheral_enable"}
    assert len(power_unresolved) == 625
    assert event_unresolved - power_unresolved == expected_power
    assert not power_unresolved - event_unresolved
    prior_power = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies/pool-state-power-vendor-current-receipt.json"
    power_evidence = json.loads(prior_power.read_text())
    assert power_evidence["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_APOLLO_POWER_C"
    assert expected_power == set(power_evidence["imports_resolved"])
    for unit in power_evidence["source_units"]:
        assert sha(ROOT / unit["source"]) == unit["source_sha256"]
    for check in power_evidence["bounded_native_checks"]:
        assert sha(ROOT / check["script"]) == check["script_sha256"]
    smp_unresolved = {line.split()[-1] for line in output(
        "arm-none-eabi-nm", "-u", str(SMP_ROWS_LINK)).splitlines()}
    assert len(smp_unresolved) == 624
    assert power_unresolved - smp_unresolved == {"audio_ble_smp_sc_rows"}
    assert not smp_unresolved - power_unresolved
    prior_smp = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies/pool-state-smp-sc-rows-current-receipt.json"
    smp_evidence = json.loads(prior_smp.read_text())
    assert smp_evidence["status"] == "PASS_EXPERIMENTAL_POOLED_MAIN_SMP_SC_ROW_STORAGE_C"
    assert smp_evidence["source_sha256"] == sha(SMP_ROWS_SOURCE)
    assert sha(ROOT / smp_evidence["native_initializer_verifier"]) == \
        smp_evidence["native_initializer_verifier_sha256"]
    receipt = {
        "status": "PASS_SOURCE_ARCHIVE_RELOCATABLE_LINK",
        "audio_archive": str(AUDIO.relative_to(ROOT)), "audio_archive_sha256": sha(AUDIO),
        "main_archive": str(MAIN.relative_to(ROOT)), "main_archive_sha256": sha(MAIN),
        "combined_object": str(COMBINED.relative_to(ROOT)), "combined_object_sha256": sha(COMBINED),
        "cordio_linked_object": str(CORDIO_LINK.relative_to(ROOT)),
        "cordio_linked_object_sha256": sha(CORDIO_LINK),
        "cordio_objects": {str(p.relative_to(ROOT)): sha(p) for p in CORDIO_OBJECTS},
        "cordio_sources": {str(p.relative_to(ROOT)): sha(p) for p in cordio_sources},
        "cordio_upstream_commit": "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6",
        "cordio_native_receipts": {str(p.relative_to(ROOT)): sha(p) for p in native_receipts},
        "cordio_imports_resolved": sorted(set(unresolved) - cordio_unresolved),
        "cordio_unresolved_imports": len(cordio_unresolved),
        "delay_linked_object": str(DELAY_LINK.relative_to(ROOT)),
        "delay_linked_object_sha256": sha(DELAY_LINK),
        "delay_native_receipt": str(delay_native.relative_to(ROOT)),
        "delay_native_receipt_sha256": sha(delay_native),
        "delay_imports_resolved": ["actual_itcm_delay"],
        "hci_event_source": str(EVENT_SOURCE.relative_to(ROOT)),
        "hci_event_source_sha256": sha(EVENT_SOURCE),
        "hci_event_object": str(EVENT_OBJECT.relative_to(ROOT)),
        "hci_event_object_sha256": sha(EVENT_OBJECT),
        "hci_event_native_bytes_matched": 86,
        "hci_event_linked_object": str(EVENT_LINK.relative_to(ROOT)),
        "hci_event_linked_object_sha256": sha(EVENT_LINK),
        "power_sources": {str((POWER_SOURCE / n).relative_to(ROOT)): sha(POWER_SOURCE / n)
                          for n in POWER_NAMES},
        "power_objects": {str(p.relative_to(ROOT)): sha(p) for p in POWER_OBJECTS},
        "power_linked_object": str(POWER_LINK.relative_to(ROOT)),
        "power_linked_object_sha256": sha(POWER_LINK),
        "power_prior_receipt": str(prior_power.relative_to(ROOT)),
        "power_prior_receipt_sha256": sha(prior_power),
        "power_imports_resolved": sorted(expected_power),
        "smp_rows_source": str(SMP_ROWS_SOURCE.relative_to(ROOT)),
        "smp_rows_source_sha256": sha(SMP_ROWS_SOURCE),
        "smp_rows_object": str(SMP_ROWS_OBJECT.relative_to(ROOT)),
        "smp_rows_object_sha256": sha(SMP_ROWS_OBJECT),
        "smp_rows_linked_object": str(SMP_ROWS_LINK.relative_to(ROOT)),
        "smp_rows_linked_object_sha256": sha(SMP_ROWS_LINK),
        "smp_rows_prior_receipt": str(prior_smp.relative_to(ROOT)),
        "smp_rows_prior_receipt_sha256": sha(prior_smp),
        "final_unresolved_imports": len(smp_unresolved),
        "build_log": str(LOG.relative_to(ROOT)), "build_log_sha256": sha(LOG),
        "source_units_compiled": 1295, "provider_units_compiled": 94,
        "archive_members": 1342, "unresolved_imports": len(unresolved),
        "transport_alias_same_symbol_address": True,
        "verified_fixed_sections": [".g2_ram_20075043", ".g2_ram_20074630", ".g2_ram_20074954"],
        "whole_image_complete": False, "native_branch_equivalent": False, "hardware_proof": False,
        "gate": "Relocatable source composition only; 624 unresolved imports after source-backed power and 84-byte SMP row storage bindings; bounded checks do not establish final placement or device execution.",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], sha(RECEIPT))


if __name__ == "__main__":
    main()
