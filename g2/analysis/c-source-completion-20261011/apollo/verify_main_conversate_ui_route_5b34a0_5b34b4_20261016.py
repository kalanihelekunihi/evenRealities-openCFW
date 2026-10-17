#!/usr/bin/env python3
"""Direct stock/C replay of two Conversate UI route wrappers."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_route_5b34a0_5b34b4.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-route-5b34a0-5b34b4"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = ((0x5b34a0, "audio_conversate_ui_route_5b34a0"),
           (0x5b34b4, "audio_conversate_ui_route_5b34b4"))
LOWERS = {"audio_conversate_route_scroll_5b22fa": (0x101010, 0x5b22fa, "scroll"),
          "audio_conversate_route_release_58c84e": (0x101020, 0x58c84e, "release")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b3514-0x438000:0x5b3518-0x438000] == struct.pack("<I", 0x20071368)
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_route_5b34a0",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, entry, handle_a, handle_b, state, value):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x2007137c, struct.pack("<II", handle_a, handle_b))
        cpu.reg_write(A.UC_ARM_REG_R0, state)
        cpu.reg_write(A.UC_ARM_REG_R1, value)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            events.append((kind, machine.reg_read(A.UC_ARM_REG_R0)))
            machine.reg_write(A.UC_ARM_REG_R0, 0xdeadbeef)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        address, symbol = ENTRIES[entry]
        cpu.emu_start((address if native else symbols[symbol])|1, 0, count=80)
        if not done[0]: raise RuntimeError("route wrapper did not return")
        return events, cpu.reg_read(A.UC_ARM_REG_R0), bytes(cpu.mem_read(0x2007137c, 8))

    cases = [(entry, a, b, state, value)
             for entry in range(2)
             for a in (0, 1, 0x12345678, 0xffffffff)
             for b in (0, 1, 0x12345678, 0xffffffff)
             for state in (0, 2, 6, 255)
             for value in (0, 0xaabbccdd)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"route wrapper mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_ROUTE_5B34A0_5B34B4_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_bodies": ["0x5b34a0..0x5b34ad", "0x5b34b4..0x5b34cb"],
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Child scroll/release routines are controlled lower contracts."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
