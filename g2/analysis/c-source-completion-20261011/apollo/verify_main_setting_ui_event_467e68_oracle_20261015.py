#!/usr/bin/env python3
"""Compare Setting UI event effects with the official Apollo Main callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/setting_ui_event_handler_467e68.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
BODY_SHA = hashlib.sha256(IMAGE[0x467e68-0x438000:0x467f02-0x438000]).hexdigest()
OUT = G2 / "build/c-firmware/20261015/main-setting-ui-event-467e68"
OUT.mkdir(parents=True, exist_ok=True)
CALLS = {"audio_log_flags": 0x43d0ce, "audio_log_extended": 0x43d574,
         "compressed_log_output": 0x43ce9e,
         "audio_uart_hub_calibration_display_update_4a7472": 0x4a7472,
         "audio_uart_hub_calibration_success_display_4a76e4": 0x4a76e4,
         "audio_settings_get_config_46b44c": 0x46b44c,
         "audio_settings_notify_device_status": 0x49be04,
         "audio_settings_notify_recalibration_status_49beac": 0x49beac}

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text("#include <stdint.h>\n"
                    "uint32_t audio_uart_calibration_snapshot_200749a8;\n"
                    "uint8_t audio_uart_calibration_status_2007501c;\n"
                    "uint8_t audio_uart_registry_context_20003a40[8];\n" +
                    "\n".join(f'__attribute__((naked)) uint32_t {s}(void){{__asm volatile("bx lr");}}'
                              for s in CALLS))
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-w",
                    "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_registry_callback_467e68", str(SOURCE),
                    str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def u32(v): return (v & 0xffffffff).to_bytes(4, "little")

    def run(compiled, event, flags, parameter, display):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x200000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        context = symbols["audio_uart_registry_context_20003a40"] if compiled else 0x20003a40
        snapshot = symbols["audio_uart_calibration_snapshot_200749a8"] if compiled else 0x200749a8
        status = symbols["audio_uart_calibration_status_2007501c"] if compiled else 0x2007501c
        config = 0x20030000
        uc.mem_write(context, u32(0x13579bdf)+u32(0xaaaaaaaa))
        uc.mem_write(snapshot, u32(0x2468ace0))
        uc.mem_write(status, b"\x55")
        uc.mem_write(config+0x40, u32(0x77777777))
        for reg, value in ((A.UC_ARM_REG_R0,event),(A.UC_ARM_REG_R1,0x1234),
                           (A.UC_ARM_REG_R2,parameter),(A.UC_ARM_REG_R3,display),
                           (A.UC_ARM_REG_SP,0x200ff000),(A.UC_ARM_REG_LR,0x600001)):
            uc.reg_write(reg,value)
        hooks = {((symbols[s] & ~1) if compiled else a): s for s,a in CALLS.items()}
        trace = []

        def cstr(ptr):
            data = bytes(uc.mem_read(ptr, 256))
            return data[:data.index(0)].decode("ascii")

        def observe(cpu, address, size, _):
            kind = hooks.get(address)
            if kind is None: return
            r = [cpu.reg_read(x) for x in (A.UC_ARM_REG_R0,A.UC_ARM_REG_R1,
                                           A.UC_ARM_REG_R2,A.UC_ARM_REG_R3)]
            result = 0
            if kind == "audio_log_flags":
                trace.append(("flags",))
                result = flags
            elif kind == "audio_log_extended":
                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                line = int.from_bytes(cpu.mem_read(sp,4),"little")
                msg = int.from_bytes(cpu.mem_read(sp+4,4),"little")
                trace.append(("extended",r[0],cstr(r[1]),cstr(r[2]),cstr(r[3]),line,cstr(msg)))
            elif kind == "compressed_log_output":
                trace.append(("compressed",r[0],cstr(r[1]),cstr(r[2])))
            elif kind == "audio_uart_hub_calibration_display_update_4a7472":
                trace.append(("display",r[0]))
            elif kind == "audio_uart_hub_calibration_success_display_4a76e4":
                trace.append(("success",))
            elif kind == "audio_settings_get_config_46b44c":
                trace.append(("config",))
                result = config
            elif kind == "audio_settings_notify_device_status":
                trace.append(("notify",))
            elif kind == "audio_settings_notify_recalibration_status_49beac":
                trace.append(("recalibration",r[0]))
            cpu.reg_write(A.UC_ARM_REG_R0,result)
            cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE,observe)
        start = symbols["audio_uart_registry_callback_467e68"] if compiled else 0x467e68
        uc.emu_start(start | 1,0x600000,count=1000)
        return (uc.reg_read(A.UC_ARM_REG_R0),uc.reg_read(A.UC_ARM_REG_R1),trace,
                bytes(uc.mem_read(context,8)),bytes(uc.mem_read(config+0x40,4)),
                bytes(uc.mem_read(status,1)))

    cases=0
    for event in (0,1,2,3,4,5,6,0xffffffff):
        for flags in (0,1,2,4,7):
            for parameter,display in ((0,0),(0x89abcdef,0x12345678)):
                native=run(False,event,flags,parameter,display)
                candidate=run(True,event,flags,parameter,display)
                if native!=candidate:
                    raise AssertionError((event,flags,parameter,display,native,candidate))
                cases+=1

    receipt={"status":"PASS_NATIVE_MAIN_SETTING_UI_EVENT_467E68",
             "source":str(SOURCE.relative_to(ROOT)),
             "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             "official_payload_sha256":IMAGE_SHA,"native_body_sha256":BODY_SHA,
             "source_owned_symbols":["audio_uart_registry_callback_467e68"],"cases":cases,
             "limits":["Calibration display and notification providers were controlled hooks; RAM initialization, placement and hardware behavior remain unverified."]}
    path=OUT/"oracle-receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],cases,hashlib.sha256(path.read_bytes()).hexdigest())
