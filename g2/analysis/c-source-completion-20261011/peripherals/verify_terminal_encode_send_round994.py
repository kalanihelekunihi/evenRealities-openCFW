#!/usr/bin/env python3
"""Native/C terminal encode/send control-flow and staging parity."""
from pathlib import Path
import hashlib, json, subprocess, tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/terminal-encode-send-round994'
out.mkdir(parents=True, exist_ok=True)
src = root / 'components/audio/uart_thread_source_candidate/terminal_encode_send_5ce7c4.c'
base = root / 'build/c-firmware/terminal-status-reply-round993/apollo-main-terminal-status-reply.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
obj = out / 'terminal_encode_send.o'; linked = out / 'apollo-main-terminal-encode-send.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-fshort-enums', '-fno-builtin', '-O2', '-Wall', '-Wextra', '-Werror',
                '-c', str(src), '-o', str(obj)], check=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('#include <stdint.h>\nconst uint8_t audio_terminal_tx_pb_descriptor[8]={0};\n'
                    'void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}\n'
                    'void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}\n'
                    'void audio_pb_ostream_from_buffer(void*a,void*b,uint32_t c){(void)a;(void)b;(void)c;}\n'
                    'uint32_t audio_pb_encode(void*a,const void*b,const void*c){(void)a;(void)b;(void)c;return 0;}\n'
                    'uint8_t audio_uart_device_role_get(void){return 0;}\n'
                    'uint32_t audio_settings_notify_ble(uint32_t a,uint32_t b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n'
                    'uint32_t audio_ring_pb_tx_ble_475b14(uint32_t a,uint32_t b,const void*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}\n'
                    'uint32_t audio_log_flags(void){return 0;}\n'
                    'void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}\n'
                    'uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}\n')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                    '-Wl,-e,audio_terminal_send_message_5ce7c4', str(src), str(shim),
                    '-o', str(elf)], check=True)
    with elf.open('rb') as f:
        e = ELFFile(f)
        segs = [(s['p_vaddr'], s.data()) for s in e.iter_segments() if s['p_type'] == 'PT_LOAD']
        syms = {s.name: s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
    cases = 0
    for tag in (9, 10, 11, 12, 13, 18, 19, 20, 22, 24, 25, 8, 26):
        for encode_ok in (False, True):
            for notify in (0, 1):
                for role in (1, 2):
                    pair = []
                    for compiled in (False, True):
                        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
                        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
                        u.mem_map(0x100000, 0x100000)
                        for addr, data in segs: u.mem_write(addr, data)
                        u.mem_map(0x20000000, 0x400000)
                        stage = syms['audio_terminal_tx_staging'] if compiled else 0x200f9694
                        encoded = syms['audio_terminal_tx_encoded'] if compiled else 0x20374378
                        payload = 0x2001f000; u.mem_write(payload, bytes(range(1, 17)))
                        trace = []
                        native = {'zero': 0x43c0e4, 'copy': 0x439c04,
                                  'ostream': 0x4905f4, 'encode': 0x490c32,
                                  'role': 0x45a568, 'notify': 0x475c1a,
                                  'tx': 0x475b14, 'flags': 0x43d0ce,
                                  'extended': 0x43d574, 'compact': 0x43ce9e}
                        names = {'zero': 'audio_uart_buffer_zero', 'copy': 'audio_uart_checksum_copy',
                                 'ostream': 'audio_pb_ostream_from_buffer', 'encode': 'audio_pb_encode',
                                 'role': 'audio_uart_device_role_get', 'notify': 'audio_settings_notify_ble',
                                 'tx': 'audio_ring_pb_tx_ble_475b14', 'flags': 'audio_log_flags',
                                 'extended': 'audio_log_extended', 'compact': 'compressed_log_output'}
                        for kind, address in native.items():
                            addr = syms[names[kind]] if compiled else address
                            def hook(cpu, at, size, user, kind=kind):
                                r0 = cpu.reg_read(A.UC_ARM_REG_R0)
                                r1 = cpu.reg_read(A.UC_ARM_REG_R1)
                                r2 = cpu.reg_read(A.UC_ARM_REG_R2)
                                r3 = cpu.reg_read(A.UC_ARM_REG_R3)
                                if kind == 'zero': cpu.mem_write(r0, b'\0' * r1)
                                elif kind == 'copy': cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
                                elif kind == 'ostream':
                                    cpu.mem_write(r0, (0).to_bytes(4,'little') + r1.to_bytes(4,'little') +
                                                  r2.to_bytes(4,'little') + b'\0'*8)
                                elif kind == 'encode':
                                    trace.append(('encode', bytes(cpu.mem_read(r2, 16))))
                                    cpu.mem_write(r0+12, (19).to_bytes(4,'little'))
                                    cpu.reg_write(A.UC_ARM_REG_R0, 1 if encode_ok else 0)
                                elif kind == 'role': cpu.reg_write(A.UC_ARM_REG_R0, role)
                                elif kind in ('notify','tx'):
                                    trace.append((kind,r0,r1,r3,bytes(cpu.mem_read(r2,4))))
                                    cpu.reg_write(A.UC_ARM_REG_R0,0)
                                elif kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0,0)
                                cpu.reg_write(A.UC_ARM_REG_PC,cpu.reg_read(A.UC_ARM_REG_LR))
                            u.hook_add(UC_HOOK_CODE, hook, begin=addr & ~1, end=addr & ~1)
                        u.reg_write(A.UC_ARM_REG_SP,0x203ff000)
                        u.mem_write(0x203ff000,(notify).to_bytes(4,'little'))
                        u.reg_write(A.UC_ARM_REG_LR,0x600001)
                        u.reg_write(A.UC_ARM_REG_R0,0xa1)
                        u.reg_write(A.UC_ARM_REG_R1,tag)
                        u.reg_write(A.UC_ARM_REG_R2,payload)
                        u.reg_write(A.UC_ARM_REG_R3,0x73)
                        u.emu_start((syms['audio_terminal_send_message_5ce7c4'] if compiled else 0x5ce7c4)|1,
                                    0x600000,count=3000)
                        pair.append((u.reg_read(A.UC_ARM_REG_R0),
                                     bytes(u.mem_read(stage,16)),trace))
                    assert pair[0]==pair[1],(tag,encode_ok,notify,role,pair)
                    cases += 1
subprocess.run(['arm-none-eabi-ld','-r',str(base),str(obj),'-o',str(linked)],check=True)
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm','-u',str(path)],text=True).splitlines()}
before,after=imports(base),imports(linked)
assert before-after=={'audio_terminal_send_message_5ce7c4'}
assert after-before=={'audio_terminal_tx_pb_descriptor'}
receipt={'round':994,'status':'PASS_TERMINAL_ENCODE_SEND_BOUNDED',
         'component':'Apollo terminal encode/send 0x5ce7c4',
         'source':str(src.relative_to(root)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
         'official_image_sha256':hashlib.sha256(blob).hexdigest(),'cases':cases,
         'validation':'M55 strict compile; native/C tag staging, encoder outcome, BLE dispatch and return with log flags zero',
         'linked_object':str(linked.relative_to(root)),
         'linked_sha256':hashlib.sha256(linked.read_bytes()).hexdigest(),
         'unresolved_before':len(before),'unresolved_after':len(after),
         'whole_image_complete':False,'hardware_proof':False,
         'gates':['Native ROM nanopb descriptor 0x77c634 needs source-owned extraction and placement',
                  'Enabled logging payloads and full image/hardware remain open']}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'],cases,len(before),len(after),receipt['linked_sha256'])
