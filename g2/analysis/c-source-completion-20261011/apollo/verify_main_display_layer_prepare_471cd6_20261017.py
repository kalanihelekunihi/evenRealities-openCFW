#!/usr/bin/env python3
"""Replay Apollo display pin grouping and layer-enable register effects."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_layer_prepare_471cd6.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-display-layer-prepare-471cd6"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_uart_pin_mux_enable": (0x4c44bc, "mux"),
          "g2_gpio_critical_save": (0x473940, "critical")}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "layer-prepare.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_layer_prepare",
                    *[f"--defsym={name}=0x{address:x}" for name, (address, _) in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, entry_kind, channel, pin, gate_value, low_bits):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x10000)
        cpu.mem_map(0x40008000, 0x1000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        register = 0x40008200 + channel * 32
        if entry_kind == "layer":
            cpu.mem_write(0x40008010, struct.pack("<I", gate_value))
            cpu.mem_write(register, struct.pack("<I", (pin << 8) | low_bits))
        cpu.reg_write(A.UC_ARM_REG_R0, pin if entry_kind == "group" else channel)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x2000f000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        kinds = {address: name for address, name in LOWERS.values()}
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            name = kinds.get(pc)
            if name is None:
                return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            r1 = machine.reg_read(A.UC_ARM_REG_R1)
            if name == "mux":
                events.append((name, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            else:
                events.append((name,))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ({"group": 0x471b9c, "layer": 0x471cd6}[entry_kind] if native
                 else symbols["audio_uart_display_pin_group_471b9c"
                              if entry_kind == "group" else
                              "audio_uart_display_layer_prepare"])
        cpu.emu_start(entry | 1, 0, count=500)
        if not done[0]:
            raise RuntimeError(f"display layer did not return: {native} {entry_kind} {channel} {pin}")
        result = cpu.reg_read(A.UC_ARM_REG_R0)
        if entry_kind == "group":
            return result, events
        return (result, struct.unpack("<I", cpu.mem_read(0x40008010, 4))[0],
                struct.unpack("<I", cpu.mem_read(register, 4))[0], events)

    cases = [("group", 0, pin, 0, 0) for pin in range(40)]
    cases += [("layer", channel, pin, gate, low)
              for channel in (0, 1, 7, 13, 14, 15)
              for pin in (0, 5, 6, 9, 10, 18, 19, 24, 25, 27, 28, 511)
              for gate, low in ((0, 0), (0xa000, 3))]
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"display layer mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_DIRECT_MAIN_DISPLAY_LAYER_PREPARE_471CD6_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_bodies": ["0x471b9c..0x471bc9", "0x471cd6..0x471d57"],
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": sha(elf_path), "source_complete": False,
              "flashable": False, "hardware_proof": False,
              "limits": ["Pin mux and interrupt-save calls are controlled lower boundaries; MMIO reads/writes are emulated, not physical hardware proof."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt))


if __name__ == "__main__":
    main()
