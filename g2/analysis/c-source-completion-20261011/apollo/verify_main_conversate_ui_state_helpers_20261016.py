#!/usr/bin/env python3
"""Compare stock/C Conversate UI-state getter and name lookup on controlled RAM."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_state_helpers_5b16d0.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-state-helpers"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_conversate_ui_state_20071368": 0x20071368,
          "audio_conversate_ui_state_names_20000540": 0x20000540}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-ui-state.o", OUT / "oracle-ui-state.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_state_get_5b16d0",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, kind, value):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20071368, bytes((value & 255,)))
        for i in range(7):
            address = 0x20025000+i*32
            cpu.mem_write(address, f"fixture state {i}\0".encode())
            cpu.mem_write(0x20000540+i*4, struct.pack("<I", address))
        cpu.reg_write(A.UC_ARM_REG_R0, value)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        done = [False]
        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
        cpu.hook_add(UC_HOOK_CODE, hook)
        native_entry = 0x5b16d0 if kind == "get" else 0x5b16dc
        compiled_entry = symbols["audio_conversate_ui_state_get_5b16d0" if kind == "get"
                                 else "audio_conversate_ui_state_name_5b16dc"]
        cpu.emu_start((native_entry if native else compiled_entry) | 1, 0, count=60)
        if not done[0]: raise RuntimeError("UI-state helper did not return")
        result = cpu.reg_read(A.UC_ARM_REG_R0)
        if kind == "get": return result
        return bytes(cpu.mem_read(result, 80)).split(b"\0")[0].decode()

    cases = [(kind, value) for kind in ("get", "name")
             for value in (0, 1, 2, 3, 4, 5, 6, 7, 8, 127, 255, 256, 262, 0xffffffff)]
    for kind, value in cases:
        a, b = run(True, kind, value), run(False, kind, value)
        if a != b: raise RuntimeError(f"UI-state helper mismatch {(kind, value)}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_STATE_HELPERS_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["UI-state RAM byte and seven-entry name table contents/initialization remain unauthenticated."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__": main()
