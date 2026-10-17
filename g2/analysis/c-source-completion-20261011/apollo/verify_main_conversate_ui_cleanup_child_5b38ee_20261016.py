#!/usr/bin/env python3
"""Direct stock/C replay of the Conversate loading-timeout caller."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_cleanup_child_5b38ee.c"
HELPER = G2 / "components/audio/uart_thread_source_candidate/conversate_timer_expired_5b3628.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-cleanup-child-5b38ee"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
    "audio_quicklist_tick_now": (0x101040, 0x44a1c6, "seconds"),
    "audio_conversate_report_5b02e4": (0x101050, 0x5b02e4, "report"),
    "audio_conversate_enter_loading_5b57ac": (0x101060, 0x5b57ac, "enter"),
    "audio_conversate_timer_1_start_5b3766": (0x101070, 0x5b3766, "restart"),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b3e48-0x438000:0x5b3e4c-0x438000] == (0x20073a3c).to_bytes(4, "little")
    objects = []
    for source in (SOURCE, HELPER):
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                        str(source), "-o", str(obj)], check=True)
        objects.append(obj)
    elf_path = OUT / "oracle.elf"
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_cleanup_child_5b38ee",
                    "--defsym=audio_conversate_timer_mgr_ram_20073a3c=0x20073a3c",
                    "--defsym=audio_conversate_ui_state_20071368=0x20071368",
                    "--defsym=audio_conversate_machine_context_200e3aec=0x200e3aec",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    *(str(p) for p in objects), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, active, deadline, tick, ui_state, machine_state, flags, seconds):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x20073a3c, bytes((active, 0xa5, 0x5a, 0xff)) + struct.pack("<I", deadline))
        cpu.mem_write(0x20071368, bytes((ui_state,)))
        cpu.mem_write(0x200e3aec, bytes((machine_state,)))
        cpu.reg_write(A.UC_ARM_REG_R0, tick)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def string(ptr):
            if not ptr: return ""
            data = bytes(cpu.mem_read(ptr, 256))
            return data.split(b"\0", 1)[0].decode("latin1")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r0 = machine.reg_read(A.UC_ARM_REG_R0)
            r1 = machine.reg_read(A.UC_ARM_REG_R1)
            r2 = machine.reg_read(A.UC_ARM_REG_R2)
            r3 = machine.reg_read(A.UC_ARM_REG_R3)
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                line, message = struct.unpack("<II", bytes(machine.mem_read(sp, 8)))
                events.append((kind, r0, string(r1), string(r2), string(r3), line, string(message)))
            elif kind == "simple":
                events.append((kind, r0, string(r1), string(r2)))
            elif kind == "seconds":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, seconds)
            elif kind == "report":
                events.append((kind, r0, r1))
                machine.reg_write(A.UC_ARM_REG_R0, 0)
            else:
                events.append((kind,))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b38ee if native else symbols["audio_conversate_ui_cleanup_child_5b38ee"])|1,
                      0, count=500)
        if not done[0]: raise RuntimeError("cleanup child did not return")
        return {"events": events, "timer": bytes(cpu.mem_read(0x20073a3c, 8)).hex(),
                "ui": bytes(cpu.mem_read(0x20071368, 1)).hex(),
                "machine": bytes(cpu.mem_read(0x200e3aec, 1)).hex()}

    cases = [(active, deadline, (deadline+delta)&0xffffffff, ui, machine, flags, seconds)
             for active in (0, 1)
             for deadline in (0, 0xfffffffe)
             for delta in (-1, 0, 1)
             for ui in (0, 1, 2)
             for machine in (0, 1, 2)
             for flags in (0, 1, 2, 4, 7)
             for seconds in (0, 127)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"cleanup child mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_DIRECT_MAIN_CONVERSATE_UI_CLEANUP_CHILD_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b38ee..0x5b39b3",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "helper": str(HELPER.relative_to(ROOT)),
              "helper_sha256": hashlib.sha256(HELPER.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
