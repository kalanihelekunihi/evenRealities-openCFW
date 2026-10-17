#!/usr/bin/env python3
"""Compare native/C SyncInfo notify paths with controlled allocator and children."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/sync_info_notify_471fa4.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-sync-info-notify-471fa4"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "codec_allocate": 0x101010, "audio_file_heap_free": 0x101020,
    "audio_uart_buffer_zero": 0x101030, "audio_get_running_app_ids": 0x101040,
    "audio_pb_ostream_from_buffer": 0x101050,
    "audio_uart_display_area_copy_439c04": 0x101060,
    "audio_pb_encode": 0x101070, "audio_settings_notify_ble": 0x101080,
    "audio_log_flags": 0x101090, "audio_log_extended": 0x1010a0,
    "audio_log_simple": 0x1010b0,
    "audio_sync_info_pb_descriptor_77c1cc": 0x77c1cc,
}
NATIVE = {0x474cd2: "alloc", 0x474d16: "free", 0x43c0e4: "zero",
          0x443504: "ids", 0x4905f4: "ostream", 0x439c04: "copy",
          0x490c32: "encode", 0x475c1a: "send", 0x43d0ce: "flags",
          0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {LOWERS[name]: kind for name, kind in (
    ("codec_allocate", "alloc"), ("audio_file_heap_free", "free"),
    ("audio_uart_buffer_zero", "zero"), ("audio_get_running_app_ids", "ids"),
    ("audio_pb_ostream_from_buffer", "ostream"),
    ("audio_uart_display_area_copy_439c04", "copy"),
    ("audio_pb_encode", "encode"), ("audio_settings_notify_ble", "send"),
    ("audio_log_flags", "flags"), ("audio_log_extended", "extended"),
    ("audio_log_simple", "simple"))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    obj, elf_path = OUT / "oracle-notify.o", OUT / "oracle-notify.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_display_sync_info",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, fail_alloc, encoded_ok, flags, sent):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20030000, bytes([0xaa])*12)
        cpu.mem_write(0x20031000, bytes([0xbb])*128)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done, allocated = [], [False], [0]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def string(address):
            return bytes(cpu.mem_read(address, 128)).split(b"\0")[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "alloc":
                allocated[0] += 1
                address = (0x20030000 if allocated[0] == 1 else 0x20031000)
                machine.reg_write(A.UC_ARM_REG_R0,
                                  0 if fail_alloc == allocated[0] else address)
                events.append((kind, r[0], fail_alloc == allocated[0]))
            elif kind == "free":
                events.append((kind, r[0]))
            elif kind == "zero":
                machine.mem_write(r[0], bytes(r[1]))
                events.append((kind, r[0], r[1]))
            elif kind == "ids":
                machine.mem_write(r[0], struct.pack("<I", 0x11223344))
                machine.mem_write(r[1], struct.pack("<I", 0x55667788))
                machine.reg_write(A.UC_ARM_REG_R0, 1)
                events.append((kind,))
            elif kind == "ostream":
                machine.mem_write(r[0], struct.pack("<5I", 0x11111111, r[1], r[2], 0, 0))
                events.append((kind, r[1], r[2]))
            elif kind == "copy":
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
                events.append((kind, r[2]))
            elif kind == "encode":
                if encoded_ok:
                    machine.mem_write(r[0]+12, struct.pack("<I", 23))
                    machine.mem_write(0x20031000, bytes(range(23)))
                machine.reg_write(A.UC_ARM_REG_R0, int(encoded_ok))
                events.append((kind, r[1] == 0x77c1cc,
                               bytes(machine.mem_read(r[2], 12)).hex()))
            elif kind == "send":
                events.append((kind, r[0], r[1], r[2], r[3]))
                machine.reg_write(A.UC_ARM_REG_R0, sent)
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
        entry = 0x471fa4 if native else symbols["audio_uart_display_sync_info"]
        cpu.emu_start(entry | 1, 0, count=1000)
        if not done[0]: raise RuntimeError("SyncInfo notify did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0),
                "response": bytes(cpu.mem_read(0x20030000, 12)).hex(),
                "buffer": bytes(cpu.mem_read(0x20031000, 128)).hex(),
                "events": events}

    cases = []
    for fail_alloc, encoded_ok, sent in ((1, False, 0), (2, False, 0),
                                         (0, False, 0), (0, True, 0),
                                         (0, True, 19)):
        for flags in (0, 1, 2, 4, 7):
            fixture = [fail_alloc, encoded_ok, flags, sent]
            native_result = run(True, *fixture)
            compiled_result = run(False, *fixture)
            if native_result != compiled_result:
                raise RuntimeError(f"SyncInfo notify mismatch {fixture}: {native_result} != {compiled_result}")
            cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_SYNC_INFO_NOTIFY_471FA4_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)),
              "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Allocator, protobuf and BLE children are controlled contracts.",
                         "Selected failure, success and log paths only; arbitrary runtime contents remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
