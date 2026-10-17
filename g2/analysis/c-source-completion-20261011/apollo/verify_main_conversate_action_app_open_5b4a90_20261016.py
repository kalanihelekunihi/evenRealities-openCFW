#!/usr/bin/env python3
"""Bounded native/C replay of the Conversate app-open action."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_action_app_open_5b4a90.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-app-open-5b4a90"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
    "audio_conversate_ui_state_get_5b16d0": (0x101040, 0x5b16d0, "state"),
    "audio_conversate_ui_state_name_5b16dc": (0x101050, 0x5b16dc, "name"),
    "audio_queue_copy_bytes": (0x101060, 0x439be4, "copy"),
    "audio_conversate_apply_config_5b133c": (0x101070, 0x5b133c, "apply"),
    "audio_conversate_page_show_54f380": (0x101080, 0x54f380, "page"),
    "audio_conversate_prep_note_update_5b43ee": (0x101090, 0x5b43ee, "prep"),
    "audio_conversate_tag_storage_init_59619e": (0x1010a0, 0x59619e, "refresh"),
    "audio_uart_device_role_get": (0x1010b0, 0x45a568, "role"),
    "audio_uart_ring_wear_persist_48eb32": (0x1010c0, 0x48eb32, "wear"),
    "audio_system_alert_command_45a8ee": (0x1010d0, 0x45a8ee, "alert"),
    "audio_quicklist_tick_now": (0x1010e0, 0x44a1c6, "resume"),
    "audio_conversate_report_5b02e4": (0x1010f0, 0x5b02e4, "report"),
}
NATIVE = {v[1]: v[2] for v in LOWERS.values()}
COMPILED = {v[0]: v[2] for v in LOWERS.values()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-open.o", OUT / "oracle-open.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_action_5b4a90",
                    "--defsym=audio_conversate_machine_context_200e3aec=0x200e3aec",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, state, config, prep, role, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        packet = bytearray(0xa0)
        packet[1] = config
        packet[2:7] = bytes((2, 3, 4, 1, 6))
        packet[7] = prep
        packet[10:20] = b"note data\0"
        packet[0x8c:0x90] = struct.pack("<I", 17)
        cpu.mem_write(0x20022000, bytes(packet))
        cpu.mem_write(0x200e3aec, b"\xaa" * 16)
        for reg, value in ((A.UC_ARM_REG_R0, 0x200e3aec),
                           (A.UC_ARM_REG_R1, 0x20022000 if present else 0),
                           (A.UC_ARM_REG_R2, 0x20023000),
                           (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 200)).split(b"\0")[0].decode("utf-8", "replace")

        def arguments(fmt, vals):
            types = []
            pos = 0
            while True:
                mark = fmt.find("%", pos)
                if mark < 0:
                    break
                if mark + 1 < len(fmt) and fmt[mark + 1] in "dsu":
                    types.append(fmt[mark + 1])
                pos = mark + 2
            return tuple(string(v) if t == "s" else v for t, v in zip(types, vals))

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None:
                return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "state":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, state)
            elif kind == "name":
                events.append((kind, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0, 0x20024000)
                machine.mem_write(0x20024000, b"invalid-state\0")
            elif kind == "copy":
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
                events.append((kind, r[0] == 0x200e3aed, r[1] == 0x20022002, r[2]))
            elif kind in ("apply", "refresh"):
                events.append((kind,))
            elif kind == "page":
                events.append((kind, r[0]))
            elif kind == "prep":
                events.append((kind, r[0] == 0x20022008))
            elif kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "wear":
                events.append((kind, r[0], r[1], tuple(struct.unpack("<II", machine.mem_read(r[2], 8)))))
            elif kind == "alert":
                events.append((kind, *r))
            elif kind == "resume":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, 0x1234)
            elif kind == "report":
                events.append((kind, r[0], r[1]))
            elif kind == "extended":
                fmt = string(word(sp + 4))
                count = fmt.count("%d") + fmt.count("%s") + fmt.count("%u")
                vals = [word(sp + 8 + i * 4) for i in range(count)]
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), fmt, arguments(fmt, vals)))
            elif kind == "simple":
                fmt = string(r[1])
                count = fmt.count("%d") + fmt.count("%s") + fmt.count("%u")
                vals = ([r[3]] if count else []) + [word(sp + i * 4) for i in range(max(0, count - 1))]
                events.append((kind, r[0], fmt, string(r[2]), arguments(fmt, vals)))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b4a90 if native else symbols["audio_conversate_action_5b4a90"]) | 1,
                      0, count=1400)
        if not done[0]:
            raise RuntimeError("App-open action did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events,
                "context": bytes(cpu.mem_read(0x200e3aec, 16)).hex()}

    bases = [(False, 0, 0, 0, 0), (True, 2, 1, 1, 1),
             (True, 0, 0, 0, 0), (True, 0, 1, 1, 1),
             (True, 0, 1, 0, 0), (True, 1, 0, 1, 0),
             (True, 1, 1, 0, 1), (True, 3, 1, 1, 1),
             (True, 3, 0, 0, 0), (True, 255, 1, 1, 1)]
    cases = [(present, state, config, prep, role, flags)
             for flags in (0, 1, 2, 4, 7)
             for present, state, config, prep, role in bases]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"App-open mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_APP_OPEN_5B4A90_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Lower calls and logging are controlled contracts.",
                         "No radio, display, flash or physical hardware behavior is proven."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
