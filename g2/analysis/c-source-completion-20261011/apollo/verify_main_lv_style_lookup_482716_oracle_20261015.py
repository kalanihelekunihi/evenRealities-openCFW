#!/usr/bin/env python3
"""Execute native/C LV style lookup over dense and sparse table layouts."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_style_lookup_482716.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
assert hashlib.sha256(IMAGE).hexdigest() == "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
BODIES = {
    "audio_uart_lv_style_is_sparse_482708": (0x482708, 0x482716,
        "5f4d8578d1c93ca71614bc46df4d853223c3b8e389efde4fef5231c6cde6f999"),
    "audio_uart_lv_style_lookup_482716": (0x482716, 0x48277e,
        "094798629ce86c61f6c7e0aee2be68676cb8e7629dba07c4d0a2959a63dabcce"),
}
for start, end, expected in BODIES.values():
    assert hashlib.sha256(IMAGE[start-0x438000:end-0x438000]).hexdigest() == expected
OUT = G2 / "build/c-firmware/20261015/main-lv-style-lookup-482716"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as tmp:
    elf = Path(tmp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_lv_style_lookup_482716",
                    str(SOURCE), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, entry, sparse, rows, property_):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x10000)
        style, data, output = 0x20001000, 0x20002000, 0x20003000
        uc.mem_write(style, data.to_bytes(4, "little"))
        uc.mem_write(style + 8, bytes([0xff if sparse else len(rows)]))
        if sparse:
            for index, (key, value) in enumerate(rows):
                uc.mem_write(data + index*8, bytes([key]) + b"\0\0\0" +
                             value.to_bytes(4, "little"))
            uc.mem_write(data + len(rows)*8, b"\0" * 8)
        else:
            for index, (key, value) in enumerate(rows):
                uc.mem_write(data + index*4, value.to_bytes(4, "little"))
                uc.mem_write(data + len(rows)*4 + index, bytes([key]))
        uc.mem_write(output, (0xdeadbeef).to_bytes(4, "little"))
        for reg, word in ((A.UC_ARM_REG_R0, style), (A.UC_ARM_REG_R1, property_),
                          (A.UC_ARM_REG_R2, output), (A.UC_ARM_REG_SP, 0x2000f000),
                          (A.UC_ARM_REG_LR, 0x600001)):
            uc.reg_write(reg, word)
        uc.emu_start((symbols[entry] if compiled else BODIES[entry][0]) | 1,
                     0x600000, count=1000)
        return uc.reg_read(A.UC_ARM_REG_R0), int.from_bytes(uc.mem_read(output, 4), "little")

    cases = 0
    layouts = [[], [(8, 0x11111111)], [(0, 0x22222222)],
               [(8, 0x11111111), (9, 0x22222222)],
               [(9, 0x11111111), (8, 0x22222222), (8, 0x33333333)]]
    for sparse in (False, True):
        for rows in layouts:
            for property_ in (0, 8, 9, 10, 0x108, 0x109):
                native = run(False, "audio_uart_lv_style_lookup_482716",
                             sparse, rows, property_)
                candidate = run(True, "audio_uart_lv_style_lookup_482716",
                                sparse, rows, property_)
                assert native == candidate, (sparse, rows, property_, native, candidate)
                cases += 1
        native = run(False, "audio_uart_lv_style_is_sparse_482708", sparse, [], 0)
        candidate = run(True, "audio_uart_lv_style_is_sparse_482708", sparse, [], 0)
        assert native == candidate, (sparse, native, candidate)
        cases += 1

receipt = {"status": "PASS_NATIVE_MAIN_LV_STYLE_LOOKUP_482716",
           "source": str(SOURCE.relative_to(ROOT)),
           "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
           "official_payload_sha256": hashlib.sha256(IMAGE).hexdigest(),
           "native_body_sha256": {name: body[2] for name, body in BODIES.items()},
           "source_owned_symbols": sorted(BODIES), "cases": cases,
           "limits": ["Sparse tests use an explicit zero-key sentinel as observed by native code.",
                      "No final image placement or hardware execution is claimed."]}
path = OUT / "oracle-receipt.json"
path.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], cases)
