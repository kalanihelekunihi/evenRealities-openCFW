#!/usr/bin/env python3
"""Audit source ELF against authenticated image-A stage-2 loader geometry.

This emits a contract, not firmware bytes: source relocation leaves holes whose
fill and indirect-root safety still need admission before packaging.
"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RD = ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
XIP_START, XIP_END = 0x10203004, 0x1020be88
SRAM_START, SRAM_END = 0x10023400, 0x10026d7c
STAGE2_LENGTH = 0xc800

def sha(data): return hashlib.sha256(data).hexdigest()

def gaps(start, end, rows):
    result=[]; cursor=start
    for row in sorted(rows,key=lambda x:x['address']):
        assert row['address']>=cursor and row['address']+row['bytes']<=end,row
        if row['address']>cursor: result.append({'start':hex(cursor),'end_exclusive':hex(row['address']),'bytes':row['address']-cursor})
        cursor=row['address']+row['bytes']
    if cursor<end:result.append({'start':hex(cursor),'end_exclusive':hex(end),'bytes':end-cursor})
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--stock-package',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    package=a.stock_package.read_bytes(); positions=[m.start() for m in re.finditer(b'BINH',package)]
    assert len(positions)>=2,positions
    offset=positions[0]; assert package[offset+4:offset+8]==bytes.fromhex('aa55aa55')
    stage2_len=int.from_bytes(package[offset+12:offset+16],'little')
    stage1_len=int.from_bytes(package[offset+16:offset+20],'little')
    stage2_start=offset+stage1_len
    xip_len=int.from_bytes(package[stage2_start:stage2_start+4],'little')
    assert (stage2_len,stage1_len,xip_len)==(STAGE2_LENGTH,0x3000,XIP_END-XIP_START)
    assert xip_len+(SRAM_END-SRAM_START)==stage2_len
    assert stage2_start+4+stage2_len<=len(package)
    table=subprocess.check_output([str(RD),'-SW',str(a.elf)],text=True)
    rows=[]
    for line in table.splitlines():
        m=re.search(r'\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)\s+\d+\s+(\S+)',line)
        if m and 'A' in m[4] and int(m[3],16):rows.append({'section':m[1],'address':int(m[2],16),'bytes':int(m[3],16)})
    xip=[r for r in rows if XIP_START<=r['address']<XIP_END]
    sram=[r for r in rows if SRAM_START<=r['address']<SRAM_END]
    assert len(rows)==len(xip)+len(sram),[r for r in rows if r not in xip+sram]
    assert next(r for r in sram if r['section']=='.gx8002_vectors')['address']==SRAM_START
    assert next(r for r in sram if r['section']=='.gx8002_request_initial')['address']+next(r for r in sram if r['section']=='.gx8002_request_initial')['bytes']==SRAM_END
    xip_holes=gaps(XIP_START,XIP_END,xip);sram_holes=gaps(SRAM_START,SRAM_END,sram)
    elf_bytes=a.elf.read_bytes()
    holes=[(int(row['start'],16),int(row['end_exclusive'],16)) for row in xip_holes+sram_holes]
    aligned_hole_words=[]
    for offset in range(0,len(elf_bytes)-3,4):
        value=int.from_bytes(elf_bytes[offset:offset+4],'little')
        if any(start<=value<end for start,end in holes):
            aligned_hole_words.append({'elf_file_offset':hex(offset),'word':hex(value)})
    out={'result':'PASS_STRUCTURAL_GEOMETRY_ONLY','stock_package_sha256':sha(package),'source_elf_sha256':sha(a.elf.read_bytes()),
         'native_binh_offset':hex(offset),'stage1_bytes':stage1_len,'stage2_payload_bytes':stage2_len,
         'stage2_flash_header_offset':hex(stage2_start),'stage2_header_word_le':hex(xip_len),
         'xip_flash_data_start':hex(stage2_start+4),'xip_flash_data_end_exclusive':hex(stage2_start+4+xip_len),
         'sram_flash_data_start':hex(stage2_start+4+xip_len),'sram_flash_data_end_exclusive':hex(stage2_start+4+stage2_len),
         'loader_xip_address_interval':[hex(XIP_START),hex(XIP_END)],'loader_sram_address_interval':[hex(SRAM_START),hex(SRAM_END)],
         'source_loaded_sections':len(rows),'xip_source_sections':len(xip),'sram_source_sections':len(sram),
         'xip_unassigned_intervals':xip_holes,'sram_unassigned_intervals':sram_holes,
         'xip_unassigned_bytes':sum(r['bytes'] for r in xip_holes),'sram_unassigned_bytes':sum(r['bytes'] for r in sram_holes),
         'aligned_absolute_words_into_unassigned_intervals':aligned_hole_words,
         'source_stage2_payload_emitted':False,
         'limits':['Gap bytes have no authenticated source fill or indirect-root exclusion; no packed binary is emitted.',
                   'Stock package geometry verifies the nominal stage-1 intervals only; modified package metadata/checksum and flash behavior remain unqualified.',
                   'The ELF entry/relocation proof and physical SRAM/DRAM alias require separate receipts.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print({k:out[k] for k in ('result','xip_unassigned_bytes','sram_unassigned_bytes','source_loaded_sections')})
if __name__=='__main__':main()
