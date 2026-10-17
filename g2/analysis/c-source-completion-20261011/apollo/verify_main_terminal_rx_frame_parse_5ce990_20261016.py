#!/usr/bin/env python3
"""Compare Terminal RX parser with stock decode, logging and replay gates."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_rx_frame_parse_5ce990.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
OUT = G2 / "build/c-firmware/20261016/main-terminal-rx-frame-5ce990"
SEQ, LAST, DATA, MESSAGE, ERROR = 0x20074fff, 0x20074874, 0x20080000, 0x20081000, 0x20082000
CALLS = {
    "audio_uart_pb_stream_init": (0x48f49c, 3),
    "audio_uart_checksum_copy": (0x439c04, 3),
    "audio_uart_pb_decode": (0x490120, 3),
    "g2_flashdb_candidate_tick": (0x4490cc, 0),
    "audio_log_flags": (0x43d0ce, 0),
    "audio_log_extended": (0x43d574, 0),
    "compressed_log_output": (0x43ce9e, 0),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf = OUT / "rx-frame-oracle.o", OUT / "rx-frame-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-DOPENCFW_ORACLE_EXTERNAL_RX_TICK",
                    "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, (address, _) in CALLS.items()}
    defs.update(audio_terminal_tx_pb_descriptor=0x77c634,
                audio_terminal_message_sequence=SEQ,
                audio_terminal_rx_last_tick_20074874=LAST)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    *(f"--defsym={name}=0x{address:x}" for name, address in defs.items()),
                    str(obj), "-o", str(elf)], check=True, stderr=subprocess.DEVNULL)
    with elf.open("rb") as f:
        e = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in e.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbol = next(s["st_value"] for s in
                      e.get_section_by_name(".symtab").iter_symbols()
                      if s.name == "audio_registry_ring_connect_parse_5ce990")
    by_address = {address: (name, argc) for name, (address, argc) in CALLS.items()}

    def run(compiled, data_ok, message_ok, decoded, error_ok, seq, incoming,
            last, tick, flags):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, content in segments:
            u.mem_write(address, content)
        u.mem_map(0x20000000, 0x100000)
        u.mem_write(SEQ, bytes((seq,)))
        u.mem_write(LAST, struct.pack("<I", last))
        u.mem_write(DATA, bytes(range(32)))
        u.mem_write(MESSAGE, bytes((0xa1, 0xb2, 0xc3, 0xd4)) + bytes(12))
        u.mem_write(ERROR, b"bad stream\0")
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, DATA if data_ok else 0)
        u.reg_write(A.UC_ARM_REG_R1, 0x10014)
        u.reg_write(A.UC_ARM_REG_R2, MESSAGE if message_ok else 0)
        trace = []
        flag_index = 0

        def cstr(cpu, ptr):
            return bytes(cpu.mem_read(ptr, 180)).split(b"\0", 1)[0]

        def hook(cpu, pc, size, _):
            nonlocal flag_index
            if pc not in by_address:
                return
            name, argc = by_address[pc]
            r = [cpu.reg_read(reg) for reg in
                 (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                  A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            result = 0
            if name == "audio_uart_pb_stream_init":
                trace.append((name, r[1], r[2]))
                cpu.mem_write(r[0], struct.pack("<IIII", 0x48f3a5, r[1], r[2], 0))
            elif name == "audio_uart_checksum_copy":
                trace.append((name, r[2]))
                cpu.mem_write(r[0], bytes(cpu.mem_read(r[1], r[2])))
            elif name == "audio_uart_pb_decode":
                trace.append((name, r[1], r[2]))
                if decoded:
                    cpu.mem_write(r[2]+1, bytes((incoming,)))
                    result = 1
                elif error_ok:
                    cpu.mem_write(r[0]+12, struct.pack("<I", ERROR))
            elif name == "g2_flashdb_candidate_tick":
                trace.append((name, ()))
                result = tick
            elif name == "audio_log_flags":
                trace.append(("flags", flag_index))
                result = flags[min(flag_index, len(flags)-1)]
                flag_index += 1
            elif name == "audio_log_extended":
                line, message = struct.unpack("<II", cpu.mem_read(sp, 8))
                n = 2 if line == 0x7e else int(line in (0x77,))
                values = struct.unpack("<" + "I"*n, cpu.mem_read(sp+8, 4*n)) if n else ()
                values = tuple(cstr(cpu, x) if line == 0x77 else x for x in values)
                trace.append(("extended", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]),
                              cstr(cpu, r[3]), line, cstr(cpu, message), values))
            elif name == "compressed_log_output":
                n = 2 if r[0] == 0x08800000 else int(r[0] == 0x04400000)
                values = (r[3],) + struct.unpack("<I", cpu.mem_read(sp, 4)) if n == 2 else \
                         ((cstr(cpu, r[3]),) if n == 1 else ())
                trace.append(("compact", r[0], cstr(cpu, r[1]), cstr(cpu, r[2]), values))
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        u.hook_add(UC_HOOK_CODE, hook)
        u.emu_start((symbol if compiled else 0x5ce990) | 1, 0x600000, count=800)
        return (trace, bytes(u.mem_read(MESSAGE, 16)), bytes(u.mem_read(SEQ, 1)),
                bytes(u.mem_read(LAST, 4)), u.reg_read(A.UC_ARM_REG_R0))

    cases = 0
    scenarios = ((0,1,1,0,1,2,100,200), (1,0,1,0,1,2,100,200),
                 (1,1,0,0,1,2,100,200), (1,1,0,1,1,2,100,200),
                 (1,1,1,0,1,1,100,200), (1,1,1,0,1,1,100,3200),
                 (1,1,1,0,1,2,100,200), (1,1,1,0,255,255,0xfffffffe,1))
    for scenario, flags in itertools.product(scenarios,
                ((0,0,0),(2,0,0),(0,1,0),(0,0,4),(2,1,4))):
        args = (*scenario, flags)
        stock, candidate = run(False, *args), run(True, *args)
        if stock != candidate:
            for n, (a,b) in enumerate(itertools.zip_longest(stock[0],candidate[0])):
                if a!=b:
                    print("first call mismatch",args,n,a,b)
                    break
            for n in range(1,len(stock)):
                if stock[n]!=candidate[n]:print("field differs",args,n,stock[n],candidate[n])
            raise RuntimeError("Terminal RX parser mismatch")
        cases += 1
    receipt = {"status":"PASS_EXPERIMENTAL_MAIN_TERMINAL_RX_FRAME_C_ORACLE",
               "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
               "payload_sha256":PIN,"oracle_elf_sha256":sha(elf),"cases":cases,
               "scope":"Null/decode gates, sequence duplicate timeout, wrap, enabled logs and state writes",
               "limits":["Nanopb decode, tick and logger effects isolated; final RAM placement and hardware remain open."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(receipt["status"],cases,sha(path))


if __name__=="__main__":
    main()
