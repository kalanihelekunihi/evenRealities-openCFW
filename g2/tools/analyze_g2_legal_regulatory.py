#!/usr/bin/env python3
"""Fail-closed audit of the G2 legal/regulatory UI object."""
import csv,hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
import analyze_g2_ux_system as c
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t
IMAGE=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin";FM=ROOT/"tools/manifests/g2-legal-regulatory-function-map.tsv";CL=ROOT/"tools/manifests/g2-legal-regulatory-closure.tsv";PM=ROOT/"tools/manifests/g2-legal-regulatory-provider-map.tsv"
PINS={FM:"2da1776c1ab07820acb91fd1fe80964aa32b6e7ce20df7d39c4dffa8e8a33e5b",CL:"fdb46bdeb65707ca87defb1ba046a4c478f0e4e74ced7a399426e3c5012c3604",PM:"289340a802b57d2cde9faf7cd52ce8fc58b3069abc4d008b856af23951b3986c"};START,END,PHYS=0x5BF7B8,0x5BF8A2,(0x5BF7B8,0x5BF964)
def sh(x):return hashlib.sha256(x).hexdigest()
def analyze(image=IMAGE):
 b=image.read_bytes()
 if len(b)!=c.IMAGE_SIZE or sh(b)!=c.IMAGE_SHA256:raise c.AuditError("image changed")
 for p,h in PINS.items():
  if sh(p.read_bytes())!=h:raise c.AuditError("manifest changed")
 with FM.open(newline="",encoding="utf8") as h:rows=list(csv.DictReader(h,delimiter="\t"))
 if len(rows)!=1:raise c.AuditError("function inventory changed")
 body=c._slice(b,START,END)
 if sh(body)!="99c67be892d730a8c6872d42af9a05f4d9906236efffe5365f1f5f76607933fb":raise c.AuditError("body changed")
 ins,calls,ind=d._recover_function(b,START,END);calls.sort()
 if len(ins)!=98 or c._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!="4c44989db5047b14b4a0518bf908b32b1068d06896d664e0cdffc4a8baa75722" or len(calls)!=15 or c._pair_digest(calls)!="d28b858f6821baf9fb7b2a3d6ae39d0b5c3f4a86549bd4ae968d4041c9283f1e" or ind:raise c.AuditError("code topology changed")
 if sh(c._slice(b,*PHYS))!="eec57b8478edf3d026cb90588c9ffcb5039bf78408d2e373cdffe6cdc1cf1151" or sh(c._slice(b,END,PHYS[1]))!="6dc058b8c38d7def8a5175fe48922df8b5ce6459e27c675fa1513d6802566422":raise c.AuditError("physical object changed")
 if sh(c._slice(b,0x5BF7A0,START))!="b70acd1c958c7ffb6d7078a136c8c87bb11ba58e9b9fcc8b8556ddc9230a5958" or sh(c._slice(b,PHYS[1],0x5BF972))!="41a7f17ded392fc42956b4da6c5adf28fbc75722b8181eddf5c9aeecb9837881":raise c.AuditError("boundary changed")
 stored=[]
 for off in range(len(b)-3):
  v=struct.unpack_from("<I",b,off)[0]
  if v in {START|1,0x5BF880|1}:stored.append((c.BASE+off,v&~1))
 if stored!=[(0x4B3C36,0x5BF880),(0x4B458E,0x5BF880),(0x6A4558,START)]:raise c.AuditError("stored/shared entries changed")
 if t._thumb_bl_target(b,0x5BB7FC)!=0x5BF88C:raise c.AuditError("shared direct tail changed")
 for a,s in {0x6ED838:r"D:\01_workspace\s200_ap510b_iar_git\app\gui\LegalRegulatory\legal_regulatory.c",0x760450:"LegalRegulatory display startup",0x760470:"LegalRegulatory display exit",0x754DC4:"legal_regulatory_ui_event_handler"}.items():
  if c._c_string(b,a)!=s:raise c.AuditError("string changed")
 return {"schema_version":1,"analysis_mode":"read-only","identity":{"image_sha256":c.IMAGE_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":1,"body_bytes":234,"physical_bytes":428,"outer_pool_bytes":194,"direct_body_calls":15,"stored_primary_entry_pointers":1,"shared_tail_direct_entries":1,"shared_tail_stored_entries":2,"indirect_body_calls":0},"provider_boundary":{"easylogger_calls":10,"lvgl_calls":1,"iar_dlib_calls":2,"first_party_calls":2,"new_version_discriminator":False},"production":{"production_routed":False}}
if __name__=="__main__":print(json.dumps(analyze(),indent=2,sort_keys=True))
