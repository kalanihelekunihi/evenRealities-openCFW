#!/usr/bin/env python3
"""Bounded absolute-word scan of packaged bytes outside image-A stage-2."""
import argparse, hashlib, json
from pathlib import Path
A_BINH=0x958c;B_BINH=0x3893c;A_STAGE1=0x3000;A_STAGE2_PAYLOAD=0xc800
RANGES=((0x10023500,0x100264e4,'resident_code'),(0x10203004,0x1020be88,'xip_code'))
p=argparse.ArgumentParser();p.add_argument('--stock-package',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();data=a.stock_package.read_bytes()
assert data[A_BINH:A_BINH+4]==data[B_BINH:B_BINH+4]==b'BINH'
assert int.from_bytes(data[A_BINH+12:A_BINH+16],'little')==A_STAGE2_PAYLOAD
areas={'A_stage1':(A_BINH,A_BINH+A_STAGE1),'inter_image_payload':(A_BINH+A_STAGE1+4+A_STAGE2_PAYLOAD,B_BINH),'B_stage1':(B_BINH,B_BINH+0x3000),'B_stage2_and_tail':(B_BINH+0x3000,len(data))}
result={}
for name,(start,end) in areas.items():
 hits=[]
 for i in range(start,end-3,4):
  word=int.from_bytes(data[i:i+4],'little')
  for low,high,kind in RANGES:
   if low<=word<high:hits.append({'package_offset':hex(i),'word':hex(word),'target_region':kind})
 result[name]={'bytes':end-start,'aligned_absolute_word_hits':hits}
out={'stock_package_sha256':hashlib.sha256(data).hexdigest(),'regions':result,'aligned_external_word_hits_total':sum(len(v['aligned_absolute_word_hits']) for v in result.values()),'qualification':'Bounded aligned absolute-word scan only. It does not exclude computed, encoded, unaligned or hardware-configured roots.'}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print({k:len(v['aligned_absolute_word_hits']) for k,v in result.items()})
