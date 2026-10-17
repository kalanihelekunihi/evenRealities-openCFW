#!/usr/bin/env python3
"""Compare native/C Conversate machine dispatch with controlled action leaves."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_machine_dispatch_5b4904.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-dispatch-5b4904"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
TARGETS = {1: 0x5b4a90, 2: 0x5b4cc8, 3: 0x5b4d10, 4: 0x5b4e98,
           5: 0x5b4dba, 8: 0x5b5150, 9: 0x5b52e0, 10: 0x5b4f72,
           11: 0x5b5428, 12: 0x5b55b4}
LOWERS = {"audio_conversate_machine_context_200e3aec": 0x200e3aec,
          "audio_conversate_event_name_5b48f8": 0x101010,
          "audio_log_flags": 0x101020,
          "audio_log_extended": 0x101030,
          "audio_log_simple": 0x101040}
for event, target in TARGETS.items():
    LOWERS[f"audio_conversate_action_{target:x}"] = 0x101100 + event*16 + 1
NATIVE = {0x5b48f8: ("name", None), 0x43d0ce: ("flags", None),
          0x43d574: ("extended", None), 0x43ce9e: ("simple", None)}
NATIVE.update({address: ("action", event) for event, address in TARGETS.items()})
COMPILED = {LOWERS["audio_conversate_event_name_5b48f8"]: ("name", None),
            LOWERS["audio_log_flags"]: ("flags", None),
            LOWERS["audio_log_extended"]: ("extended", None),
            LOWERS["audio_log_simple"]: ("simple", None)}
COMPILED.update({LOWERS[f"audio_conversate_action_{address:x}"] & ~1:
                 ("action", event) for event, address in TARGETS.items()})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-dispatch.o", OUT / "oracle-dispatch.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_dispatch_5b4904",
                    *[f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, flags, action_result):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20025000, b"fixture event\0")
        for reg, value in ((A.UC_ARM_REG_R0, event),
                           (A.UC_ARM_REG_R1, 0x20022000),
                           (A.UC_ARM_REG_R2, 0x20023000),
                           (A.UC_ARM_REG_R3, 0x20024000),
                           (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def word(address): return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 180)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            item = (NATIVE if native else COMPILED).get(pc)
            if item is None: return
            kind, route = item
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "name":
                events.append((kind, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20025000)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "action":
                events.append((kind, route, r[0] == 0x200e3aec,
                               r[1] == 0x20022000, r[2] == 0x20023000))
                machine.reg_write(A.UC_ARM_REG_R0, action_result)
            elif kind == "extended":
                fmt = string(word(sp+4))
                args = [word(sp+8+i*4) for i in range(fmt.count("%d")+fmt.count("%s"))]
                if "%s" in fmt and args: args[-1] = string(args[-1])
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, tuple(args)))
            elif kind == "simple":
                fmt = string(r[1])
                argc = fmt.count("%d")+fmt.count("%s")
                args = ([r[3]] if argc else []) + [word(sp+i*4) for i in range(max(0, argc-1))]
                if "%s" in fmt and args: args[-1] = string(args[-1])
                events.append((kind, r[0], fmt, string(r[2]), tuple(args)))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b4904 if native else symbols["audio_conversate_dispatch_5b4904"]
        cpu.emu_start(entry | 1, 0, count=1500)
        if not done[0]: raise RuntimeError("Conversate dispatch did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events}

    cases = []
    for event in (*range(13), 13, 127, 255):
        for flags in (0, 1, 2, 4, 7):
            for action_result in (0, 5):
                fixture = (event, flags, action_result)
                a, b = run(True, *fixture), run(False, *fixture)
                if a != b: raise RuntimeError(f"Conversate dispatch mismatch {fixture}: {a} != {b}")
                cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_DISPATCH_5B4904_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "stock_action_table": {str(k): hex(v | 1) for k, v in TARGETS.items()},
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Ten action bodies, event-name table, logging and machine context are controlled lowers.",
                         "No arbitrary action or hardware behavior is established."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__": main()
