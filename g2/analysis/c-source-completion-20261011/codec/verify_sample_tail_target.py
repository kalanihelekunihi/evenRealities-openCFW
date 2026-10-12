#!/usr/bin/env python3
"""Verify target C initializer bytes and nine address relocations."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BIN = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
              'codec-canonical-images-003/images')
OBJ = HERE/'sample-tail-target/resident_sample_product_data.o'
TOOL = ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin'
stock = (BIN/'binh_a_stage2_sram.bin').read_bytes()
xip = (BIN/'binh_a_stage2_xip.bin').read_bytes()
checks = []

def compare(section, base, address, length, ignored=(), image=stock):
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)/'section.bin'
        subprocess.run([str(TOOL/'csky-elfabiv2-objcopy'),
                        '--dump-section',f'{section}={target}',str(OBJ)],
                       check=True,capture_output=True)
        actual = target.read_bytes()
    expected = image[address-base:address-base+length]
    assert len(actual)==length==len(expected),(section,len(actual),length)
    ignored_bytes = {i for off in ignored for i in range(off,off+4)}
    differences = [i for i,(a,b) in enumerate(zip(actual,expected))
                   if i not in ignored_bytes and a!=b]
    checks.append({'section':section,'address':hex(address),'bytes':length,
                   'compared_bytes':length-len(ignored_bytes),
                   'stock_sha256':hashlib.sha256(expected).hexdigest(),
                   'mismatches':differences})
    assert not differences,(section,differences[:10])

for section,address,length in [
    ('.gx8002.uart_rx_config.26c74',0x10026c74,8),
    ('.gx8002.kws_keywords.26c7c',0x10026c7c,176),
    ('.gx8002.sample_prestate.26d2c',0x10026d2c,4),
    ('.gx8002.request_initial.26d5c',0x10026d5c,32),
]:
    compare(section,0x10023400,address,length)
compare('.gx8002.sample_registration.26d30',0x10023400,
        0x10026d30,44,ignored=tuple(range(8,44,4)))
for section,address,length in [
    ('.gx8002.sample_name.b649',0x1020b649,11),
    ('.gx8002.sample_name.b654',0x1020b654,17),
    ('.gx8002.sample_name.b665',0x1020b665,16),
]:
    compare(section,0x10203004,address,length,image=xip)

rel = subprocess.run([str(TOOL/'csky-elfabiv2-readelf'),'-rW',str(OBJ)],
                     check=True,capture_output=True,text=True).stdout
lines = [line for line in rel.splitlines() if 'R_CKCORE_ADDR32' in line]
assert len(lines)==9,lines
offsets = [int(line.split()[0],16) for line in lines]
assert offsets==list(range(8,44,4)),offsets
receipt={'target_object_sha256':hashlib.sha256(OBJ.read_bytes()).hexdigest(),
         'checks':checks,'relocation_count':len(lines),
         'relocation_offsets':[hex(o) for o in offsets],
         'compared_bytes':sum(c['compared_bytes'] for c in checks),
         'scope':'exact source scalar/string bytes and relocation slots; final addresses and startup copy remain unqualified'}
(HERE/'sample-tail-target-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'compared_bytes':receipt['compared_bytes'],
                  'relocations':len(lines)}))
