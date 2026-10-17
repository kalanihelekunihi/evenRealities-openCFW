#!/usr/bin/env python3
"""Stock/C boundaries for HCI LE supported-features and create-cancel."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_le_features_cancel_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-hci-le-features-cancel"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "hci.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_ble_hci_controller_state_20071478=0x20071478",
                    "--defsym=audio_ble_hci_cmd_alloc_52ae38=0x52ae39",
                    "--defsym=audio_ble_hci_cmd_send=0x52ae5f",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, which, value):
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
        cpu.mem_write(0x20071500, value.to_bytes(8, "little"))
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x52ae38:
                calls.append(("alloc", machine.reg_read(A.UC_ARM_REG_R0),
                              machine.reg_read(A.UC_ARM_REG_R1)))
                machine.reg_write(A.UC_ARM_REG_R0, value & 0xffffffff)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x52ae5e:
                calls.append(("send", machine.reg_read(A.UC_ARM_REG_R0)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        name = "audio_ble_hci_get_le_supported_features_530d3c" if which == "features" else "audio_ble_hci_create_conn_cancel_52b0a4"
        entry = (0x530d3c if which == "features" else 0x52b0a4) if stock else symbols[name]
        cpu.emu_start(entry | 1, 0, count=150)
        assert done[0], (stock, which, value, calls)
        result = (cpu.reg_read(A.UC_ARM_REG_R0) |
                  (cpu.reg_read(A.UC_ARM_REG_R1) << 32)) if which == "features" else None
        return calls, result, bytes(cpu.mem_read(0x20071500, 8))

    values = (0, 1, 2, 3, 0x100000002, 0xffffffffffffffff,
              0x123456789abcdef0, 0x20011000)
    for which in ("features", "cancel"):
        for value in values:
            native, compiled = run(True, which, value), run(False, which, value)
            if native != compiled:
                raise RuntimeError(f"HCI {which} mismatch {value:#x}: {native} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_HCI_LE_FEATURES_CANCEL_C",
              "cases": len(values) * 2,
              "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["HCI command allocator and sender are controlled at their call boundaries.",
                         "Source ownership of controller state does not establish final RAM placement."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
