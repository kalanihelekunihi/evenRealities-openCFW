#!/usr/bin/env python3
"""Compare native LV label text ownership branches with C source."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc,UcError,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE,UC_HOOK_MEM_WRITE_UNMAPPED
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_label_set_text_49942e.c"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest()==IMAGE_SHA
BODY_SHA=hashlib.sha256(IMAGE[0x49942e-0x438000:0x49954c-0x438000]).hexdigest()
OUT=G2/"build/c-firmware/20261015/main-lv-label-set-text-49942e"
OUT.mkdir(parents=True,exist_ok=True)
CALLS={"audio_uart_lvgl_log":0x44d25c,
       "audio_uart_page_event_prepare_49aacc":0x49aacc,
       "audio_uart_page_text_length_49abd4":0x49abd4,
       "audio_uart_lv_realloc_44f76a":0x44f76a,
       "audio_uart_lv_heap_free":0x44f758,
       "audio_uart_lv_malloc":0x44f718,
       "audio_uart_page_text_content_init_49abe0":0x49abe0,
       "audio_uart_page_layout_update_49a602":0x49a602}

with tempfile.TemporaryDirectory() as temp:
    shim=Path(temp)/"shim.c"
    shim.write_text("#include <stdint.h>\n"+
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf=Path(temp)/"candidate.elf"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-w",
                    "-nostdlib","-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_page_49942e",str(SOURCE),str(shim),"-o",str(elf)],check=True)
    with elf.open("rb") as handle:
        parsed=ELFFile(handle)
        segments=[(s["p_vaddr"],s.data()) for s in parsed.iter_segments()
                  if s["p_type"]=="PT_LOAD"]
        symbols={s.name:s["st_value"] for s in
                 parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v):return (v&0xffffffff).to_bytes(4,"little")

    def run(compiled,old_kind,requested_kind,is_static,replacement_kind,
            failure=None):
        uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        uc.mem_map(0x400000,0x400000)
        uc.mem_write(0x438000,IMAGE)
        uc.mem_map(0x100000,0x200000)
        for address,data in segments:uc.mem_write(address,data)
        uc.mem_map(0x20000000,0x100000)
        page,old_addr,new_addr=0x20020000,0x20031000,0x20032000
        uc.mem_write(old_addr,b"old text\0")
        uc.mem_write(new_addr,b"new text\0")
        old=old_addr if old_kind else 0
        requested={"null":0,"same":old,"new":new_addr}[requested_kind]
        uc.mem_write(page+0x2c,u32(old))
        uc.mem_write(page+0x5c,bytes([0x10 if is_static else 0]))
        uc.reg_write(A.UC_ARM_REG_R0,0 if failure=="null" else page)
        uc.reg_write(A.UC_ARM_REG_R1,requested)
        uc.reg_write(A.UC_ARM_REG_SP,0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR,0x600001)
        hooks={((symbols[s]&~1) if compiled else a):s for s,a in CALLS.items()}
        trace=[]

        def cstr(ptr):
            data=bytes(uc.mem_read(ptr,256))
            return data[:data.index(0)].decode("ascii")

        def observe(cpu,address,size,_):
            kind=hooks.get(address)
            if kind is None:return
            r0,r1=(cpu.reg_read(A.UC_ARM_REG_R0),cpu.reg_read(A.UC_ARM_REG_R1))
            result=0
            if kind=="audio_uart_page_event_prepare_49aacc":trace.append(("prepare",r0))
            elif kind=="audio_uart_page_text_length_49abd4":
                trace.append(("length",r0))
                if r0:
                    data=bytes(cpu.mem_read(r0,32))
                    result=data.index(0)+1
                else:result=1
            elif kind=="audio_uart_lv_realloc_44f76a":
                trace.append(("realloc",r0,r1))
                result=0 if failure=="realloc" else \
                    (old_addr if replacement_kind=="same" else 0x20033000)
            elif kind=="audio_uart_lv_heap_free":trace.append(("free",r0))
            elif kind=="audio_uart_lv_malloc":
                trace.append(("malloc",r0))
                result=0 if failure=="malloc" else 0x20034000
            elif kind=="audio_uart_page_text_content_init_49abe0":
                trace.append(("init",r0,r1))
            elif kind=="audio_uart_page_layout_update_49a602":trace.append(("layout",r0))
            elif kind=="audio_uart_lvgl_log":
                sp=cpu.reg_read(A.UC_ARM_REG_SP)
                fmt=int.from_bytes(cpu.mem_read(sp,4),"little")
                expression=int.from_bytes(cpu.mem_read(sp+4,4),"little")
                reason=int.from_bytes(cpu.mem_read(sp+8,4),"little")
                trace.append(("fatal_log",r0,cstr(r1),cpu.reg_read(A.UC_ARM_REG_R2),
                              cstr(cpu.reg_read(A.UC_ARM_REG_R3)),cstr(fmt),
                              cstr(expression),cstr(reason)))
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        def fault(cpu,access,address,size,value,_):
            trace.append(("fatal_write",address,size,value))
            return False
        uc.hook_add(UC_HOOK_MEM_WRITE_UNMAPPED,fault)
        start=symbols["audio_uart_page_49942e"] if compiled else 0x49942e
        try:
            uc.emu_start(start|1,0x600000,count=1500)
        except UcError:
            if not failure or not trace or trace[-1][0]!="fatal_write":raise
        if failure:
            return trace
        return (uc.reg_read(A.UC_ARM_REG_R0),trace,
                bytes(uc.mem_read(page+0x2c,4)),bytes(uc.mem_read(page+0x5c,1)))

    cases=0
    for old_kind in (0,1):
        for requested_kind in ("null","same","new"):
            for is_static in (0,1):
                for replacement_kind in ("same","new"):
                    native=run(False,old_kind,requested_kind,is_static,replacement_kind)
                    candidate=run(True,old_kind,requested_kind,is_static,replacement_kind)
                    if native!=candidate:
                        raise AssertionError((old_kind,requested_kind,is_static,replacement_kind,
                                              native,candidate))
                    cases+=1
    for failure,old_kind,requested_kind in (("null",1,"new"),
                                            ("realloc",1,"same"),
                                            ("malloc",1,"new")):
        native=run(False,old_kind,requested_kind,0,"new",failure)
        candidate=run(True,old_kind,requested_kind,0,"new",failure)
        if native!=candidate:
            raise AssertionError((failure,native,candidate))
        cases+=1
    receipt={"status":"PASS_NATIVE_MAIN_LV_LABEL_SET_TEXT_49942E",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_page_49942e"],"cases":cases,
             "limits":["Allocation, text and layout providers were controlled; fatal paths were compared through the observed 0xffffffff write, while final placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
