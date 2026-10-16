#!/usr/bin/env python3
"""Bounded no-log stock/C EvenAI frame routing comparison."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
UPSTREAM = ROOT / "third-party/upstream/nanopb"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
COMP = G2 / "components/audio/uart_thread_source_candidate"
ARCHIVE = G2 / "build/c-firmware/20261016/main-nanopb-pinned/libg2_nanopb.a"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert sys.argv[1:] in ([], ["--real-rx"], ["--real-all"], ["--real-service"],
                        ["--log-extended"], ["--log-short"], ["--log-short4"])
LOG_EXT = sys.argv[1:] == ["--log-extended"]
LOG_SHORT = sys.argv[1:] in (["--log-short"], ["--log-short4"])
LOG_VALUE = 2 if LOG_EXT else 4 if sys.argv[1:] == ["--log-short4"] else 1 if LOG_SHORT else 0
REAL_SERVICE = sys.argv[1:] == ["--real-service"]
REAL_ALL = sys.argv[1:] in (["--real-all"], ["--real-service"])
REAL_RX = sys.argv[1:] in (["--real-rx"], ["--real-all"], ["--real-service"])
COMMANDS = ["ctrl", "vad", "ask", "analyse", "reply", "skill", "prompt",
            "event", "heartbeat", "config"]
RX = [0x4e3530, 0x4e391a, 0x4e3d34, 0x4e403c, 0x4e42b4, 0x4e4538,
      0x4e47a0, 0x4e4a34, 0x4e4e5c, 0x4e50d8]
TX = [0x4e35fc, 0x4e39ea, 0x4e3ea4, 0x4e412c, 0x4e43a0, 0x4e4608,
      0x4e4888, 0x4e4b20, 0x4e4f30, 0x4e51c0]

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    stub = tmp / "stub.c"
    lines = ["#include <stddef.h>", "#include <stdint.h>", "#include <stdarg.h>",
             "uint8_t audio_even_ai_last_frame[2];",
             "uint32_t audio_even_ai_trace[4];",
             "uint32_t audio_even_ai_trace_count;",
             "uint32_t audio_even_ai_fail_rx;",
             "uint32_t audio_log_flag_value, audio_log_trace_count, audio_log_trace[112];",
             "uint32_t audio_short_trace_count, audio_short_trace[64];",
             "const uint8_t audio_even_ai_duplicate_status=7;",
             "const uint8_t audio_even_ai_generic_status=8;",
             "uint32_t audio_log_flags(void){return audio_log_flag_value;}",
             "void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){uint32_t*i=audio_log_trace+7*audio_log_trace_count++;i[0]=a;i[1]=(uint32_t)b;i[2]=(uint32_t)c;i[3]=(uint32_t)d;i[4]=e;i[5]=(uint32_t)f;i[6]=0;for(const char*p=f;*p;p++)if(*p=='%'){va_list v;va_start(v,f);i[6]=va_arg(v,uint32_t);va_end(v);break;}}",
             "uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){uint32_t*i=audio_short_trace+4*audio_short_trace_count++;i[0]=a;i[1]=(uint32_t)b;i[2]=(uint32_t)c;i[3]=0;for(const char*p=c;*p;p++)if(*p=='%'){va_list v;va_start(v,c);i[3]=va_arg(v,uint32_t);va_end(v);break;}return 0;}",
             "void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}",
             "void *memset(void*d,int c,size_t n){unsigned char*a=d;for(size_t i=0;i<n;i++)a[i]=(unsigned char)c;return d;}"]
    if not REAL_SERVICE:
        lines.append("uint32_t audio_even_ai_encode_common(uint8_t a,const void*b){(void)b;audio_even_ai_trace[audio_even_ai_trace_count++]=0x40000000u|a;return 0x2ee;}")
    if REAL_RX and not REAL_SERVICE:
        lines.append("int32_t audio_even_ai_service_dispatch_497ea2(uint8_t k,const void*p,uint32_t n){(void)n;const uint8_t*b=p;audio_even_ai_trace[audio_even_ai_trace_count++]=0x20000000u|((uint32_t)k<<16)|b[0];return (int32_t)audio_even_ai_fail_rx;}")
    if REAL_SERVICE:
        lines.extend(["uint8_t audio_even_ai_service_state_2006ed10[0x218];",
                      "uint8_t audio_even_ai_config_state_20074974[3];",
                      "void audio_even_ai_heartbeat_timer_start_4e304c(uint32_t v){(void)v;}",
                      "void audio_even_ai_state_lock_4e1fa6(void){}",
                      "void audio_even_ai_state_unlock_4e1fbe(void){}"])
    if REAL_RX:
        lines.append("void audio_ring_pb_assert_509b48(const void *p){(void)p;}")
    if REAL_ALL:
        lines.extend(["uint8_t audio_even_ai_tx_buffer_2037c4a0[256];",
                      "uint8_t audio_even_ai_proto_message_200f5884[0x20c];",
                      "uint32_t audio_ring_pb_tx_ble_475b14(uint32_t t,uint32_t c,const void*p,uint32_t n){(void)p;(void)n;audio_even_ai_trace[audio_even_ai_trace_count++]=0x10000000u|((t&255u)<<16)|(c&255u);return 0;}"])
    for index, name in enumerate(COMMANDS, 1):
        if not REAL_RX:
            lines.append(f"uint32_t audio_even_ai_rx_{name}(uint8_t a,const void*b){{(void)b;audio_even_ai_trace[audio_even_ai_trace_count++]=({index}u<<16)|a;return audio_even_ai_fail_rx;}}")
        if not REAL_ALL:
            lines.append(f"uint32_t audio_even_ai_tx_{name}(uint8_t a,const void*b){{(void)b;audio_even_ai_trace[audio_even_ai_trace_count++]=0x80000000u|({index}u<<16)|a;return 0x{0x200+index:x};}}")
    stub.write_text("\n".join(lines) + "\n")
    elf = tmp / "frame.elf"
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
             '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
             "-I", str(CONFIG), "-I", str(UPSTREAM)]
    rx_sources = ([str(COMP / name) for name in (
        "even_ai_rx_ctrl_4e3530.c", "even_ai_rx_vad_4e391a.c",
        "even_ai_rx_analyse_4e403c.c", "even_ai_rx_simple_4e47a0.c",
        "even_ai_rx_remaining_4e3d34.c")] if REAL_RX else [])
    tx_sources = ([str(COMP / "even_ai_tx_ctrl_4e35fc.c")] if REAL_ALL else [])
    subprocess.run(["clang", *flags, "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_even_ai_frame_process_4e31cc",
                    str(COMP / "even_ai_frame_process_4e31cc.c"),
                    str(COMP / "even_ai_decoder_context_48f49c.c"),
                    str(COMP / "even_ai_descriptor_777144.c"), *rx_sources,
                    *tx_sources, *([str(COMP / "even_ai_service_dispatch_497ea2.c"),
                                    str(COMP / "even_ai_common_response_4e5338.c")]
                                   if REAL_SERVICE else []), str(stub),
                    str(ARCHIVE), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, wire, null_input=False, duplicate=False, receiver_fails=False):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x400000)
        cpu.mem_write(0x20001000, wire + b"\xa5" * (128 - len(wire)))
        if REAL_ALL:
            cpu.mem_write(0x2037c4a0, b"\xa5" * 256)
            cpu.mem_write(0x200f5884, b"\xa5" * 0x20c)
            cpu.mem_write(symbols["audio_even_ai_tx_buffer_2037c4a0"], b"\xa5" * 256)
            cpu.mem_write(symbols["audio_even_ai_proto_message_200f5884"], b"\xa5" * 0x20c)
        if REAL_SERVICE:
            seed = bytes((i * 17 + 43) & 255 for i in range(0x218))
            config = b"\xa1\xb2\xc3"
            service_addr = symbols["audio_even_ai_service_state_2006ed10"] if compiled else 0x2006ed10
            config_addr = symbols["audio_even_ai_config_state_20074974"] if compiled else 0x20074974
            cpu.mem_write(service_addr, seed)
            cpu.mem_write(config_addr, config)
        sequence = wire[3] if len(wire) >= 4 and wire[2] == 0x10 else 0
        last = bytes([1, sequence]) if duplicate else b"\x00\x00"
        cpu.mem_write(0x20074f36, last)
        cpu.mem_write(symbols["audio_even_ai_last_frame"], last)
        cpu.mem_write(symbols["audio_even_ai_fail_rx"],
                      (1 if receiver_fails else 0).to_bytes(4, "little"))
        cpu.mem_write(symbols["audio_log_flag_value"],
                      LOG_VALUE.to_bytes(4, "little"))
        cpu.reg_write(A.UC_ARM_REG_R0, 0 if null_input else 0x20001000)
        cpu.reg_write(A.UC_ARM_REG_R1, len(wire))
        cpu.reg_write(A.UC_ARM_REG_R2, 0)
        cpu.reg_write(A.UC_ARM_REG_R3, 0)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        trace = []
        logs = []
        short_logs = []
        if not compiled:
            hooks = {0x43d0ce: ("flags", LOG_VALUE)}
            if LOG_EXT:
                hooks[0x43d574] = ("extended", 0)
            if LOG_SHORT:
                hooks[0x43ce9e] = ("short", 0)
            if not REAL_SERVICE:
                hooks[0x4e5338] = ("common", 0x2ee)
            if REAL_SERVICE:
                hooks.update({0x4e304c: ("timer", 0), 0x4e1fa6: ("lock", 0),
                              0x4e1fbe: ("unlock", 0)})
            elif REAL_RX:
                hooks[0x497ea2] = ("service", 1 if receiver_fails else 0)
            else:
                hooks.update({address: (f"rx{index}", 1 if receiver_fails else 0)
                              for index, address in enumerate(RX, 1)})
            if REAL_ALL:
                hooks[0x475b14] = ("send", 0)
            else:
                hooks.update({address: (f"tx{index}", 0x200+index)
                              for index, address in enumerate(TX, 1)})
            def intercept(uc, address, size, _):
                if address not in hooks:
                    return
                name, result = hooks[address]
                if name == "extended":
                    sp = uc.reg_read(A.UC_ARM_REG_SP)
                    words = [uc.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
                    words.extend(int.from_bytes(uc.mem_read(sp + i, 4), "little")
                                 for i in (0, 4, 8))
                    logs.append(tuple(words))
                if name == "short":
                    short_logs.append(tuple(uc.reg_read(reg) for reg in
                                            (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                                             A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)))
                if name not in ("flags", "timer", "lock", "unlock"):
                    if name in ("extended", "short"):
                        uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
                        return
                    if name == "service":
                        kind = uc.reg_read(A.UC_ARM_REG_R0) & 0xff
                        pointer = uc.reg_read(A.UC_ARM_REG_R1)
                        trace.append((f"service{kind}", uc.mem_read(pointer, 1)[0]))
                    elif name == "send":
                        kind = uc.reg_read(A.UC_ARM_REG_R0) & 0xff
                        command = uc.reg_read(A.UC_ARM_REG_R1) & 0xff
                        trace.append(("send", (kind << 8) | command))
                    else:
                        trace.append((name, uc.reg_read(A.UC_ARM_REG_R0) & 0xff))
                uc.reg_write(A.UC_ARM_REG_R0, result)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, intercept)
        entry = symbols["audio_even_ai_frame_process_4e31cc"] if compiled else 0x4e31cc
        cpu.emu_start(entry | 1, 0x600000, count=500000)
        state_addr = symbols["audio_even_ai_last_frame"] if compiled else 0x20074f36
        if compiled:
            count = int.from_bytes(cpu.mem_read(symbols["audio_even_ai_trace_count"], 4), "little")
            assert count <= 4
            raw = cpu.mem_read(symbols["audio_even_ai_trace"], 4 * count)
            trace = [(('common' if value & 0x40000000 else
                       ('service' + str((value >> 16) & 0xff) if value & 0x20000000 else
                        ('send' if value & 0x10000000 else
                       ('tx' if value & 0x80000000 else 'rx') +
                       str((value >> 16) & 0x7fff)))),
                      (((value >> 16) & 0xff) << 8 | (value & 0xff))
                      if value & 0x10000000 else value & 0xff)
                     for value in (int.from_bytes(raw[i:i+4], "little")
                                   for i in range(0, len(raw), 4))]
            if LOG_EXT:
                count = int.from_bytes(cpu.mem_read(symbols["audio_log_trace_count"], 4), "little")
                assert count <= 16
                raw = cpu.mem_read(symbols["audio_log_trace"], 28 * count)
                logs = [tuple(int.from_bytes(raw[i+j:i+j+4], "little")
                              for j in range(0, 28, 4)) for i in range(0, len(raw), 28)]
            if LOG_SHORT:
                count = int.from_bytes(cpu.mem_read(symbols["audio_short_trace_count"], 4), "little")
                assert count <= 16
                raw = cpu.mem_read(symbols["audio_short_trace"], 16 * count)
                short_logs = [tuple(int.from_bytes(raw[i+j:i+j+4], "little")
                                    for j in range(0, 16, 4)) for i in range(0, len(raw), 16)]
        result = (cpu.reg_read(A.UC_ARM_REG_R0),
                  bytes(cpu.mem_read(state_addr, 2)), trace)
        if REAL_ALL:
            out_addr = symbols["audio_even_ai_tx_buffer_2037c4a0"] if compiled else 0x2037c4a0
            msg_addr = symbols["audio_even_ai_proto_message_200f5884"] if compiled else 0x200f5884
            result += (bytes(cpu.mem_read(out_addr, 256)),
                       bytes(cpu.mem_read(msg_addr, 0x20c)))
        if REAL_SERVICE:
            result += (bytes(cpu.mem_read(service_addr, 0x218)),
                       bytes(cpu.mem_read(config_addr, 3)))
        if LOG_EXT:
            def string(address):
                return bytes(cpu.mem_read(address, 160)).split(b"\x00", 1)[0].decode("ascii")
            def argument(fmt, value):
                return string(value) if "%s" in fmt else value if "%" in fmt else None
            result += ([(row[0], string(row[1]), string(row[2]),
                         string(row[3]), row[4], string(row[5]),
                         argument(string(row[5]), row[6])) for row in logs],)
        if LOG_SHORT:
            def string(address):
                return bytes(cpu.mem_read(address, 160)).split(b"\x00", 1)[0].decode("ascii")
            def argument(fmt, value):
                return string(value) if "%s" in fmt else value if "%" in fmt else None
            result += ([(row[0], string(row[1]), string(row[2]),
                         argument(string(row[2]), row[3]))
                        for row in short_logs],)
        return result

    results = []
    for command in range(1, 11):
        sequence = command + 20
        wire = bytes([0x08, command, 0x10, sequence,
                      ((command + 3) << 3) | 2, 0x00])
        stock = run(False, wire)
        source = run(True, wire)
        assert stock == source, (command, stock[:3], source[:3])
        expected_first = (f"service{command}", 0) if REAL_RX and not REAL_SERVICE else (f"rx{command}", sequence)
        expected_last = ("send", 0x107) if REAL_ALL else (f"tx{command}", sequence)
        expected_trace = [expected_last] if REAL_SERVICE else [expected_first, expected_last]
        if not REAL_SERVICE:
            assert stock[2] == expected_trace, (command, stock[:3])
        row = {"command": command, "wire": wire.hex(), "result": stock[0],
               "last_frame": stock[1].hex()}
        if LOG_EXT or LOG_SHORT:
            row["logs"] = stock[-1]
        results.append(row)

    edge_cases = [
        ("null", b"", True, False, False),
        ("decode_error", b"\x08", False, False, False),
        ("generic_zero", b"\x08\x00\x10\x05", False, False, False),
        ("generic_unknown", b"\x08\x0b\x10\x06", False, False, False),
        ("duplicate", b"\x08\x01\x10\x15\x22\x00", False, True, False),
        ("receiver_failure", b"\x08\x01\x10\x15\x22\x00", False, False, True),
    ]
    for name, wire, null_input, duplicate, receiver_fails in edge_cases:
        if REAL_SERVICE and receiver_fails:
            continue
        stock = run(False, wire, null_input, duplicate, receiver_fails)
        source = run(True, wire, null_input, duplicate, receiver_fails)
        assert stock == source, (name, stock, source)
        row = {"edge": name, "wire": wire.hex(), "result": stock[0],
               "last_frame": stock[1].hex()}
        if LOG_EXT or LOG_SHORT:
            row["logs"] = stock[-1]
        results.append(row)

    output = G2 / ("build/c-firmware/20261016/main-even-ai-frame-log-short4-4e31cc/oracle-receipt.json"
                   if sys.argv[1:] == ["--log-short4"] else
                   "build/c-firmware/20261016/main-even-ai-frame-log-short-4e31cc/oracle-receipt.json"
                   if LOG_SHORT else
                   "build/c-firmware/20261016/main-even-ai-frame-log-extended-4e31cc/oracle-receipt.json"
                   if LOG_EXT else
                   "build/c-firmware/20261016/main-even-ai-frame-transitive-service-4e31cc/oracle-receipt.json"
                   if REAL_SERVICE else
                   "build/c-firmware/20261016/main-even-ai-frame-transitive-all-4e31cc/oracle-receipt.json"
                   if REAL_ALL else
                   "build/c-firmware/20261016/main-even-ai-frame-transitive-4e31cc/oracle-receipt.json"
                   if REAL_RX else
                   "build/c-firmware/20261016/main-even-ai-frame-dispatch-4e31cc/oracle-receipt.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": ("PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_SHORT4_4E31CC"
                           if sys.argv[1:] == ["--log-short4"] else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_SHORT_4E31CC" if LOG_SHORT else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_LOG_EXTENDED_4E31CC" if LOG_EXT else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_TRANSITIVE_SERVICE_4E31CC" if REAL_SERVICE else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_TRANSITIVE_ALL_4E31CC" if REAL_ALL else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_TRANSITIVE_4E31CC" if REAL_RX else
                           "PASS_NATIVE_MAIN_EVEN_AI_FRAME_DISPATCH_4E31CC"),
               "cases": len(results), "results": results,
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "source_sha256": hashlib.sha256((COMP / "even_ai_frame_process_4e31cc.c").read_bytes()).hexdigest(),
               "bounds": ("compressed logging flag 1 or 4; compares mask, two format strings, and first formatted value; logger effects and later variadic values excluded; receiver/encoder controlled"
                          if LOG_SHORT else
                          "extended logging flag 2; compares level, module, path, function, line, format string, and first formatted value; logger effects and later variadic values excluded; receiver/encoder controlled"
                          if LOG_EXT else
                          "no-log frame through ten C receive, ten C transmit, C shared service, and common response encoder bodies plus pinned nanopb; timer, state lock, and BLE send controlled; no logging or source-owned RAM placement"
                          if REAL_SERVICE else
                          "no-log frame through ten C receive and ten C transmit bodies plus pinned nanopb; service and BLE send controlled; no logging or service implementation"
                          if REAL_ALL else
                          "no-log frame through ten C receive bodies; service and encoders controlled; no logging or service implementation"
                          if REAL_RX else
                          "no-log command 1-10 routing and six edge paths with controlled receiver/encoder returns; no actual command bodies or logging")}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(results), hashlib.sha256(output.read_bytes()).hexdigest())
