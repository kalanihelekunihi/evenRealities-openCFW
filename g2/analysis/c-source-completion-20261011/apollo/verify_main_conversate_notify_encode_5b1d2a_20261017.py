#!/usr/bin/env python3
"""Bounded stock/C replay of Conversate notify frame encoding."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_notify_encode_5b1d2a.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-conversate-notify-5b1d2a"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
DATA = {"audio_conversate_response_frame_200f4808": 0x200f4808,
        "audio_conversate_response_encoded_2037c2a0": 0x2037c2a0,
        "audio_conversate_last_magic_20074ff8": 0x20074ff8,
        "audio_conversate_response_descriptor_775b24": 0x775b24}
LOWERS = {"audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
          "audio_pb_ostream_from_buffer": (0x101020, 0x4905f4, "ostream"),
          "audio_uart_display_area_copy_439c04": (0x101030, 0x439c04, "copy"),
          "audio_pb_encode": (0x101040, 0x490c32, "encode"),
          "audio_uart_device_role_get": (0x101050, 0x45a568, "role"),
          "audio_ring_pb_tx_ble_475c1a": (0x101060, 0x475c1a, "send"),
          "audio_log_flags": (0x101070, 0x43d0ce, "flags"),
          "audio_log_extended": (0x101080, 0x43d574, "extended"),
          "compressed_log_output": (0x101090, 0x43ce9e, "simple")}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-start.o", OUT / "oracle-start.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_close_notify_5b1d2a",
                    *[f"--defsym={name}=0x{address:x}" for name, address in DATA.items()],
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD" and part["p_vaddr"] < 0x20000000]
        symbols = {item.name: item["st_value"] for item in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, magic, success, error_present, role, flags, notification):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x400000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x200f4808, bytes([0xaa])*4012)
        cpu.mem_write(0x2037c2a0, bytes([0xbb])*256)
        cpu.mem_write(0x20074ff8, bytes([magic]))
        cpu.mem_write(0x20023000, b"bad wire\0")
        cpu.mem_write(0x20024000, struct.pack("<H", notification or 0))
        for reg, value in ((A.UC_ARM_REG_SP, 0x200ff000),
                           (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        cpu.reg_write(A.UC_ARM_REG_R0, 0 if notification is None else 0x20024000)
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
                machine.mem_write(r[0], bytes(r[1]))
                events.append((kind, r[0], r[1]))
            elif kind == "ostream":
                machine.mem_write(r[0], struct.pack("<5I", 0x11111111, r[1], r[2], 0, 0))
                events.append((kind, r[1], r[2]))
            elif kind == "copy":
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
                events.append((kind, r[2]))
            elif kind == "encode":
                if success:
                    machine.mem_write(r[0]+12, struct.pack("<I", 23))
                    machine.mem_write(0x2037c2a0, bytes(range(23)))
                else:
                    machine.mem_write(r[0]+16, struct.pack("<I", 0x20023000 if error_present else 0))
                machine.reg_write(A.UC_ARM_REG_R0, int(success))
                events.append((kind, r[1] == 0x775b24,
                               bytes(machine.mem_read(r[2], 12)).hex()))
            elif kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "send":
                events.append((kind, r[0], r[1], r[2], r[3]))
                machine.reg_write(A.UC_ARM_REG_R0, 19)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                fmt = string(word(sp+4))
                item = (kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                        word(sp), fmt)
                if "%s" in fmt:
                    item += (string(word(sp+8)),)
                events.append(item)
            elif kind == "simple":
                item = (kind, r[0], string(r[1]), string(r[2]))
                if "%s" in string(r[1]):
                    item += (string(r[3]),)
                events.append(item)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b1d2a if native else symbols["audio_conversate_ui_close_notify_5b1d2a"]) | 1,
                      0, count=800)
        if not done[0]: raise RuntimeError("Conversate notify did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0),
                "frame_sha256": hashlib.sha256(bytes(cpu.mem_read(0x200f4808, 4012))).hexdigest(),
                "encoded_sha256": hashlib.sha256(bytes(cpu.mem_read(0x2037c2a0, 256))).hexdigest(),
                "events": events}

    cases = [(magic, success, error_present, role, flags, notification)
             for magic in (0, 255)
             for success, error_present in ((False, False), (False, True), (True, False))
             for role in (0, 1) for flags in (0, 1, 2, 4, 7)
             for notification in (None, 0, 0x1234)]
    for fixture in cases:
        a, b = run(True, *fixture), run(False, *fixture)
        if a != b:
            raise RuntimeError(f"Conversate notify mismatch {fixture}: {a} != {b}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_NOTIFY_5B1D2A_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Nanopb encoding, role and BLE send are controlled lower contracts.",
                         "Arbitrary protobuf contents and wider Main behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
