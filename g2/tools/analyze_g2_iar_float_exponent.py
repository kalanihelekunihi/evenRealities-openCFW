#!/usr/bin/env python3
"""Fail-closed audit of newly isolated IAR DLIB frexpf/ldexpf bodies."""
import csv,hashlib,json,sys
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin';FM=ROOT/'tools/manifests/g2-iar-float-exponent-function-map.tsv';CL=ROOT/'tools/manifests/g2-iar-float-exponent-closure.tsv'
PINS={FM:'f220f26f4cb37314d84d844396e5a0d9639e7a71baae761c0abf25bd7736e02f',CL:'2a13e86eb2c35ba25a4f152d10cb93229b27e442376db60d5b9d6b410a8f2f13'}
F=((0x59D244,0x59D258),(0x59D258,0x59D28C),(0x59D28C,0x59D350));PHYS=(0x59D244,0x59D350)
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError('official image changed')
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError(f'manifest changed: {p.name}')
 with FM.open(newline='',encoding='utf8') as h:rows=list(csv.DictReader(h,delimiter='\t'))
 if tuple((int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows)!=F:raise c.AuditError('function inventory changed')
 md=Cs(CS_ARCH_ARM,CS_MODE_THUMB);starts={a for a,_ in F};inter=set();ins=[];calls=[];body=b'';tail=[]
 for row,(a,z) in zip(rows,F):
  raw=c._slice(b,a,z);ii=list(md.disasm(raw,a))
  if len(raw)!=int(row['stock_bytes']) or sh(raw)!=row['stock_sha256'] or sum(x.size for x in ii)!=len(raw):raise c.AuditError('body changed')
  body+=raw;ins += [(x.address,x.size) for x in ii];inter.update(range(a+2,z,2))
  for x in ii:
   y=t._thumb_bl_target(b,x.address)
   if y is not None:calls.append((x.address,y))
   if x.mnemonic=='b.w':tail.append((x.address,x.op_str))
 if len(ins)!=96 or c._instruction_digest(ins)!='01e3f07567b26067786a826d762ce422dc329843e8b1677bc8df933e522d627e' or calls!=[(0x59D24C,0x59D258)] or c._pair_digest(calls)!='7f88f590e7e81e70985f4ecb5136371f3e01d462304bc83c488e3d5711e42220' or tail!=[(0x59D34A,'#0x439cb2')]:raise c.AuditError('control-flow closure changed')
 if len(body)!=268 or sh(body)!='aa1f326578d9f4fc257821facd6a8ff4e602c91132e02121794b150757da7ff2' or sh(c._slice(b,*PHYS))!=sh(body):raise c.AuditError('physical closure changed')
 if sh(c._slice(b,0x59D234,0x59D244))!='38ce46aa6222b8855ecc7495dc48f1dfcb60149ac6fd66cc4691c4e165f4bec8' or sh(c._slice(b,0x59D350,0x59D360))!='5aa05e7694fefbf58945a6b9acb8c3208e81b1dd5a11cb288dbfe0d52f8e979f':raise c.AuditError('boundary changed')
 entries=[];strict=[]
 for a in range(c.BASE,c.BASE+len(b)-3,2):
  y=t._thumb_bl_target(b,a)
  if y in starts:entries.append((a,y))
  elif y in inter:strict.append((a,y))
 if len(entries)!=10 or c._pair_digest(entries)!='e712da9c8e49d7f4d6586904de11094f888600b10edb8ccdca4336caeacc6cfa' or strict:raise c.AuditError('ingress changed')
 return {'schema_version':1,'analysis_mode':'read-only raw-image closure','identity':{'image_sha256':c.IMAGE_SHA256,'family':'IAR-DLIB','origin':'IAR EWARM DLIB math runtime','version_floor':'9.20+','leading_compatibility_candidate':'9.60.2','exact_release':None,'source_commit':None},'surface':{'linked_functions':3,'body_bytes':268,'physical_bytes':268,'reachable_instructions':96,'direct_bl_entry_sites':10,'external_public_entry_sites':9,'internal_direct_calls':1,'stored_entry_pointers':0,'strict_interior_ingress':0},'behavior':{'frexpf_hard_float_abi':True,'binary32_normalization_helper':True,'ldexpf_hard_float_abi':True,'subnormal_vfp_rounding':True,'overflow_erange_tail':True,'signed_zero_nan_infinity_preservation':True},'provenance':{'iar_dlib':True,'official_dlib_standard_c_family_evidence':True,'official_vfp_optimization_lineage_since_ewarm_5_50':True,'new_exact_release_discriminator':False},'production':{'production_routed':True,'production_profiles':['apple-clang'],'pending_profiles':['linux-clang'],'clean_room_candidate':'components/apollo_main/core_overlay/candidates/iar_runtime_float_exponent.S','exact_stock_reproduction':True,'differential_cases_per_entry':4000,'remaining_functional_gap':False}}
if __name__=='__main__':print(json.dumps(analyze(),indent=2,sort_keys=True))
