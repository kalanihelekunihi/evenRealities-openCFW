#!/usr/bin/env python3
"""Direct stock/C replay of the UI dispatcher using controlled route entries."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_action_5b1724.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-action-5b1724"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_log_flags": (0x101010, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101020, 0x43d574, "extended"),
    "audio_log_simple": (0x101030, 0x43ce9e, "simple"),
    "audio_conversate_ui_event_name_5b16fc": (0x101040, 0x5b16fc, "event_name"),
    "audio_conversate_ui_state_name_5b16dc": (0x101050, 0x5b16dc, "state_name"),
    "audio_conversate_ui_transition_5b3d86": (0x101060, 0x5b3d86, "transition"),
}
HANDLER = 0x101080
TABLE = 0x686920


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    assert payload[0x5b1b20-0x438000:0x5b1b24-0x438000] == struct.pack("<I", TABLE)
    obj, elf_path = OUT / "oracle.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_conversate_ui_action_5b1724",
                    f"--defsym=audio_conversate_ui_action_matrix_686920=0x{TABLE:x}",
                    "--defsym=audio_conversate_ui_state_20071368=0x20071368",
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, state, event, value, route_present, next_state, handler_result, flags):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data: cpu.mem_write(start, data)
        cpu.mem_write(0x101e00, b"TEST_EVENT_NAME\0")
        cpu.mem_write(0x101e40, b"TEST_STATE_NAME\0")
        cpu.mem_write(TABLE, b"\0"*(7*0xa8))
        if route_present and state < 7 and (event & 0xff) < 21:
            entry = TABLE + state*0xa8 + (event & 0xff)*8
            cpu.mem_write(entry, struct.pack("<II", next_state, HANDLER|1))
        cpu.mem_write(0x20071368, bytes((state,)))
        cpu.reg_write(A.UC_ARM_REG_R0, event)
        cpu.reg_write(A.UC_ARM_REG_R1, value)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]
        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def string(ptr):
            return bytes(cpu.mem_read(ptr, 256)).split(b"\0", 1)[0].decode("latin1") if ptr else ""

        def normalize_args(fmt, raw):
            if "no match action" in fmt or " -> " in fmt:
                return (raw[0], string(raw[1]), raw[2], string(raw[3]))
            if "UI event [" in fmt:
                return (raw[0], string(raw[1]))
            if "invalid:" in fmt:
                return (raw[0],)
            return ()

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            if pc == HANDLER:
                events.append(("handler", machine.reg_read(A.UC_ARM_REG_R0),
                               machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, handler_result)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
                return
            kind = names.get(pc)
            if kind is None: return
            r0, r1, r2, r3 = [machine.reg_read(x) for x in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind in ("event_name", "state_name"):
                events.append((kind, r0))
                machine.reg_write(A.UC_ARM_REG_R0, 0x101e00 if kind == "event_name" else 0x101e40)
            elif kind == "extended":
                line, ptr = struct.unpack("<II", bytes(machine.mem_read(sp, 8)))
                fmt = string(ptr)
                argc = 4 if line in (601, 611) else 2 if line == 590 else 1 if line in (586, 593) else 0
                raw = struct.unpack("<"+"I"*argc, bytes(machine.mem_read(sp+8, argc*4))) if argc else ()
                events.append((kind, r0, string(r1), string(r2), string(r3),
                               line, fmt, normalize_args(fmt, raw)))
            elif kind == "simple":
                fmt = string(r1)
                argc = 4 if "no match action" in fmt or " -> " in fmt else 2 if "UI event [" in fmt else 1 if "invalid:" in fmt else 0
                raw = (r3,) + struct.unpack("<"+"I"*(argc-1),
                       bytes(machine.mem_read(sp, (argc-1)*4))) if argc else ()
                events.append((kind, r0, fmt, string(r2), normalize_args(fmt, raw)))
            else:
                events.append((kind, r0, r1))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b1724 if native else symbols["audio_conversate_ui_action_5b1724"])|1,
                      0, count=1000)
        if not done[0]: raise RuntimeError("UI action did not return")
        return events, bytes(cpu.mem_read(0x20071368, 1))

    cases = [(state, event, 0x12345678, route, next_state, result, flags)
             for state in (0, 2, 6, 7)
             for event in (0, 1, 20, 21, 255, 0x101)
             for route in (False, True)
             for next_state in (0, 2, 6)
             for result in (0, 1)
             for flags in (0, 1, 2, 4, 7)]
    for case in cases:
        stock, selected = run(True, *case), run(False, *case)
        if stock != selected:
            raise RuntimeError(f"UI action mismatch {case}: {stock} != {selected}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_ACTION_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "native_body": "0x5b1724..0x5b198b",
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Route matrix is synthetic in replay; stock ROM matrix is separately pinned.",
                         "Handler and transition callbacks are controlled lower contracts."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
