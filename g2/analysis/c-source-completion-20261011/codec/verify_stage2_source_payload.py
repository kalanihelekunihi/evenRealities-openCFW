#!/usr/bin/env python3
"""Independent structural byte check of conditional source stage-2 payload."""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
RD=ROOT/'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
p=argparse.ArgumentParser();p.add_argument('--elf',type=Path,required=True);p.add_argument('--payload',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
e=a.elf.read_bytes();b=a.payload.read_bytes();r=json.loads(a.receipt.read_text());assert hashlib.sha256(e).hexdigest()==r['source_elf_sha256'];assert hashlib.sha256(b).hexdigest()==r['output_sha256'];assert len(b)==51204
assert int.from_bytes(b[:4],'little')==0x8e84
regions=((0x10203004,0x1020be88,4),(0x10023400,0x10026d7c,4+0x8e84))
sections=[]
for line in subprocess.check_output([str(RD),'-SW',str(a.elf)],text=True).splitlines():
 m=re.search(r'\]\s+(\S+)\s+PROGBITS\s+([0-9a-f]+)\s+([0-9a-f]+)\s+([0-9a-f]+)\s+\d+\s+(\S+)',line)
 if not m or 'A' not in m[5] or int(m[4],16)==0:continue
 name,addr,off,size=m[1],int(m[2],16),int(m[3],16),int(m[4],16)
 matched=[(low,high,base) for low,high,base in regions if low<=addr and addr+size<=high];assert len(matched)==1,(name,hex(addr))
 low,high,base=matched[0]; assert b[base+addr-low:base+addr-low+size]==e[off:off+size],name
 sections.append(name)
assert len(sections)==r['loaded_source_sections']==29
assert int.from_bytes(b[4+0x8e84:4+0x8e84+4],'little')==0x10023500
out={'result':'PASS_STRUCTURAL_BYTES_ONLY','source_elf_sha256':r['source_elf_sha256'],'payload_sha256':r['output_sha256'],'exact_source_sections_checked':len(sections),'xip_header_word':hex(int.from_bytes(b[:4],'little')),'first_sram_vector':hex(int.from_bytes(b[4+0x8e84:4+0x8e84+4],'little')),'limits':['Caller-selected 854 gap bytes and actual package/hardware startup remain unqualified.']}
a.output.write_text(json.dumps(out,indent=2)+'\n');print(out)
