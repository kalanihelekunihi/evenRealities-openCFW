#!/usr/bin/env python3
"""Compare stock and compiled SyncInfo common-data callback with controlled children."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/sync_info_common_data_handler_472102.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-sync-info-common-472102"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

LOWERS = {"audio_uart_pb_stream_init": 0x101010,
          "audio_uart_display_area_copy_439c04": 0x101020,
          "audio_uart_pb_decode": 0x101030,
          "audio_sync_info_command_471ee8": 0x101040,
          "audio_log_flags": 0x101050,
          "audio_log_extended": 0x101060,
          "audio_log_simple": 0x101070,
          "audio_sync_info_state_200740bc": 0x200740bc,
          "audio_sync_info_pb_descriptor_77c1cc": 0x77c1cc}
NATIVE = {0x43c0e4: "zero", 0x48f49c: "stream", 0x439c04: "copy",
          0x490120: "decode", 0x471ee8: "command", 0x43d0ce: "flags",
          0x43d574: "extended", 0x43ce9e: "simple"}
COMPILED = {value: name for name, value in LOWERS.items() if name in (
    "audio_uart_pb_stream_init", "audio_uart_display_area_copy_439c04",
    "audio_uart_pb_decode", "audio_sync_info_command_471ee8",
    "audio_log_flags", "audio_log_extended", "audio_log_simple")}
COMPILED = {address: {"audio_uart_pb_stream_init": "stream",
                      "audio_uart_display_area_copy_439c04": "copy",
                      "audio_uart_pb_decode": "decode",
                      "audio_sync_info_command_471ee8": "command",
                      "audio_log_flags": "flags", "audio_log_extended": "extended",
                      "audio_log_simple": "simple"}[name] for address, name in COMPILED.items()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA:
        raise RuntimeError("stock Main payload changed")
    obj, elf_path = OUT / "callback.o", OUT / "callback.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_registry_callback_472102",
                    *[f"--defsym={name}=0x{value:x}" for name, value in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(part["p_vaddr"], part.data()) for part in elf.iter_segments()
                    if part["p_type"] == "PT_LOAD"]
        symbols = {item.name: item["st_value"] for item in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, success, command, flags, error_present):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x20021000, b"bad wire\0")
        cpu.mem_write(0x200740bc, bytes(range(12)))
        for register, value in ((A.UC_ARM_REG_R0, event), (A.UC_ARM_REG_R1, 0x20022000),
                                (A.UC_ARM_REG_R2, 7), (A.UC_ARM_REG_SP, 0x200ff000),
                                (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(register, value)
        events, done = [], [False]

        def word(address):
            return struct.unpack("<I", cpu.mem_read(address, 4))[0]

        def cstr(address):
            if address == 0: return ""
            result = bytearray()
            for offset in range(256):
                c = cpu.mem_read(address+offset, 1)[0]
                if c == 0: break
                result.append(c)
            return result.decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = (NATIVE if native else COMPILED).get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "zero":
                machine.mem_write(r[0], bytes(r[1]))
            elif kind == "stream":
                machine.mem_write(r[0], struct.pack("<4I", 0x11111111, r[1], r[2], 0))
            elif kind == "copy":
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
            elif kind == "decode":
                if success:
                    machine.mem_write(r[2], bytes((command, 5)))
                else:
                    machine.mem_write(r[0]+12, struct.pack("<I", 0x20021000 if error_present else 0))
                machine.reg_write(A.UC_ARM_REG_R0, 1 if success else 0)
                events.append((kind, r[1] == 0x77c1cc))
            elif kind == "command":
                events.append((kind, r[0]))
                machine.reg_write(A.UC_ARM_REG_R0, 17)
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                fmt = cstr(word(sp+4))
                value = cstr(word(sp+8)) if "%s" in fmt else word(sp+8)
                events.append((kind, r[0], cstr(r[1]), cstr(r[2]), cstr(r[3]),
                               word(sp), fmt, value))
            elif kind == "simple":
                fmt = cstr(r[1])
                events.append((kind, r[0], fmt, cstr(r[2]),
                               cstr(r[3]) if "%s" in fmt else r[3]))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x472102 if native else symbols["audio_uart_registry_callback_472102"]
        cpu.emu_start(entry | 1, 0, count=600)
        if not done[0]: raise RuntimeError("SyncInfo callback did not return")
        return {"result": cpu.reg_read(A.UC_ARM_REG_R0),
                "state": bytes(cpu.mem_read(0x200740bc, 12)).hex(), "events": events}

    cases = []
    for event in (0, 1):
        for success, command, error_present in ((False, 0, False), (False, 0, True),
                                                (True, 0, False), (True, 7, False)):
            for flags in (0, 1, 2, 4, 7):
                native_result = run(True, event, success, command, flags, error_present)
                compiled_result = run(False, event, success, command, flags, error_present)
                fixture = [event, success, command, flags, error_present]
                if native_result != compiled_result:
                    raise RuntimeError(f"SyncInfo mismatch {fixture}: {native_result} != {compiled_result}")
                cases.append(fixture)
    record = {"status": "PASS_BOUNDED_MAIN_SYNC_INFO_COMMON_472102_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "object": str(obj.relative_to(ROOT)), "object_sha256": hashlib.sha256(obj.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)), "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "cases": len(cases), "fixtures": cases,
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Protobuf descriptor and command handler are controlled lower contracts.",
                         "Only the selected success/failure and log flag paths were compared; arbitrary schema contents and formatter behavior remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
