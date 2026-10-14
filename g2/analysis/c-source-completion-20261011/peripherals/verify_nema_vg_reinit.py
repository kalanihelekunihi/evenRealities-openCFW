#!/usr/bin/env python3
"""Compare authenticated native and C VG reinit child-call traces."""
from pathlib import Path
import hashlib, json, struct, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_nema_vg_reinit.c'
blob = OTA.read_bytes()
ota_hash = hashlib.sha256(blob).hexdigest()
assert ota_hash == '36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
raw = blob[0x20:]
records = [raw[address-0x438000:address-0x438000+8]
           for address in (0x5225d4, 0x5225dc, 0x5225e4, 0x5225ec, 0x5225f4)]
assert struct.unpack_from('<I', raw, 0x522568-0x438000)[0] == 0x20074f08

with tempfile.TemporaryDirectory() as temporary:
    shim = Path(temporary) / 'children.c'
    shim.write_text('''#include <stdint.h>
__attribute__((noinline)) void audio_uart_nema_instruction_upload_522920(const uint32_t *p,uint32_t a,uint32_t b){(void)p;(void)a;(void)b;}
__attribute__((noinline)) void audio_uart_nema_child_514846(uint32_t a,uint32_t b){(void)a;(void)b;}
__attribute__((noinline)) void *audio_uart_nema_vg_framebuffer_get_51562e(void){return (void *)0x12345678u;}
''')
    elf_path = Path(temporary) / 'vg.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_uart_nema_vg_reinit_5224b6',
                    str(SOURCE), str(shim), '-o', str(elf_path)], check=True)
    symbols = {parts[2]: int(parts[0], 16)
               for line in subprocess.check_output(['arm-none-eabi-nm', str(elf_path)], text=True).splitlines()
               if len(parts := line.split()) == 3}
    with elf_path.open('rb') as stream:
        segments = [(seg['p_vaddr'], seg.data()) for seg in ELFFile(stream).iter_segments()
                    if seg['p_type'] == 'PT_LOAD']

    def run(candidate):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        uc.ctl_set_cpu_model(A.UC_CPU_ARM_CORTEX_M4)
        uc.mem_map(0x20000000, 0x80000)
        if candidate:
            uc.mem_map(0x100000, 0x200000)
            for address, data in segments:
                uc.mem_write(address, data)
            call_addresses = {
                symbols['audio_uart_nema_instruction_upload_522920'] & ~1: 'record',
                symbols['audio_uart_nema_child_514846'] & ~1: 'mode',
                symbols['audio_uart_nema_vg_framebuffer_get_51562e'] & ~1: 'context',
            }
            entry = symbols['audio_uart_nema_vg_reinit_5224b6'] | 1
            output_cell = symbols['audio_uart_nema_vg_framebuffer_context_cell_20074f08']
        else:
            uc.mem_map(0x438000, (len(raw)+4095) & ~4095)
            uc.mem_write(0x438000, raw)
            call_addresses = {0x522920: 'record', 0x514846: 'mode', 0x51562e: 'context'}
            entry = 0x5224b7
            output_cell = 0x20074f08
        uc.reg_write(A.UC_ARM_REG_SP, 0x2007f000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        trace = []
        def hook(cpu, pc, size, user):
            kind = call_addresses.get(pc)
            if kind is None:
                return
            a = cpu.reg_read(A.UC_ARM_REG_R0)
            b = cpu.reg_read(A.UC_ARM_REG_R1)
            if kind == 'record':
                trace.append((kind, bytes(cpu.mem_read(a, 8)).hex(), b,
                              cpu.reg_read(A.UC_ARM_REG_R2)))
            elif kind == 'mode':
                trace.append((kind, a, b))
            else:
                trace.append((kind,))
            cpu.reg_write(A.UC_ARM_REG_R0, 0x12345678 if kind == 'context' else 0)
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        uc.hook_add(UC_HOOK_CODE, hook)
        uc.emu_start(entry, 0x600000, count=2000)
        stored = struct.unpack('<I', uc.mem_read(output_cell, 4))[0]
        return trace, stored

    native, candidate = run(False), run(True)
    expected = [('record', records[0].hex(), 1, 0x16),
                ('record', records[1].hex(), 1, 0x17),
                ('mode', 0x388, 1),
                ('record', records[2].hex(), 1, 0x15),
                ('record', records[3].hex(), 1, 0x14),
                ('record', records[4].hex(), 1, 0x13), ('context',)]
    assert native == candidate == (expected, 0x12345678), (native, candidate)

result = {'status': 'PASS_NEMA_VG_REINIT_CONNECTED_BOUNDED',
          'ota_sha256': ota_hash,
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'native_call_trace': expected,
          'stored_context': '0x12345678',
          'limits': 'Outer call order, record bytes and store match with child calls intercepted; child behavior, final placement, boot and hardware remain unproven.'}
(OUT / 'nema-vg-reinit-results.json').write_text(json.dumps(result, indent=2) + '\n')
print(result['status'], len(expected))
