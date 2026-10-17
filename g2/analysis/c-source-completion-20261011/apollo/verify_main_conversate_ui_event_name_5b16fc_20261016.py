#!/usr/bin/env python3
"""Direct stock/C replay of the UI event-name lookup using a synthetic table."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_event_name_5b16fc.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-event-name-5b16fc"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b1afc-0x438000:0x5b1b00-0x438000] == (0x785820).to_bytes(4, "little")
    assert payload[0x5b1b00-0x438000:0x5b1b04-0x438000] == (0x20000560).to_bytes(4, "little")
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_event_name_5b16fc",
                    "--defsym=audio_conversate_ui_event_names_20000560=0x20000560",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        for index in range(21):
            ptr = 0x20001000 + index*32
            cpu.mem_write(0x20000560 + index*4, struct.pack("<I", ptr))
            cpu.mem_write(ptr, f"SYNTHETIC_UI_EVENT_{index:02d}".encode()+b"\0")
        cpu.reg_write(A.UC_ARM_REG_R0, event)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        cpu.emu_start((0x5b16fc if native else symbols["audio_conversate_ui_event_name_5b16fc"])|1,
                      0x101f00, count=60)
        ptr = cpu.reg_read(A.UC_ARM_REG_R0)
        return bytes(cpu.mem_read(ptr, 64)).split(b"\0", 1)[0].decode("latin1")

    cases = list(range(256)) + [0x100, 0x101, 0x114, 0x115, 0xffffffff]
    for event in cases:
        stock, selected = run(True, event), run(False, event)
        if stock != selected:
            raise RuntimeError(f"UI event name mismatch {event}: {stock} != {selected}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_NAME_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b16fc..0x5b1715",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "remaining_gate": "Table contents and initializer at RAM 0x20000560 remain unauthenticated."}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
