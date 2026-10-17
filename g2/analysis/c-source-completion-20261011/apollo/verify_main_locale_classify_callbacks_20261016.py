#!/usr/bin/env python3
"""Compare three stock ASCII classification leaves with C implementations."""
import hashlib
import importlib.util
import json
import random
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_ring_locale_classify_callbacks_4d4368.c"
PACKAGE = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PRIOR_SCRIPT = G2 / "analysis/c-source-completion-20261011/apollo/verify_main_locale_ascii_callbacks_20261016.py"
PRIOR = G2 / "build/c-firmware/20261016/main-locale-ascii-callbacks/receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-locale-classify-callbacks"
FUNCTIONS = (("audio_uart_locale_ascii_lowercase_4d4368", 0x4d4368),
             ("audio_uart_locale_ascii_uppercase_4d436c", 0x4d436c),
             ("audio_uart_locale_ascii_alpha_4d436e", 0x4d436e))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prior = json.loads(PRIOR.read_text())
    if prior["status"] != "PASS_EXPERIMENTAL_MAIN_LOCALE_ASCII_CALLBACKS_C" or \
            prior["package_sha256"] != sha(PACKAGE):
        raise RuntimeError("locale callback source proof changed")
    spec = importlib.util.spec_from_file_location("previous_locale_oracle", PRIOR_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = PACKAGE.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701":
        raise RuntimeError("Apollo Main payload changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj, elf_path = OUT / "locale-classify-callbacks.o", OUT / "locale-classify-callbacks.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-o", str(elf_path),
                    str(obj)], check=True, stderr=subprocess.DEVNULL)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {item.name: item["st_value"] for item in
                   elf.get_section_by_name(".symtab").iter_symbols()}
        segments = [(item["p_vaddr"], item.data()) for item in elf.iter_segments()
                    if item["p_type"] == "PT_LOAD"]
    values = sorted(set(range(0x80)) | {0x80, 0xff, 0x100, 0xffff, 0x10000,
                                         0x7fffffff, 0x80000000, 0xffffffe0,
                                         0xfffffff6, 0xfffffff7, 0xffffffff} |
                    {random.Random(0x4d4368 + i).getrandbits(32) for i in range(128)})
    comparisons = 0
    for name, stock in FUNCTIONS:
        if name not in symbols:
            raise RuntimeError("compiled classifier missing: " + name)
        for value in values:
            native = module.run((), payload, stock, value)
            compiled = module.run(segments, payload, symbols[name], value)
            if native != compiled:
                raise RuntimeError(f"classifier mismatch {name} {value:#x}: "
                                   f"{native:#x} {compiled:#x}")
            comparisons += 1
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_LOCALE_CLASSIFY_CALLBACKS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "package": str(PACKAGE.relative_to(ROOT)), "package_sha256": sha(PACKAGE),
               "prior_script": str(PRIOR_SCRIPT.relative_to(ROOT)),
               "prior_script_sha256": sha(PRIOR_SCRIPT),
               "prior_receipt": str(PRIOR.relative_to(ROOT)),
               "prior_receipt_sha256": sha(PRIOR),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "elf": str(elf_path.relative_to(ROOT)), "elf_sha256": sha(elf_path),
               "stock_addresses": {name: hex(address) for name, address in FUNCTIONS},
               "inputs_per_callback": len(values), "comparisons": comparisons,
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Controlled stock/C comparison covers ASCII, boundaries and deterministic 32-bit inputs for three classifier leaves. Table ownership and runtime mutation are separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], comparisons, sha(path))


if __name__ == "__main__":
    main()
