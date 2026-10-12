#!/usr/bin/env python3
"""Construct a conditional Codec-A stage-2 payload from source ELF sections.

Requires an explicit byte policy for the three unresolved placement gaps. The
output is an analysis candidate, not a production package or hardware image.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
RD=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
XIP0,XIP1=0x10203004,0x1020be88
SRAM0,SRAM1=0x10023400,0x10026d7c
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--geometry',type=Path,required=True);p.add_argument('--gap-fill-byte',type=lambda x:int(x,0),required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
assert 0<=a.gap_fill_byte<=255
geometry=json.loads(a.geometry.read_text());assert geometry['source_elf_sha256']==hashlib.sha256(a.elf.read_bytes()).hexdigest()
assert geometry['result']=='PASS_STRUCTURAL_GEOMETRY_ONLY'
data=a.elf.read_bytes();table=subprocess.check_output([str(RD),'-SW',str(a.elf)],text=True)
xip=bytearray([a.gap_fill_byte]*(XIP1-XIP0));sram=bytearray([a.gap_fill_byte]*(SRAM1-SRAM0));written=[]
for line in table.splitlines():
 m=re.search(r'\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+\d+\s+(\S+)',line)
 if not m or 'A' not in m[5] or int(m[4],16)==0:continue
 name,address,offset,size=m[1],int(m[2],16),int(m[3],16),int(m[4],16)
 assert offset+size<=len(data)
 if XIP0<=address< XIP1:buffer,base=xip,XIP0
 elif SRAM0<=address<SRAM1:buffer,base=sram,SRAM0
 else:raise AssertionError((name,hex(address)))
 assert address+size<=base+len(buffer)
 buffer[address-base:address-base+size]=data[offset:offset+size]
 written.append({'section':name,'address':hex(address),'bytes':size,'elf_file_offset':hex(offset)})
assert len(written)==geometry['source_loaded_sections']
header=(XIP1-XIP0).to_bytes(4,'little');blob=header+bytes(xip)+bytes(sram)
assert len(blob)==4+0xc800 and int.from_bytes(blob[:4],'little')==0x8e84
assert len(blob[4:4+0x8e84])==0x8e84 and len(blob[4+0x8e84:])==0x397c
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(blob)
receipt={'status':'CONDITIONAL_SOURCE_PAYLOAD_ONLY','source_elf_sha256':hashlib.sha256(data).hexdigest(),'geometry_sha256':hashlib.sha256(a.geometry.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(blob).hexdigest(),'output_bytes':len(blob),'explicit_gap_fill_byte':hex(a.gap_fill_byte),'loaded_source_sections':len(written),'stage2_header_word':hex(int.from_bytes(blob[:4],'little')),'xip_interval':[hex(XIP0),hex(XIP1)],'sram_interval':[hex(SRAM0),hex(SRAM1)],'xip_bytes':len(xip),'sram_bytes':len(sram),'unassigned_bytes':geometry['xip_unassigned_bytes']+geometry['sram_unassigned_bytes'],'firmware_image_complete':False,'limits':['Gap fill byte is caller supplied and not authenticated to the product.','The A stage-1 container, checksums, indirect roots, runtime alias and hardware behavior are not qualified.']}
(a.output.with_suffix(a.output.suffix+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n');print({k:receipt[k] for k in ('status','output_bytes','output_sha256','unassigned_bytes')})
