#!/usr/bin/env python3
"""Compare ATT client response dispatch and state transitions with stock Main."""
import hashlib
import itertools
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_proc_rsp_4b5448_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-proc-rsp"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
HANDLERS = {
    "audio_attc_rsp_error_4b5230": 0x4b5230,
    "audio_attc_rsp_mtu_4b527a": 0x4b527a,
    "audio_attc_rsp_find_read_4b52c2": 0x4b52c2,
    "audio_attc_rsp_find_type_56c3b0": 0x56c3b0,
    "audio_attc_rsp_read_4b53da": 0x4b53da,
    "audio_attc_rsp_read_long_56c454": 0x56c454,
    "audio_attc_rsp_write_4b53dc": 0x4b53dc,
    "audio_attc_rsp_prepare_write_539dcc": 0x539dcc,
    "audio_attc_rsp_read_multi_var_4b53e2": 0x4b53e2,
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "proc-rsp.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {name: address | 1 for name, address in HANDLERS.items()}
    defs.update({"audio_ble_att_common_state": 0x200610ac,
                 "audio_ble_attc_state": 0x2006f904,
                 "WsfTimerStop": 0x52a4d3,
                 "audio_ble_attc_free_pkt_531ac0": 0x531ac1,
                 "audio_ble_attc_send_req_531144": 0x531145,
                 "audio_ble_attc_setup_req_531160": 0x531161})
    cmd = ["arm-none-eabi-ld", "-Ttext=0x100000"]
    cmd += [f"--defsym={name}={address}" for name, address in defs.items()]
    subprocess.run(cmd + [str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, method, request, length, continuing, handler_status,
            callback, flow_disabled, pending_pkt, on_deck, slot):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not stock:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        ccb, main_ccb, packet = 0x20011000, 0x20012000, 0x20013000
        on_deck_ptr = 0x2006f904 + 0x180 + 3 * 12
        cpu.mem_write(ccb, bytes(64))
        cpu.mem_write(ccb, main_ccb.to_bytes(4, "little"))
        cpu.mem_write(ccb + 4, (3).to_bytes(2, "little"))
        cpu.mem_write(ccb + 6, bytes([request, continuing]))
        cpu.mem_write(ccb + 8, (0x20014000 if pending_pkt else 0).to_bytes(4, "little"))
        cpu.mem_write(ccb + 12, (0x4567).to_bytes(2, "little"))
        cpu.mem_write(ccb + 0x28, bytes([slot, 3]))
        cpu.mem_write(main_ccb, bytes(64))
        cpu.mem_write(main_ccb + slot * 4 + 2, bytes([2 if flow_disabled else 0]))
        data = bytearray([0xa5] * 32)
        data[8] = method * 2 + 1
        cpu.mem_write(packet, bytes(data))
        cpu.mem_write(on_deck_ptr + 2, bytes([on_deck]))
        cpu.mem_write(0x200610ac + 0x58, (0x101d01 if callback else 0).to_bytes(4, "little"))
        cpu.reg_write(A.UC_ARM_REG_R0, ccb)
        cpu.reg_write(A.UC_ARM_REG_R1, length)
        cpu.reg_write(A.UC_ARM_REG_R2, packet)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x52a4d2:
                calls.append(("timer", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc in HANDLERS.values():
                regs = tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                event = bytes(machine.mem_read(regs[3], 13))
                # param and continuing are assigned after the handler returns.
                calls.append(("handler", hex(pc), regs[:3], event[2:12]))
                machine.mem_write(regs[3] + 3, bytes([handler_status]))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x531ac0:
                calls.append(("free", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x531144:
                calls.append(("send", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x531160:
                calls.append(("setup", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x101d00:
                ptr = machine.reg_read(A.UC_ARM_REG_R0)
                calls.append(("callback", bytes(machine.mem_read(ptr, 13))))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b5448 if stock else symbols["audio_ble_attc_proc_rsp_4b5448"]
        cpu.emu_start(entry | 1, 0, count=600)
        assert done[0], (stock, method, request, length, calls)
        return calls, bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(on_deck_ptr, 12))

    cases = [(method, request, length, continuing, handler_status, callback,
              flow_disabled, pending_pkt, on_deck, slot)
             for method, request, length, continuing, handler_status, callback,
             flow_disabled, pending_pkt, on_deck, slot in itertools.product(
                 (0, 1, 2, 3, 5, 9, 10, 11, 12, 13, 16, 17, 18),
                 (0, 1, 2, 5, 16), (0, 1, 2, 5, 98), (0, 1), (0, 5),
                 (False, True), (False, True), (False, True), (0, 5), (0, 1))]
    cases = [case for index, case in enumerate(cases) if index % 1729 == 0]
    cases += [(method, method, length, continuing, status, True, False, False, 5, 0)
              for method, length, continuing, status in itertools.product(
                  (0, 1, 2, 3, 5, 9, 10, 11, 12, 16, 17),
                  (0, 1, 2, 5, 98), (0, 1), (0, 5))]
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT response mismatch {case}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_PROC_RSP_C", "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Response handlers, timer, free/send/setup helpers, callback and ATT RAM placement are controlled.",
                         "Method 17 with length at least 116 reaches a stock out-of-table branch and is rejected by the C candidate; it is outside this matched domain."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
