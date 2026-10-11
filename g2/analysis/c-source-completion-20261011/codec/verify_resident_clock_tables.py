#!/usr/bin/env python3
"""Compare typed clock source records with retained image-A SRAM bytes."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
IMAGE=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
OBJECT=ROOT/'g2/build/c-firmware/20261011/codec-resident-kws-clockdata-round/codec/resident_clock_product_tables.o'
OBJCOPY=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objcopy'
stock=IMAGE.read_bytes()
checks=[]
for address in [0x10026904,0x10026954]:
    name=f'.gx8002.clock_sources.{address & 0xfffff:x}'
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'section.bin'
        subprocess.run([str(OBJCOPY),'--dump-section',f'{name}={path}',str(OBJECT)],
                       check=True,capture_output=True,text=True)
        actual=path.read_bytes()
    expected=stock[address-0x10023400:address-0x10023400+80]
    checks.append({'address':hex(address),'section':name,'bytes':len(actual),
                   'exact':actual==expected,
                   'stock_sha256':hashlib.sha256(expected).hexdigest(),
                   'object_sha256':hashlib.sha256(actual).hexdigest()})
result={'image_sha256':hashlib.sha256(stock).hexdigest(),
        'checks':checks,'all_exact':all(x['exact'] and x['bytes']==80 for x in checks),
        'scope':'target object section bytes only; runtime alias and final placement unqualified'}
Path(__file__).with_name('resident-clock-table-receipt.json').write_text(
    json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'bytes':sum(x['bytes'] for x in checks),
                  'all_exact':result['all_exact']}))
raise SystemExit(not result['all_exact'])
