#!/usr/bin/env python3
"""Compare three Cordio ATT control callbacks with stock Main."""
import hashlib
import itertools
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_att_control_callbacks_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-att-control-callbacks"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
LOWERS = {
    "audio_ble_attc_ccb_by_conn_id_531820": 0x531820,
    "audio_ble_attc_ind_confirm_4b5838": 0x4b5838,
    "audio_ble_attc_write_cmd_callback_530de6": 0x530de6,
    "audio_ble_att_registration_lookup": 0x534f14,
    "audio_ble_atts_ind_ntf_callback_53394c": 0x53394c,
    "audio_ble_atts_state": 0x20016000,
}
ADDRESSES = ((0x531330, "audio_ble_attc_ctrl_531330"),
             (0x533c4c, "audio_ble_atts_ind_ctrl_533c4c"),
             (0x534c8a, "audio_ble_atts_ctrl_534c8a"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    assert struct.unpack_from("<I", payload, 0x535448 - 0x438000)[0] == 0x2006e5f0
    obj, elf_path = OUT / "att-control.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_attc_ctrl_531330",
                    *(f"--defsym={name}=0x{address|1:x}" if address < 0x20000000 else
                      f"--defsym={name}=0x{address:x}" for name, address in LOWERS.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, address, name, connection, present):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for start, data in segments:
                if data:
                    cpu.mem_write(start, data)
        message, interface = 0x20011000, 0x20018000
        cpu.mem_write(message, struct.pack("<H", connection))
        for state in (0x20016000, 0x2006e5f0):
            cpu.mem_write(state + 0x260, struct.pack("<I", interface))
        cpu.mem_write(interface + 4, struct.pack("<I", 0x20019001))
        cpu.reg_write(A.UC_ARM_REG_R0, message)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        events, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
                return
            r0, r1, r2 = (machine.reg_read(x) for x in
                           (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1, A.UC_ARM_REG_R2))
            if pc in (0x531820, 0x534f14):
                events.append(("lookup", pc, r0, r1))
                value = 0x20012000 if present else 0
            elif pc == 0x4b5838:
                events.append(("confirm", r0))
                value = 0
            elif pc in (0x530de6, 0x53394c):
                events.append(("callback", pc, r0, r1, r2))
                value = 0
            elif pc == 0x20019000:
                events.append(("indirect", r0))
                value = 0
            else:
                return
            machine.reg_write(A.UC_ARM_REG_R0, value)
            machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = address if native else symbols[name]
        cpu.emu_start(entry | 1, 0, count=200)
        assert done[0], (native, address, events)
        return events

    cases = list(itertools.product(ADDRESSES, (0, 1, 255, 256, 0x1234),
                                   (False, True)))
    for (address, name), connection, present in cases:
        stock = run(True, address, name, connection, present)
        compiled = run(False, address, name, connection, present)
        if stock != compiled:
            raise RuntimeError(f"ATT control mismatch {name} {connection} {present}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATT_CONTROL_CALLBACKS_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Connection lookup, pending callbacks and indication dispatch are controlled lower calls."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
