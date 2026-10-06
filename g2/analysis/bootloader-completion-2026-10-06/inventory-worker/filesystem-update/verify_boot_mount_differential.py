#!/usr/bin/env python3
"""Compare stock 0x421210 with ARM-compiled boot_mount.c on synthetic NOR."""
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path
from unicorn import arm_const as a

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
COMP = ROOT / "g2/components/bootloader/filesystem"
BUILD = ROOT / "g2/build/bootloader-completion/filesystem"
NOR = 0x01400000
NOR_SIZE = 3008 * 4096
STOP = 0x08000000
SP = 0x2003F000

spec = importlib.util.spec_from_file_location("verify_arm", COMP / "verify_arm.py")
armfs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(armfs)
v = armfs.v


def build_elf(out):
    flags = ["--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
             "-mfloat-abi=soft", "-ffreestanding", "-fno-builtin", "-std=c11",
             "-O2", "-fwrapv", "-Wall", "-Wextra", "-Werror", "-I" + str(COMP),
             "-I" + str(COMP / "freestanding_include"), "-DLFS_NO_DEBUG",
             "-DLFS_NO_WARN", "-DLFS_NO_ERROR", "-DLFS_NO_ASSERT",
             "-DLFS_NO_INTRINSICS", "-DLFS_DEFINES=boot_lfs_defines.h"]
    with tempfile.TemporaryDirectory(prefix="boot-mount-diff-") as td:
        temp = Path(td)
        objects = []
        for src in ["filesystem.c", "boot_mount.c", "runtime_memory.c",
                    "upstream/lfs.c", "upstream/lfs_util.c"]:
            obj = temp / (src.replace("/", "_").replace(".c", ".o"))
            subprocess.run(["clang", *flags, "-c", str(COMP / src), "-o", str(obj)], check=True)
            objects.append(str(obj))
        linker = temp / "module.ld"
        linker.write_text("""ENTRY(opencfw_provider_421210)
SECTIONS { . = 0x00010000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
opencfw_boot_nor_read = 0x420f71;
opencfw_boot_nor_prog = 0x420b0d;
opencfw_boot_nor_erase = 0x420a09;
opencfw_boot_fs_error = 0x415faf;
opencfw_boot_fs_alloc = 0x41552d;
opencfw_boot_fs_free = 0x415559;
""")
        subprocess.run(["arm-none-eabi-ld", "-T", str(linker), "-o", str(out), *objects], check=True)


class BootMachine(v.Machine):
    def __init__(self, nor_image, source=False, segments=(), symbols=None,
                 fail_program_at=None):
        super().__init__(source, segments, symbols)
        self.cpu.mem_map(NOR, NOR_SIZE)
        self.cpu.mem_write(NOR, nor_image)
        self.cpu.mem_map(0x21000000, 0x200000)
        self.heap = 0x21000000
        self.programs = self.erases = self.reads = 0
        self.log_calls = self.error_adapter_calls = 0
        self.logger_program_counts = []
        self.fail_program_at = fail_program_at

    def code(self, uc, pc, size, user):
        if pc == 0x41552c:
            n = (self.args()[0] + 7) & ~7
            address = self.heap
            self.heap += n
            assert self.heap <= 0x21200000
            self.cpu.mem_write(address, b"\0" * n)
            self.ret(address)
            return
        if pc == 0x415558:
            self.ret()
            return
        if pc == 0x415fae:
            self.error_adapter_calls += 1
            self.logger_program_counts.append(self.programs)
            self.ret()
            return
        if pc == 0x420f70:
            address, out, n, _ = self.args()
            assert NOR <= address <= address + n <= NOR + NOR_SIZE
            self.cpu.mem_write(out, bytes(self.cpu.mem_read(address, n)))
            self.reads += 1
            self.ret()
            return
        if pc == 0x420b0c:
            address, src, n, _ = self.args()
            assert NOR <= address <= address + n <= NOR + NOR_SIZE
            self.programs += 1
            if self.fail_program_at == self.programs:
                self.ret(1)
                return
            old = bytes(self.cpu.mem_read(address, n))
            new = bytes(self.cpu.mem_read(src, n))
            assert all((before & after) == after for before, after in zip(old, new))
            self.cpu.mem_write(address, new)
            self.ret()
            return
        if pc == 0x420a08:
            address = self.args()[0]
            assert NOR <= address <= address + 4096 <= NOR + NOR_SIZE
            assert address % 4096 == 0
            self.cpu.mem_write(address, b"\xff" * 4096)
            self.erases += 1
            self.ret()
            return
        if pc == 0x4176ce:
            self.log_calls += 1
            self.logger_program_counts.append(self.programs)
            self.ret()
            return
        super().code(uc, pc, size, user)

    def call_initializer(self, source=False):
        self.finished = False
        self.events = []
        for reg in (a.UC_ARM_REG_R0, a.UC_ARM_REG_R1, a.UC_ARM_REG_R2, a.UC_ARM_REG_R3):
            self.cpu.reg_write(reg, 0)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        entry = (self.symbols["opencfw_provider_421210"] & ~1) if source else 0x421210
        self.cpu.emu_start(entry | 1, STOP + 2, count=20000000)
        assert self.finished, (source, hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return self.cpu.reg_read(a.UC_ARM_REG_R0)

    def call_symbol(self, name, args):
        self.finished = False
        for reg, value in zip((a.UC_ARM_REG_R0, a.UC_ARM_REG_R1,
                               a.UC_ARM_REG_R2, a.UC_ARM_REG_R3), args + [0] * 4):
            self.cpu.reg_write(reg, value)
        self.cpu.reg_write(a.UC_ARM_REG_SP, SP)
        self.cpu.reg_write(a.UC_ARM_REG_LR, STOP | 1)
        self.cpu.emu_start((self.symbols[name] & ~1) | 1, STOP + 2, count=20000000)
        assert self.finished, (name, hex(self.cpu.reg_read(a.UC_ARM_REG_PC)))
        return self.cpu.reg_read(a.UC_ARM_REG_R0)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    elf_path = BUILD / "boot-mount-differential.elf"
    build_elf(elf_path)
    _, segments, symbols = v.elf.elf_info(elf_path)
    blank = b"\xff" * NOR_SIZE
    original = BootMachine(blank)
    source = BootMachine(blank, True, segments, symbols)
    outputs = []
    for run in range(2):
        original_return = original.call_initializer(False)
        source_return = source.call_initializer(True)
        assert original_return == source_return == 0, (run, original_return, source_return)
        assert original.u(0x2002711c) == source.u(0x2002711c) == 1
        original_image = bytes(original.cpu.mem_read(NOR, NOR_SIZE))
        source_image = bytes(source.cpu.mem_read(NOR, NOR_SIZE))
        assert original_image == source_image, ("NOR mismatch", run)
        outputs.append({
            "run": run + 1, "return": original_return,
            "ready": original.u(0x2002711c),
            "nor_sha256": hashlib.sha256(original_image).hexdigest(),
            "boot_count_object_sha256": hashlib.sha256(bytes(original.cpu.mem_read(0x20026c0c, 96))).hexdigest(),
            "original_nor_reads_programs_erases": [original.reads, original.programs, original.erases],
            "source_nor_reads_programs_erases": [source.reads, source.programs, source.erases],
            "original_logger_calls": original.log_calls,
            "source_logger_adapter_calls": source.error_adapter_calls,
            "original_logger_program_counts": original.logger_program_counts,
            "source_logger_program_counts": source.logger_program_counts,
        })

    # Existing regular file at /firmware makes stock lfs_dir_open fail with a
    # non-ENOENT status. This exercises directory-error logging and 0x4211b0
    # unmount/format/remount recovery on both instruction/source machines.
    seed = BootMachine(blank, True, segments, symbols)
    cfg = symbols["opencfw_boot_lfs_config"]
    fs_addr, file_addr, path_addr, data_addr = 0x20026878, 0x20006000, 0x20008000, 0x20009000
    assert seed.call_symbol("lfs_format", [fs_addr, cfg]) == 0
    assert seed.call_symbol("lfs_mount", [fs_addr, cfg]) == 0
    seed.cpu.mem_write(path_addr, b"firmware\0")
    seed.cpu.mem_write(data_addr, b"x")
    assert seed.call_symbol("lfs_file_open", [fs_addr, file_addr, path_addr, 0x502]) == 0
    assert seed.call_symbol("lfs_file_write", [fs_addr, file_addr, data_addr, 1]) == 1
    assert seed.call_symbol("lfs_file_close", [fs_addr, file_addr]) == 0
    assert seed.call_symbol("lfs_unmount", [fs_addr]) == 0
    conflict_image = bytes(seed.cpu.mem_read(NOR, NOR_SIZE))
    conflict_original = BootMachine(conflict_image)
    conflict_source = BootMachine(conflict_image, True, segments, symbols)
    conflict_original_return = conflict_original.call_initializer(False)
    conflict_source_return = conflict_source.call_initializer(True)
    conflict_original_nor = bytes(conflict_original.cpu.mem_read(NOR, NOR_SIZE))
    conflict_source_nor = bytes(conflict_source.cpu.mem_read(NOR, NOR_SIZE))
    assert conflict_original_return == conflict_source_return == 0
    assert conflict_original.u(0x2002711c) == conflict_source.u(0x2002711c) == 1
    assert conflict_original_nor == conflict_source_nor
    outputs.append({
        "scenario": "existing regular file at /firmware triggers 4211b0 recovery",
        "return": conflict_original_return, "ready": conflict_original.u(0x2002711c),
        "nor_sha256": hashlib.sha256(conflict_original_nor).hexdigest(),
        "original_logger_calls": conflict_original.log_calls,
        "source_logger_adapter_calls": conflict_source.error_adapter_calls,
    })

    # Start with a valid, mounted-on-disk empty littlefs and fail the first
    # program request. Stock mkdir failure only logs and continues; it does
    # not enter the non-ENOENT directory-open recovery branch.
    seed_empty = BootMachine(blank, True, segments, symbols)
    assert seed_empty.call_symbol("lfs_format", [fs_addr, cfg]) == 0
    assert seed_empty.call_symbol("lfs_mount", [fs_addr, cfg]) == 0
    assert seed_empty.call_symbol("lfs_unmount", [fs_addr]) == 0
    empty_image = bytes(seed_empty.cpu.mem_read(NOR, NOR_SIZE))
    failed_original = BootMachine(empty_image, fail_program_at=1)
    failed_source = BootMachine(empty_image, True, segments, symbols, fail_program_at=1)
    failed_original_return = failed_original.call_initializer(False)
    failed_source_return = failed_source.call_initializer(True)
    failed_original_nor = bytes(failed_original.cpu.mem_read(NOR, NOR_SIZE))
    failed_source_nor = bytes(failed_source.cpu.mem_read(NOR, NOR_SIZE))
    assert failed_original_return == failed_source_return == 0
    assert failed_original.u(0x2002711c) == failed_source.u(0x2002711c) == 1
    assert failed_original_nor == failed_source_nor
    outputs.append({
        "scenario": "first mkdir program provider fails once; helper logs and continues",
        "return": failed_original_return, "ready": failed_original.u(0x2002711c),
        "nor_sha256": hashlib.sha256(failed_original_nor).hexdigest(),
        "original_logger_calls": failed_original.log_calls,
        "source_logger_adapter_calls": failed_source.error_adapter_calls,
        "original_program_attempts": failed_original.programs,
        "source_program_attempts": failed_source.programs,
    })
    result = {
        "status": "PASS", "cases": len(outputs),
        "locked_image_sha256": v.SHA,
        "source_elf_sha256": v.sha(elf_path),
        "stock_function_sha256": "07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8",
        "source_sha256": {name: v.sha(COMP / name) for name in ["boot_mount.c", "boot_mount.h", "filesystem.c", "upstream/lfs.c", "upstream/lfs_util.c"]},
        "runs": outputs,
        "limits": [
            "Original instructions and ARM-compiled candidate execute against separate but byte-identical synthetic NOR models; callbacks directly model low-level read/program/erase.",
            "The comparison covers blank-media format/mount, directory open/create/close, a non-ENOENT directory error with 0x4211b0 recovery, one synthetic mkdir program failure that logs and continues, static boot_count read/seek/write/close, ready flag, and final NOR bytes. Logger payload/ABI is intercepted and not compared.",
            "No physical filesystem image/device, hardware, or flash was used. This does not establish exact toolchain/object identity or bootability."
        ]
    }
    out = HERE / "boot-mount-differential.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "runs": outputs}, indent=2))


if __name__ == "__main__":
    main()
