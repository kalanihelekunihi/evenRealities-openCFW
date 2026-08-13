#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/onboarding/onboarding.c."""

import csv, hashlib, json, struct, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-onboarding-controller-function-map.tsv"
CL = ROOT / "tools/manifests/g2-onboarding-controller-closure.tsv"
PM = ROOT / "tools/manifests/g2-onboarding-controller-provider-map.tsv"
PINS = {
    FM: "a98ea6013d5f1f0f1d7e31d6a9b544884337c7dba77330b9fba35d9e2d247596",
    CL: "3370b4e8f8885cba8e8adc30f13155f3a1703a9696da411dd2f8cffc0d89dedb",
    PM: "603e93603eb6ef824bd8ef95e4eb8b3ab4c635c4d93eae9b0a8a3e314cb3795a",
}
F = (
    (0x467FF0,0x467FFE),(0x467FFE,0x46800C),(0x46800C,0x46801E),
    (0x46801E,0x468034),(0x468034,0x46805A),(0x46805A,0x4680C8),
    (0x4680C8,0x4682AA),(0x4682AA,0x468484),(0x468484,0x468A30),
    (0x468A40,0x468C24),(0x468C68,0x468F04),(0x468F24,0x46908C),
)
PHYS = (0x467FF0, 0x46916C)
POOLS = ((0x468A30,0x468A40),(0x468C24,0x468C68),(0x468F04,0x468F24),(0x46908C,0x46916C))
EASY = {0x43CE9E,0x43D0CE,0x43D574}
LVGL = {0x43E2BC,0x44102E,0x44104C,0x441068,0x4412EC,0x4413CE,0x4413DE,0x4413FE,0x44140E,0x44BDEA,0x44DCE2,0x44DDEA,0x488F6A,0x498B50}
CMSIS = {0x44971C}
IAR = {0x43C0E4}
DATA_MANAGER = {0x47E470,0x47E51C,0x47E58E}
KVDB = {0x4A7832,0x4A7838}
PROTOBUF = {0x4A78D0}
BLE_CALLBACK = {0x4ABCC6,0x4ABD14}
FIRST = {0x443484,0x4434D0,0x45A568,0x464B2E,0x464BB2,0x464C36,0x465480,0x4A8E6C,0x4A99D0,0x4A9C0C,0x4ABA58,0x4ABBA4}
EXTERNAL_TARGET_COUNTS = {
    0x43C0E4:2,0x43CE9E:33,0x43D0CE:99,0x43D574:33,0x43E2BC:2,
    0x44102E:2,0x44104C:6,0x441068:2,0x4412EC:2,0x4413CE:2,
    0x4413DE:2,0x4413FE:2,0x44140E:2,0x443484:5,0x4434D0:6,
    0x44971C:1,0x44BDEA:2,0x44DCE2:2,0x44DDEA:2,0x45A568:11,
    0x464B2E:2,0x464BB2:4,0x464C36:2,0x465480:1,0x47E470:3,
    0x47E51C:1,0x47E58E:1,0x488F6A:2,0x498B50:2,0x4A7832:2,
    0x4A7838:2,0x4A78D0:1,0x4A8E6C:6,0x4A99D0:1,0x4A9C0C:1,
    0x4ABA58:1,0x4ABBA4:1,0x4ABCC6:1,0x4ABD14:1,
}
PATH_CELLS = {
    0x468A38:[0x46808E,0x4681AA,0x468210,0x46825C,0x468384,0x4683EA,0x468436,0x4684A6,0x468574,0x468600,0x46864A,0x4686C6,0x46877C,0x4687EC,0x468882,0x4688F0,0x468938,0x468996,0x4689FC],
    0x4690DC:[0x468A60,0x468AAE,0x468B00,0x468B58,0x468BE6,0x468C94,0x468CEC,0x468D60,0x468DBE,0x468ED6,0x468F46,0x468FB6,0x468FF2,0x46904A],
}
ENTRIES = [(0x442D6E,0x468034),(0x4680D8,0x467FF0),(0x4680F4,0x467FFE),(0x46829C,0x4680C8),(0x4682CE,0x467FFE),(0x468476,0x4682AA),(0x4684D4,0x46801E),(0x468824,0x46805A),(0x468D1A,0x4680C8),(0x468D8E,0x4682AA),(0x468F72,0x46801E),(0x49834E,0x468034),(0x4983F2,0x468034),(0x498432,0x468034),(0x49EC2E,0x46805A),(0x4C5A60,0x468034),(0x5850D2,0x46800C)]
STORED = [(0x469150,0x468A41),(0x6A45A4,0x468485),(0x6A45A8,0x468F25),(0x793670,0x468C69)]

def sh(value): return hashlib.sha256(value).hexdigest()
def cstring(blob,address):
    o=address-c.BASE;e=blob.find(b"\0",o)
    if o<0 or e<0: raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[o:e].decode("ascii")

def provenance():
    easy=json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
    cmsis=json.loads((ROOT/"third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel=json.loads((ROOT/"third_party/freertos-kernel/PROVENANCE.json").read_text())
    deps=json.loads((ROOT/"tools/manifests/g2-third-party-dependency-closure.json").read_text())
    by_name={row["family"]:row for row in deps["dependencies"]}
    if easy["upstream"]["selected_commit"]!="a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24": raise c.AuditError("EasyLogger changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]!="d213f261b5be6bb29a7cce8b84071706b72f4d53": raise c.AuditError("CMSIS-FreeRTOS changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"]!="2b7495b8535bdcb306dac29b9ded4cfb679d7e5c": raise c.AuditError("CMSIS_5 changed")
    if kernel["upstream"]["selected_commit"]!="def7d2df2b0506d3d249334974f51e427c17a41c": raise c.AuditError("FreeRTOS changed")
    if by_name["nanopb"]["selected_source_commit"]!="98bf4db69897b53434f3d0ba72e0a3ab1a902824": raise c.AuditError("nanopb changed")
    if "344c7c318047b7348e1be8572a9fd4260c251cfa" not in (ROOT/"third_party/lvgl/README.openCFW.md").read_text(): raise c.AuditError("LVGL changed")
    iar=(ROOT/"docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar: raise c.AuditError("IAR changed")

def analyze(image=IMAGE):
    blob=image.read_bytes()
    if len(blob)!=c.IMAGE_SIZE or sh(blob)!=c.IMAGE_SHA256: raise c.AuditError("image changed")
    for path,expected in PINS.items():
        if sh(path.read_bytes())!=expected: raise c.AuditError(f"manifest changed: {path.name}")
    provenance()
    with FM.open(newline="",encoding="utf-8") as handle: rows=list(csv.DictReader(handle,delimiter="\t"))
    if len(rows)!=len(F): raise c.AuditError("inventory changed")
    starts,interiors,instructions=set(),set(),{}
    body=b"";calls=[];indirect=[];anchored=0
    for row,bounds in zip(rows,F):
        start,end=int(row["stock_start"],0),int(row["stock_end_exclusive"],0);raw=c._slice(blob,start,end)
        if (start,end)!=bounds or len(raw)!=int(row["stock_bytes"]) or sh(raw)!=row["stock_sha256"]: raise c.AuditError("body changed")
        decoded,direct,dynamic=q._recover_function(blob,start,end)
        if c._uncovered(bounds,decoded): raise c.AuditError("uncovered function bytes")
        starts.add(start);interiors.update(range(start+2,end,2));instructions.update(decoded);calls+=direct;indirect+=dynamic;body+=raw;anchored+=row["source_path_anchor"]=="yes"
    calls.sort();code=b"".join(c._slice(blob,a,a+i.size) for a,i in sorted(instructions.items()))
    if anchored!=7 or len(body)!=4136 or sh(body)!="e64dd2dbff5d025d4a39083fbd38430578bf599084f6dca83ad6de7613cc9e21": raise c.AuditError("body closure changed")
    if code!=body or len(instructions)!=1558 or c._instruction_digest(sorted((a,i.size) for a,i in instructions.items()))!="e4734f51558eb8e2412195b1186ca1dc0b58d4c50fa5c2e7680327ea433f776d" or indirect: raise c.AuditError("instruction closure changed")
    noncode=b"".join(c._slice(blob,*bounds) for bounds in POOLS)
    if len(noncode)!=340 or sh(noncode)!="ca02be62085826488b4c15197466762738f7d99a345f902f047f2383317008dc": raise c.AuditError("pool closure changed")
    if sh(c._slice(blob,*PHYS))!="0bf00373acb4c371e9e067880a6adf26192efdb5e745fed685b3caf253ffa1da": raise c.AuditError("physical closure changed")
    if sh(c._slice(blob,0x467FE0,PHYS[0]))!="be3980824717d85dadbe5b48529012aaf39e6d25ab48afc26cb6f740a35b4ab1" or sh(c._slice(blob,PHYS[1],0x46917C))!="41a3c0c6991ac0885c3292b653566251d481cdeba7a866b1aa32a18c4895abd8": raise c.AuditError("boundary changed")
    external=Counter(target for _,target in calls if target not in starts);providers=(EASY,LVGL,CMSIS,IAR,DATA_MANAGER,KVDB,PROTOBUF,BLE_CALLBACK,FIRST)
    if len(calls)!=263 or sum(target in starts for _,target in calls)!=10 or c._pair_digest(calls)!="3fd750dd072eb38357f4e8082720fa0e3963854e45fb37312813bbeda2655f2f": raise c.AuditError("call topology changed")
    if external!=Counter(EXTERNAL_TARGET_COUNTS) or set(external)!=set().union(*providers): raise c.AuditError("provider targets changed")
    if tuple(sum(external[x] for x in provider) for provider in providers)!=(165,32,1,2,5,4,1,2,41): raise c.AuditError("provider accounting changed")
    entries=[];strict=[]
    for address in range(c.BASE,c.BASE+len(blob)-3,2):
        target=t._thumb_bl_target(blob,address)
        if target in starts: entries.append((address,target))
        elif target in interiors: strict.append((address,target))
    if entries!=ENTRIES or c._pair_digest(entries)!="44f78bda026b15b315123bfb8bb16c85e4cacb5b1ac84c2702be2746239b83db" or strict: raise c.AuditError("entry topology changed")
    encoded=starts|{start|1 for start in starts}
    stored=[(c.BASE+o,struct.unpack_from("<I",blob,o)[0]) for o in range(len(blob)-3) if struct.unpack_from("<I",blob,o)[0] in encoded]
    if stored!=STORED: raise c.AuditError("stored callbacks changed")
    if cstring(blob,0x704390)!=r"D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\onboarding.c": raise c.AuditError("path changed")
    for cell,refs in PATH_CELLS.items():
        if t.literal_references(blob,cell)!=refs: raise c.AuditError("path references changed")
    for address,expected in {0x76E8BC:"onboarding_check_start_disp",0x740AD0:"onboarding_darken_widget_colors_recursive",0x740B54:"onboarding_resume_widget_colors_recursive",0x762A10:"Onboarding_common_data_handler",0x762A50:"onboarding_ble_status_callback",0x762A70:"onboarding_page_event_handler",0x76E8D8:"Onboarding_ui_event_handler"}.items():
        if cstring(blob,address)!=expected: raise c.AuditError("symbol changed")
    overlay=json.loads((ROOT/"components/apollo_main/core_overlay/overlay.json").read_text())
    routed=any(item.get("path","").replace("\\","/").endswith("/onboarding/onboarding.c") for item in overlay["sources"])
    if routed: raise c.AuditError("unimplemented controller entered overlay")
    return {"schema_version":1,"analysis_mode":"read-only raw-image closure; corpus-independent","identity":{"image_sha256":c.IMAGE_SHA256,"retained_path":r"app\gui\onboarding\onboarding.c","embedded_third_party_definitions":[]},"surface":{"linked_functions":12,"ghidra_discovered_functions":9,"restored_functions":3,"path_anchored_functions":7,"baseline_path_anchored_functions":4,"body_bytes":4136,"physical_bytes":4476,"noncode_bytes":340,"reachable_instructions":1558,"direct_body_calls":263,"internal_direct_body_calls":10,"external_direct_body_calls":253,"indirect_body_calls":0,"direct_bl_entry_sites":17,"stored_entry_pointers":4,"strict_interior_ingress":0},"behavior":{"distinct_stored_callback_targets":3,"recursive_color_transform_pairs":1,"process_record_address":"0x200F4800","ble_resume_record_address":"0x200F47C4","common_data_protobuf_dispatch":True,"ble_disconnect_state_save":True,"ble_reconnect_state_restore":True,"ui_init_registers_ble_callback":True,"ui_exit_unregisters_ble_callback":True},"provider_boundary":{"easylogger_calls":165,"lvgl_calls":32,"cmsis_freertos_calls":1,"iar_memset_calls":2,"closed_onboarding_data_manager_calls":5,"closed_onboarding_kvdb_calls":4,"closed_onboarding_protobuf_calls":1,"closed_ble_callback_facade_calls":2,"first_party_policy_calls":41,"easylogger_commit":"a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24","lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","cmsis_freertos_commit":"d213f261b5be6bb29a7cce8b84071706b72f4d53","selected_nanopb_commit":"98bf4db69897b53434f3d0ba72e0a3ab1a902824","new_version_discriminator":False,"private_generating_commit_recoverable":False},"production":{"production_routed":False}}

if __name__=="__main__": print(json.dumps(analyze(),indent=2,sort_keys=True))
