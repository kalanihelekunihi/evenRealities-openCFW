#!/usr/bin/env python3
"""Compare stock/C time-string lower-call frames for the Main logger."""
import hashlib
import json
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/log_time_string_44aaa8.c"
BASE = G2 / "build/c-firmware/20261016/main-log-task-context/candidate.o"
OUT = G2 / "build/c-firmware/20261016/main-log-time-string"
PAYLOAD_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
FORMAT = b"%d/%d/%d %02d:%02d:%02d %d"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uc_new():
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in ((0x100000, 0x100000), (0x300000, 0x1000),
                          (0x400000, 0x400000), (0x20000000, 0x80000)):
        uc.mem_map(address, size)
    uc.reg_write(UC_ARM_REG_SP, 0x2007f000)
    uc.reg_write(UC_ARM_REG_LR, 0x300001)
    return uc


def string(uc, address, length=64):
    return bytes(uc.mem_read(address, length)).split(b"\0", 1)[0]


def run(entry, image, cuts, date, tick):
    uc = uc_new()
    if image == "stock":
        uc.mem_write(0x438000, STOCK.read_bytes()[32:])
    else:
        for address, data in image:
            if data:
                uc.mem_write(address, data)
    trace = []

    def hook(engine, address, size, _):
        role = cuts.get(address)
        if role is None:
            return
        if role == "date":
            dest = engine.reg_read(UC_ARM_REG_R0)
            engine.mem_write(dest, b"\0" * 12 +
                             b"".join(value.to_bytes(4, "little") for value in date))
            trace.append("date")
        elif role == "tick":
            engine.reg_write(UC_ARM_REG_R0, tick)
            trace.append("tick")
        else:
            dest = engine.reg_read(UC_ARM_REG_R0)
            capacity = engine.reg_read(UC_ARM_REG_R1)
            fmt = string(engine, engine.reg_read(UC_ARM_REG_R2))
            sp = engine.reg_read(UC_ARM_REG_SP)
            args = [engine.reg_read(UC_ARM_REG_R3)]
            args += [int.from_bytes(engine.mem_read(sp + i*4, 4), "little") for i in range(6)]
            trace.append({"capacity": capacity, "format": fmt.decode(), "args": args})
            engine.mem_write(dest, b"ok\0")
            engine.reg_write(UC_ARM_REG_R0, 2)
        engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, 0x300000, count=10000)
    result = string(uc, uc.reg_read(UC_ARM_REG_R0), 3)
    return trace, result


def main():
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PAYLOAD_SHA or \
            payload[0x44ab0c-0x438000:0x44ab0c-0x438000+4] != (0x76b66c).to_bytes(4, "little") or \
            payload[0x76b66c-0x438000:0x76b66c-0x438000+len(FORMAT)] != FORMAT:
        raise RuntimeError("Main stock time format changed")
    stubs = OUT / "time-string-oracle-stubs.c"
    stubs.write_text("""#include <stdint.h>
void g2_log_datetime_now_44a19a(void *p) { (void)p; }
uint32_t g2_flashdb_candidate_tick(void) { return 0; }
int32_t g2_audio_dump_snprintf(char *p, uint32_t n, const char *f, ...) {
    (void)p; (void)n; (void)f; return 0;
}
""")
    oracle = OUT / "time-string-oracle.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mthumb", "-O2", "-nostdlib", "-ffreestanding", "-fno-builtin",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,g2_log_time_string",
                    str(SOURCE), str(stubs), "-o", str(oracle)], check=True)
    with oracle.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(seg["p_vaddr"], seg.data()) for seg in elf.iter_segments()
                    if seg["p_type"] == "PT_LOAD"]
        symbols = {sym.name: sym["st_value"] for sym in elf.get_section_by_name(".symtab").iter_symbols()}
    oldcuts = {0x44a19a: "date", 0x4490cc: "tick", 0x44b728: "format"}
    newcuts = {symbols["g2_log_datetime_now_44a19a"] & ~1: "date",
               symbols["g2_flashdb_candidate_tick"] & ~1: "tick",
               symbols["g2_audio_dump_snprintf"] & ~1: "format"}
    rows = []
    for date, tick in (((2026, 10, 16, 12, 34, 56), 1234),
                       ((1, 2, 3, 4, 5, 6), 0),
                       ((9999, 12, 31, 23, 59, 59), 0xffffffff)):
        old, result_old = run(0x44aaa8, "stock", oldcuts, date, tick)
        new, result_new = run(symbols["g2_log_time_string"], segments, newcuts, date, tick)
        if old != new or result_old != result_new or old[-1] != {
                "capacity": 28, "format": FORMAT.decode(), "args": list(date) + [tick]}:
            raise RuntimeError(f"Main time-string frame mismatch: {old!r} vs {new!r}")
        rows.append({"date": list(date), "tick": tick, "trace": old})
    candidate = OUT / "candidate.o"
    baseline_imports = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(BASE)], text=True).splitlines() if line.strip()}
    current_imports = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(candidate)], text=True).splitlines() if line.strip()}
    if (len(baseline_imports) != 132 or len(current_imports) != 132 or
            baseline_imports - current_imports != {"g2_log_time_string"} or
            current_imports - baseline_imports != {"g2_log_datetime_now_44a19a"}):
        raise RuntimeError("Main time-string import frontier changed")
    result = {"status": "PASS_BOUNDED_MAIN_LOG_TIME_STRING_C",
              "stock_payload_sha256": PAYLOAD_SHA,
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "baseline_object": str(BASE.relative_to(ROOT)), "baseline_object_sha256": sha(BASE),
              "candidate_object": str(candidate.relative_to(ROOT)), "candidate_object_sha256": sha(candidate),
              "oracle_elf": str(oracle.relative_to(ROOT)), "oracle_elf_sha256": sha(oracle),
              "oracle_stubs": str(stubs.relative_to(ROOT)), "oracle_stubs_sha256": sha(stubs),
              "cases": rows, "case_count": len(rows),
              "unresolved_before": 132, "unresolved_after": 132,
              "replaced_import": "g2_log_time_string", "new_explicit_import": "g2_log_datetime_now_44a19a",
              "source_complete": False, "flashable": False, "hardware_proof": False,
              "limits": ["The three cases compare native/C lower-call frames and return buffer, not full formatter output.",
                         "Datetime provider 0x44a19a remains an unresolved source gap.",
                         "Final time-buffer RAM placement and whole Main image remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(rows), sha(path))


if __name__ == "__main__":
    main()
