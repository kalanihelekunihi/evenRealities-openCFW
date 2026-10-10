#!/usr/bin/env python3
"""Bounded independent comparison of EM9305 v4.2 linked functions to locked G2.

This deliberately masks only encodings whose value is position dependent:
Thumb B/BL/BLX/CBZ/CBNZ and PC-relative ADR/LDR-literal immediates.  It does not
mask arbitrary constants or literal pools, so a match retains useful content.
"""
from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
V42 = ROOT/'third-party/local-vendor/sources/em9305-v4.2-public-mirror/emcore/bin/v4.2/standard'
V46 = ROOT/'third-party/local-vendor/sources/em9305-v4.6/EM9305_SDK/EM9305_EM_BLEU_SDK_v4.6/emcore/bin/v4.6/standard'
TARGET = ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_ble_em9305.bin'
TARGET_BASE = 0x301fdc

def ihex(path):
    mem={}; upper=0
    for line in path.read_text().splitlines():
        if not line.startswith(':'): continue
        b=bytes.fromhex(line[1:]); n=b[0]; a=int.from_bytes(b[1:3],'big'); typ=b[3]; data=b[4:4+n]
        if typ==0:
            for i,x in enumerate(data): mem[upper+a+i]=x
        elif typ==4: upper=int.from_bytes(data,'big')<<16
    return mem

def syms(path):
    out={}
    for line in path.read_text(errors='replace').splitlines():
        m=re.match(r'([^#!][^=]*)=0x([0-9a-fA-F]+) 0x([0-9a-fA-F]+)$',line)
        if m: out[m.group(1)]=(int(m.group(2),16),int(m.group(3),16))
    return out

def body(mem,a,n):
    try:return bytes(mem[x] for x in range(a,a+n))
    except KeyError:return None

def mask_thumb(buf):
    b=bytearray(buf); mask=bytearray(len(b)); i=0; kinds=[]
    while i+1<len(b):
        h=b[i]|b[i+1]<<8
        kind=None; width=2
        if i+3<len(b) and (h&0xf800)==0xf000:
            h2=b[i+2]|b[i+3]<<8
            if (h2&0xc000)==0xc000: kind='bl_blx'; width=4
        if kind is None and (h&0xf800)==0xe000: kind='b16'
        if kind is None and (h&0xf000)==0xd000 and (h&0x0f00)!=0x0f00: kind='bcond16'
        if kind is None and (h&0xf500)==0xb100: kind='cbz_cbnz'
        if kind is None and (h&0xf800)==0x4800: kind='ldr_literal16'
        if kind is None and (h&0xf800)==0xa000: kind='adr16'
        if kind:
            for j in range(i,min(i+width,len(b))): mask[j]=1; b[j]=0
            kinds.append([i,width,kind])
        i+=width
    return bytes(b),bytes(mask),kinds

def masked_equal(x,y):
    nx,mx,_=mask_thumb(x); ny,my,_=mask_thumb(y)
    # Require the same relocation-sensitive instruction positions and all
    # remaining bytes identical.
    return mx==my and nx==ny, sum(1 for z in mx if z)

def candidate_offsets(pattern, target):
    norm,mask,_=mask_thumb(pattern); segs=[]; start=None
    for i,z in enumerate(mask+b'\x01'):
        if not z and start is None:start=i
        if z and start is not None:
            segs.append((i-start,start,norm[start:i])); start=None
    if not segs:return []
    _,delta,anchor=max(segs)
    hits=[]; pos=target.find(anchor)
    while pos>=0:
        off=pos-delta
        if off>=0 and off%2==0 and off+len(pattern)<=len(target):
            ok,_=masked_equal(pattern,target[off:off+len(pattern)])
            if ok:hits.append(off)
        pos=target.find(anchor,pos+1)
    return sorted(set(hits))

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    m42=ihex(V42/'emcore_standard.ihex'); m46=ihex(V46/'emcore_standard.ihex')
    s42=syms(V42/'emcore_standard.sym'); s46=syms(V46/'emcore_standard.sym')
    target=TARGET.read_bytes(); rows=[]
    canonical={}
    for line in (ROOT/'g2/symbols/ble_em9305.tsv').read_text().splitlines()[1:]:
        p=line.split('\t')
        if len(p)>=6: canonical[(int(p[0],16),int(p[1],16))]=(p[3],p[4],p[5])
    for name,(a,n) in sorted(s42.items()):
        if n<24 or not (0x300000<=a<0x360000): continue
        x=body(m42,a,n)
        if x is None: continue
        v46=s46.get(name); v46b=body(m46,*v46) if v46 and v46[1]==n else None
        for off in candidate_offsets(x,target):
            y=target[off:off+n]; exact=x==y; reloc,masked=masked_equal(x,y)
            if exact or reloc:
                ta=TARGET_BASE+off; canon=canonical.get((ta,ta+n))
                version_class=('absent_in_v46' if v46 is None else
                    'size_changed_in_v46' if v46[1]!=n else
                    'body_changed_in_v46' if v46b!=x else 'same_in_v46')
                rows.append({'name':name,'v42_address':hex(a),'target_address':hex(ta),'target_file_offset':off,'size':n,
                    'match':'exact' if exact else 'relocation_masked','masked_bytes':0 if exact else masked,
                    'v46_present':v46 is not None,'v46_size':v46[1] if v46 else None,
                    'v46_same_size':v46b is not None,'v42_equals_v46':v46b==x if v46b is not None else None,
                    'target_equals_v46':v46b==y if v46b is not None else None,
                    'version_class':version_class,
                    'canonical_exact_boundary':canon is not None,
                    'canonical_name_agrees':canon is not None and canon[0]==name,
                    'canonical_record':{'name':canon[0],'module':canon[1],'confidence':canon[2]} if canon else None,
                    'v42_sha256':hashlib.sha256(x).hexdigest(),'target_sha256':hashlib.sha256(y).hexdigest()})
    exact=[r for r in rows if r['match']=='exact']; rel=[r for r in rows if r['match']=='relocation_masked']
    # Negative control is the unconstrained whole-target search above. Retain
    # only target-unique signatures and report multiplicity.
    for r in rows:
        a=s42[r['name']][0]; n=r['size']; x=body(m42,a,n)
        hits=[hex(TARGET_BASE+o) for o in candidate_offsets(x,target)]
        r['whole_target_masked_hit_count']=len(hits); r['whole_target_masked_hits']=hits
        r['unique_after_negative_control']=len(hits)==1 and hits[0]==r['target_address']
    result={'format':'openCFW.em9305-v42-reloc-independent.v1','scope':{
      'method':'whole-target aligned search anchored by the longest unmasked byte run; target location and name are unconstrained',
      'target_base_address':hex(TARGET_BASE),
      'minimum_size':24,'masked_encodings':['Thumb BL/BLX','B16','Bcond16','CBZ/CBNZ','LDR literal16','ADR16'],
      'not_masked':['literal pools','arbitrary immediates','data pointers','32-bit non-branch PC-relative encodings']},
      'inputs':{'v42_ihex_sha256':sha(V42/'emcore_standard.ihex'),'v42_sym_sha256':sha(V42/'emcore_standard.sym'),
      'v46_ihex_sha256':sha(V46/'emcore_standard.ihex'),'v46_sym_sha256':sha(V46/'emcore_standard.sym'),'target_sha256':sha(TARGET)},
      'counts':{'accepted_total':len(rows),'exact':len(exact),'relocation_masked':len(rel),
      'unique_after_negative_control':sum(r['unique_after_negative_control'] for r in rows),
      'canonical_boundary_and_name_agreement':sum(r['canonical_name_agrees'] for r in rows),
      'v42_version_discriminators':sum(r['version_class']!='same_in_v46' for r in rows)},'matches':rows}
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['counts'],indent=2))

if __name__=='__main__':main()
