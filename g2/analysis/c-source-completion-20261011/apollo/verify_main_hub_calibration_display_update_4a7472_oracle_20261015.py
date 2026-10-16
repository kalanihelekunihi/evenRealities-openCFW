#!/usr/bin/env python3
"""Compare calibration display construction and RAM slots with official Main."""
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
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_display_update_4a7472.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x4a7472-0x438000:0x4a76e4-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-display-update-4a7472"
OUT.mkdir(parents=True,exist_ok=True)
CALLS={
    "audio_uart_page_43de82":(0x43de82,1),
    "audio_uart_page_499416":(0x499416,1),
    "audio_uart_page_43f4c0":(0x43f4c0,3),
    "audio_uart_page_43f09a":(0x43f09a,3),
    "audio_uart_page_43dfa4":(0x43dfa4,2),
    "audio_uart_page_44104c":(0x44104c,1),
    "audio_uart_page_44127e":(0x44127e,3),
    "audio_uart_page_44129e":(0x44129e,3),
    "audio_uart_page_44131c":(0x44131c,3),
    "audio_uart_page_44146a":(0x44146a,3),
    "audio_uart_hub_calibration_labels_update_4a7440":(0x4a7440,3),
    "audio_uart_page_44145a":(0x44145a,3),
    "audio_uart_page_44140e":(0x44140e,3),
    "audio_uart_page_44143e":(0x44143e,3),
    "audio_uart_page_460084":(0x460084,1),
    "audio_uart_page_45fffe":(0x45fffe,2),
    "audio_uart_page_49942e":(0x49942e,2),
    "audio_uart_page_43f568":(0x43f568,2),
    "audio_uart_page_43f506":(0x43f506,2),
    "audio_uart_page_43f66c":(0x43f66c,1),
    "audio_uart_lv_obj_width_43fd9e":(0x43fd9e,1),
    "audio_uart_page_43f0e0":(0x43f0e0,2),
    "audio_uart_page_43f142":(0x43f142,2),
}
SLOTS={"audio_uart_calibration_snapshot_200749a8":0x200749a8,
       "audio_uart_calibration_success_primary_200749ac":0x200749ac,
       "audio_uart_calibration_success_secondary_200749b0":0x200749b0,
       "audio_uart_ring_secondary_head_cell":0x200746e0,
       "audio_uart_calibration_panel_left_200749b4":0x200749b4,
       "audio_uart_calibration_panel_right_200749b8":0x200749b8,
       "audio_uart_calibration_panel_mark_200749bc":0x200749bc}

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text("#include <stdint.h>\n"+
                    "\n".join(f"uint32_t {s};" for s in SLOTS)+"\n"+
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_hub_calibration_display_update_4a7472",
                    str(SOURCE),str(shim),"-o",str(elf)],check=True)
    with elf.open("rb") as handle:
        parsed=ELFFile(handle)
        segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                  if s["p_type"]=="PT_LOAD"]
        symbols={s.name:s["st_value"] for s in
                 parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v):return (v&0xffffffff).to_bytes(4,"little")

    def run(compiled,parent,width):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,IMAGE)
        uc.mem_map(0x100000,0x200000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x100000)
        for name,address in SLOTS.items():
            place=symbols[name] if compiled else address
            uc.mem_write(place,u32(0x20030000 if "secondary_head" in name else 0xaaaaaaaa))
        uc.reg_write(A.UC_ARM_REG_R0,parent)
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        hooks={((symbols[s]&~1) if compiled else a): (s,arity)
               for s,(a,arity) in CALLS.items()}
        trace=[]
        counts={"audio_uart_page_43de82":0,"audio_uart_page_499416":0}

        def cstr(ptr):
            data=bytes(uc.mem_read(ptr,64))
            return data[:data.index(0)].decode("ascii")

        def observe(cpu,address,size,_):
            target=hooks.get(address)
            if target is None:return
            kind,arity=target
            regs=[cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                            A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
            args=regs[:arity]
            if kind in ("audio_uart_page_460084","audio_uart_page_45fffe"):
                args[0]=cstr(args[0])
            trace.append((kind,*args))
            result=0
            if kind=="audio_uart_page_43de82":
                result=0x20040000+0x100*counts[kind]
                counts[kind]+=1
            elif kind=="audio_uart_page_499416":
                result=0x20050000+0x100*counts[kind]
                counts[kind]+=1
            elif kind=="audio_uart_page_44104c":result=(regs[0]^0x55aa55aa)&0xffffffff
            elif kind=="audio_uart_page_460084":result=11 if args[0].endswith("_1") else 22
            elif kind=="audio_uart_page_45fffe":result=0x20060000+regs[1]
            elif kind=="audio_uart_lv_obj_width_43fd9e":result=width
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start=symbols["audio_uart_hub_calibration_display_update_4a7472"] if compiled else 0x4a7472
        uc.emu_start(start|1,0x600000,count=5000)
        values=tuple(int.from_bytes(uc.mem_read(symbols[name] if compiled else address,4),"little")
                     for name,address in SLOTS.items())
        return trace,values

    cases=0
    for parent in (0,0x20020000):
        for width in (0,1,0x240,0x241,0xffffffff):
            native=run(False,parent,width)
            candidate=run(True,parent,width)
            if native!=candidate:raise AssertionError((parent,width,native,candidate))
            cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_HUB_CALIBRATION_DISPLAY_UPDATE_4A7472",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_hub_calibration_display_update_4a7472"],
             "cases":cases,
             "limits":["UI providers and seven RAM slots were controlled; final placement, initialization and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
