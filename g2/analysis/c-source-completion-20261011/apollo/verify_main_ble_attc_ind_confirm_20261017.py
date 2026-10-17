#!/usr/bin/env python3
"""Stock/C ATT client indication-confirm call and packet contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_ind_confirm_4b5838_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-ind-confirm"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "confirm.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    definitions = {"audio_ble_attc_ccb_by_handle_531a7c": 0x531a7d,
                   "attMsgAlloc": 0x4b50af,
                   "L2cDataReq": 0x530bbd,
                   "audio_ble_hci_vendor_log_enabled_4c9c50": 0x4c9c51,
                   "audio_ble_hci_vendor_compare_44b610": 0x44b611,
                   "audio_log_flags": 0x43d0cf,
                   "audio_log_extended": 0x43d575,
                   "audio_ble_hci_wsf_trace": 0x52a63d}
    command = ["arm-none-eabi-ld", "-Ttext=0x100000"]
    command += [f"--defsym={name}={address}" for name, address in definitions.items()]
    subprocess.run(command + [str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, connection, control, handle, lookup_ok, alloc_ok,
            enabled, responses, flags):
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
        cpu.mem_write(ccb, bytes(64))
        cpu.mem_write(ccb, main_ccb.to_bytes(4, "little"))
        cpu.mem_write(main_ccb, bytes(64))
        cpu.mem_write(main_ccb + 2, bytes([control]))
        cpu.mem_write(main_ccb + 12, handle.to_bytes(2, "little"))
        cpu.mem_write(packet, bytes([0xa5] * 32))
        cpu.reg_write(A.UC_ARM_REG_R0, connection)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done, compare_index = [], [False], [0]

        def string(machine, address):
            data = bytes(machine.mem_read(address, 256))
            return data.split(b"\0", 1)[0].decode("utf-8", "replace")

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x531a7c:
                calls.append(("lookup", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, ccb if lookup_ok else 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x4b50ae:
                calls.append(("alloc", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_R0, packet if alloc_ok else 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x530bbc:
                calls.append(("send",) + tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x4c9c50:
                calls.append(("enabled",))
                machine.reg_write(A.UC_ARM_REG_R0, enabled)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x44b610:
                args = tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                calls.append(("compare", string(machine, args[0]),
                              string(machine, args[1]), args[2]))
                result = responses[min(compare_index[0], len(responses) - 1)]
                compare_index[0] += 1
                machine.reg_write(A.UC_ARM_REG_R0, result)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x43d0ce:
                calls.append(("flags",))
                machine.reg_write(A.UC_ARM_REG_R0, flags)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x43d574:
                regs = tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                sp = machine.reg_read(A.UC_ARM_REG_SP)
                line, message, value = (int.from_bytes(machine.mem_read(sp + i * 4, 4), "little")
                                        for i in range(3))
                calls.append(("log", regs[0], string(machine, regs[1]),
                              string(machine, regs[2]), string(machine, regs[3]),
                              line, string(machine, message), value))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x52a63c:
                regs = tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
                calls.append(("trace", string(machine, regs[0]),
                              string(machine, regs[1]), regs[2]))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b5838 if stock else symbols["audio_ble_attc_ind_confirm_4b5838"]
        cpu.emu_start(entry | 1, 0, count=600)
        assert done[0], (stock, connection, control, lookup_ok, alloc_ok, calls)
        return calls, bytes(cpu.mem_read(main_ccb, 64)), bytes(cpu.mem_read(packet, 32))

    choices = ((0,), (1,), (1, 0), (1, 1, 0), (1, 1, 1))
    zero_cases = [(0, 0, 0, False, False, enabled, responses, flags)
                  for enabled, responses, flags in itertools.product((0, 1), choices, (0, 2))]
    live_cases = [(connection, control, handle, lookup_ok, alloc_ok, 0, (1,), 0)
                  for connection, control, handle, lookup_ok, alloc_ok in
                  itertools.product((1, 2, 255), (0, 0x10, 0x12, 0x30, 0xff),
                                    (0, 0x1234, 0xffff), (False, True),
                                    (False, True))]
    cases = zero_cases + live_cases
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT confirm mismatch {case}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_IND_CONFIRM_C",
              "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["CCB lookup, allocator, sender, and logger are controlled at call boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
