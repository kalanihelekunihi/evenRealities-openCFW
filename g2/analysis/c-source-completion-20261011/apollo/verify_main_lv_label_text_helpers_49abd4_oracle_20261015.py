#!/usr/bin/env python3
"""Compare native LV label length and content copy helpers with C."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_label_text_helpers_49abd4.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODIES={"audio_uart_page_text_length_49abd4":(0x49abd4,0x49abe0),
        "audio_uart_page_text_content_init_49abe0":(0x49abe0,0x49abea)}
OUT=G2/"build/c-firmware/20261015/main-lv-label-text-helpers-49abd4"
OUT.mkdir(parents=True,exist_ok=True)

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text('#include <stdint.h>\n'
                    '__attribute__((naked)) uint32_t audio_uart_lv_string_length_454768(void){__asm volatile("bx lr");}\n'
                    '__attribute__((naked)) uint32_t strcpy(void){__asm volatile("bx lr");}\n')
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_page_text_length_49abd4",
                    str(SOURCE),str(shim),"-o",str(elf)],check=True)
    with elf.open("rb") as handle:
        parsed=ELFFile(handle)
        segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                  if s["p_type"]=="PT_LOAD"]
        symbols={s.name:s["st_value"] for s in
                 parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v):return (v&0xffffffff).to_bytes(4,"little")

    def run(compiled,name,content):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,IMAGE)
        uc.mem_map(0x100000,0x200000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x100000)
        page,source,destination=0x20020000,0x20030000,0x20040000
        uc.mem_write(source,content+b"\0")
        uc.mem_write(destination,b"\xa5"*96)
        uc.mem_write(page+0x2c,u32(destination))
        uc.reg_write(A.UC_ARM_REG_R0,source if name.endswith("length_49abd4") else page)
        uc.reg_write(A.UC_ARM_REG_R1,source)
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        length_target=(symbols["audio_uart_lv_string_length_454768"]&~1) if compiled else 0x454768
        copy_target=(symbols["strcpy"]&~1) if compiled else 0x4547b6
        trace=[]

        def observe(cpu,address,size,_):
            if address==length_target:
                r0=cpu.reg_read(A.UC_ARM_REG_R0)
                trace.append(("length",r0))
                cpu.reg_write(A.UC_ARM_REG_R0,len(content))
            elif address==copy_target:
                r0,r1=cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1)
                trace.append(("copy",r0,r1))
                cpu.mem_write(r0,content+b"\0")
                cpu.reg_write(A.UC_ARM_REG_R0,r0)
            else:return
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols[name] if compiled else BODIES[name][0]
        uc.emu_start(start|1,0x600000,count=100)
        if name.endswith("length_49abd4"):
            return uc.reg_read(A.UC_ARM_REG_R0),trace
        return trace,bytes(uc.mem_read(destination,96))

    cases=0
    for content in (b"",b"a",b"hello",b"x"*31,b"y"*80):
        for name in BODIES:
            native=run(False,name,content)
            candidate=run(True,name,content)
            if native!=candidate:raise AssertionError((name,content,native,candidate))
            cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_LV_LABEL_TEXT_HELPERS_49ABD4",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,
             "native_body_sha256":{name:hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest()
                                   for name,(start,end) in BODIES.items()},
             "source_owned_symbols":sorted(BODIES),"cases":cases,
             "limits":["String length and copy providers were controlled; final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
