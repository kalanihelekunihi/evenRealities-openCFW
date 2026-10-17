#!/usr/bin/env python3
"""Bounded native/C comparison of the Conversate receive and duplicate gate."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_receive_frame_5b1b4c.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-receive-5b1b4c"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_conversate_last_magic_20074ff8": 0x20074ff8,
    "audio_conversate_last_frame_tick_2007485c": 0x2007485c,
    "audio_conversate_response_descriptor_775b24": 0x775b24,
    "audio_dump_hex": 0x101010,
    "audio_uart_pb_stream_init": 0x101020,
    "audio_uart_display_area_copy_439c04": 0x101030,
    "audio_uart_pb_decode": 0x101040,
    "g2_flashdb_candidate_tick": 0x101050,
    "audio_log_flags": 0x101060,
    "audio_log_extended": 0x101070,
    "audio_log_simple": 0x101080,
}
NATIVE = {0x43dacc: "dump", 0x48f49c: "stream", 0x439c04: "copy",
          0x490120: "decode", 0x4490cc: "tick", 0x43d0ce: "flags",
          0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {LOWERS[name]: kind for name, kind in (
    ("audio_dump_hex", "dump"), ("audio_uart_pb_stream_init", "stream"),
    ("audio_uart_display_area_copy_439c04", "copy"),
    ("audio_uart_pb_decode", "decode"), ("g2_flashdb_candidate_tick", "tick"),
    ("audio_log_flags", "flags"), ("audio_log_extended", "extended"),
    ("audio_log_simple", "simple"))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-receive.o", OUT / "oracle-receive.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_receive_5b1b4c",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as f:
        elf = ELFFile(f)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments() if p["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, length, success, error_present, command, magic,
            last_magic, last_tick, now, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20022000, bytes(range(64)))
        cpu.mem_write(0x20023000, b"\xaa" * 32)
        cpu.mem_write(0x20024000, b"bad wire\0")
        cpu.mem_write(0x20074ff8, bytes((last_magic,)))
        cpu.mem_write(0x2007485c, struct.pack("<I", last_tick))
        for reg, val in ((A.UC_ARM_REG_R0, 0x20022000 if present & 1 else 0),
                         (A.UC_ARM_REG_R1, length),
                         (A.UC_ARM_REG_R2, 0x20023000 if present & 2 else 0),
                         (A.UC_ARM_REG_SP, 0x200ff000),
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
            if kind == "dump":
                events.append((kind, string(r[0]), r[1], r[2] == 0x20022000, r[3]))
            elif kind == "stream":
                machine.mem_write(r[0], struct.pack("<4I", 0x11111111, r[1], r[2], 0))
                events.append((kind, r[1] == 0x20022000, r[2]))
            elif kind == "copy":
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
                events.append((kind, r[2]))
            elif kind == "decode":
                if success:
                    machine.mem_write(r[2], bytes((command, magic)))
                else:
                    machine.mem_write(r[0]+12, struct.pack("<I", 0x20024000 if error_present else 0))
                machine.reg_write(A.UC_ARM_REG_R0, int(success))
                events.append((kind, r[1] == 0x775b24, r[2] == 0x20023000))
            elif kind == "tick":
                machine.reg_write(A.UC_ARM_REG_R0, now)
                events.append((kind,))
            elif kind == "flags":
                machine.reg_write(A.UC_ARM_REG_R0, flags)
                events.append((kind,))
            elif kind == "extended":
                fmt = string(word(sp+4))
                args = tuple(word(sp+8+i*4) for i in range(fmt.count("%d") + fmt.count("%s")))
                if "%s" in fmt: args = tuple(string(x) for x in args)
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, args))
            elif kind == "simple":
                fmt = string(r[1])
                argc = fmt.count("%d") + fmt.count("%s")
                args = tuple(([r[3]] if argc else []) +
                             [word(sp+i*4) for i in range(max(0, argc-1))])
                if "%s" in fmt: args = tuple(string(x) for x in args)
                events.append((kind, r[0], fmt, string(r[2]), args))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5b1b4c if native else symbols["audio_conversate_receive_5b1b4c"]
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]: raise RuntimeError("Conversate receive did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events,
                "message": bytes(cpu.mem_read(0x20023000, 2)).hex(),
                "last_magic": bytes(cpu.mem_read(0x20074ff8, 1)).hex(),
                "last_tick": word(0x2007485c)}

    cases = []
    fixtures = [
        (0, 5, True, False, 1, 7, 7, 100, 100, 7),
        (1, 5, True, False, 1, 7, 7, 100, 100, 0),
        (2, 5, True, False, 1, 7, 7, 100, 100, 4),
    ]
    for success in (False, True):
        for error_present in (False, True):
            for length in (5, 33, 65535):
                for flags in (0, 1, 2, 4, 7):
                    for magic, last_magic, last_tick, now in (
                            (9, 7, 100, 101), (7, 7, 100, 100),
                            (7, 7, 100, 3099), (7, 7, 100, 3100),
                            (7, 7, 0xfffffffe, 1)):
                        fixtures.append((3, length, success, error_present, 3, magic,
                                         last_magic, last_tick, now, flags))
    for fixture in fixtures:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b: raise RuntimeError(f"Conversate receive mismatch {fixture}: {a} != {b}")
        cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_RECEIVE_5B1B4C_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Nanopb decode, stream setup, tick, and logging are controlled lower contracts.",
                         "No full packet grammar or hardware behavior is established."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__": main()
