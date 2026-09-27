#!/usr/bin/env python3
"""Read-only P1 validators for EM9305, touch, case and bootloader payloads.

This command emits a campaign-owned inventory record only. It never writes to
firmware/source/manifests or performs build, flash, hardware, or subprocess work.
"""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, struct, sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
CAMP='20260926T223240Z'; BASE=ROOT/'g2/build/pseudocode-first'/CAMP
TARGET=json.loads((ROOT/'g2/workflow/target.json').read_text())
MANIFEST=json.loads((ROOT/'g2/manifests/g2-2.2.6.10.json').read_text())
OUTER=json.loads((BASE/'inventory/outer-container.json').read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
def file_sha(p): return sha((ROOT/p).read_bytes())
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def comp(cid): return next(x for x in TARGET['components'] if x['id']==cid)
def entry(cid): return next(x for x in OUTER['entry_spans'] if x['payload_id']==cid)
def add_map(cid, payload_start,payload_end,runtime_start=None,kind='identity'):
    e=entry(cid)
    return {'package_offset':[e['payload_offset'][0]+payload_start,e['payload_offset'][0]+payload_end],
            'payload_offset':[payload_start,payload_end],
            'runtime_address':[runtime_start,runtime_start+(payload_end-payload_start)] if runtime_start is not None else None,
            'transform':kind}
def main():
    open_cfw=load_module('g2_campaign_open_cfw','g2/tools/open_cfw.py')
    receipt={'schema_version':1,'campaign_id':CAMP,'source':'coordinator P1 read-only inventory','target_sha256':TARGET['bundle']['sha256'],'components':{}}
    # EM9305: nested record package parser performs an in-memory exact roundtrip only.
    cid='ble_em9305'; c=comp(cid); p=ROOT/c['local_payload_path']; b=p.read_bytes(); open_cfw.validate_em9305(b)
    em=load_module('g2_campaign_em9305_record_package','g2/components/em9305/source_image/record_package.py')
    parsed=em.parse_package(b); assert em.build_package(parsed.records,parsed.erase_sectors)==b
    assert (len(b),sha(b))==(c['size'],c['sha256']) and parsed.metadata_size==124 and len(parsed.records)==4
    records=[]; intervals=[{'start':0,'end':124,'kind':'container','evidence':'record-package header, four descriptors, 29 erase-sector entries and zero alignment padding validated'}]
    for i,r in enumerate(parsed.records):
        start=sum(len(x.payload) for x in parsed.records[:i])+parsed.metadata_size; end=start+len(r.payload)
        records.append({'record':i,'payload_offset':[start,end],'runtime_address':[r.address,r.address+len(r.payload)],'sha256':sha(r.payload),'kind':'unknown','entry_point':'unknown'})
        intervals.append({'start':start,'end':end,'kind':'unknown','evidence':'authenticated contiguous record with exact target address; internal code/data not classified in P1'})
    receipt['components'][cid]={'size':len(b),'sha256':sha(b),'validator':'open_cfw.validate_em9305','validation':'passed','package_parser':'record_package.parse_package; exact in-memory build_package roundtrip','records':records,'erase_sectors':list(parsed.erase_sectors),'images':[{'image_id':'ble_em9305:record_3_application','architecture':'ARCv2 EM; exact endian/ISA configuration remains to be checked against direct image-bound decoder evidence','endianness':'little-endian record/container fields; instruction mode pending corpus confirmation','address_space':'EM9305 record address space','mapping':add_map(cid,0,124,None,'metadata')},* [{'image_id':f'ble_em9305:record_{r["record"]}','architecture':'ARCv2 EM (inventory lead; assignment checks target-pinned processor/config provenance)','endianness':'little-endian; assignment checks exact image-bound decoder provenance','address_space':f'EM9305:{r["runtime_address"][0]:08x}','mapping':add_map(cid,*r['payload_offset'],r['runtime_address'][0]),'record':r} for r in records]],'coverage':{'intervals':intervals,'accounted_bytes':sum(x['end']-x['start'] for x in intervals),'total_bytes':len(b)}}
    # Touch: call only pure audit(blob), never its main/write_manifests entry point.
    cid='touch'; c=comp(cid); p=ROOT/c['local_payload_path']; b=p.read_bytes(); open_cfw.validate_touch(b)
    ti=load_module('g2_campaign_touch_identity','g2/tools/analyze_g2_touch_identity.py'); trep=ti.audit(b)
    regions=[]
    for n,s,e,h,k,status,note in ti.REGIONS:
        po0=32+s;po1=32+e
        cls='code' if k=='code+pools' else ('padding' if k.startswith('fill-') else 'data')
        regions.append({'name':n,'payload_offset':[po0,po1],'runtime_address':[s,e],'sha256':h,'kind':cls,'confidence':status,'evidence':note})
    assert sum(r['payload_offset'][1]-r['payload_offset'][0] for r in regions)==34432
    receipt['components'][cid]={'size':len(b),'sha256':sha(b),'validator':'open_cfw.validate_touch + analyze_g2_touch_identity.audit(bytes)','validation':'passed','audit_checks':len(trep['checks']),'wrapper':{'payload_offset':[0,32],'kind':'container','magic':'FWPK','record_payload_offset':32,'record_size':34432,'record_type':3},'image':{'image_id':'touch:application','architecture':'Infineon PSoC 4000T Cortex-M0+ (identity audit)','endianness':'little-endian','isa_mode':'Thumb/ARMv6-M','address_space':'touch flash','entry_vector':{'initial_sp':struct.unpack_from('<I',b,32)[0],'reset_vector_raw':struct.unpack_from('<I',b,36)[0]},'mapping':add_map(cid,32,len(b),0),'regions':regions},'coverage':{'intervals':[{'start':0,'end':32,'kind':'container','evidence':'FWPK record header; size/CRC/record validated'},* [{'start':r['payload_offset'][0],'end':r['payload_offset'][1],'kind':r['kind'],'evidence':r['evidence']} for r in regions]],'accounted_bytes':len(b),'total_bytes':len(b)}}
    # Case: read-only wrapper/additive checksum/vector validation. Keep app internals unknown.
    cid='case'; c=comp(cid); p=ROOT/c['local_payload_path']; b=p.read_bytes(); open_cfw.validate_case(b)
    raw=b[32:]; sp,rv=struct.unpack_from('<II',raw,0)
    receipt['components'][cid]={'size':len(b),'sha256':sha(b),'validator':'open_cfw.validate_case','validation':'passed','wrapper':{'payload_offset':[0,32],'kind':'container','magic':'EVEN','version':[1,2,57,0],'inner_length':len(raw),'reserved_zero':b[16:32]==bytes(16)},'image':{'image_id':'case:application','architecture':'STM32G0 Cortex-M0+ per authenticated manifest; exact ISA evidence to be independently verified','endianness':'little-endian vector words','isa_mode':'Thumb / Cortex-M0+ pending full processor attribution','address_space':'case STM32 logical bank-1 flash','entry_vector':{'initial_sp':sp,'reset_vector_raw':rv,'reset_address':rv&~1},'mapping':add_map(cid,32,len(b),0x08000000)},'coverage':{'intervals':[{'start':0,'end':32,'kind':'container','evidence':'EVEN wrapper length, additive checksum and reserved fields validated'},{'start':32,'end':len(b),'kind':'unknown','evidence':'loaded Cortex-M image; detailed code/data boundaries not classified in this inventory pass'}],'accounted_bytes':len(b),'total_bytes':len(b)}}
    # Apollo bootloader: vector validator confirms load range and Thumb reset, all internal bytes unknown.
    cid='apollo_bootloader'; c=comp(cid); p=ROOT/c['local_payload_path']; b=p.read_bytes(); open_cfw.validate_apollo_bootloader(b)
    sp,rv=struct.unpack_from('<II',b,0)
    receipt['components'][cid]={'size':len(b),'sha256':sha(b),'validator':'open_cfw.validate_apollo_bootloader','validation':'passed','image':{'image_id':'apollo_bootloader:payload-root','architecture':'Arm Cortex-M family indicated by valid M-profile vector/Thumb reset; exact core revision requires source/tool config confirmation','endianness':'little-endian','isa_mode':'Thumb state; exact profile pending','address_space':'Apollo510B internal MRAM','entry_vector':{'initial_sp':sp,'reset_vector_raw':rv,'reset_address':rv&~1},'mapping':add_map(cid,0,len(b),0x00410000),'external_dependencies':['secure resident bootloader','hardware/MMIO','external interfaces not fully inventoried']},'coverage':{'intervals':[{'start':0,'end':len(b),'kind':'unknown','evidence':'validated executable image range and first vector words; internal code/data boundary not classified in this inventory pass'}],'accounted_bytes':len(b),'total_bytes':len(b)}}
    source_paths=['g2/workflow/target.json','g2/manifests/g2-2.2.6.10.json','g2/tools/open_cfw.py','g2/components/em9305/source_image/record_package.py','g2/tools/analyze_g2_touch_identity.py']
    receipt['source_hashes']={x:file_sha(x) for x in source_paths}
    out=BASE/'inventory'/'secondary-payloads.json';out.write_text(json.dumps(receipt,indent=2)+'\n');print(out.relative_to(ROOT))
if __name__=='__main__': main()
