#!/usr/bin/env python3
"""Compare calibration success display call flow with official Main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_success_display_4a76e4.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4a76e4-0x438000:0x4a774e-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-success-display-4a76e4"
OUT.mkdir(parents=True,exist_ok=True)
CALLS={"audio_uart_page_460084":0x460084,"audio_uart_page_45fffe":0x45fffe,
       "audio_uart_page_49942e":0x49942e,"audio_uart_page_43f506":0x43f506,
       "audio_uart_page_43f66c":0x43f66c,"audio_uart_lv_obj_width_43fd9e":0x43fd9e,
       "audio_uart_page_43f0e0":0x43f0e0}

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text("#include <stdint.h>\n"
                    "uint32_t audio_uart_calibration_success_primary_200749ac;\n"
                    "uint32_t audio_uart_calibration_success_secondary_200749b0;\n"+
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_hub_calibration_success_display_4a76e4",
                    str(SOURCE),str(shim),"-o",str(elf)],check=True)
    with elf.open("rb") as handle:
        parsed=ELFFile(handle)
        segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                  if s["p_type"]=="PT_LOAD"]
        symbols={s.name:s["st_value"] for s in
                 parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v):return (v&0xffffffff).to_bytes(4,"little")

    def run(compiled,primary,secondary,width):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,IMAGE)
        uc.mem_map(0x100000,0x200000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x100000)
        first=symbols["audio_uart_calibration_success_primary_200749ac"] if compiled else 0x200749ac
        second=symbols["audio_uart_calibration_success_secondary_200749b0"] if compiled else 0x200749b0
        uc.mem_write(first,u32(primary))
        uc.mem_write(second,u32(secondary))
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
        trace=[]

        def cstr(ptr):
            data=bytes(uc.mem_read(ptr,64))
            return data[:data.index(0)].decode("ascii")

        def observe(cpu,address,size,_):
            kind=hooks.get(address)
            if kind is None:return
            r0,r1=(cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1))
            result=0
            if kind=="audio_uart_page_460084":
                key=cstr(r0)
                trace.append(("measure",key))
                result=11 if key.endswith("_1") else 22
            elif kind=="audio_uart_page_45fffe":
                key=cstr(r0)
                trace.append(("lookup",key,r1))
                result=0x11110000+r1
            elif kind=="audio_uart_page_49942e":trace.append(("set_text",r0,r1))
            elif kind=="audio_uart_page_43f506":trace.append(("style",r0,r1))
            elif kind=="audio_uart_page_43f66c":trace.append(("layout",r0))
            elif kind=="audio_uart_lv_obj_width_43fd9e":
                trace.append(("width",r0))
                result=width
            elif kind=="audio_uart_page_43f0e0":trace.append(("set_x",r0,r1))
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols["audio_uart_hub_calibration_success_display_4a76e4"] if compiled else 0x4a76e4
        uc.emu_start(start|1,0x600000,count=1000)
        return trace

    cases=0
    for primary in (0,0x20010000):
        for secondary in (0,0x20020000):
            for width in (0,1,0x240,0x241,0xffffffff):
                native=run(False,primary,secondary,width)
                candidate=run(True,primary,secondary,width)
                if native!=candidate:
                    raise AssertionError((primary,secondary,width,native,candidate))
                cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_HUB_CALIBRATION_SUCCESS_DISPLAY_4A76E4",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_hub_calibration_success_display_4a76e4"],
             "cases":cases,
             "limits":["Display providers and RAM object slots were controlled; final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
