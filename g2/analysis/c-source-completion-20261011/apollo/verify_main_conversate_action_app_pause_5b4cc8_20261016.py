#!/usr/bin/env python3
"""Bounded native/C check for the Conversate app-pause action."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_action_app_pause_5b4cc8.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-app-pause-5b4cc8"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_log_flags": 0x101010, "audio_log_extended": 0x101020,
          "audio_log_simple": 0x101030}
NATIVE = {0x43d0ce: "flags", 0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {v: k.removeprefix("audio_log_") for k, v in LOWERS.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-pause.o", OUT / "oracle-pause.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_action_5b4cc8",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments() if p["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, flags, context, arg1, arg2):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        for reg, val in ((A.UC_ARM_REG_R0, context), (A.UC_ARM_REG_R1, arg1),
                         (A.UC_ARM_REG_R2, arg2), (A.UC_ARM_REG_SP, 0x200ff000),
                         (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, val)
        events, done = [], [False]

        def word(address): return struct.unpack("<I", cpu.mem_read(address, 4))[0]
        def string(address):
            return bytes(cpu.mem_read(address, 180)).split(b"\0")[0].decode("utf-8", "replace")
        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2])))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b4cc8 if native else symbols["audio_conversate_action_5b4cc8"]) | 1,
                      0, count=300)
        if not done[0]: raise RuntimeError("App-pause action did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events}

    cases = [(flags, ctx, arg1, arg2)
             for flags in (0, 1, 2, 3, 4, 7, 255)
             for ctx, arg1, arg2 in ((0, 0, 0), (0x20022000, 0x20023000, 0x20024000))]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"App-pause mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_APP_PAUSE_5B4CC8_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Logging lower contracts are controlled; no hardware behavior is established."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__": main()
