#!/usr/bin/env python3
"""Compare native and compiled terminal status reply call/return contracts."""
from pathlib import Path
import hashlib, json, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/terminal-status-reply-round993'
out.mkdir(parents=True, exist_ok=True)
src = root / 'components/audio/uart_thread_source_candidate/terminal_status_reply.c'
base = root / 'build/c-firmware/terminal-running-apps-round992/apollo-main-terminal-running-apps.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj = out / 'terminal_status_reply.o'
linked = out / 'apollo-main-terminal-status-reply.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-fshort-enums', '-fno-builtin', '-O2', '-Wall', '-Wextra', '-Werror',
                '-c', str(src), '-o', str(obj)], check=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('#include <stdint.h>\nuint32_t audio_log_flags(void){return 0;}\n'
                    'void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n'
                    'uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n'
                    'uint32_t audio_terminal_send_message_5ce7c4(uint32_t a,uint32_t b,const void*c,uint32_t d,uint32_t e){(void)a;(void)b;(void)c;(void)d;(void)e;return 0;}\n')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_terminal_send_status_reply', str(src), str(shim),
                    '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        syms = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    cases = 0
    for present in (False, True):
        for sequence in (0, 1, 254, 255):
            for flags in (0, 1, 2, 4, 7):
                pair = []
                for compiled in (False, True):
                    u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                    u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
                    u.mem_map(0x100000, 0x100000)
                    for addr, data in segs: u.mem_write(addr, data)
                    u.mem_map(0x20000000, 0x200000)
                    seq_addr = syms['audio_terminal_message_sequence'] if compiled else 0x20074fff
                    u.mem_write(seq_addr, bytes([sequence]))
                    reply = 0x2001f000
                    u.mem_write(reply, b'\x52\x03')
                    trace = []
                    hooks = {'flags': syms['audio_log_flags'] if compiled else 0x43d0ce,
                             'extended': syms['audio_log_extended'] if compiled else 0x43d574,
                             'compact': syms['compressed_log_output'] if compiled else 0x43ce9e,
                             'send': syms['audio_terminal_send_message_5ce7c4'] if compiled else 0x5ce7c4}
                    for kind, address in hooks.items():
                        def hook(cpu, at, size, user, kind=kind):
                            if kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0, flags)
                            elif kind == 'send':
                                sp = cpu.reg_read(A.UC_ARM_REG_SP)
                                fifth = int.from_bytes(cpu.mem_read(sp, 4), 'little')
                                trace.append((kind, cpu.reg_read(A.UC_ARM_REG_R0),
                                              cpu.reg_read(A.UC_ARM_REG_R1),
                                              bytes(cpu.mem_read(cpu.reg_read(A.UC_ARM_REG_R2), 2)),
                                              cpu.reg_read(A.UC_ARM_REG_R3), fifth))
                                cpu.reg_write(A.UC_ARM_REG_R0, 0x1234)
                            else: trace.append((kind, cpu.reg_read(A.UC_ARM_REG_R0)))
                            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
                        u.hook_add(UC_HOOK_CODE, hook, begin=address & ~1, end=address & ~1)
                    u.reg_write(A.UC_ARM_REG_R0, reply if present else 0)
                    u.reg_write(A.UC_ARM_REG_SP, 0x201ff000)
                    u.reg_write(A.UC_ARM_REG_LR, 0x600001)
                    u.emu_start((syms['audio_terminal_send_status_reply'] if compiled else 0x5ceba2) | 1,
                                0x600000, count=1000)
                    pair.append((u.reg_read(A.UC_ARM_REG_R0), trace,
                                 bytes(u.mem_read(seq_addr, 1))))
                assert pair[0] == pair[1], (present, sequence, flags, pair)
                cases += 1
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}
before, after = imports(base), imports(linked)
assert before - after == {'audio_terminal_send_status_reply'} and not after - before
receipt = {'round': 993, 'status': 'PASS_TERMINAL_STATUS_REPLY',
           'component': 'Apollo terminal status reply 0x5ceba2',
           'source': str(src.relative_to(root)),
           'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
           'official_image_sha256': hashlib.sha256(blob).hexdigest(),
           'cases': cases,
           'validation': 'M55 strict compile; native/C return, send arguments, log call classes, and sequence state',
           'linked_object': str(linked.relative_to(root)),
           'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
           'unresolved_before': len(before), 'unresolved_after': len(after),
           'whole_image_complete': False, 'hardware_proof': False,
           'gates': ['Logger string payload parity and terminal send child 0x5ce7c4 remain open',
                     'Full image layout and hardware proof remain open']}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], cases, len(before), len(after), receipt['linked_sha256'])
