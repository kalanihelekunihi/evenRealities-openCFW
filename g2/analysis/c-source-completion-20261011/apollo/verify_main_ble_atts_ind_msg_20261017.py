#!/usr/bin/env python3
"""Compare the selected stock Cordio indication message callback with C."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_atts_ind_msg_533bcc_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-atts-ind-msg"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "ind-msg.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defs = {"audio_ble_att_registration_lookup": 0x534f15,
            "WsfMsgFree": 0x4bf9b1,
            "audio_ble_atts_pend_ind_ntf_5338ac": 0x5338ad,
            "audio_ble_atts_exec_callback_533934": 0x533935,
            "audio_ble_atts_setup_msg_5339ac": 0x5339ad,
            "audio_ble_att_decode_msg_param_4b50fe": 0x4b50ff}
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000", "-e",
                    "audio_ble_atts_ind_msg_533bcc",
                    *(f"--defsym={name}={hex(value)}" for name, value in defs.items()),
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, event, raw_param, slot, valid, pending):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        cpu.mem_map(0x438000, (len(payload) + 4095) & ~4095)
        cpu.mem_write(0x438000, payload)
        cpu.mem_map(0x100000, 0x20000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                if data:
                    cpu.mem_write(address, data)
        msg, packet, ccb = 0x20011000, 0x20012000, 0x20013000
        cpu.mem_write(msg, bytes(24))
        cpu.mem_write(msg, struct.pack("<H", raw_param))
        cpu.mem_write(msg + 2, bytes([event]))
        cpu.mem_write(msg + 4, struct.pack("<I", packet))
        cpu.mem_write(msg + 8, bytes([slot]))
        cpu.mem_write(packet, bytes(32))
        cpu.mem_write(packet + 2, struct.pack("<H", 0x1234))
        cpu.reg_write(A.UC_ARM_REG_R0, msg)
        cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(A.UC_ARM_REG_LR, 0x101f01)
        calls, done = [], [False]
        targets = {0x534f14: "lookup", 0x4bf9b0: "free", 0x5338ac: "pending",
                   0x533934: "callback", 0x5339ac: "setup", 0x4b50fe: "decode"}

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc in targets:
                label = targets[pc]
                args = tuple(machine.reg_read(x) for x in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
                if label == "lookup":
                    calls.append((label, args[0], args[1]))
                    machine.reg_write(A.UC_ARM_REG_R0, ccb if valid else 0)
                elif label == "pending":
                    calls.append((label, args[0] == ccb, args[1] == packet))
                    machine.reg_write(A.UC_ARM_REG_R0, int(pending))
                elif label == "decode":
                    calls.append((label, args[0], args[1] != 0, args[2] != 0))
                    machine.mem_write(args[1], bytes([raw_param & 0xff]))
                    machine.mem_write(args[2], bytes([(raw_param >> 8) & 0xff]))
                    machine.reg_write(A.UC_ARM_REG_R0, 0)
                elif label == "free":
                    calls.append((label, args[0] == packet))
                elif label == "callback":
                    calls.append((label, args[:3]))
                elif label == "setup":
                    calls.append((label, args[0] == ccb, args[1], args[2],
                                  args[3] == packet))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x533bcc if native else symbols["audio_ble_atts_ind_msg_533bcc"]
        cpu.emu_start(entry | 1, 0, count=300)
        assert done[0], (native, event, calls)
        return calls, bytes(cpu.mem_read(msg, 12)).hex()

    cases = list(itertools.product((0, 0x21, 0x22, 0x23), (1, 0x1234),
                                   (0, 2), (False, True), (False, True)))
    for case in cases:
        stock, compiled = run(True, *case), run(False, *case)
        if stock != compiled:
            raise RuntimeError(f"ATT indication message mismatch {case}: {stock} != {compiled}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTS_IND_MSG_C",
              "cases": len(cases), "source": str(SOURCE.relative_to(ROOT)),
              "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA,
              "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Six downstream calls are controlled; timeout lookup branch has no further stock action."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], len(cases), sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
