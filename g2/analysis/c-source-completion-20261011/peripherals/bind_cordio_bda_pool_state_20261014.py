#!/usr/bin/env python3
"""Compare a source projection with pinned Cordio and bind its C provider."""
import ctypes
import hashlib
import json
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE_RECEIPT = OUT / "pool-state-norflash-remaining-current-receipt.json"
SOURCE = G2 / "components/main/cordio_bda_candidate_20261014/bda_is_zeros.c"
UPSTREAM_ROOT = ROOT / "third-party/upstream/cordio"
UPSTREAM = UPSTREAM_ROOT / "wsf/sources/util/bda.c"
HOST_SOURCE = OUT / "bda-is-zeros-host.dylib"
HOST_UPSTREAM = OUT / "bda-cordio-upstream-host.dylib"
OBJECT = OUT / "bda-is-zeros-pool-state-abi.o"
BOUND = OUT / "apollo-main-pool-state-bda-bound.o"
RECEIPT = OUT / "pool-state-bda-current-receipt.json"
PROVIDER = "BdaIsZeros"
PIN = "3656312d6b73e2a2c1c8b33ee0385bc199dd97e6"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *flags):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", *flags, str(path)], text=True).splitlines()}


def host_function(path):
    library = ctypes.CDLL(str(path))
    function = library.BdaIsZeros
    function.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
    function.restype = ctypes.c_uint8
    return library, function


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_POOLED_MAIN_NORFLASH_RECORDED_ALIASES"
    assert subprocess.check_output(["git", "-C", str(UPSTREAM_ROOT), "rev-parse", "HEAD"],
                                   text=True).strip() == PIN
    assert "BDA_ADDR_LEN                  6" in (UPSTREAM_ROOT / "wsf/include/util/bda.h").read_text()
    assert "bool_t BdaIsZeros(const uint8_t *pAddr)" in UPSTREAM.read_text()
    subprocess.run(["clang", "-dynamiclib", "-fPIC", "-std=c11", "-O2", str(SOURCE),
                    "-o", str(HOST_SOURCE)], check=True)
    subprocess.run(["clang", "-dynamiclib", "-fPIC", "-std=c11", "-O2",
                    "-I" + str(UPSTREAM_ROOT / "wsf/include"),
                    "-I" + str(UPSTREAM_ROOT / "platform/include"),
                    str(UPSTREAM), "-o", str(HOST_UPSTREAM)], check=True)
    ours_lib, ours = host_function(HOST_SOURCE)
    upstream_lib, stock = host_function(HOST_UPSTREAM)
    cases = [bytes(6)]
    cases += [bytes(255 if j == i else 0 for j in range(6)) for i in range(6)]
    rng = random.Random(0xBDA20261014)
    cases += [rng.randbytes(6) for _ in range(10000)]
    for sample in cases:
        data = (ctypes.c_uint8 * 6).from_buffer_copy(sample)
        assert ours(data) == stock(data) == int(all(x == 0 for x in sample))
    assert ours_lib and upstream_lib
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-fshort-enums", "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(OBJECT)],
                   check=True)
    assert names(OBJECT, "-g", "--defined-only") == {PROVIDER}
    assert not names(OBJECT, "-u")
    original = ROOT / base["linked_object"]
    assert sha(original) == base["linked_sha256"]
    before = names(original, "-u")
    assert PROVIDER in before
    subprocess.run(["arm-none-eabi-ld", "-r", str(original), str(OBJECT),
                    "-o", str(BOUND)], check=True)
    after = names(BOUND, "-u")
    assert after == before - {PROVIDER}
    receipt = {
        "status": "PASS_POOLED_MAIN_CORDIO_BDA_SOURCE_C",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "upstream": str(UPSTREAM.relative_to(ROOT)),
        "upstream_sha256": sha(UPSTREAM),
        "upstream_commit": PIN,
        "host_parity_cases": len(cases),
        "pool_abi_object": str(OBJECT.relative_to(ROOT)),
        "pool_abi_object_sha256": sha(OBJECT),
        "imports_resolved": [PROVIDER],
        "imports_added": [],
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "linked_object": str(BOUND.relative_to(ROOT)),
        "linked_sha256": sha(BOUND),
        "whole_image_complete": False,
        "hardware_proof": False,
        "gates": ["Pinned upstream host parity does not prove stock native equivalence or full call domain.",
                  "Other Main imports, final placement and device execution remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
