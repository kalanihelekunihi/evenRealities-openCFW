#!/usr/bin/env python3
"""Check typed C-SKY product data against authenticated native image bytes.

Pointer slots are checked by relocation ownership separately from scalar bytes;
no final address placement or runtime copy is claimed here.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
IMAGE=ROOT/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images'
OBJ=ROOT/'g2/build/c-firmware/20261011/codec-resident-flash-product-data-corrected-round/codec'
OBJCOPY=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objcopy'
READELF=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
sram=(IMAGE/'binh_a_stage2_sram.bin').read_bytes()
xip=(IMAGE/'binh_a_stage2_xip.bin').read_bytes()

def stock(image:bytes,base:int,address:int,length:int)->bytes:
    return image[address-base:address-base+length]

def section(obj:str,name:str)->bytes:
    with tempfile.TemporaryDirectory() as td:
        target=Path(td)/'section.bin'
        subprocess.run([str(OBJCOPY),'--dump-section',f'{name}={target}',str(OBJ/obj)],
                       check=True,capture_output=True,text=True)
        return target.read_bytes()

checks=[]
def check(obj,section_name,image,base,address,length,mask=None):
    actual=section(obj,section_name)
    expected=stock(image,base,address,length)
    assert len(actual)==length==len(expected),(obj,section_name,len(actual),length,len(expected))
    if mask is None: mask=bytes([1])*length
    mismatches=[i for i in range(length) if mask[i] and actual[i]!=expected[i]]
    checks.append({'section':section_name,'address':hex(address),'bytes':length,
                   'compared_bytes':sum(mask),'stock_sha256':hashlib.sha256(expected).hexdigest(),
                   'mismatches':mismatches[:10],'mismatch_count':len(mismatches)})
    return not mismatches

ok=True
for a,n in [(0x1002657c,40),(0x100265a4,56),(0x100265dc,72)]:
    ok &= check('resident_flash_product_otp_data.o',f'.gx8002.otp_protect.{a & 0xfffff:x}',sram,0x10023400,a,n)
for a,n in [(0x1020be54,8),(0x1020be5c,8),(0x1020be64,8),
            (0x1020be6c,9),(0x1020be75,9),(0x1020be7e,10)]:
    ok &= check('resident_flash_product_catalog.o',f'.gx8002.flash_name.{a & 0xffff:x}',xip,0x10203004,a,n)
ok &= check('resident_flash_product_catalog.o','.gx8002.flash_otp_config.266cc',sram,0x10023400,0x100266cc,20)
ok &= check('resident_module_product_data.o','.gx8002.module_config.26880',sram,0x10023400,0x10026880,72)
# Catalog: compare JEDEC/capacity/field12 and zero sentinel; pointer bytes
# carry R_CKCORE_ADDR32 relocations to source symbols.
mask=bytearray(168)
for i in range(7):
    for j in range(4,16): mask[i*24+j]=1
for j in range(144,168): mask[j]=1
ok &= check('resident_flash_product_catalog.o','.gx8002.flash_catalog.26624',sram,0x10023400,0x10026624,168,mask)
# Module records: ID, bit fields and reserved byte are exact; address words
# are source relocations to the typed config object.
mask=bytearray(416)
for i in range(26):
    for j in range(8): mask[i*16+j]=1
    old=stock(sram,0x10023400,0x100266e0+i*16,16)
    for j in (8,12):
        if old[j:j+4]==b'\0\0\0\0': mask[i*16+j:i*16+j+4]=b'\1'*4
ok &= check('resident_module_product_data.o','.gx8002.module_table.266e0',sram,0x10023400,0x100266e0,416,mask)
relocs={}
for obj in ['resident_flash_product_catalog.o','resident_module_product_data.o']:
    out=subprocess.run([str(READELF),'-rW',str(OBJ/obj)],check=True,capture_output=True,text=True).stdout
    lines=[line.strip() for line in out.splitlines() if 'R_CKCORE_ADDR32' in line]
    relocs[obj]={'count':len(lines),'symbol_lines':lines}
assert relocs['resident_flash_product_catalog.o']['count']==14
assert relocs['resident_module_product_data.o']['count']==20
receipt={'source_sram_sha256':hashlib.sha256(sram).hexdigest(),
         'source_xip_sha256':hashlib.sha256(xip).hexdigest(),
         'checks':checks,'relocations':relocs,
         'all_compared_bytes_match':bool(ok),
         'scope':'target-object scalar bytes, named strings, and relocation ownership; final placement/copy/runtime unqualified'}
Path(__file__).with_name('resident-product-data-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'compared_bytes':sum(x['compared_bytes'] for x in checks),
                  'mismatches':sum(x['mismatch_count'] for x in checks),
                  'relocations':{k:v['count'] for k,v in relocs.items()}}))
raise SystemExit(not ok)
