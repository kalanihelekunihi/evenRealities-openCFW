#!/usr/bin/env python3
"""Compare EvenAI control encoder C and pinned nanopb against stock."""
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
COMP = G2 / "components/audio/uart_thread_source_candidate"
SOURCE = COMP / "even_ai_tx_ctrl_4e35fc.c"
assert sys.argv[1:] in ([], ["--vad"], ["--prompt"], ["--event"],
                        ["--heartbeat"], ["--ask"], ["--analyse"],
                        ["--reply"], ["--skill"], ["--config"])
VARIANT = sys.argv[1][2:] if len(sys.argv) > 1 else "ctrl"
SPECS = {"ctrl": ("audio_even_ai_tx_ctrl", 0x4e35fc,
                  "main-even-ai-tx-ctrl-4e35fc", "PASS_NATIVE_MAIN_EVEN_AI_TX_CTRL_4E35FC"),
         "vad": ("audio_even_ai_tx_vad", 0x4e39ea,
                 "main-even-ai-tx-vad-4e39ea", "PASS_NATIVE_MAIN_EVEN_AI_TX_VAD_4E39EA"),
         "prompt": ("audio_even_ai_tx_prompt", 0x4e4888,
                    "main-even-ai-tx-prompt-4e4888", "PASS_NATIVE_MAIN_EVEN_AI_TX_PROMPT_4E4888"),
         "event": ("audio_even_ai_tx_event", 0x4e4b20,
                   "main-even-ai-tx-event-4e4b20", "PASS_NATIVE_MAIN_EVEN_AI_TX_EVENT_4E4B20"),
         "heartbeat": ("audio_even_ai_tx_heartbeat", 0x4e4f30,
                       "main-even-ai-tx-heartbeat-4e4f30", "PASS_NATIVE_MAIN_EVEN_AI_TX_HEARTBEAT_4E4F30"),
         "ask": ("audio_even_ai_tx_ask", 0x4e3ea4,
                 "main-even-ai-tx-ask-4e3ea4", "PASS_NATIVE_MAIN_EVEN_AI_TX_ASK_4E3EA4"),
         "analyse": ("audio_even_ai_tx_analyse", 0x4e412c,
                     "main-even-ai-tx-analyse-4e412c", "PASS_NATIVE_MAIN_EVEN_AI_TX_ANALYSE_4E412C"),
         "reply": ("audio_even_ai_tx_reply", 0x4e43a0,
                   "main-even-ai-tx-reply-4e43a0", "PASS_NATIVE_MAIN_EVEN_AI_TX_REPLY_4E43A0"),
         "skill": ("audio_even_ai_tx_skill", 0x4e4608,
                   "main-even-ai-tx-skill-4e4608", "PASS_NATIVE_MAIN_EVEN_AI_TX_SKILL_4E4608"),
         "config": ("audio_even_ai_tx_config", 0x4e51c0,
                    "main-even-ai-tx-config-4e51c0", "PASS_NATIVE_MAIN_EVEN_AI_TX_CONFIG_4E51C0")}
SYMBOL, STOCK_ENTRY, BUILD_DIR, STATUS = SPECS[VARIANT]
UPSTREAM = ROOT / "third-party/upstream/nanopb"
CONFIG = G2 / "config-recovered/nanopb/g2-config"
ARCHIVE = G2 / "build/c-firmware/20261016/main-nanopb-pinned/libg2_nanopb.a"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    stub = tmp / "stub.c"
    stub.write_text("""#include <stdint.h>
#include <stddef.h>
uint8_t audio_even_ai_tx_buffer_2037c4a0[256];
uint8_t audio_even_ai_proto_message_200f5884[0x20c];
uint32_t send_called,send_type,send_command,send_payload,send_length;
uint32_t fault_called,fault_record[5];
struct record{uint32_t type,detail;const char *path,*function;uint32_t line;};
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
void audio_ring_pb_assert_509b48(const struct record *p){const uint32_t*w=(const uint32_t*)p;fault_called=1;for(int i=0;i<5;i++)fault_record[i]=w[i];}
uint32_t audio_ring_pb_tx_ble_475b14(uint32_t t,uint32_t c,const void*p,uint32_t n){send_called=1;send_type=t;send_command=c;send_payload=(uint32_t)p;send_length=n;return 0;}
void *memcpy(void*d,const void*s,size_t n){unsigned char*a=d;const unsigned char*b=s;for(size_t i=0;i<n;i++)a[i]=b[i];return d;}
void *memset(void*d,int c,size_t n){unsigned char*a=d;for(size_t i=0;i<n;i++)a[i]=(unsigned char)c;return d;}
""")
    elf = tmp / "encode.elf"
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb", "-std=c11",
             "-ffreestanding", "-fno-builtin", "-O2", "-Wall", "-Wextra", "-Werror",
             '-DPB_SYSTEM_HEADER="pb_g2_system.h"', "-include", str(CONFIG / "pb_g2_options.h"),
             "-I", str(CONFIG), "-I", str(UPSTREAM)]
    subprocess.run(["clang", *flags, "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e," + SYMBOL, str(SOURCE),
                    str(COMP / "even_ai_descriptor_777144.c"), str(stub),
                    str(ARCHIVE), "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, sequence, value, null_input=False):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x400000)
        cpu.mem_write(0x20000100, bytes([value, 0x47, 0x58, 0x69]))
        cpu.mem_write(0x2037c4a0, b"\xa5" * 256)
        cpu.mem_write(0x200f5884, b"\xa5" * 0x20c)
        cpu.mem_write(symbols["audio_even_ai_tx_buffer_2037c4a0"], b"\xa5" * 256)
        cpu.mem_write(symbols["audio_even_ai_proto_message_200f5884"], b"\xa5" * 0x20c)
        cpu.reg_write(A.UC_ARM_REG_R0, sequence)
        cpu.reg_write(A.UC_ARM_REG_R1, 0 if null_input else 0x20000100)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x203ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        calls = []
        if not compiled:
            def intercept(uc, address, size, _):
                if address == 0x43d0ce:
                    result = 0
                elif address == 0x475b14:
                    t = uc.reg_read(A.UC_ARM_REG_R0)
                    c = uc.reg_read(A.UC_ARM_REG_R1)
                    ptr = uc.reg_read(A.UC_ARM_REG_R2)
                    n = uc.reg_read(A.UC_ARM_REG_R3)
                    calls.append(("send", t, c, n, bytes(uc.mem_read(ptr, n)).hex()))
                    result = 0
                elif address == 0x509b48:
                    ptr = uc.reg_read(A.UC_ARM_REG_R0)
                    raw = bytes(uc.mem_read(ptr, 20))
                    calls.append(("fault", tuple(int.from_bytes(raw[i:i+4], "little")
                                                 for i in range(0, 20, 4))))
                    result = 0
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_R0, result)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, intercept)
        entry = symbols[SYMBOL] if compiled else STOCK_ENTRY
        cpu.emu_start(entry | 1, 0x600000, count=500000)
        if compiled:
            def field(name):
                return int.from_bytes(cpu.mem_read(symbols[name], 4), "little")
            if field("send_called"):
                n = field("send_length")
                calls.append(("send", field("send_type"), field("send_command"),
                              n, bytes(cpu.mem_read(field("send_payload"), n)).hex()))
            if field("fault_called"):
                raw = bytes(cpu.mem_read(symbols["fault_record"], 20))
                calls.append(("fault", tuple(int.from_bytes(raw[i:i+4], "little")
                                             for i in range(0, 20, 4))))
        normalized = []
        for call in calls:
            if call[0] != "fault":
                normalized.append(call)
                continue
            fields = call[1]
            def string(address):
                return bytes(cpu.mem_read(address, 160)).split(b"\x00", 1)[0].decode("ascii")
            normalized.append(("fault", fields[0], fields[1],
                               string(fields[2]), string(fields[3]), fields[4]))
        output_addr = (symbols["audio_even_ai_tx_buffer_2037c4a0"] if compiled else 0x2037c4a0)
        message_addr = (symbols["audio_even_ai_proto_message_200f5884"] if compiled else 0x200f5884)
        return (cpu.reg_read(A.UC_ARM_REG_R0), normalized,
                bytes(cpu.mem_read(output_addr, 256)),
                bytes(cpu.mem_read(message_addr, 0x20c)))

    results = []
    for sequence in (0, 1, 127, 255):
        for value in (0, 1, 3, 255):
            stock = run(False, sequence, value)
            source = run(True, sequence, value)
            assert stock == source, (sequence, value, stock[:2], source[:2],
                                     stock[2][:32].hex(), source[2][:32].hex())
            results.append({"sequence": sequence, "value": value,
                            "return": stock[0], "calls": [x[0] for x in stock[1]]})
    stock = run(False, 5, 0, True)
    source = run(True, 5, 0, True)
    assert stock[:2] == source[:2], ("null", stock[:2], source[:2])
    results.append({"null": True, "return": stock[0], "calls": [x[0] for x in stock[1]]})

    output = G2 / "build/c-firmware/20261016" / BUILD_DIR / "oracle-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": STATUS,
               "cases": len(results), "results": results,
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "nanopb_archive_sha256": hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "bounds": "logging disabled; pinned protobuf encode, shared buffers, send args, and null fault; BLE send callee controlled"}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(results), hashlib.sha256(output.read_bytes()).hexdigest())
