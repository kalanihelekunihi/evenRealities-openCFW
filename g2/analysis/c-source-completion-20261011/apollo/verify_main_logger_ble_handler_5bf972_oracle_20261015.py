#!/usr/bin/env python3
"""Compare the bounded BLE logger handler with the official Main body."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_logger_ble_handler_5bf972.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x5bf972-0x438000:0x5bf9f6-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-logger-ble-handler-5bf972"
OUT.mkdir(parents=True, exist_ok=True)
STUBS = ("audio_uart_buffer_zero", "audio_pb_ostream_from_buffer", "audio_pb_encode",
         "audio_ring_pb_tx_ble_475c1a")
NATIVE = {"audio_uart_buffer_zero": 0x43c0e4, "copy": 0x439be4,
          "audio_pb_ostream_from_buffer": 0x4905f4, "stream_copy": 0x439c04,
          "audio_pb_encode": 0x490c32, "audio_ring_pb_tx_ble_475c1a": 0x475c1a}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\nconst uint8_t audio_uart_ble_log_pb_descriptor_777da4[4]={0};\n" +
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in STUBS))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-w",
                    "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_logger_ble_handler_5bf972", str(SOURCE),
                    str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")

    def run(compiled, length, encoded):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x200000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.mem_map(0x20300000, 0x100000)
        input_addr = 0x20010000
        pattern = bytes((i*17+11)&255 for i in range(max(length, 1)))
        uc.mem_write(input_addr, pattern)
        frame = symbols["audio_uart_ble_log_frame_20069b24"] if compiled else 0x20069b24
        buffer = symbols["audio_uart_ble_log_encoded_2037cba0"] if compiled else 0x2037cba0
        descriptor = symbols["audio_uart_ble_log_pb_descriptor_777da4"] if compiled else 0x777da4
        uc.mem_write(frame, b"\xa5"*0x508)
        uc.reg_write(A.UC_ARM_REG_R0, input_addr)
        uc.reg_write(A.UC_ARM_REG_R1, length)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        hooks = {((symbols[s] & ~1) if compiled else a): s
                 for s, a in NATIVE.items() if not compiled or s in STUBS}
        trace = []

        def observe(cpu, address, size, _):
            kind = hooks.get(address)
            if kind is None: return
            r = [cpu.reg_read(x) for x in (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                           A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            result = 0
            if kind == "audio_uart_buffer_zero":
                assert r == [frame, 0x508, 0, r[3]]
                cpu.mem_write(r[0], bytes(r[1]))
            elif kind in ("copy", "stream_copy"):
                cpu.mem_write(r[0], bytes(cpu.mem_read(r[1], r[2])))
            elif kind == "audio_pb_ostream_from_buffer":
                assert r[1:3] == [buffer, 0xc8]
                cpu.mem_write(r[0], u32(0)+u32(buffer)+u32(0xc8)+u32(0)+u32(0))
            elif kind == "audio_pb_encode":
                assert r[1] == descriptor and r[2] == frame
                cpu.mem_write(r[0]+12, u32(0x10123))
                result = encoded
            elif kind == "audio_ring_pb_tx_ble_475c1a":
                trace.append((kind, r[0], r[1], r[2] == buffer, r[3]))
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols["audio_uart_logger_ble_handler_5bf972"] if compiled else 0x5bf972
        uc.emu_start(start | 1, 0x600000, count=10000)
        return (uc.reg_read(A.UC_ARM_REG_R0), bytes(uc.mem_read(frame, 0x508)), trace)

    cases = 0
    for length in (0, 1, 2, 0x7f, 0x80, 0x81, 0x100, 0x200):
        for encoded in (0, 1):
            native = run(False, length, encoded)
            candidate = run(True, length, encoded)
            if native != candidate:
                raise AssertionError((length, encoded, native[0], candidate[0],
                                      native[1][:140].hex(), candidate[1][:140].hex(),
                                      native[2], candidate[2]))
            cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LOGGER_BLE_HANDLER_5BF972",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA, "native_body_sha256": BODY_SHA,
               "source_owned_symbols": ["audio_uart_logger_ble_handler_5bf972"],
               "cases": cases,
               "limits": ["Nanopb encode and BLE transmit were controlled hooks; final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2)+"\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
