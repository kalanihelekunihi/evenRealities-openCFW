#!/usr/bin/env python3
"""Stock/C HCI LE create-connection command buffer contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_create_conn_52afcc_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-hci-create-conn"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "create.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_ble_hci_cmd_alloc_52ae38=0x52ae39",
                    "--defsym=audio_ble_copy_address6_4d293c=0x4d293d",
                    "--defsym=audio_ble_hci_cmd_send=0x52ae5f",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, interval, window, policy, addr_type, own_type, seed, alloc_ok):
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
        peer, spec, command = 0x20011000, 0x20012000, 0x20013000
        cpu.mem_write(peer, bytes((seed + i * 17) & 255 for i in range(8)))
        cpu.mem_write(spec, bytes((seed * 3 + i * 29) & 255 for i in range(16)))
        cpu.mem_write(command, bytes([0xa5] * 40))
        sp = 0x200ff000
        for i, value in enumerate((peer, own_type, spec)):
            cpu.mem_write(sp + i * 4, value.to_bytes(4, "little"))
        for reg, value in zip((A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3),
                              (interval, window, policy, addr_type)):
            cpu.reg_write(reg, value)
        cpu.reg_write(A.UC_ARM_REG_SP, sp)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x52ae38:
                calls.append(("alloc", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, command if alloc_ok else 0)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x4d293c:
                destination = machine.reg_read(A.UC_ARM_REG_R0)
                source = machine.reg_read(A.UC_ARM_REG_R1)
                calls.append(("copy", destination, source))
                machine.mem_write(destination, bytes(machine.mem_read(source, 6)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x52ae5e:
                calls.append(("send", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x52afcc if stock else symbols["audio_ble_hci_create_conn_52afcc"]
        cpu.emu_start(entry | 1, 0, count=400)
        assert done[0], (stock, interval, window, policy, addr_type, calls)
        return calls, bytes(cpu.mem_read(command, 40))

    cases = list(itertools.product((0, 0x1234, 0xffff), (0, 0x55aa),
                                   (0, 1, 255), (0, 2), (0, 3),
                                   (0, 17), (False, True)))
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"HCI create mismatch {case}: {native} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_HCI_CREATE_CONN_C",
              "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["HCI allocator, address copy, and sender are controlled at call boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
