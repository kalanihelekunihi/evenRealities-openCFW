from pathlib import Path
import hashlib
import json
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import UC_CPU_ARM_CORTEX_M4, UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / 'g2/components/main/diagnostic_flags_candidates_20261010/flags.c'
IMAGE = ROOT / 'g2/build/pseudocode-first/20260930T190500Z/attempts/P1-canonical-fixed-images-005/002/apollo_main-flash.bin'
stock = IMAGE.read_bytes()
assert hashlib.sha256(stock).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
body = stock[0x43d0ce - 0x438000:0x43d0d4 - 0x438000]
assert hashlib.sha256(body).hexdigest() == '67a7f1251b188a6b8e0f3c03b6f0c6141f47f1eb600a68648867c25253c712d5'
assert int.from_bytes(stock[0x43d13c - 0x438000:0x43d140 - 0x438000], 'little') == 0x20004543
gate_body = stock[0x4c9c50 - 0x438000:0x4c9c56 - 0x438000]
assert hashlib.sha256(gate_body).hexdigest() == 'ef5da08dc20aa6715047232e8b3ef13a3b0df0b5cdb3a18881f13ff05537803b'
assert int.from_bytes(stock[0x4c9cd4 - 0x438000:0x4c9cd8 - 0x438000], 'little') == 0x2007502f
obj, elf = OUT / 'flags.o', OUT / 'flags.elf'
compile_cmd = ['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb', '-std=c11', '-Oz', '-ffreestanding', '-fno-builtin', '-Wall', '-Wextra', '-Werror', '-c', str(SRC), '-o', str(obj)]
subprocess.run(compile_cmd, check=True)
subprocess.run(['arm-none-eabi-ld', '-Ttext=0x100000', '-e', 'g2_flashdb_candidate_flags', str(obj), '-o', str(elf)], check=True)
with elf.open('rb') as f:
    image = ELFFile(f)
    segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments() if s['p_type'] == 'PT_LOAD']
    entries = {s.name: s['st_value'] for s in image.get_section_by_name('.symtab').iter_symbols()}

def run(original, value, name, original_entry, ram_address):
    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x438000, (len(stock) + 4095) & ~4095)
    u.mem_write(0x438000, stock)
    u.mem_map(0x100000, 0x10000)
    for address, data in segments:
        if address >= 0x100000:
            u.mem_write(address, bytes(data))
    u.mem_map(0x20000000, 0x80000)
    u.mem_write(ram_address, bytes([value]))
    before = bytes(u.mem_read(ram_address - 3, 7))
    stop = 0x100f00
    u.reg_write(UC_ARM_REG_SP, 0x2000f000)
    u.reg_write(UC_ARM_REG_LR, stop | 1)
    u.reg_write(UC_ARM_REG_R0, 0xaabbccdd)
    u.hook_add(UC_HOOK_CODE, lambda cpu, address, size, _: cpu.emu_stop() if address == stop else None)
    u.emu_start((original_entry if original else entries[name]) | 1, stop, count=20)
    assert u.reg_read(UC_ARM_REG_PC) == stop
    assert u.reg_read(UC_ARM_REG_SP) == 0x2000f000
    assert bytes(u.mem_read(ram_address - 3, 7)) == before
    return u.reg_read(UC_ARM_REG_R0)

for name, original_entry, ram_address in [
    ('g2_flashdb_candidate_flags', 0x43d0ce, 0x20004543),
    ('g2_smp_candidate_log_flags', 0x43d0ce, 0x20004543),
    ('g2_smp_candidate_log_gate', 0x4c9c50, 0x2007502f),
]:
    for value in range(256):
        assert run(True, value, name, original_entry, ram_address) == run(False, value, name, original_entry, ram_address) == value
receipt = {
    'status': 'PASS', 'cases': 768, 'unique_original_getters': 2, 'original_body_bytes': 12,
    'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
    'elf_sha256': hashlib.sha256(elf.read_bytes()).hexdigest(),
    'compile_command': compile_cmd,
    'limits': ['Scalar Cortex-M4 Unicorn oracle; Cortex-M55 source compilation.',
               'Initial RAM state is synthetic; writer and firmware placement remain unresolved.'],
}
(OUT / 'results.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
