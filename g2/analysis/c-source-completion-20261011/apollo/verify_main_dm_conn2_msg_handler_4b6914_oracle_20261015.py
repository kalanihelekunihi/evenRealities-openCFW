#!/usr/bin/env python3
"""Compare compiled Cordio Conn2 message dispatch with pinned HCI calls."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / 'g2'
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_msg_handler_4b6914.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-msg-handler-4b6914'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
SHIM = '''#include <stdint.h>
__attribute__((noinline)) void *dmConnCcbById(uint8_t a){(void)a;return 0;}
__attribute__((noinline)) void audio_ble_hci_read_rssi_cmd_52b63a(uint16_t a){(void)a;}
__attribute__((noinline)) void audio_ble_hci_remote_conn_param_req_reply_52b0be(uint16_t a,uint16_t b,uint16_t c,uint16_t d,uint16_t e,uint16_t f,uint16_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;}
__attribute__((noinline)) void audio_ble_hci_remote_conn_param_req_neg_reply_52b146(uint16_t a,uint8_t b){(void)a;(void)b;}
__attribute__((noinline)) void audio_ble_hci_set_data_len_52b176(uint16_t a,uint16_t b,uint16_t c){(void)a;(void)b;(void)c;}
__attribute__((noinline)) void audio_ble_hci_write_auth_payload_timeout_52b70c(uint16_t a,uint16_t b){(void)a;(void)b;}
__attribute__((noinline)) void audio_ble_hci_request_peer_sca_52b87a(uint16_t a){(void)a;}
'''
CHILDREN = {
    'lookup': ('dmConnCcbById', 0x4b62a8, 1),
    'rssi': ('audio_ble_hci_read_rssi_cmd_52b63a', 0x52b63a, 1),
    'reply': ('audio_ble_hci_remote_conn_param_req_reply_52b0be', 0x52b0be, 7),
    'negative': ('audio_ble_hci_remote_conn_param_req_neg_reply_52b146', 0x52b146, 2),
    'data_len': ('audio_ble_hci_set_data_len_52b176', 0x52b176, 3),
    'auth_to': ('audio_ble_hci_write_auth_payload_timeout_52b70c', 0x52b70c, 2),
    'peer_sca': ('audio_ble_hci_request_peer_sca_52b87a', 0x52b87a, 1),
}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConn2MsgHandler(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('dmConnCcbById', 'HciReadRssiCmd',
                 'HciLeRemoteConnParamReqReply', 'HciLeRemoteConnParamReqNegReply',
                 'HciLeSetDataLen', 'HciWriteAuthPayloadTimeout',
                 'HciLeRequestPeerScaCmd'):
        if term not in body:
            raise RuntimeError('Cordio Conn2 message source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn2_msg_handler_4b6914',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, found, param, handle, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytearray((seed + i * 3) & 0xff for i in range(64))
            ccb[0x0c:0x0e] = handle.to_bytes(2, 'little')
            msg = bytearray((seed + i * 7) & 0xff for i in range(64))
            msg[:2] = param.to_bytes(2, 'little')
            msg[2] = event
            cpu.mem_write(0x20001000, bytes(ccb))
            cpu.mem_write(0x20002000, bytes(msg))
            addresses = {(symbols[name] & ~1) if compiled else stock: (label, argc)
                         for label, (name, stock, argc) in CHILDREN.items()}
            calls = []
            regs = (A.UC_ARM_REG_R0, A.UC_ARM_REG_R1,
                    A.UC_ARM_REG_R2, A.UC_ARM_REG_R3)
            def hook(uc, address, size, user):
                item = addresses.get(address)
                if item is None:
                    return
                label, argc = item
                args = [uc.reg_read(reg) for reg in regs]
                sp = uc.reg_read(A.UC_ARM_REG_SP)
                for i in range(max(argc - 4, 0)):
                    args.append(int.from_bytes(uc.mem_read(sp + i * 4, 4), 'little'))
                if label == 'lookup':
                    calls.append((label, args[0] & 0xff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if found else 0)
                else:
                    calls.append((label, tuple(args[:argc])))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn2_msg_handler_4b6914'] if compiled else 0x4b6914
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for event in (0, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0xff):
            for found in (False, True):
                for param, handle, seed in ((0, 0, 0), (0x1234, 0x2345, 0x55),
                                            (0xffff, 0xffff, 0xa5)):
                    stock = run(False, event, found, param, handle, seed)
                    candidate = run(True, event, found, param, handle, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{event=} {found=} {param=} {handle=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_MSG_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native six event cases, unrecognized events, HCI command call order/arguments and preserved CCB/message.',
               'limits': ['HCI command effects and CCB lookup are cut at native call boundaries; controller behavior remains open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
