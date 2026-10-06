#!/usr/bin/env python3
"""Compare the private DFU runtime-context getter/wrapper with stock."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
BLOB = ROOT / "g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BLOB_BASE = 0x410000
BLOB_SHA = "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
STOP = 0x08000000
STOCK_GET = 0x42D88A
STOCK_WRAPPER = 0x42DD68
STOCK_WORD = 0x42E104
STOCK_WORD_VALUE = 0x00604000

spec = importlib.util.spec_from_file_location(
    "elf_reader", ROOT / "g2/components/bootloader/update_core/elf_reader.py")
elf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(elf)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Machine:
    def __init__(self, source=False, segments=(), symbols=None):
        self.cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.cpu.ctl_set_cpu_model(a.UC_CPU_ARM_CORTEX_M33)
        self.source = source
        self.finished = False
        self.trace = {}
        self.cpu.mem_map(0, 0x1000)
        self.cpu.mem_map(BLOB_BASE, 0x25000)
        self.cpu.mem_write(BLOB_BASE, BLOB.read_bytes())
        self.cpu.mem_map(0x10000, 0x10000)
        self.cpu.mem_map(0x20000000, 0x40000)
        self.cpu.mem_map(STOP, 0x10000)
        if source:
            for segment in segments:
                self.cpu.mem_write(segment["address"], segment["data"])
            self.symbols = symbols
        else:
            self.symbols = {}
        self.cpu.hook_add(UC_HOOK_CODE, self.code)

    def code(self, uc, pc, size, _):
        if pc == STOP:
            self.finished = True
            uc.emu_stop()
        elif not self.source:
            self.trace[pc] = bytes(uc.mem_read(pc, size))

    def run(self, operation, r7=0x13579bdf):
        self.trace = {}
        if operation == "get":
            entry = (self.symbols["opencfw_boot_dfu_runtime_context_get"]
                     if self.source else STOCK_GET)
        else:
            entry = (self.symbols["opencfw_boot_dfu_runtime_context"]
                     if self.source else STOCK_WRAPPER)
        self.cpu.reg_write(a.UC_ARM_REG_R0, 0xaaaaaaaa)
        self.cpu.reg_write(a.UC_ARM_REG_R7, r7)
        self.cpu.reg_write(a.UC_ARM_REG_SP, 0x2002f000)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.finished = False
        self.cpu.emu_start(entry | 1, STOP + 2, count=1000)
        assert self.finished, (self.source, operation,
                               hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return {"r0": self.cpu.reg_read(a.UC_ARM_REG_R0),
                "r7": self.cpu.reg_read(a.UC_ARM_REG_R7),
                "sp": self.cpu.reg_read(a.UC_ARM_REG_SP)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    image = BLOB.read_bytes()
    assert sha(image) == BLOB_SHA
    assert int.from_bytes(image[STOCK_WORD - BLOB_BASE:
                                 STOCK_WORD - BLOB_BASE + 4], "little") == STOCK_WORD_VALUE
    _, segments, symbols = elf.elf_info(args.elf)

    getter_stock = Machine().run("get")
    getter_source = Machine(True, segments, symbols).run("get")
    assert getter_stock == getter_source == {
        "r0": STOCK_WORD_VALUE, "r7": 0x13579bdf, "sp": 0x2002f000}

    wrapper_cases = []
    traces = {}
    for incoming_r7 in [0, 1, 0x13579bdf, 0xffffffff, 0x00604000]:
        stock = Machine()
        source = Machine(True, segments, symbols)
        result_stock = stock.run("wrapper", incoming_r7)
        result_source = source.run("wrapper", incoming_r7)
        assert result_stock == result_source == {
            "r0": incoming_r7, "r7": incoming_r7, "sp": 0x2002f000}, {
                "r7": hex(incoming_r7), "stock": result_stock,
                "source": result_source}
        wrapper_cases.append({"incoming_r7": hex(incoming_r7),
                              "result": result_stock})
        traces.update(stock.trace)

    used = {address + i for address, raw in traces.items()
            for i in range(len(raw))}
    stock_functions = {
        "getter": {"range": ["0x42d88a", "0x42d890"], "size": 6,
                   "sha256": "a38decb7c6c890f46354bc3a4b166bd89e4dac78108f0a6eb1e6123e61ad8087"},
        "wrapper": {"range": ["0x42dd68", "0x42dd70"], "size": 8,
                    "sha256": "86bf8be3cfef3a107d8691b1fb960ba63cc40d3ef6eb8ed906638e24001e1a84"},
    }
    for name, row in stock_functions.items():
        start = int(row["range"][0], 16) - BLOB_BASE
        body = image[start:start + row["size"]]
        assert sha(body) == row["sha256"]
    result = {
        "status": "PASS",
        "getter_direct_cases": 1,
        "wrapper_cases": len(wrapper_cases),
        "original_instruction_bytes_reached": len(used),
        "original_image_sha256": BLOB_SHA,
        "source_elf_sha256": sha(args.elf.read_bytes()),
        "source_sha256": {
            "runtime_context.c": sha((ROOT / "g2/components/bootloader/dfu_task/runtime_context.c").read_bytes()),
            "runtime_context.h": sha((ROOT / "g2/components/bootloader/dfu_task/runtime_context.h").read_bytes()),
        },
        "stock_word": {"address": hex(STOCK_WORD),
                       "value": hex(STOCK_WORD_VALUE),
                       "bytes": "00406000"},
        "stock_functions": stock_functions,
        "wrapper_cases": wrapper_cases,
        "trace": {hex(pc): raw.hex() for pc, raw in sorted(traces.items())},
        "limits": [
            "The helper returns the literal word at 0x42e104; the wrapper discards it and returns the incoming R7 value in R0.",
            "The orchestrator call at 0x42dd1e ignores the wrapper return. No state write, queue action, or runtime initialization occurs in this closure.",
            "Only the getter/wrapper call closure is compared; scheduler, queue creation, publication, and hardware services are outside this fixture.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in (
        "status", "getter_direct_cases", "wrapper_cases",
        "original_instruction_bytes_reached")}))


if __name__ == "__main__":
    main()
