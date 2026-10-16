#!/usr/bin/env python3
"""Compare defined callback fields of two Cordio secondary HCI actions."""
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
SOURCE = G2 / 'components/audio/uart_thread_source_candidate/display_ble_dm_conn2_actions_rssi_param_4b6a38.c'
UPSTREAM = ROOT / 'third-party/upstream/cordio/ble-host/sources/stack/dm/dm_conn.c'
PAYLOAD = G2 / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OUT = G2 / 'build/c-firmware/20261015/main-dm-conn2-actions-rssi-param-4b6a38'
PINNED_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
CASES = {
    'rssi': ('audio_ble_dm_conn2_act_rssi_read_4b6a38', 0x4b6a38,
             (0, 1, 2, 3, 4, 6, 7, 8)),
    'param': ('audio_ble_dm_conn2_act_remote_conn_param_req_4b6a6e', 0x4b6a6e,
              tuple(range(14))),
}
SHIM = 'unsigned char audio_dm_connection_records[0x100];\n'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PINNED_SHA:
        raise RuntimeError('Apollo payload changed')
    upstream = UPSTREAM.read_text()
    for name in ('dmConn2ActRssiRead', 'dmConn2ActRemoteConnParamReq'):
        if name not in upstream:
            raise RuntimeError('Cordio action source changed')
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        shim, elf = Path(td) / 'shim.c', Path(td) / 'oracle.elf'
        shim.write_text(SHIM)
        subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4',
                        '-mthumb', '-std=c11', '-ffreestanding', '-fno-builtin',
                        '-O2', '-nostdlib', '-Wl,-Ttext=0x100000',
                        '-Wl,-e,audio_ble_dm_conn2_act_rssi_read_4b6a38',
                        str(SOURCE), str(shim), '-o', str(elf)], check=True)
        with elf.open('rb') as f:
            image = ELFFile(f)
            segments = [(s['p_vaddr'], s.data()) for s in image.iter_segments()
                        if s['p_type'] == 'PT_LOAD']
            symbols = {s.name: s['st_value'] for s in
                       image.get_section_by_name('.symtab').iter_symbols()}

        def run(compiled, kind, cseed, mseed):
            symbol, stock_addr, defined = CASES[kind]
            cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
            cpu.mem_map(0x400000, 0x400000)
            cpu.mem_write(0x438000, blob)
            cpu.mem_map(0x100000, 0x200000)
            for address, data in segments:
                cpu.mem_write(address, data)
            cpu.mem_map(0x20000000, 0x100000)
            callback = 0x2000a001
            record = symbols['audio_dm_connection_records'] if compiled else 0x200712a4
            cpu.mem_write(record + 0x9c, callback.to_bytes(4, 'little'))
            ccb = bytes((cseed + i * 3) & 0xff for i in range(64))
            msg = bytes((mseed + i * 7) & 0xff for i in range(64))
            cpu.mem_write(0x20081000, ccb)
            cpu.mem_write(0x20082000, msg)
            calls = []
            def hook(uc, addr, size, user):
                if addr == callback - 1:
                    p = uc.reg_read(A.UC_ARM_REG_R0)
                    data = bytes(uc.mem_read(p, 16))
                    calls.append(tuple(data[i] for i in defined))
                    uc.reg_write(A.UC_ARM_REG_PC, uc.reg_read(A.UC_ARM_REG_LR))
            cpu.hook_add(UC_HOOK_CODE, hook)
            cpu.reg_write(A.UC_ARM_REG_R0, 0x20081000)
            cpu.reg_write(A.UC_ARM_REG_R1, 0x20082000)
            cpu.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
            cpu.reg_write(A.UC_ARM_REG_LR, 0x600001)
            entry = symbols[symbol] if compiled else stock_addr
            cpu.emu_start(entry | 1, 0x600000, count=1000)
            return calls, bytes(cpu.mem_read(0x20081000, 64)), bytes(cpu.mem_read(0x20082000, 64))

        count = 0
        for kind in CASES:
            for cseed in (0, 0x55, 0xa5, 0xff):
                for mseed in (0, 0x39, 0x80, 0xff):
                    stock = run(False, kind, cseed, mseed)
                    candidate = run(True, kind, cseed, mseed)
                    if stock != candidate:
                        raise RuntimeError(f'{kind=} {cseed=} {mseed=}: {stock} != {candidate}')
                    count += 1
    receipt = {'status': 'PASS_EXPERIMENTAL_MAIN_DM_CONN2_ACTIONS_RSSI_PARAM_ORACLE',
               'source': str(SOURCE.relative_to(ROOT)), 'source_sha256': sha(SOURCE),
               'upstream_source': str(UPSTREAM.relative_to(ROOT)),
               'upstream_sha256': sha(UPSTREAM), 'payload_sha256': PINNED_SHA,
               'cases': count,
               'comparison_scope': 'Native callback call and source-defined event bytes; unchanged CCB and input message.',
               'limits': ['Unwritten callback stack bytes are excluded; callback effects and final RAM placement remain open.']}
    path = OUT / 'oracle-receipt.json'
    path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], count)

if __name__ == '__main__': main()
