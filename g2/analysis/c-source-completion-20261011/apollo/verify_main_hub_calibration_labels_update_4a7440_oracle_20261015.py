#!/usr/bin/env python3
"""Compare calibration label setter ordering with official Main."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_labels_update_4a7440.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4a7440-0x438000:0x4a7472-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-labels-update-4a7440"
OUT.mkdir(parents=True,exist_ok=True)
CALLS={"audio_uart_page_44122a":0x44122a,"audio_uart_page_441238":0x441238,
       "audio_uart_page_44120e":0x44120e,"audio_uart_page_44121c":0x44121c}

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text("#include <stdint.h>\n"+
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_hub_calibration_labels_update_4a7440",
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
        hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
        trace=[]

        def observe(cpu,address,size,_):
            kind=hooks.get(address)
            if kind is None:return
            r=tuple(cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,A.UC_ARM_REG_R2))
            trace.append((kind,*r))
            cpu.reg_write(A.UC_ARM_REG_R0,0)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols["audio_uart_hub_calibration_labels_update_4a7440"] if compiled else 0x4a7440
        uc.emu_start(start|1,0x600000,count=500)
        return trace

    cases=0
    for args in ((0,0,0),(0x20010000,0,0),(0x20020000,1,2),
                 (0xffffffff,0x12345678,0x87654321)):
        native=run(False,args)
        candidate=run(True,args)
        if native!=candidate:raise AssertionError((args,native,candidate))
        cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_HUB_CALIBRATION_LABELS_UPDATE_4A7440",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_hub_calibration_labels_update_4a7440"],
             "cases":cases,
             "limits":["Style setter calls were controlled; final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
