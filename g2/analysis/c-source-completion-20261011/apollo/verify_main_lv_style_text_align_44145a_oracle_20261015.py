#!/usr/bin/env python3
"""Compare native 0x5e LV style wrapper argument forwarding."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_style_text_align_44145a.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x44145a-0x438000:0x44146a-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261015/main-lv-style-text-align-44145a"
OUT.mkdir(parents=True,exist_ok=True)

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text('#include <stdint.h>\n__attribute__((naked)) void audio_uart_page_style_apply_44be4c(void){__asm volatile("bx lr");}\n')
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_page_44145a",
                    str(SOURCE),str(shim),"-o",str(elf)],check=True)
    with elf.open("rb") as handle:
        parsed=ELFFile(handle)
        segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                  if s["p_type"]=="PT_LOAD"]
        symbols={s.name:s["st_value"] for s in
                 parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled,args):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,IMAGE)
        uc.mem_map(0x100000,0x200000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x100000)
        for reg,value in zip((A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2),args):
            uc.reg_write(reg,value)
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        target=(symbols["audio_uart_page_style_apply_44be4c"]&~1) if compiled else 0x44be4c
        trace=[]

        def observe(cpu,address,size,_):
            if address!=target:return
            trace.append(tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                                        A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)))
            cpu.reg_write(A.UC_ARM_REG_R0,0)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols["audio_uart_page_44145a"] if compiled else 0x44145a
        uc.emu_start(start|1,0x600000,count=100)
        return trace

    cases=0
    for object_ in (0,0x20010000):
        for align in (0,1,2,255,256,0xffffffff):
            for selector in (0,0x3fffffff):
                args=(object_,align,selector)
                native=run(False,args)
                candidate=run(True,args)
                if native!=candidate:raise AssertionError((args,native,candidate))
                cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_LV_STYLE_TEXT_ALIGN_44145A",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_page_44145a"],"cases":cases,
             "limits":["Style application was controlled; final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
