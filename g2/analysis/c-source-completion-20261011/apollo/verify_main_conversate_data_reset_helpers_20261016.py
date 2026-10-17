#!/usr/bin/env python3
"""Direct stock/C replay of six Conversate data reset/accessor leaves."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_data_reset_helpers_20261016.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-data-reset-helpers"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
ENTRIES = {"transcribe_reset": (0x5b430e, "audio_conversate_transcribe_reset_5b430e"),
           "transcribe_get": (0x5b4364, "audio_conversate_transcribe_get_5b4364"),
           "list_clear": (0x5b43d4, "audio_conversate_reply_list_clear_5b43d4"),
           "list_get": (0x5b43e8, "audio_conversate_reply_list_get_5b43e8"),
           "note_reset": (0x5b473a, "audio_conversate_prep_note_reset_5b473a"),
           "note_get": (0x5b4766, "audio_conversate_prep_note_get_5b4766")}
RAM = {"audio_conversate_prep_note_ram_200d7630": 0x200d7630,
       "audio_conversate_reply_status_200d6b84": 0x200d6b84,
       "audio_conversate_transcribe_output_200e2ae4": 0x200e2ae4,
       "audio_conversate_transcribe_length_2007439c": 0x2007439c}
LOWERS = {"audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
          "audio_log_flags": (0x101020, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101030, 0x43d574, "extended"),
          "audio_log_simple": (0x101040, 0x43ce9e, "simple")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-helpers.o", OUT / "oracle-helpers.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_transcribe_reset_5b430e",
                    *[f"--defsym={name}=0x{address:x}" for name, address in RAM.items()],
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, helper, flags, length):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x200d5bd8, bytes((i*11+7)&255 for i in range(0xcf09)))
        cpu.mem_write(0x2007439c, struct.pack("<I", length))
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
            kind = ({v[1]: v[2] for v in LOWERS.values()} if native else
                    {v[0]: v[2] for v in LOWERS.values()}).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "zero":
                events.append((kind, r[0], r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2]&255])*r[1])
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2])))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        stock, symbol = ENTRIES[helper]
        cpu.emu_start((stock if native else symbols[symbol]) | 1, 0, count=400)
        if not done[0]: raise RuntimeError(f"Conversate {helper} did not return")
        result = cpu.reg_read(A.UC_ARM_REG_R0) if helper.endswith("get") else None
        return {"result": result, "events": events,
                "ram_sha256": hashlib.sha256(bytes(cpu.mem_read(0x200d5bd8, 0xcf09))).hexdigest()}

    cases = [(helper, flags, length) for helper in ENTRIES
             for flags in (0, 1, 2, 4, 7) for length in (0, 12)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Conversate reset helper mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_DATA_RESET_HELPERS_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Zeroing and logging are controlled lower contracts.",
                         "The reset helpers are not yet bound to a wider caller replay."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
