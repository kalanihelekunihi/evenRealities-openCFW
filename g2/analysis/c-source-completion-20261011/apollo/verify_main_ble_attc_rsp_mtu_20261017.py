#!/usr/bin/env python3
"""Stock/C Cordio ATT MTU response argument and call-order contract."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_rsp_mtu_4b527a_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-rsp-mtu"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "mtu.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_ble_att_cfg_ptr_200004b4=0x200004b4",
                    "--defsym=audio_ble_hci_max_rx_acl_len_530d4c=0x530d4d",
                    "--defsym=audio_ble_att_set_mtu_4b503c=0x4b503d",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, peer, configured, first_acl, second_acl, slot):
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
        ccb, main_ccb, packet, event = (0x20011000, 0x20012000,
                                        0x20013000, 0x20014000)
        cpu.mem_write(ccb, bytes(64))
        cpu.mem_write(ccb, main_ccb.to_bytes(4, "little"))
        cpu.mem_write(ccb + 0x28, bytes([slot]))
        cpu.mem_write(main_ccb, bytes(64))
        data = bytearray([0xa5] * 32)
        data[9:11] = peer.to_bytes(2, "little")
        cpu.mem_write(packet, bytes(data))
        cpu.mem_write(event, bytes([0x5a] * 16))
        cpu.mem_write(0x200004b4, (0x20000414).to_bytes(4, "little"))
        cpu.mem_write(0x20000414 + 4, configured.to_bytes(2, "little"))
        for register, value in ((A.UC_ARM_REG_R0, ccb), (A.UC_ARM_REG_R1, 3),
                                (A.UC_ARM_REG_R2, packet), (A.UC_ARM_REG_R3, event),
                                (A.UC_ARM_REG_SP, 0x200ff000),
                                (A.UC_ARM_REG_LR, 0x101f01)):
            cpu.reg_write(register, value)
        calls, done = [], [False]

        def hook(machine, pc, _size, _user):
            if pc == 0x101f00:
                done[0] = True
                machine.emu_stop()
            elif pc == 0x530d4c:
                calls.append(("HciGetMaxRxAclLen",))
                machine.reg_write(A.UC_ARM_REG_R0,
                                  first_acl if sum(c[0] == "HciGetMaxRxAclLen" for c in calls) == 1
                                  else second_acl)
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))
            elif pc == 0x4b503c:
                calls.append(("attSetMtu",) + tuple(machine.reg_read(reg) for reg in
                             (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                              A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b527a if stock else symbols["audio_attc_rsp_mtu_4b527a"]
        cpu.emu_start(entry | 1, 0, count=150)
        assert done[0], (stock, peer, configured, first_acl, second_acl, calls)
        return calls, bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(event, 16))

    cases = list(itertools.product((0, 1, 246, 247, 248, 0xffff),
                                   (0, 20, 247, 251, 500, 0xffff),
                                   (0, 3, 4, 247, 251, 500, 0xffff),
                                   (0, 251, 500, 0xffff), (0, 1, 3)))
    cases = [case for index, case in enumerate(cases) if index % 17 == 0]
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT MTU mismatch {case}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_RSP_MTU_C", "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["HCI ACL length and ATT negotiated-MTU setter are controlled call boundaries."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
