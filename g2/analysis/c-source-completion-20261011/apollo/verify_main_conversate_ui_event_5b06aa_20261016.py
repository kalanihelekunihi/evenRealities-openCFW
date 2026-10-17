#!/usr/bin/env python3
"""Bounded stock/C branch replay for the Conversate UI callback."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/conversate_ui_event_callback_5b06aa.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-conversate-ui-event-5b06aa"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_uart_buffer_zero": (0x101010, 0x43c0e4, "zero"),
    "audio_conversate_enter_5b01ca": (0x101020, 0x5b01ca, "enter"),
    "audio_conversate_leave_5b0284": (0x101030, 0x5b0284, "leave"),
    "audio_log_flags": (0x101040, 0x43d0ce, "flags"),
    "audio_log_extended": (0x101050, 0x43d574, "extended"),
    "audio_log_simple": (0x101060, 0x43ce9e, "simple"),
    "g2_flashdb_candidate_tick": (0x101070, 0x4490cc, "tick"),
    "audio_tracepoint_reset_pull_478110": (0x101080, 0x478110, "pull"),
    "audio_conversate_success_5b03c2": (0x101090, 0x5b03c2, "success"),
    "audio_conversate_ui_start_5b14ce": (0x1010a0, 0x5b14ce, "start"),
    "audio_conversate_ui_action_5b1724": (0x1010b0, 0x5b1724, "action"),
    "audio_queue_copy_bytes": (0x1010c0, 0x439be4, "copy"),
    "audio_conversate_ui_stop_5b03d8": (0x1010d0, 0x5b03d8, "stop"),
    "audio_conversate_ui_cancel_5b23ae": (0x1010e0, 0x5b23ae, "cancel"),
    "audio_conversate_ui_cleanup_5b3d62": (0x1010f0, 0x5b3d62, "cleanup"),
    "audio_conversate_reply_list_clear_5b43d4": (0x101100, 0x5b43d4, "list_clear"),
    "audio_conversate_prep_note_reset_5b473a": (0x101110, 0x5b473a, "note_reset"),
    "audio_conversate_transcribe_reset_5b430e": (0x101120, 0x5b430e, "transcribe_reset"),
    "audio_conversate_ui_exit_child_59624e": (0x101130, 0x59624e, "exit_child"),
    "audio_conversate_ui_exit_finalize_5b156c": (0x101140, 0x5b156c, "exit_finalize"),
    "audio_terminal_reset_mode_notice_54f50e": (0x101150, 0x54f50e, "release"),
    "audio_ble_param_reset_delayed_event": (0x101160, 0x478252, "ble_reset"),
    "audio_conversate_ui_close_notify_5b1d2a": (0x101170, 0x5b1d2a, "notify"),
    "audio_uart_ring_u64_div_47cc60": (0x101180, 0x47cc60, "divide"),
    "audio_uart_device_role_get": (0x101190, 0x45a568, "role"),
    "audio_uart_ring_wear_persist_48eb32": (0x1011a0, 0x48eb32, "persist"),
}
RAM = {
    "audio_conversate_machine_context_200e3aec": 0x200e3aec,
    "audio_uart_registry_context_200004d8": 0x200004d8,
    "audio_conversate_ui_start_tick_20074390": 0x20074390,
    "audio_conversate_ui_app_id_200743a0": 0x200743a0,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA
    obj, elf_path = OUT / "oracle-ui-event.o", OUT / "oracle-ui-event.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding", "-c",
                    str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_uart_registry_callback_5b06aa",
                    *[f"--defsym={name}=0x{address:x}" for name, address in RAM.items()],
                    *[f"--defsym={name}=0x{row[0]:x}" for name, row in LOWERS.items()],
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, flags, machine_state, role):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload)+4095)&~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data: cpu.mem_write(address, data)
        cpu.mem_write(0x200e3aec, bytes([machine_state, 2, 3, 4, 5, 6, 7, 8]))
        cpu.mem_write(0x200004d8, struct.pack("<II", 0xabcdef01, 0xabcdef02))
        cpu.mem_write(0x20074390, struct.pack("<I", 0x10000))
        cpu.mem_write(0x200743a0, struct.pack("<I", 0x41424344))
        cpu.mem_write(0x20022000, bytes([9, 8, 7, 6, 5, 4, 3, 2]))
        for reg, value in ((A.UC_ARM_REG_R0, event), (A.UC_ARM_REG_R1, 0x20022000),
                           (A.UC_ARM_REG_R2, 0x9999), (A.UC_ARM_REG_R3, 0x1234),
                           (A.UC_ARM_REG_SP, 0x200ff000), (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(reg, value)
        events, done, ticks = [], [False], [0]

        def word(addr):
            return struct.unpack("<I", cpu.mem_read(addr, 4))[0]

        def string(addr):
            return bytes(cpu.mem_read(addr, 160)).split(b"\0")[0].decode("utf-8", "replace")

        names = {row[1 if native else 0]: row[2] for row in LOWERS.values()}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            kind = names.get(pc)
            if kind is None: return
            r = [machine.reg_read(getattr(A, f"UC_ARM_REG_R{i}")) for i in range(4)]
            sp = machine.reg_read(A.UC_ARM_REG_SP)
            if kind == "zero":
                # Stack addresses differ between compiler and stock; compare length/fill.
                events.append((kind, r[1], r[2]))
                machine.mem_write(r[0], bytes([r[2]&255])*r[1])
            elif kind == "copy":
                events.append((kind, r[2], bytes(machine.mem_read(r[1], r[2])).hex()))
                machine.mem_write(r[0], bytes(machine.mem_read(r[1], r[2])))
                machine.reg_write(A.UC_ARM_REG_R0, r[0])
            elif kind == "flags":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
            elif kind == "extended":
                events.append((kind, r[0], string(r[1]), string(r[2]), string(r[3]),
                               word(sp), string(word(sp+4))))
            elif kind == "simple":
                events.append((kind, r[0], string(r[1]), string(r[2])))
            elif kind == "tick":
                events.append((kind,))
                ticks[0] += 1
                machine.reg_write(A.UC_ARM_REG_R0, 0x12345 if ticks[0] == 1 else 0x13579)
            elif kind == "action":
                events.append((kind, r[0], r[1]))
            elif kind == "notify":
                events.append((kind, bytes(machine.mem_read(r[0], 2)).hex()))
            elif kind == "divide":
                events.append((kind, *r))
                dividend = (r[1]<<32) | r[0]
                divisor = (r[3]<<32) | r[2]
                machine.reg_write(A.UC_ARM_REG_R0, (dividend//divisor)&0xffffffff)
                machine.reg_write(A.UC_ARM_REG_R1, (dividend//divisor)>>32)
            elif kind == "role":
                events.append((kind,))
                machine.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == "persist":
                events.append((kind, r[0], r[1], bytes(machine.mem_read(r[2], 8)).hex()))
            elif kind in ("pull", "start", "release", "ble_reset"):
                events.append((kind, r[0]))
            else:
                events.append((kind,))
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        cpu.emu_start((0x5b06aa if native else symbols["audio_uart_registry_callback_5b06aa"])|1,
                      0, count=1000)
        if not done[0]: raise RuntimeError(f"UI callback did not return: {native, event, flags}")
        return {"events": events,
                "machine": bytes(cpu.mem_read(0x200e3aec, 8)).hex(),
                "registry": bytes(cpu.mem_read(0x200004d8, 8)).hex(),
                "start_tick": word(0x20074390)}

    cases = [(event, flags, state, role) for event in range(7)
             for flags in (0, 1, 2, 4, 7) for state in (0, 1, 2) for role in (0, 1)]
    for fixture in cases:
        native, compiled = run(True, *fixture), run(False, *fixture)
        if native != compiled:
            raise RuntimeError(f"Conversate UI event mismatch {fixture}: {native} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_CONVERSATE_UI_EVENT_C",
              "stock_payload_sha256": PAYLOAD_SHA, "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "oracle_elf": str(elf_path.relative_to(ROOT)),
              "oracle_elf_sha256": hashlib.sha256(elf_path.read_bytes()).hexdigest(),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Child providers are controlled lower contracts.",
                         "Incidental return register is not compared."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True)+"\n")
    print(record["status"], len(cases), hashlib.sha256(receipt.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
