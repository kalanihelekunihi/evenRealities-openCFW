#!/usr/bin/env python3
"""Composed native/C replay of app-config copy and UI settings update."""
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
SOURCE_DIR = G2 / "components/audio/uart_thread_source_candidate"
SOURCES = [SOURCE_DIR / "conversate_action_app_config_5b4dba.c",
           SOURCE_DIR / "conversate_ui_settings_update_5b133c.c"]
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-app-config-composed"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {"audio_log_flags": (0x101010, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101020, 0x43d574, "extended"),
          "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
          "audio_queue_copy_bytes": (0x101040, 0x439be4, "copy"),
          "audio_conversate_report_5b02e4": (0x101050, 0x5b02e4, "report")}
NATIVE = {v[1]: v[2] for v in LOWERS.values()}
COMPILED = {v[0]: v[2] for v in LOWERS.values()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    objects = []
    for index, source in enumerate(SOURCES):
        obj = OUT / f"composed-{index}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                        str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    elf_path = OUT / "oracle-composed.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_action_5b4dba",
                    "--defsym=audio_conversate_machine_context_200e3aec=0x200e3aec",
                    "--defsym=audio_conversate_ui_settings_extension_20071369=0x20071369",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    *(str(obj) for obj in objects), "-o", str(elf_path)],
                   check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, present, enabled, settings):
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
        packet = bytes((0, enabled, *settings)) + bytes(24)
        cpu.mem_write(0x20022000, packet)
        cpu.mem_write(0x200e3aec, b"\xaa" * 8)
        cpu.mem_write(0x20071368, bytes((i * 19 + 5) & 255 for i in range(0x95)))
        for reg, value in ((A.UC_ARM_REG_R0, 0x200e3aec),
                           (A.UC_ARM_REG_R1, 0x20022000 if present else 0),
                           (A.UC_ARM_REG_R2, 0x20023000),
                           (A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None:
                return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            elif kind == "copy":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
            elif kind == "report":
                events.append((kind, r[0], r[1]))
            else:
                raise RuntimeError(f"unexpected logging call with flags=0: {kind}")
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b4dba if native else symbols["audio_conversate_action_5b4dba"]) | 1,
                      0, count=1500)
        if not done[0]:
            raise RuntimeError("Composed app-config path did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0), "events": events,
                "machine": bytes(cpu.mem_read(0x200e3aec, 8)).hex(),
                "ui": bytes(cpu.mem_read(0x20071368, 0x95)).hex()}

    cases = [(False, 0, (0, 0, 0, 0, 0)),
             (True, 0, (1, 1, 1, 1, 1)),
             (True, 1, (0, 0, 0, 0, 0)),
             (True, 1, (1, 0, 1, 0, 4)),
             (True, 1, (0, 1, 1, 1, 255)),
             (True, 1, (1, 1, 1, 1, 5)),
             (True, 255, (255, 128, 127, 64, 32))]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Composed app-config mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_COMPOSED_MAIN_CONVERSATE_APP_CONFIG_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "sources": [{"path": str(source.relative_to(ROOT)),
                           "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
                          for source in SOURCES],
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Copy, logging and report remain controlled contracts.",
                         "The fixture covers bounded settings but not startup initialization or physical UI behavior."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
