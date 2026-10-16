#!/usr/bin/env python3
"""Compare tracepoint BLE decode and child dispatch with stock Main."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/tracepoint_ble_data_5ee8bc.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-tracepoint-ble-data-5ee8bc'
PINNED = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
blob = PAYLOAD.read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == PINNED
assert int.from_bytes(blob[0x5ef020-0x438000:0x5ef024-0x438000], 'little') == 0x2037b9c0
assert int.from_bytes(blob[0x5ef024-0x438000:0x5ef028-0x438000], 'little') == 0x77cd84
OUT.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as td:
    shim = Path(td) / 'shim.c'
    shim.write_text('''#include <stdint.h>
uint8_t audio_tracepoint_decode_buffer[0x206];
const uint8_t audio_tracepoint_message_descriptor[4]={0};
uint32_t audio_tracepoint_role_char_5edadc(void){return 82;}
void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_pb_stream_init(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
void audio_uart_checksum_copy(void*a,const void*b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_pb_decode(void*a,const void*b,void*c){(void)a;(void)b;(void)c;return 0;}
void audio_tracepoint_request_file_name_5ee1f8(uint8_t a){(void)a;}
void audio_tracepoint_delete_file_5ee488(uint8_t a,const void*b){(void)a;(void)b;}
void audio_tracepoint_delete_all_5ee7b4(uint8_t a){(void)a;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...)
{(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...)
{(void)a;(void)b;(void)c;return 0;}
''')
    elf = Path(td) / 'test.elf'
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-ffreestanding', '-fno-builtin', '-O2', '-nostdlib',
                    '-Wl,-Ttext=0x100000', '-Wl,-e,audio_tracepoint_handle_ble_data_5ee8bc',
                    str(SOURCE), str(shim), '-o', str(elf)], check=True)
    syms = {p[2]: int(p[0], 16) for line in subprocess.check_output(
        ['arm-none-eabi-nm', str(elf)], text=True).splitlines() if len(p := line.split()) == 3}
    with elf.open('rb') as f:
        segments = [(s['p_vaddr'], s.data()) for s in ELFFile(f).iter_segments()
                    if s['p_type'] == 'PT_LOAD']
    def run(compiled, present, length, role, log_mask, command, which, decode_ok):
        u = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        u.mem_map(0x400000, 0x400000); u.mem_write(0x438000, blob)
        u.mem_map(0x100000, 0x100000)
        for addr, data in segments: u.mem_write(addr, data)
        u.mem_map(0x20000000, 0x400000)
        data = 0x20073000 if present else 0
        u.mem_write(0x20075000, b'decode-error\0')
        buffer = syms['audio_tracepoint_decode_buffer'] if compiled else 0x2037b9c0
        hooks = ({syms['audio_tracepoint_role_char_5edadc'] & ~1: 'role',
                  syms['audio_uart_buffer_zero'] & ~1: 'zero',
                  syms['audio_uart_pb_stream_init'] & ~1: 'stream',
                  syms['audio_uart_checksum_copy'] & ~1: 'copy',
                  syms['audio_uart_pb_decode'] & ~1: 'decode',
                  syms['audio_tracepoint_request_file_name_5ee1f8'] & ~1: 'request',
                  syms['audio_tracepoint_delete_file_5ee488'] & ~1: 'delete',
                  syms['audio_tracepoint_delete_all_5ee7b4'] & ~1: 'all',
                  syms['audio_log_flags'] & ~1: 'flags',
                  syms['audio_log_extended'] & ~1: 'extended',
                  syms['compressed_log_output'] & ~1: 'compact'} if compiled else
                 {0x5edadc: 'role', 0x43c0e4: 'zero', 0x48f49c: 'stream',
                  0x439c04: 'copy', 0x490120: 'decode', 0x5ee1f8: 'request',
                  0x5ee488: 'delete', 0x5ee7b4: 'all', 0x43d0ce: 'flags',
                  0x43d574: 'extended', 0x43ce9e: 'compact'})
        calls = []
        def string(cpu, addr):
            return bytes(cpu.mem_read(addr, 256)).split(b'\0')[0].decode('ascii')
        def word(cpu, addr): return int.from_bytes(cpu.mem_read(addr, 4), 'little')
        def fmt_args(cpu, fmt, words):
            count = fmt.count('%')
            out = []
            for i in range(count):
                v = words[i]
                out.append(string(cpu, v) if '%s' in fmt and count == 1 else v)
            return tuple(out)
        def hook(cpu, pc, size, user):
            kind = hooks.get(pc)
            if kind is None: return
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                               A.UC_ARM_REG_R2, A.UC_ARM_REG_R3))
            sp = cpu.reg_read(A.UC_ARM_REG_SP)
            if kind == 'role': cpu.reg_write(A.UC_ARM_REG_R0, role)
            elif kind == 'flags': cpu.reg_write(A.UC_ARM_REG_R0, log_mask)
            elif kind == 'zero':
                calls.append(('zero', r1, r2)); cpu.mem_write(r0, b'\0'*r1)
            elif kind == 'stream':
                calls.append(('stream', r1 == data, r2))
                cpu.mem_write(r0, (0x12345679).to_bytes(4,'little')+
                              r1.to_bytes(4,'little')+r2.to_bytes(4,'little')+bytes(4))
            elif kind == 'copy':
                calls.append(('copy', r2)); cpu.mem_write(r0, bytes(cpu.mem_read(r1,r2)))
            elif kind == 'decode':
                calls.append(('decode', r2 == buffer))
                cpu.mem_write(r2, bytes((command, 0x47, which & 255, which >> 8)) + b'XYZ')
                if not decode_ok: cpu.mem_write(r0+12, (0x20075000).to_bytes(4,'little'))
                cpu.reg_write(A.UC_ARM_REG_R0, int(decode_ok))
            elif kind == 'extended':
                fmt = string(cpu, word(cpu,sp+4))
                args = [word(cpu,sp+8+4*i) for i in range(4)]
                calls.append(('extended', r0, string(cpu,r1), string(cpu,r2),
                              string(cpu,r3), word(cpu,sp), fmt,
                              fmt_args(cpu,fmt,args)))
            elif kind == 'compact':
                fmt = string(cpu,r1)
                args = [r3] + [word(cpu,sp+4*i) for i in range(3)]
                calls.append(('compact', r0, fmt, string(cpu,r2),
                              fmt_args(cpu,fmt,args)))
            elif kind == 'request': calls.append(('request',r0))
            elif kind == 'delete': calls.append(('delete',r0,r1-buffer))
            else: calls.append(('all',r0))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE, hook)
        for reg,val in ((A.UC_ARM_REG_R0,data),(A.UC_ARM_REG_R1,length),
                        (A.UC_ARM_REG_SP,0x2007f000),(A.UC_ARM_REG_LR,0x600001)):
            u.reg_write(reg,val)
        entry = syms['audio_tracepoint_handle_ble_data_5ee8bc'] if compiled else 0x5ee8bc
        u.emu_start(entry | 1,0x600000,count=30000)
        return {'return':u.reg_read(A.UC_ARM_REG_R0),'calls':calls,
                'decoded_prefix':bytes(u.mem_read(buffer,7)).hex()}
    cases=[]
    for present in (False,True):
      for length in (0,0x20):
       for role in (ord('R'),ord('L')):
        for log_mask in (0,1,2,4,7):
         for command,which,decode_ok in ((0,0,True),(1,0,True),(2,4,True),
                                         (2,3,True),(3,0,True),(9,0,True),
                                         (0,0,False)):
          native=run(False,present,length,role,log_mask,command,which,decode_ok)
          source=run(True,present,length,role,log_mask,command,which,decode_ok)
          if native!=source:
           raise AssertionError((present,length,role,log_mask,command,which,decode_ok,native,source))
          cases.append({'present':present,'length':length,'role':role,
                        'log_mask':log_mask,'command':command,'which':which,
                        'decode_ok':decode_ok,'calls':len(native['calls'])})
    receipt={'status':'PASS_BOUNDED_MAIN_TRACEPOINT_BLE_DATA_NATIVE_C',
             'cases':cases,'source':str(SOURCE.relative_to(ROOT)),
             'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             'payload_sha256':PINNED,
             'limits':['Nanopb decode and command children are compared at call boundaries; final placement and hardware are unproved.']}
    path=OUT/'oracle.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
