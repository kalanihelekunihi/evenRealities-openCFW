#!/usr/bin/env python3
"""Fail-closed object/provider audit for conversate_ui_menu_page.c."""
from __future__ import annotations

import csv, hashlib, json, struct, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as indirect_common
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb

AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-conversate-ui-menu-page-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-conversate-ui-menu-page-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-conversate-ui-menu-page-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "f2a03f2dea0a33e05a87aacde04c98e6971f71527cb88da60f96a0d829f2e2ef",
    CLOSURE: "4c20cc7cfa6c4463d5c380414813eedf6a9ad9d7e97e672e02e3499f98b6e727",
    PROVIDER_MAP: "069aeac21cf15d91f50bd7bdcf8debe9c461797e3912cc81c06d618e7942cdce",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate_ui_menu_page.c"
PATH_RUN, PATH_CELL = 0x006E6EF8, 0x005B5CD4
FUNCTIONS = ((0x5B57AC,0x5B5886),(0x5B5886,0x5B58E8),(0x5B58E8,0x5B59FA),(0x5B59FA,0x5B5B96),(0x5B5B96,0x5B5BF0),(0x5B5BF0,0x5B5CC8),(0x5B5D2C,0x5B5D5E),(0x5B5D5E,0x5B5DE4))
PHYSICAL, PHYSICAL_SHA256 = (0x5B57AC,0x5B5DE4), "d2671c3a9b277491e2d1b76fa521ee498c56f607ec4bfde3dff07043fac563f9"
BODY_SHA256 = "e9f2b902996d7cc94a3ec8b085df479649b5ca7824250e3ade2f6af139735a65"
INSTRUCTION_COUNT, INSTRUCTION_DIGEST = 561, "03b626db50a5c6b5bd4502f478a8db0bb9ed0c6de9cc46079ba3cf4a22a86a23"
POOL, POOL_SHA256 = (0x5B5CC8,0x5B5D2C), "812d0ca20cce942426480e0468ad8e56521a88da7d2a4a185690f0adbb6541e3"
CALL_DIGEST = "a3b6e4643dd3580675918f06152a1738cad0858cedc7a09cb6ff6e0c546fd09e"
ENTRY_DIGEST = "9bf7c71ca7a1c14715e41fd5422d955f35afbe1890ca725c77f911244682aa9f"
STORED = [(0x68692C,0x5B58E8),(0x686934,0x5B59FA),(0x686B2C,0x5B59FA),(0x686B8C,0x5B5B96),(0x686B94,0x5B5BF0)]
STORED_DIGEST = "d02eef795960fecae35d9ff6f9f8c7e9c6c5d1f0f7fd5922cdb2e30fd0635d6f"
ENTRIES = [(0x5B1652,0x5B5886),(0x5B39AA,0x5B57AC),(0x5B52AE,0x5B57AC),(0x5B58A6,0x5B57AC),(0x5B6076,0x5B5D2C),(0x5B6180,0x5B5D2C),(0x5B6244,0x5B5D5E)]
EASY = {0x43CE9E,0x43D0CE,0x43D574}
LVGL = {0x43DE82,0x43DFA4,0x43F09A,0x43F4C0,0x43F66C,0x43FDDA,0x44104C,0x44120E,0x44121C,0x44122A,0x441238,0x44129E,0x44131C,0x44140E,0x44143E,0x44145A,0x44146A,0x44D878,0x44DCE2,0x44EA2E,0x499416,0x49942E}
FIRST_PARTY = {0x45FFFE,0x460084,0x46AE9C,0x47D8CE,0x5896FC,0x58BFB2,0x5B02E4,0x5B1072,0x5B1150,0x5B12BA,0x5B1E52,0x5B1F2E,0x5B43E8,0x5B5720,0x5B5752,0x5B577C}
STRINGS = {PATH_RUN: RETAINED_PATH,0x785880:"conversate.ui",0x752F64:"conversate_ui_send_start_request",0x748A0C:"conversate_ui_action_display_menu_page",0x73D2C8:"conversate_ui_action_menu_page_scroll_down",0x775F8C:"No next button found"}

def sha(value: bytes) -> str: return hashlib.sha256(value).hexdigest()

def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or sha(blob) != common.IMAGE_SHA256: raise AuditError("official image changed")
    for path, expected in INPUT_PINS.items():
        if sha(path.read_bytes()) != expected: raise AuditError(f"pinned input changed: {path.name}")
    easy = json.loads((ROOT/"third_party/easylogger/PROVENANCE.json").read_text())
    lvgl = json.loads((ROOT/"third_party/lvgl/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24" or lvgl["upstream"]["selected_commit"] != "344c7c318047b7348e1be8572a9fd4260c251cfa": raise AuditError("provider selection changed")
    with FUNCTION_MAP.open(newline="",encoding="utf8") as h: rows=list(csv.DictReader(h,delimiter="\t"))
    with PROVIDER_MAP.open(newline="",encoding="utf8") as h: providers=list(csv.DictReader(h,delimiter="\t"))
    if len(rows)!=8 or len(providers)!=3 or sum(int(r["edges"].split()[0]) for r in providers)!=101: raise AuditError("manifest inventory changed")
    starts,interiors,bodies,ins,calls,ind=set(),set(),[],{},[],[]; anchored=0
    for row,bounds in zip(rows,FUNCTIONS):
        a,z=int(row["stock_start"],0),int(row["stock_end_exclusive"],0)
        if (a,z)!=bounds: raise AuditError("bounds changed")
        body=common._slice(blob,a,z)
        if len(body)!=int(row["stock_bytes"]) or sha(body)!=row["stock_sha256"]: raise AuditError(f"body changed: {row['function']}")
        recovered,cs,ii=indirect_common._recover_function(blob,a,z)
        if common._uncovered(bounds,recovered): raise AuditError("uncovered function bytes")
        starts.add(a); interiors.update(range(a+2,z,2)); bodies.append(body); ins.update(recovered); calls+=cs; ind+=ii; anchored += row["source_path_anchor"]=="yes"
    calls.sort(); code=b"".join(common._slice(blob,a,a+i.size) for a,i in sorted(ins.items()))
    if anchored!=1 or len(code)!=1492 or code!=b"".join(bodies) or sha(code)!=BODY_SHA256 or len(ins)!=INSTRUCTION_COUNT or common._instruction_digest(sorted((a,i.size) for a,i in ins.items()))!=INSTRUCTION_DIGEST or ind: raise AuditError("instruction closure changed")
    if len(common._slice(blob,*PHYSICAL))!=1592 or sha(common._slice(blob,*PHYSICAL))!=PHYSICAL_SHA256 or len(common._slice(blob,*POOL))!=100 or sha(common._slice(blob,*POOL))!=POOL_SHA256: raise AuditError("physical object changed")
    if sha(common._slice(blob,0x5B5790,0x5B57AC))!="72067a80c0518a82a5ac2d4821ec88dfa873aa5c889bd32e185566df40bdb409" or sha(common._slice(blob,0x5B5DE4,0x5B5DEC))!="51c5b5458499805e5856ae40ce03ed8c5a5313963b4e619bf2297ebb728fa000": raise AuditError("adjacent boundary changed")
    external=Counter(y for _,y in calls if y not in starts)
    if len(calls)!=102 or sum(y in starts for _,y in calls)!=1 or common._pair_digest(calls)!=CALL_DIGEST or set(external)!=EASY|LVGL|FIRST_PARTY: raise AuditError("call topology changed")
    if sum(external[x] for x in EASY)!=35 or sum(external[x] for x in LVGL)!=34 or sum(external[x] for x in FIRST_PARTY)!=32: raise AuditError("provider counts changed")
    entries=[]; strict=[]
    for a in range(common.BASE,common.BASE+len(blob)-3,2):
        y=thumb._thumb_bl_target(blob,a)
        if y in starts: entries.append((a,y))
        elif y in interiors: strict.append((a,y))
    if entries!=ENTRIES or common._pair_digest(entries)!=ENTRY_DIGEST or strict: raise AuditError("BL ingress changed")
    stored=[]; strict_stored=[]
    for off in range(len(blob)-3):
        value=struct.unpack_from("<I",blob,off)[0]; target=value&~1
        if value&1 and target in starts: stored.append((common.BASE+off,target))
        elif value&1 and target in interiors: strict_stored.append((common.BASE+off,target))
    if stored!=STORED or common._pair_digest(stored)!=STORED_DIGEST or strict_stored: raise AuditError("stored callback topology changed")
    for a,s in STRINGS.items():
        if common._c_string(blob,a)!=s: raise AuditError(f"string changed at 0x{a:08x}")
    if thumb.literal_references(blob,PATH_CELL)!=[0x5B57EA,0x5B584E,0x5B5908,0x5B59D0,0x5B5C2C,0x5B5C7E]: raise AuditError("path references changed")
    return {"schema_version":1,"analysis_mode":"read-only; no hardware or flash operation","identity":{"image_sha256":common.IMAGE_SHA256,"retained_path":RETAINED_PATH,"physical_interval":[*PHYSICAL],"physical_sha256":PHYSICAL_SHA256,"embedded_third_party_definitions":[]},"surface":{"linked_functions":8,"ghidra_discovered_functions":2,"additional_recovered_functions":6,"path_anchored_functions":1,"body_bytes":1492,"reachable_instruction_bytes":1492,"outer_pool_regions":1,"outer_pool_bytes":100,"physical_bytes":1592,"direct_bl_entry_sites":7,"external_direct_bl_entry_sites":6,"direct_body_calls":102,"internal_direct_body_calls":1,"external_direct_body_calls":101,"indirect_body_calls":0,"stored_entry_pointers":5,"strict_interior_raw_bl_decodes":0,"unrecovered_direct_object_targets":0},"provider_boundary":{"direct_external_calls":101,"easylogger_calls":35,"lvgl_calls":34,"first_party_calls":32,"lvgl_commit":"344c7c318047b7348e1be8572a9fd4260c251cfa","new_version_discriminator":False},"behavior":{"stored_ui_callbacks":5,"menu_page_state":0x20071368,"selected_note_record_stride":0x88},"production":{"production_routed":False}}

def main()->int:
    print(json.dumps(analyze(),indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())
