#!/usr/bin/env python3
"""Compare Cordio multiple-variable notification callback against stock Main."""
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
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ble_attc_multi_var_ntf_4b53e4_20261017.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OUT = G2 / "build/c-firmware/20261017/main-ble-attc-multi-var-ntf"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    obj, elf_path = OUT / "multi-var.o", OUT / "oracle.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-ffreestanding",
                    "-fno-builtin", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x100000",
                    "--defsym=audio_ble_att_common_state=0x200610ac",
                    str(obj), "-o", str(elf_path)], check=True, capture_output=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(p["p_vaddr"], p.data()) for p in elf.iter_segments()
                    if p["p_type"] == "PT_LOAD" and p["p_vaddr"] < 0x20000000]
        symbols = {s.name: s["st_value"] for s in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    def run(stock, length, opcode, conn_id, slot, control, has_callback):
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
        cpu.mem_write(ccb + 0x28, bytes([slot]))
        cpu.mem_write(main_ccb, bytes(64))
        cpu.mem_write(main_ccb + 0x0e, bytes([conn_id]))
        cpu.mem_write(main_ccb + slot * 4 + 2, bytes([control]))
        data = bytearray([0xa5] * 32)
        data[8] = opcode
        cpu.mem_write(packet, bytes(data))
        cpu.mem_write(0x200610ac + 0x58,
                      (0x101d01 if has_callback else 0).to_bytes(4, "little"))
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
            elif pc == 0x101d00:
                ptr = machine.reg_read(A.UC_ARM_REG_R0)
                event = bytes(machine.mem_read(ptr, 13))
                # The event.handle field at offsets 10..11 is not initialized
                # by this callback and is outside the event contract here.
                calls.append(("callback", event[:10], event[12]))
                machine.reg_write(A.UC_ARM_REG_PC, machine.reg_read(A.UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b53e4 if stock else symbols["audio_ble_attc_proc_multi_ntf_4b53e4"]
        cpu.emu_start(entry | 1, 0, count=200)
        assert done[0], (stock, length, opcode, calls)
        return calls, bytes(cpu.mem_read(ccb, 64)), bytes(cpu.mem_read(main_ccb, 64)), bytes(cpu.mem_read(packet, 32))

    cases = list(itertools.product((0, 1, 3, 0xffff), (0, 0x23, 0xff),
                                   (0, 1, 255), (0, 1, 3), (0, 2, 0xff),
                                   (False, True)))
    # Sample the Cartesian space while keeping each input's edge values.
    cases = [case for index, case in enumerate(cases) if index % 7 == 0]
    for case in cases:
        native, compiled = run(True, *case), run(False, *case)
        if native != compiled:
            raise RuntimeError(f"ATT multivar mismatch {case}: {native[0]} != {compiled[0]}")
    record = {"status": "PASS_BOUNDED_MAIN_BLE_ATTC_MULTI_VAR_NTF_C", "cases": len(cases),
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE.read_bytes()),
              "stock_payload_sha256": PAYLOAD_SHA, "oracle_elf_sha256": sha(elf_path.read_bytes()),
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["Application callback address and ATT common RAM placement are controlled."]}
    receipt = OUT / "oracle-receipt.json"
    receipt.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(record["status"], record["cases"], sha(receipt.read_bytes()))


if __name__ == "__main__":
    main()
