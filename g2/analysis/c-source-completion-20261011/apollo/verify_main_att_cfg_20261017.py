#!/usr/bin/env python3
"""Compare C ATT config bytes and pointer against authenticated Main stock."""
import hashlib
import json
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
from decode_main_low_ram_20261016 import decode

ROOT = Path(__file__).resolve().parents[4]
CORDIO = ROOT / 'third-party/upstream/cordio'
HERE = ROOT / 'g2/build/c-firmware/20261017/main-att-cfg'
SOURCE = ROOT / 'g2/components/audio/uart_thread_source_candidate/display_ble_att_cfg_200004b4_20261017.c'
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
OBJECT, ELF, OUT = HERE / 'att-cfg.o', HERE / 'att-cfg.elf', HERE / 'oracle-receipt.json'
BASE = 0x438000
CONFIG_ADDR, POINTER_ADDR = 0x78d154, 0x200004b4
PAYLOAD_SHA = '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    payload = STOCK.read_bytes()[32:]
    assert sha(payload) == PAYLOAD_SHA
    config = payload[CONFIG_ADDR - BASE:CONFIG_ADDR - BASE + 8]
    pointer = decode()[POINTER_ADDR - 0x20000000:POINTER_ADDR - 0x20000000 + 4]
    assert config == bytes.fromhex('0f000000e0011e04')
    assert pointer == CONFIG_ADDR.to_bytes(4, 'little')
    dirs = [CORDIO / 'wsf/include', CORDIO / 'ble-host/include']
    dirs += sorted({p.parent for p in CORDIO.rglob('*.h')})
    flags = []
    for path in dict.fromkeys(dirs):
        flags += ['-I', str(path)]
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                    '-ffreestanding', '-fno-builtin', *flags, '-c', str(SOURCE),
                    '-o', str(OBJECT)], check=True)
    subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb',
                    '-nostdlib', '-Wl,--section-start=.g2_flash_0078d154=0x78d154',
                    '-Wl,--section-start=.g2_ram_200004b4=0x200004b4',
                    '-Wl,-e,0', str(OBJECT), '-o', str(ELF)], check=True)
    with ELF.open('rb') as stream:
        elf = ELFFile(stream)
        built_config = elf.get_section_by_name('.g2_flash_0078d154')
        built_pointer = elf.get_section_by_name('.g2_ram_200004b4')
        assert built_config['sh_addr'] == CONFIG_ADDR and built_config.data() == config
        assert built_pointer['sh_addr'] == POINTER_ADDR and built_pointer.data() == pointer
    record = {'status': 'PASS_MAIN_ATT_CFG_EXACT_STOCK_BYTES',
              'stock_payload_sha256': PAYLOAD_SHA,
              'source_sha256': sha(SOURCE.read_bytes()),
              'object_sha256': sha(OBJECT.read_bytes()),
              'config_address': hex(CONFIG_ADDR), 'config_bytes': config.hex(),
              'pointer_address': hex(POINTER_ADDR), 'pointer_bytes': pointer.hex(),
              'scope': 'Exact eight-byte ATT configuration and initialized RAM pointer, linked at stock addresses',
              'remaining_gate': 'Whole-image placement and startup remain separate.'}
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(record['status'], sha(OUT.read_bytes()))


if __name__ == '__main__':
    main()
