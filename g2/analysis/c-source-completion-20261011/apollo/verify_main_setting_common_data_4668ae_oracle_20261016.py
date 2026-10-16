#!/usr/bin/env python3
"""Controlled native/C comparison for the stock Setting common-data callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/setting_common_data_handler_4668ae.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x4668ae-0x438000:0x466976-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261016/main-setting-common-data-4668ae"
CALLS = {"audio_log_flags": 0x43d0ce, "audio_log_extended": 0x43d574,
         "compressed_log_output": 0x43ce9e,
         "audio_setting_parse_data_package_49b1f8": 0x49b1f8,
         "audio_setting_process_data_466976": 0x466976,
         "audio_setting_handle_command5_46bbb4": 0x46bbb4}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        shim = Path(temp) / "shim.c"
        shim.write_text("#include <stdint.h>\nuint8_t audio_settings_last_message_state[104];\n" +
            "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                      for s in CALLS))
        elf = Path(temp) / "candidate.elf"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-w",
                        "-nostdlib", "-Wl,-Ttext=0x100000",
                        "-Wl,-e,audio_uart_registry_callback_4668ae", str(SOURCE),
                        str(shim), "-o", str(elf)], check=True)
        with elf.open("rb") as handle:
            parsed = ELFFile(handle)
            segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                        if s["p_type"] == "PT_LOAD"]
            symbols = {s.name: s["st_value"] for s in
                       parsed.get_section_by_name(".symtab").iter_symbols()}

        def run(compiled, command, ptr, length, flags, parsed_result):
            uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            uc.mem_map(0x400000, 0x400000)
            uc.mem_write(0x438000, IMAGE)
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments: uc.mem_write(address, data)
            uc.mem_map(0x20000000, 0x100000)
            context = symbols["audio_settings_last_message_state"] if compiled else 0x20072608
            uc.mem_write(context, bytes(range(13)))
            if ptr: uc.mem_write(ptr, b"0123456789abcdef")
            for reg, value in ((A.UC_ARM_REG_R0,command),(A.UC_ARM_REG_R1,ptr),
                               (A.UC_ARM_REG_R2,length),(A.UC_ARM_REG_SP,0x200ff000),
                               (A.UC_ARM_REG_LR,0x600001)):
                uc.reg_write(reg,value)
            hooks = {((symbols[s] & ~1) if compiled else a): s for s,a in CALLS.items()}
            trace = []
            def cstr(address):
                data = bytes(uc.mem_read(address, 192))
                return data.split(b"\0",1)[0].decode("ascii")
            def observe(cpu,address,size,_):
                kind=hooks.get(address)
                if kind is None: return
                r=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                              A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
                result=0
                if kind == "audio_log_flags":
                    trace.append(("flags",))
                    result=flags
                elif kind == "audio_log_extended":
                    sp=cpu.reg_read(A.UC_ARM_REG_SP)
                    line=int.from_bytes(cpu.mem_read(sp,4),"little")
                    message=int.from_bytes(cpu.mem_read(sp+4,4),"little")
                    trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,cstr(message)))
                elif kind == "compressed_log_output":
                    trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2])))
                elif kind == "audio_setting_parse_data_package_49b1f8":
                    trace.append(("parse",r[0],r[1],r[2]==context))
                    result=parsed_result
                elif kind == "audio_setting_process_data_466976":
                    trace.append(("process",r[0]==context))
                elif kind == "audio_setting_handle_command5_46bbb4":
                    trace.append(("command5",r[0],r[1]))
                cpu.reg_write(A.UC_ARM_REG_R0,result)
                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
            uc.hook_add(UC_HOOK_CODE,observe)
            start=symbols["audio_uart_registry_callback_4668ae"] if compiled else 0x4668ae
            uc.emu_start(start | 1,0x600000,count=1000)
            return (uc.reg_read(A.UC_ARM_REG_R0),trace,bytes(uc.mem_read(context,13)))

        cases=0
        for command in (0,1,5,0xffffffff):
            for ptr in (0,0x20020000):
                for length in (0,1,16):
                    for flags in (0,1,2,4,7):
                        for parsed_result in (0,1,0x100):
                            native=run(False,command,ptr,length,flags,parsed_result)
                            candidate=run(True,command,ptr,length,flags,parsed_result)
                            if native != candidate:
                                raise AssertionError((command,ptr,length,flags,parsed_result,native,candidate))
                            cases+=1
        receipt={"status":"PASS_NATIVE_MAIN_SETTING_COMMON_DATA_4668AE",
                 "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
                 "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
                 "source_owned_symbols":["audio_uart_registry_callback_4668ae"],
                 "cases":cases,
                 "limits":["Parser, process, command-5 and logger calls are controlled hooks; global RAM initialization, final placement and hardware behavior remain open."]}
        path=OUT/"oracle-receipt.json"
        path.write_text(json.dumps(receipt,indent=2)+"\n")
        print(receipt["status"],cases,sha(path))

if __name__ == "__main__": main()
