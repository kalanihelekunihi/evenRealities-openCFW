#!/usr/bin/env python3
"""Compare Terminal type-two incremental event with pinned Apollo stock."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_type2_5eabde.c"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-type2-5eabde"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CALLS = (
    ("audio_terminal_resource_597324", 0x597324, 0),
    ("audio_terminal_last_record_597350", 0x597350, 0),
    ("audio_terminal_item_height_5ea67a", 0x5ea67a, 1),
    ("audio_terminal_recompute_offsets_5ea6da", 0x5ea6da, 1),
    ("audio_terminal_event_apply_input_5eaa96", 0x5eaa96, 1),
    ("audio_terminal_event_default_5eaad4", 0x5eaad4, 1),
    ("audio_terminal_list_rollover_5eab8e", 0x5eab8e, 0),
    ("audio_terminal_event_refresh_view_5ea992", 0x5ea992, 0),
    ("audio_uart_lv_obj_y_44e498", 0x44e498, 1),
    ("audio_terminal_view_position_5ea926", 0x5ea926, 1),
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    stub = OUT / "type2-oracle-stub.c"
    stub.write_text("#include <stdint.h>\nuint8_t audio_terminal_ui_state_base[0x2a0];\n" +
                    "\n".join(f"__attribute__((noinline,used)) uint32_t {name}"
                              "(uint32_t a){(void)a;return 0;}"
                              for name, _, _ in CALLS) + "\n")
    elf = OUT / "type2-oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_terminal_event_type2_5eabde",
                    str(SOURCE), str(stub), "-o", str(elf)], check=True)
    symbols = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ["arm-none-eabi-nm", str(elf)], text=True).splitlines()
        if len(p := line.split()) == 3}
    with elf.open("rb") as f:
        segments = [(s["p_vaddr"], s.data()) for s in ELFFile(f).iter_segments()
                    if s["p_type"] == "PT_LOAD"]

    def run(compiled, root, resource, last, count, prior, input_kind, flag):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000)
        u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for address, data in segments:
            u.mem_write(address, data)
        u.mem_map(0x20000000, 0x100000)
        state = symbols["audio_terminal_ui_state_base"] if compiled else 0x2006e0d0
        u.mem_write(state, bytes((0x5a,)) * 0x2a0)
        u.mem_write(state + 4, struct.pack("<I", 0x20002000 if root else 0))
        u.mem_write(state + 0x1c4, struct.pack("<H", prior))
        u.mem_write(state + 0x28c, bytes((flag,)))
        u.mem_write(0x20009500, struct.pack("<H", count))
        input_addr = 0 if input_kind == 0 else 0x20003000
        u.mem_write(0x20003000, bytes((1 if input_kind == 2 else 0, 0, 0, 0)))
        cuts = {(symbols[name] if compiled else address) & ~1: index
                for index, (name, address, _) in enumerate(CALLS)}
        trace = []
        def hook(cpu, pc, size, _):
            index = cuts.get(pc)
            if index is None:
                return
            name, _, arity = CALLS[index]
            arg = cpu.reg_read(A.UC_ARM_REG_R0)
            trace.append((name,) if arity == 0 else (name, arg))
            result = 0
            if index == 0:
                result = 0x20001000 if resource else 0
            elif index == 1:
                result = 0x20004000 if last else 0
            elif index == 2:
                result = 0x37
            elif index == 8:
                result = 0x1234
            cpu.reg_write(A.UC_ARM_REG_R0, result)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        u.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        u.reg_write(A.UC_ARM_REG_LR, 0x600001)
        u.reg_write(A.UC_ARM_REG_R0, input_addr)
        entry = symbols["audio_terminal_event_type2_5eabde"] if compiled else 0x5eabde
        u.emu_start(entry | 1, 0x600000, count=10000)
        return bytes(u.mem_read(state, 0x2a0)), trace

    cases = 0
    for root in (0, 1):
        for resource in (0, 1):
            for last in (0, 1):
                for count, prior in ((0, 0), (1, 0), (2, 1), (2, 0), (64, 64), (64, 63)):
                    for input_kind in (0, 1, 2):
                        for flag in (0, 1):
                            stock = run(False, root, resource, last, count, prior, input_kind, flag)
                            selected = run(True, root, resource, last, count, prior, input_kind, flag)
                            if stock != selected:
                                raise RuntimeError(f"type2 mismatch {root=} {resource=} {last=} "
                                                   f"{count=} {prior=} {input_kind=} {flag=}: "
                                                   f"{stock[1]} vs {selected[1]}")
                            cases += 1
    result = {"status": "PASS_EXPERIMENTAL_TERMINAL_EVENT_TYPE2_C_ORACLE",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "payload_sha256": PIN, "oracle_elf_sha256": sha(elf), "cases": cases,
              "scope": "incremental, 64-row rollover and fallback branches with full Terminal RAM and call trace",
              "limits": ["Last-record and rollover child effects plus final RAM placement remain open."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], cases, sha(receipt))

if __name__ == "__main__":
    main()
