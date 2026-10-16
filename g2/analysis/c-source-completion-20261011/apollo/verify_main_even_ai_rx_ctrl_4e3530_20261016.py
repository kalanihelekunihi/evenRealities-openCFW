#!/usr/bin/env python3
"""Compare Apollo EvenAI control receive C against stock with bounded callees."""
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
assert sys.argv[1:] in ([], ["--vad"], ["--analyse"], ["--prompt"],
                        ["--event"], ["--heartbeat"], ["--ask"],
                        ["--reply"], ["--skill"], ["--config"])
VARIANT = sys.argv[1][2:] if len(sys.argv) > 1 else "ctrl"
SPECS = {"ctrl": ("even_ai_rx_ctrl_4e3530.c", "audio_even_ai_rx_ctrl", 0x4e3530,
                  "main-even-ai-rx-ctrl-4e3530", "PASS_NATIVE_MAIN_EVEN_AI_RX_CTRL_4E3530"),
         "vad": ("even_ai_rx_vad_4e391a.c", "audio_even_ai_rx_vad", 0x4e391a,
                 "main-even-ai-rx-vad-4e391a", "PASS_NATIVE_MAIN_EVEN_AI_RX_VAD_4E391A"),
         "analyse": ("even_ai_rx_analyse_4e403c.c", "audio_even_ai_rx_analyse", 0x4e403c,
                     "main-even-ai-rx-analyse-4e403c", "PASS_NATIVE_MAIN_EVEN_AI_RX_ANALYSE_4E403C"),
         "prompt": ("even_ai_rx_simple_4e47a0.c", "audio_even_ai_rx_prompt", 0x4e47a0,
                    "main-even-ai-rx-prompt-4e47a0", "PASS_NATIVE_MAIN_EVEN_AI_RX_PROMPT_4E47A0"),
         "event": ("even_ai_rx_simple_4e47a0.c", "audio_even_ai_rx_event", 0x4e4a34,
                   "main-even-ai-rx-event-4e4a34", "PASS_NATIVE_MAIN_EVEN_AI_RX_EVENT_4E4A34"),
         "heartbeat": ("even_ai_rx_simple_4e47a0.c", "audio_even_ai_rx_heartbeat", 0x4e4e5c,
                       "main-even-ai-rx-heartbeat-4e4e5c", "PASS_NATIVE_MAIN_EVEN_AI_RX_HEARTBEAT_4E4E5C"),
         "ask": ("even_ai_rx_remaining_4e3d34.c", "audio_even_ai_rx_ask", 0x4e3d34,
                 "main-even-ai-rx-ask-4e3d34", "PASS_NATIVE_MAIN_EVEN_AI_RX_ASK_4E3D34"),
         "reply": ("even_ai_rx_remaining_4e3d34.c", "audio_even_ai_rx_reply", 0x4e42b4,
                   "main-even-ai-rx-reply-4e42b4", "PASS_NATIVE_MAIN_EVEN_AI_RX_REPLY_4E42B4"),
         "skill": ("even_ai_rx_remaining_4e3d34.c", "audio_even_ai_rx_skill", 0x4e4538,
                   "main-even-ai-rx-skill-4e4538", "PASS_NATIVE_MAIN_EVEN_AI_RX_SKILL_4E4538"),
         "config": ("even_ai_rx_remaining_4e3d34.c", "audio_even_ai_rx_config", 0x4e50d8,
                    "main-even-ai-rx-config-4e50d8", "PASS_NATIVE_MAIN_EVEN_AI_RX_CONFIG_4E50D8")}
FILENAME, SYMBOL, STOCK_ENTRY, BUILD_DIR, STATUS = SPECS[VARIANT]
SOURCE = G2 / "components/audio/uart_thread_source_candidate" / FILENAME
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    stub = tmp / "stub.c"
    stub.write_text("""#include <stdint.h>
struct record {uint32_t type,detail;const char *path,*function;uint32_t line;};
uint32_t service_result, trace_opcode, trace_payload, trace_length, trace_service_called;
uint32_t fault_record[5], trace_fault_called;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_even_ai_service_dispatch_497ea2(uint8_t kind,const void *p,uint32_t n){trace_service_called=1;trace_opcode=kind;trace_payload=(uint32_t)p;trace_length=n;return (int32_t)service_result;}
void audio_ring_pb_assert_509b48(const struct record *p){const uint32_t *w=(const uint32_t *)p;trace_fault_called=1;for(int i=0;i<5;i++)fault_record[i]=w[i];}
""")
    elf = tmp / "rx.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e," + SYMBOL, str(SOURCE), str(stub),
                    "-o", str(elf)], check=True)
    with elf.open("rb") as f:
        parsed = ELFFile(f)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, status, result):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, IMAGE)
        cpu.mem_map(0x100000, 0x100000)
        for address, blob in segments:
            cpu.mem_write(address, blob)
        cpu.mem_map(0x20000000, 0x100000)
        cpu.mem_write(0x20000100, bytes([status or 0, 0x47]))
        cpu.mem_write(symbols["service_result"], result.to_bytes(4, "little"))
        cpu.reg_write(A.UC_ARM_REG_R0, 0x35)
        cpu.reg_write(A.UC_ARM_REG_R1, 0 if status is None else 0x20000100)
        cpu.reg_write(A.UC_ARM_REG_R2, 0)
        cpu.reg_write(A.UC_ARM_REG_R3, 0)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
        calls = []
        if not compiled:
            def intercept(uc, address, size, _):
                if address == 0x43d0ce:
                    value = 0
                elif address == 0x497ea2:
                    calls.append(("service", uc.reg_read(A.UC_ARM_REG_R0) & 0xff,
                                  uc.reg_read(A.UC_ARM_REG_R1), uc.reg_read(A.UC_ARM_REG_R2)))
                    value = result
                elif address == 0x509b48:
                    pointer = uc.reg_read(A.UC_ARM_REG_R0)
                    raw = bytes(uc.mem_read(pointer, 20))
                    calls.append(("fault", tuple(int.from_bytes(raw[i:i+4], "little")
                                                 for i in range(0, 20, 4))))
                    value = 0
                else:
                    return
                uc.reg_write(A.UC_ARM_REG_R0, value)
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, intercept)
        entry = symbols[SYMBOL] if compiled else STOCK_ENTRY
        cpu.emu_start(entry | 1, 0x600000, count=100000)
        if compiled:
            def field(name):
                return int.from_bytes(cpu.mem_read(symbols[name], 4), "little")
            if field("trace_service_called"):
                calls.append(("service", field("trace_opcode"), field("trace_payload"),
                              field("trace_length")))
            if field("trace_fault_called"):
                raw = bytes(cpu.mem_read(symbols["fault_record"], 20))
                calls.append(("fault", tuple(int.from_bytes(raw[i:i+4], "little")
                                             for i in range(0, 20, 4))))
        normalized = []
        for call in calls:
            if call[0] == "fault":
                fields = call[1]
                def string(address):
                    data = bytes(cpu.mem_read(address, 160))
                    return data.split(b"\x00", 1)[0].decode("ascii")
                normalized.append(("fault", fields[0], fields[1],
                                   string(fields[2]), string(fields[3]), fields[4]))
            else:
                normalized.append(call)
        return cpu.reg_read(A.UC_ARM_REG_R0), normalized

    cases = []
    for status in (None, 0, 1, 2, 3, 255):
        for result in (0, 1, 0xffffffff):
            stock = run(False, status, result)
            source = run(True, status, result)
            assert stock == source, (status, result, stock, source)
            cases.append({"status": status, "service_result": result,
                          "return": stock[0], "calls": [x[0] for x in stock[1]]})
    output = G2 / "build/c-firmware/20261016" / BUILD_DIR / "oracle-receipt.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt = {"status": STATUS,
               "cases": len(cases), "results": cases,
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "stock_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
               "bounds": "logging flags zero; controlled service and fault callees; no service implementation"}
    output.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], len(cases), hashlib.sha256(output.read_bytes()).hexdigest())
