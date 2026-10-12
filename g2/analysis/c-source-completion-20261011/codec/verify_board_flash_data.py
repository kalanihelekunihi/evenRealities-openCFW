#!/usr/bin/env python3
"""Target-object byte/relocation proof for board, flash, and console BSS."""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OBJ = HERE/'sample-tail-target'
TOOLS = ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
IMAGE = ROOT/('g2/build/pseudocode-first/20260930T190500Z/reviews/'
              'codec-canonical-images-003/images/binh_a_stage2_sram.bin')
stock = IMAGE.read_bytes()

def section(obj, name):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)/'x'
        subprocess.run([str(TOOLS/'csky-elfabiv2-objcopy'),
                        '--dump-section',f'{name}={p}',str(OBJ/obj)],
                       check=True,capture_output=True)
        return p.read_bytes()

def native(start,length):
    return stock[start-0x10023400:start-0x10023400+length]

board = section('resident_board_product_state.o','.gx8002.board_state.269a4')
state = section('resident_flash_api_data.o','.gx8002.flash_state.264e4')
api = section('resident_flash_api_data.o','.gx8002.flash_api.26504')
assert len(board)==240 and board==native(0x100269a4,240)
assert len(state)==32 and state==native(0x100264e4,32)
expected_api = native(0x10026504,120)
assert len(api)==120
native_words = [int.from_bytes(expected_api[i:i+4],'little')
                for i in range(0,120,4)]
zero_slots = [i for i,word in enumerate(native_words) if word==0]
assert all(api[4*i:4*i+4]==bytes(4) for i in zero_slots)

def relocs(obj):
    out = subprocess.run([str(TOOLS/'csky-elfabiv2-readelf'),'-rW',
                          str(OBJ/obj)],check=True,capture_output=True,
                         text=True).stdout
    return [line for line in out.splitlines() if 'R_CKCORE_ADDR32' in line]

api_relocs = relocs('resident_flash_api_data.o')
assert len(api_relocs)==23
offsets = [int(line.split()[0],16) for line in api_relocs]
assert offsets==[i*4 for i,word in enumerate(native_words) if word!=0]
for offset,line in zip(offsets,api_relocs):
    native_target = native_words[offset//4]
    assert line.split('+')[0].strip().endswith(
        f'_{native_target & 0xfffff:x}'), (hex(offset),hex(native_target),line)

board_relocs = relocs('board_uart.o')
assert any('gx8002_board_state_269a4' in line for line in board_relocs)
sections = subprocess.run([str(TOOLS/'csky-elfabiv2-readelf'),'-SW',
                           str(OBJ/'resident_xip_console_state.o')],
                          check=True,capture_output=True,text=True).stdout
assert re.search(r'\.bss\.gx8002\.console_port\.2731c\s+NOBITS\s+\S+\s+\S+\s+000004\s+\S+\s+WA',sections)

receipt = {'stock_image_sha256':hashlib.sha256(stock).hexdigest(),
           'board':{'address':'0x100269a4','bytes':240,'exact':True,
                    'sha256':hashlib.sha256(board).hexdigest(),
                    'getter_relocation':True},
           'flash_state':{'address':'0x100264e4','bytes':32,'exact':True,
                          'sha256':hashlib.sha256(state).hexdigest()},
           'flash_api':{'address':'0x10026504','bytes':120,
                        'zero_slots_exact':len(zero_slots),
                        'pointer_relocations':len(api_relocs),
                        'relocation_targets_match_native':True,
                        'stock_sha256':hashlib.sha256(expected_api).hexdigest()},
           'console_bss':{'runtime_address':'0x2002731c',
                          'section_type':'NOBITS','bytes':4,
                          'inside_native_clear_span':True},
           'limit':'target source bytes and relocation identities; final address placement, copy, and native runtime remain unqualified'}
(HERE/'board-flash-data-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'board_exact':True,'flash_state_exact':True,
                  'flash_api_relocations':len(api_relocs),
                  'console_bss_nobits':True}))
