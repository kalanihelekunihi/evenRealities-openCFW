#!/usr/bin/env python3
"""Fail-closed whole-object/provider audit for ui_quicklist_page.c."""
import csv, hashlib, json, struct, sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target

IMAGE=ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
FM=ROOT/'tools/manifests/g2-ui-quicklist-page-function-map.tsv'
PM=ROOT/'tools/manifests/g2-ui-quicklist-page-provider-map.tsv'
CL=ROOT/'tools/manifests/g2-ui-quicklist-page-closure.tsv'
PINS={FM:'61432e4d1efcec0a6d7837aea19d54e41906e2b12dffaafc89050229d10d17fc',PM:'059932e4f9b3d8013a0dec05e6da13277576ceab8ebd5b230026a1a1b29f2c8f',CL:'7b124c7cd33cead430434aac54adcfdc46205a568c6471f64c67b2eddb92eada'}
PHYS=(0x004F5596,0x004FB1C0)
PATH=0x006F7538
PATH_CELLS=(0x004F6310,0x004F6D38,0x004F7588,0x004F81DC,0x004F8914,0x004F9AF8,0x004FA400,0x004FB07C)
EASY={0x0043CE9E,0x0043D0CE,0x0043D574};CMSIS={0x004490CC};IAR={0x00439BE4,0x00439C04,0x0043C0E4}
LVGL={0x43DE82,0x43DED4,0x43DFA4,0x43E0E0,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,0x43F4C0,0x43F506,0x43F568,0x43F66C,0x43F6B8,0x43F6D6,0x43FC70,0x43FCE0,0x43FD9E,0x43FDDA,0x44104C,0x441094,0x4410A6,0x441164,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,0x44129E,0x4412EC,0x44131C,0x44133A,0x441378,0x441386,0x441394,0x4413A2,0x4413B0,0x44140E,0x44142E,0x44143E,0x44145A,0x44146A,0x441488,0x44D7B8,0x44D878,0x44DCE2,0x44DDEA,0x44E368,0x44E3CA,0x44E498,0x44E4BC,0x44EA04,0x4503D6,0x450408,0x4506CE,0x45A568,0x498668,0x498680,0x499416,0x49942E,0x499678}

def sh(data): return hashlib.sha256(data).hexdigest()
def cstring(blob,address):
    off=address-common.BASE;end=blob.find(b'\0',off)
    if off<0 or end<off: raise common.AuditError('unterminated path')
    return blob[off:end].decode('ascii')

def analyze(image=IMAGE):
    blob=image.read_bytes()
    if len(blob)!=common.IMAGE_SIZE or sh(blob)!=common.IMAGE_SHA256: raise common.AuditError('official image changed')
    for path,digest in PINS.items():
        if sh(path.read_bytes())!=digest: raise common.AuditError(f'manifest changed: {path.name}')
    easy=json.loads((ROOT/'third_party/easylogger/PROVENANCE.json').read_text())
    cmsis=json.loads((ROOT/'third_party/cmsis-freertos/PROVENANCE.json').read_text())
    if easy['upstream']['selected_commit']!='a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24' or cmsis['upstreams']['cmsis_freertos']['selected_commit']!='d213f261b5be6bb29a7cce8b84071706b72f4d53': raise common.AuditError('provider provenance changed')
    if '344c7c318047b7348e1be8572a9fd4260c251cfa' not in (ROOT/'third_party/lvgl/README.openCFW.md').read_text(): raise common.AuditError('LVGL provenance changed')
    with FM.open(newline='',encoding='utf8') as handle: rows=list(csv.DictReader(handle,delimiter='\t'))
    funcs=[(int(r['stock_start'],0),int(r['stock_end_exclusive'],0)) for r in rows]
    if len(funcs)!=80 or sum(r['path_anchored']=='yes' for r in rows)!=43: raise common.AuditError('function inventory changed')
    starts={a for a,_ in funcs};ins={};calls=[];dynamic=[];body=b''
    for start,end in funcs:
        recovered,direct,indirect=cfg._recover_function(blob,start,end)
        if common._uncovered((start,end),recovered): raise common.AuditError(f'uncovered body at 0x{start:08X}')
        if set(ins)&set(recovered): raise common.AuditError('instruction overlap')
        ins.update(recovered);calls+=direct;dynamic+=indirect;body+=common._slice(blob,start,end)
    calls.sort()
    if len(body)!=21886 or sh(body)!='ff0c6bf6cfe04e5de386358def184b9146839a26d1d83cd08e78b993e68b501e' or len(ins)!=8233 or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!='ebb944887828b3c161fcb0e38a79fef8788ec4e83cc84930cbd8507341da24d0' or dynamic: raise common.AuditError('body closure changed')
    covered=set()
    for address,instruction in ins.items(): covered.update(range(address,address+instruction.size))
    outer=bytes(v for a,v in zip(range(*PHYS),common._slice(blob,*PHYS)) if a not in covered)
    if len(outer)!=1708 or sh(outer)!='868d9a08120744b2c65f12ef140bf46f7f392827a43002b6ba420595fc012138' or sh(common._slice(blob,*PHYS))!='f44c3d005fd997e8b105a0c4d63cb887eb96aee43bb777597c138e50bf1dd121': raise common.AuditError('physical closure changed')
    if sh(common._slice(blob,PHYS[0]-16,PHYS[0]))!='71d6f511f8aedf85cd822f4c41e5596cb7c42f5f3cb1882954fb79134df1f4e7' or sh(common._slice(blob,PHYS[1],PHYS[1]+16))!='72eb732d8169f978a5c6d8c2a8bc8650905e60574cdebc35c0e97cf8a0a62351': raise common.AuditError('adjacent boundary changed')
    ext=Counter(t for _,t in calls if t not in starts);first=set(ext)-LVGL-EASY-CMSIS-IAR
    if len(calls)!=1144 or sum(t in starts for _,t in calls)!=154 or common._pair_digest(calls)!='55deedf7948ae287904319a2501094823836de28ad1f39daa1cce94301b18d04' or tuple(sum(ext[t] for t in s) for s in (LVGL,EASY,CMSIS,IAR,first))!=(415,465,5,24,81) or len(first)!=30: raise common.AuditError('provider closure changed')
    interiors=set(ins)-starts;entries=[];strict=[];noncode=[];wide=[];wide_strict=[]
    for address in range(common.BASE,common.BASE+len(blob)-3,2):
        target=thumb._thumb_bl_target(blob,address)
        if target in starts: entries.append((address,target))
        elif target in interiors: strict.append((address,target))
        elif target is not None and PHYS[0]<=target<PHYS[1]: noncode.append((address,target))
        first_half,second_half=struct.unpack('<HH',common._slice(blob,address,address+4));target=wide_branch_target(address,first_half,second_half)
        if target in starts: wide.append((address,target))
        elif target in interiors: wide_strict.append((address,target))
    if len(entries)!=164 or common._pair_digest(entries)!='3d846e68a6f1c4dc4b054d6fff3dca40827996b038f9e50a8bb801914fc64481' or strict or noncode or wide or wide_strict: raise common.AuditError('whole-image branch closure changed')
    raw=[];stored=[]
    for off in range(len(blob)-3):
        value=struct.unpack_from('<I',blob,off)[0];target=value&~1
        if target in starts or target in interiors:
            raw.append((common.BASE+off,value,target))
            if target in starts and (common.BASE+off)%4==0 and value&1: stored.append((common.BASE+off,value))
    if len(raw)!=22 or sh(b''.join(struct.pack('<III',*x) for x in raw))!='6da1cebf53bad61d79ba7b1628c40ceb80626c2cbb9fed5350438bab65a2bec9' or len(stored)!=15 or common._pair_digest(stored)!='a6c57578572e2526fc9a684e582176c7c9413f8f4d7edc57529f3bf81d65bbcc': raise common.AuditError('stored-entry closure changed')
    if cstring(blob,PATH)!=r'D:\01_workspace\s200_ap510b_iar_git\app\gui\quicklist\ui_quicklist_page.c': raise common.AuditError('path changed')
    refs=sorted((cell,a) for cell in PATH_CELLS for a in thumb.literal_references(blob,cell))
    if len(refs)!=94 or common._pair_digest(refs)!='0068824bc3568c1bfbdb1d413c17292c1632e20a8e72069cbdce655d4ac470cd': raise common.AuditError('path references changed')
    overlay=json.loads((ROOT/'components/apollo_main/core_overlay/overlay.json').read_text())
    routed=any('ui_quicklist_page' in item.get('path','').lower() for item in overlay['sources'])
    if routed: raise common.AuditError('unimplemented object routed')
    return {'schema_version':1,'identity':{'image_sha256':common.IMAGE_SHA256,'retained_path':r'app\gui\quicklist\ui_quicklist_page.c','embedded_third_party_definitions':[]},'surface':{'linked_functions':80,'ghidra_discovered_functions':63,'path_anchored_functions':43,'restored_non_anchor_functions':17,'body_bytes':21886,'physical_bytes':23594,'outer_pool_bytes':1708,'reachable_instructions':8233,'direct_body_calls':1144,'internal_direct_body_calls':154,'external_direct_body_calls':990,'indirect_body_calls':0,'direct_bl_entry_sites':164,'stored_function_pointers':15,'strict_interior_ingress':0},'provider_boundary':{'lvgl_calls':415,'easylogger_calls':465,'cmsis_freertos_calls':5,'iar_runtime_calls':24,'first_party_calls':81,'lvgl_commit':'344c7c318047b7348e1be8572a9fd4260c251cfa','easylogger_commit':'a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24','cmsis_freertos_commit':'d213f261b5be6bb29a7cce8b84071706b72f4d53','historical_quicklist_commit':None,'new_version_discriminator':False},'production':{'production_routed':routed}}

if __name__=='__main__': print(json.dumps(analyze(),indent=2,sort_keys=True))
