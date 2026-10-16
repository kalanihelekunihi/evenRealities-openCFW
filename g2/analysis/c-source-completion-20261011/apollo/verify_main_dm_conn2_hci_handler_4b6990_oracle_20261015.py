#!/usr/bin/env python3
"""Compare Cordio secondary HCI routing with pinned Apollo native calls."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_hci_handler_4b6990.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-hci-handler-4b6990'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CHILDREN = {
    'lookup': ('audio_ble_dm_conn_ccb_by_handle_4b601c', 0x4b601c),
    'rssi': ('audio_ble_dm_conn2_act_rssi_read_4b6a38', 0x4b6a38),
    'param': ('audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e', 0x4b6a6e),
    'data': ('audio_ble_dm_conn2_act_data_len_change_4b6ab8', 0x4b6ab8),
    'auth_cmpl': ('audio_ble_dm_conn2_act_write_auth_to_cmpl_4b6afa', 0x4b6afa),
    'auth_expired': ('audio_ble_dm_conn2_act_auth_to_expired_4b6b28', 0x4b6b28),
    'features': ('audio_ble_dm_conn2_act_read_remote_features_cmpl_4b6b50', 0x4b6b50),
    'version': ('audio_ble_dm_conn2_act_read_remote_ver_info_cmpl_4b6bac', 0x4b6bac),
    'sca': ('audio_ble_dm_conn2_act_req_peer_sca_4b6bee', 0x4b6bee),
}
SHIM = '#include <stdint.h>\n'
for label, (name, _) in CHILDREN.items():
    if label == 'lookup':
        SHIM += f'__attribute__((noinline)) void *{name}(uint16_t a){{(void)a;return 0;}}\n'
    else:
        SHIM += f'__attribute__((noinline)) void {name}(void*a,void*b){{(void)a;(void)b;}}\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    start = upstream.index('void dmConn2HciHandler(')
    body = upstream[start:upstream.index('\n}', start)]
    for term in ('dmConnCcbByHandle', 'dmConn2ActRssiRead',
                 'dmConn2ActRemoteConnParamReq', 'dmConn2ActDataLenChange',
                 'dmConn2ActWriteAuthToCmpl', 'dmConn2ActAuthToExpired',
                 'dmConn2ActReadRemoteFeaturesCmpl',
                 'dmConn2ActReadRemoteVerInfoCmpl', 'dmConn2ActReqPeerSca'):
        if term not in body:
            raise RuntimeError('Cordio secondary HCI handler source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn2_hci_handler_4b6990',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, event, found, handle, seed):
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x100000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x10000)
            ccb = bytes((seed + i * 3) & 0xff for i in range(64))
            msg = bytearray((seed + i * 7) & 0xff for i in range(64))
            msg[:2] = handle.to_bytes(2, 'little')
            msg[2] = event
            cpu.mem_write(0x20001000, ccb)
            cpu.mem_write(0x20002000, bytes(msg))
            addresses = {(symbols[name] & ~1) if compiled else stock: label
                         for label, (name, stock) in CHILDREN.items()}
            calls = []
            def hook(uc, address, size, user):
                label = addresses.get(address)
                if label is None: return
                a = uc.reg_read(A.UC_ARM_REG_R0)
                b = uc.reg_read(A.UC_ARM_REG_R1)
                if label == 'lookup':
                    calls.append((label, a & 0xffff))
                    uc.reg_write(A.UC_ARM_REG_R0, 0x20001000 if found else 0)
                else:
                    calls.append((label, a, b))
                uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20002000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x2000ff00)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols['audio_ble_dm_conn2_hci_handler_4b6990'] if compiled else 0x4b6990
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20001000, 64)), bytes(cpu.mem_read(0x20002000, 64))

        cases = 0
        for event in (0, 7, 10, 11, 0x23, 0x24, 0x27, 0x28, 0x47, 0xff):
            for found in (False, True):
                for handle, seed in ((0, 0), (0x1234, 0x55), (0xffff, 0xa5)):
                    stock = run(False, event, found, handle, seed)
                    candidate = run(True, event, found, handle, seed)
                    if stock != candidate:
                        raise RuntimeError(f'{event=} {found=} {handle=} {seed=}: {stock} != {candidate}')
                    cases += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_HCI_HANDLER_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': cases,
               'comparison_scope': 'Native eight event cases, unrecognized events, CCB lookup and action-call order/arguments.',
               'limits': ['Eight action effects and CCB lookup are cut at native call boundaries; controller behavior remains open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], cases)

if __name__ == '__main__': main()
