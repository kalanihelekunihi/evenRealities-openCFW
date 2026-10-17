#!/usr/bin/env python3
"""Compare native/C Conversate action-lock branches with controlled CMSIS."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_action_lock_5b01ca.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-lock-5b01ca"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_conversate_action_mutex_20074398": 0x20074398,
          "audio_conversate_mutex_init_5b0120": 0x101010,
          "audio_file_mutex_acquire": 0x101020,
          "audio_log_flags": 0x101030,
          "audio_log_extended": 0x101040,
          "audio_log_simple": 0x101050}
NATIVE = {0x5b0120: "init", 0x4497b6: "acquire", 0x43d0ce: "flags",
          0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {0x101010: "init", 0x101020: "acquire", 0x101030: "flags",
            0x101040: "extended", 0x101050: "simple"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    obj, elf_path = OUT / "oracle-lock.o", OUT / "oracle-lock.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_enter_5b01ca",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, handle, init_result, acquire_result, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20074398, struct.pack("<I", handle))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 160)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "init":
                events.append((kind,))
                if init_result == 0:
                    machine.mem_write(0x20074398, struct.pack("<I", 0x20045000))
                machine.reg_write(A.UC_ARM_REG_R0, init_result)
            elif kind == "acquire":
                events.append((kind, r[0], r[1]))
                machine.reg_write(A.UC_ARM_REG_R0, acquire_result)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                fmt = string(word(sp+4))
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, word(sp+8) if "%d" in fmt else None))
            elif kind == "simple":
                fmt = string(r[1])
                events.append((kind, r[0], fmt, string(r[2]),
                               r[3] if "%d" in fmt else None))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b01ca if native else symbols["audio_conversate_enter_5b01ca"]
        cpu.emu_start(entry | 1, 0, count=400)
        if not done[0]: raise RuntimeError("Conversate lock did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0),
                "handle": word(0x20074398), "events": events}

    cases = []
    for handle in (0, 0x20045000):
        for init_result in (0, 7):
            for acquire_result in (0, 5, 0xffffffff):
                for flags in (0, 1, 2, 4, 7):
                    fixture = [handle, init_result, acquire_result, flags]
                    native_result = run(True, *fixture)
                    compiled_result = run(False, *fixture)
                    if native_result != compiled_result:
                        raise RuntimeError(f"Conversate lock mismatch {fixture}: {native_result} != {compiled_result}")
                    cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_LOCK_5B01CA_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Mutex initialization/acquire and logging are controlled lower contracts."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
