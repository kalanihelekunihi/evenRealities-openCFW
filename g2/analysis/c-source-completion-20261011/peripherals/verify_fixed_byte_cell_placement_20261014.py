#!/usr/bin/env python3
"""Check fixed RAM placement for source-owned Apollo Main state."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "pool-state-byte-cells-current-receipt.json"
SERVICE = OUT / "pool-state-service-mode-current-receipt.json"
OTA = OUT / "pool-state-ota-export-current-receipt.json"
BLE = OUT / "pool-state-ble-handler-current-receipt.json"
BLE_CODEC = OUT / "pool-state-ble-codec-cells-current-receipt.json"
SERVICE_STATES = OUT / "pool-state-ble-service-states-current-receipt.json"
TIMING = OUT / "pool-state-timing-state-current-receipt.json"
HCI_SOURCE = ROOT / "g2/components/audio/uart_thread_source_candidate/display_ble_hci_radio_boot_cells.c"
HCI_OBJECT = OUT / "hci-radio-boot-cells-fixed-placement.o"
HCI_CELLS = {
    "audio_ble_hci_radio_context_ptr": ("0x20074630", 4),
    "audio_ble_hci_radio_aux_ptr": ("0x20074634", 4),
    "audio_ble_hci_radio_active": ("0x20074638", 4),
    "audio_ble_hci_radio_pending": ("0x2007463c", 4),
    "audio_ble_hci_radio_command_cell": ("0x20074640", 4),
    "audio_ble_hci_radio_revision_cell": ("0x20074954", 4),
    "audio_ble_hci_radio_boot_retry": ("0x20074fcc", 1),
}
SCRIPT = OUT / "fixed-byte-cell-placement.ld"
ELF = OUT / "fixed-byte-cell-placement.elf"
RECEIPT = OUT / "fixed-byte-cell-placement-receipt.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = json.loads(BASE.read_text())
    service = json.loads(SERVICE.read_text())
    ota = json.loads(OTA.read_text())
    ble = json.loads(BLE.read_text())
    ble_codec = json.loads(BLE_CODEC.read_text())
    service_states = json.loads(SERVICE_STATES.read_text())
    timing = json.loads(TIMING.read_text())
    assert base["unresolved_after"] == 462 and ota["unresolved_after"] == 459
    assert ble["unresolved_after"] == 457
    assert ble_codec["unresolved_after"] == 446
    assert service_states["unresolved_after"] == 441
    assert timing["unresolved_after"] == 433
    cells = dict(base["native_ram_addresses"])
    cells["g2_audio_service_mode"] = "0x20075024"
    cells["audio_ble_ota_export_state"] = "0x20072730"
    cells["audio_ble_msgtx_handler_id"] = "0x20074f8e"
    cells.update(ble_codec["native_ram_addresses"])
    cells.update(service_states["native_ram_addresses"])
    cells.update({name: span[0] for name, span in timing["native_ram_spans"].items()})
    cells.update({name: span[0] for name, span in HCI_CELLS.items()})
    addresses = [int(value, 16) for value in cells.values()]
    assert len(addresses) == len(set(addresses)) == 40
    service_addresses = {int(value, 16) for value in service_states["native_ram_addresses"].values()}
    timing_extents = {int(span[0], 16): span[1] for span in timing["native_ram_spans"].values()}
    hci_extents = {int(span[0], 16): span[1] for span in HCI_CELLS.values()}
    def extent(address):
        return 0x60 if address == 0x20072730 else 2 if address == 0x20074f2c else hci_extents.get(address, timing_extents.get(address, 4 if address in service_addresses else 1))
    spans = [(int(address, 16), 0x60 if name == "audio_ble_ota_export_state"
              else 2 if name == "g2_audio_log_wake_enabled" else extent(int(address, 16)))
             for name, address in cells.items()]
    ordered = sorted(spans)
    assert all(a + size <= next_a for (a, size), (next_a, _) in zip(ordered, ordered[1:]))
    lines = ["SECTIONS", "{"]
    for address in sorted(addresses):
        section = f".g2_ram_{address:08x}"
        size = extent(address)
        lines.append(f"  {section} 0x{address:08x} (NOLOAD) : {{ KEEP(*({section})) }}")
        lines.append(f'  ASSERT(SIZEOF({section}) == {size}, "{section} size mismatch")')
    lines.append("}")
    SCRIPT.write_text("\n".join(lines) + "\n")
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-Wall", "-Wextra",
                    "-Werror", "-O2", "-c", str(HCI_SOURCE), "-o", str(HCI_OBJECT)], check=True)
    objects = [ROOT / service["source_object"], ROOT / base["source_object"],
               ROOT / ota["source_object"], ROOT / ble["source_object"],
               ROOT / ble_codec["source_object"], ROOT / service_states["source_object"],
               ROOT / timing["source_object"]]
    assert all(sha(path) == recorded for path, recorded in zip(
        objects, [service["source_object_sha256"], base["source_object_sha256"],
                  ota["source_object_sha256"], ble["source_object_sha256"],
                  ble_codec["source_object_sha256"], service_states["source_object_sha256"],
                  timing["source_object_sha256"]]))
    objects.append(HCI_OBJECT)
    subprocess.run(["arm-none-eabi-ld", "-T", str(SCRIPT), *map(str, objects),
                    "-o", str(ELF)], check=True)
    with ELF.open("rb") as stream:
        elf = ELFFile(stream)
        syms = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        for name, address in cells.items():
            assert syms[name] == int(address, 16), name
            section = elf.get_section_by_name(f".g2_ram_{int(address, 16):08x}")
            assert section["sh_addr"] == int(address, 16)
            assert section["sh_size"] == extent(int(address, 16))
            assert section["sh_type"] == "SHT_NOBITS"
        assert syms["audio_ble_ota_sync_status"] == syms["g2_audio_service_mode"]
        assert syms["g2_audio_log_transport_alt"] == syms["audio_ble_ota_export_state"]
        assert syms["audio_ota_transfer_flag"] == syms["audio_ble_ota_export_state"]
        assert syms["audio_uart_display_state"] == syms["g2_audio_log_wake_enabled"]
        assert syms["audio_ble_connect_event_handler"] == syms["audio_ble_msgtx_handler_id"]
        assert syms["audio_ble_discovery_handler_id_20074f8a"] == syms["audio_ble_profile_handler_id"]
    receipt = {
        "status": "PASS_FIXED_SOURCE_RAM_PLACEMENT",
        "pool_receipt": str(BASE.relative_to(ROOT)), "pool_receipt_sha256": sha(BASE),
        "service_receipt": str(SERVICE.relative_to(ROOT)), "service_receipt_sha256": sha(SERVICE),
        "ota_receipt": str(OTA.relative_to(ROOT)), "ota_receipt_sha256": sha(OTA),
        "ble_receipt": str(BLE.relative_to(ROOT)), "ble_receipt_sha256": sha(BLE),
        "ble_codec_receipt": str(BLE_CODEC.relative_to(ROOT)),
        "ble_codec_receipt_sha256": sha(BLE_CODEC),
        "service_states_receipt": str(SERVICE_STATES.relative_to(ROOT)),
        "service_states_receipt_sha256": sha(SERVICE_STATES),
        "timing_receipt": str(TIMING.relative_to(ROOT)), "timing_receipt_sha256": sha(TIMING),
        "hci_source": str(HCI_SOURCE.relative_to(ROOT)), "hci_source_sha256": sha(HCI_SOURCE),
        "hci_object": str(HCI_OBJECT.relative_to(ROOT)), "hci_object_sha256": sha(HCI_OBJECT),
        "symbol_addresses": cells, "cell_count": len(cells),
        "linker_script": str(SCRIPT.relative_to(ROOT)), "linker_script_sha256": sha(SCRIPT),
        "linked_elf": str(ELF.relative_to(ROOT)), "linked_elf_sha256": sha(ELF),
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["The isolated link proves forty source allocation placements and nonoverlap, including OTA, BLE service, HCI radio, timing and codec routing spans; integration with every other native RAM object, startup initialization, and hardware behavior remain open.",
                  "The current Main pool still contains the earlier HCI cell object; its section changes require a full selected-source rebuild."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cells), sha(RECEIPT))


if __name__ == "__main__":
    main()
