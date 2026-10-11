#!/usr/bin/env python3
from pathlib import Path
import re,struct,json,collections,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2]
raw=(R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
lines=(R/'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt').read_text().splitlines()
inst=[]
for line in lines:
 parts=line.split('\t')
 if len(parts)>=4 and re.match(r'^\s*[0-9a-f]+:',parts[0]):
  inst.append((int(parts[0].strip().rstrip(':'),16),parts[2].strip(),parts[3].strip(),line))
branches={'b','bx','bl','blx','cbz','cbnz','tbb','tbh','pop'}
def getstr(p):
 if not 0x438000<=p<0x438000+len(raw):return None
 data=raw[p-0x438000:p-0x438000+200].split(b'\0')[0]
 if not data or len(data)>=200 or any(c<32 or c>126 for c in data):return None
 return data.decode()
def load_reg(window,reg):
 for a,op,args,line in reversed(window):
  if re.match(rf'^{reg},',args):
   if op.startswith('ldr'):
    m=re.search(r'@\s*\(?0x([0-9a-f]+)\)?',line)
    if m:
     lit=int(m[1],16)
     if 0x438000<=lit<=0x438000+len(raw)-4:return struct.unpack_from('<I',raw,lit-0x438000)[0],a
   if op.startswith('mov'):
    m=re.match(rf'{reg},\s*(r[0-9]+)',args)
    if m:return load_reg([(aa,oo,ar,li) for aa,oo,ar,li in window if aa<a],m[1])
   return None,a
 return None,None
records=[];resolved=[]
for i,(a,op,args,line) in enumerate(inst):
 if op!='bl' or '0x43ce9e' not in args:continue
 window=inst[max(0,i-12):i]
 # Require the setting and use to be in a straight-line suffix.
 p,src=load_reg(window,'r1')
 valid=src is not None and all(not (o.startswith('b') and o not in ('bic','bfi','bfc')) for aa,o,ar,li in window if aa>src)
 s=getstr(p) if valid and p is not None else None
 records.append({'call':hex(a),'pointer':hex(p) if s else None,'format':s})
 if s:resolved.append(s)
counts=collections.Counter(resolved)
receipt={'image_sha256':hashlib.sha256(raw).hexdigest(),'total_direct_calls':len(records),'linear_literal_string_calls':len(resolved),'distinct_strings':len(counts),'top_formats':counts.most_common(35),'calls':records,'unresolved_calls':len(records)-len(resolved),'classification_limit':'Conservative <=12-instruction straight-line literal provenance for r1; unresolved includes indirect/earlier/runtime/ADR or branches. Syntactic source compatibility is not behavioral proof of caller varargs or pointer ownership.'}
(H/'short-logger-call-domain.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt)
