#!/usr/bin/env python3
"""Prepare, promote, and package the G2 Cordio security-service closure."""
import argparse, importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("g2_sec_base",ROOT/"tools/integrate_g2_lvgl_font_manager_overlay.py")
base=importlib.util.module_from_spec(SPEC);assert SPEC.loader is not None;SPEC.loader.exec_module(base)
base.SOURCE=ROOT/"components/apollo_main/core_overlay/cordio_sec_api.c"
base.RECORDER="apple-cordio-sec-api-record";base.LEAF_DEFINE_PREFIX="OPEN_CFW_CORDIO_SEC_";base.PATCH_PREFIX="replace_cordio_sec_api_"
base.EVIDENCE="docs/research/cordio-sec-api-source-recovery.md"
base.LICENSE="Apache-2.0"
base.ORIGIN="Packetcraft Cordio r20.05c Apache-2.0 security-service queueing, CMAC framing, ECC byte order, and HCI completion behavior"
base.SELECTORS=(
 ("HCI_CALLBACK","open_cfw_cordio_sec_hci_callback",0x00536234,0x00536324),
 ("INIT","open_cfw_cordio_sec_init",0x00536324,0x0053634E),
 ("RANDOM","open_cfw_cordio_sec_random",0x0053634E,0x005363AE),
 ("LE_ENCRYPT","open_cfw_cordio_sec_le_encrypt",0x005363AE,0x005363E4),
 ("NEXT_TOKEN","open_cfw_cordio_sec_next_token",0x005363FC,0x00536426),
 ("AES","open_cfw_cordio_sec_aes",0x00536426,0x00536470),
 ("AES_CALLBACK","open_cfw_cordio_sec_aes_callback",0x00536470,0x0053648E),
 ("AES_INIT","open_cfw_cordio_sec_aes_init",0x0053648E,0x00536496),
 ("CMAC_BLOCK","open_cfw_cordio_sec_cmac_block",0x005364A4,0x0053653A),
 ("CMAC_SUBKEY1","open_cfw_cordio_sec_cmac_subkey1",0x0053653A,0x0053655C),
 ("CMAC_SHIFT","open_cfw_cordio_sec_cmac_shift",0x0053655C,0x005365A6),
 ("CMAC_SUBKEY2","open_cfw_cordio_sec_cmac_subkey2",0x005365A6,0x00536608),
 ("CMAC_COMPLETE","open_cfw_cordio_sec_cmac_complete",0x00536608,0x00536620),
 ("CMAC_CALLBACK","open_cfw_cordio_sec_cmac_callback",0x00536620,0x0053665C),
 ("CMAC","open_cfw_cordio_sec_cmac",0x0053665C,0x005366CC),
 ("CMAC_INIT","open_cfw_cordio_sec_cmac_init",0x005366CC,0x005366D4),
 ("ECC_CALLBACK","open_cfw_cordio_sec_ecc_callback",0x005366DC,0x0053673E),
 ("ECC_KEY","open_cfw_cordio_sec_ecc_key",0x0053673E,0x00536774),
 ("ECC_SECRET","open_cfw_cordio_sec_ecc_secret",0x00536774,0x005367CA),
 ("ECC_INIT","open_cfw_cordio_sec_ecc_init",0x005367CA,0x005367D2),
)
base.PROVIDERS={
 "open_cfw_retained_cordio_sec_alloc":0x004BF99E,"open_cfw_retained_cordio_sec_free":0x004BF9B0,
 "open_cfw_retained_cordio_sec_send":0x004BF9BA,"open_cfw_retained_cordio_sec_enqueue":0x004BF9DE,"open_cfw_retained_cordio_sec_dequeue":0x004BF9EC,
 "open_cfw_retained_cordio_sec_memcpy":0x00439BE4,"open_cfw_retained_cordio_sec_memset":0x0043C0E4,
 "open_cfw_retained_cordio_sec_reverse":0x0056D8F0,"open_cfw_retained_cordio_sec_reverse_copy":0x0056D8C4,
 "open_cfw_retained_cordio_sec_copy128":0x00542A44,"open_cfw_retained_cordio_sec_xor128":0x00542A60,
 "open_cfw_retained_cordio_sec_hci_register":0x005367EA,"open_cfw_retained_cordio_sec_hci_random":0x0052B304,
 "open_cfw_retained_cordio_sec_hci_encrypt":0x0052B266,"open_cfw_retained_cordio_sec_hci_public_key":0x0052B1F4,
 "open_cfw_retained_cordio_sec_hci_dh_key":0x0052B20E,
}

def sync_manifest():
 m=json.loads(base.MANIFEST.read_text());r=json.loads(base.REPORT.read_text());run=json.loads(base.CONFIG.read_text())["run_base"]
 override=m["component_overrides"]["apollo_main"];provider=override["provider"];pp=ROOT/provider["path"];provider["size"]=pp.stat().st_size;provider["sha256"]=base.sha(pp.read_bytes())
 override["function"]="Even Apollo510B main firmware with maintained source overlays including Cordio security, system startup, display, sensor, health, and case policy"
 regions=[x for x in override["regions"] if not x["name"].startswith("cordio_sec_api_")]
 stock=sorted(base.SELECTORS,key=lambda x:x[2]);first,last=stock[0][2],stock[-1][3]
 oi=next(i for i,x in enumerate(regions) if x.get("address_status")=="official_blob" and x.get("target_address",0)<=first and x.get("target_address",0)+x["size"]>=last)
 owner=regions[oi];os,oe=owner["target_address"],owner["target_address"]+owner["size"];split=[]
 if os<first:
  before=dict(owner);before["size"]=first-os;split.append(before)
 cursor=first
 for i,(_s,f,a,z) in enumerate(stock,1):
  if cursor<a:split.append(base.region(f"cordio_sec_api_retained_gap_{i:02d}","Official Cordio security literal/alignment bytes","official_blob",32+cursor-run,a-cursor,cursor,f"apollo510b/main-opaque-cordio-sec-gap-0x{cursor:08x}.bin"))
  split.append(base.region(f"cordio_sec_api_{i:02d}_source_replacement",f"Generated guarded redirect replacing {f}","generated_source_entry_replacement",32+a-run,z-a,a,f"apollo510b/main-generated-cordio-sec-{i:02d}-0x{a:08x}.bin"));cursor=z
 if cursor<oe:split.append(base.region("opaque_after_cordio_sec_api","Official Apollo bytes after source-replaced Cordio security service","official_blob",32+cursor-run,oe-cursor,cursor,f"apollo510b/main-opaque-0x{cursor:08x}.bin"))
 regions[oi:oi+1]=split
 leaves=[x for x in r["relocated_leaves"] if x.get("source",{}).get("path","").endswith("cordio_sec_api.c")]
 for x in leaves:
  e,p=x["extraction"],x["placement"];f=e["function"];slug=f.removeprefix("open_cfw_cordio_sec_").replace("_","-")
  if p["padding_before"]:
   a=p["runtime_address"]-p["padding_before"];regions.append(base.region(f"cordio_sec_api_{slug}_overlay_alignment",f"Generated alignment before {f}","generated_alignment",32+a-run,p["padding_before"],a,f"apollo510b/main-source-cordio-sec-{slug}-alignment.bin"))
  regions.append(base.region(f"cordio_sec_api_{slug}_source_text",f"Apache-2.0 Cordio security leaf ({f})","source_compiled",32+p["runtime_address"]-run,e["size"],p["runtime_address"],f"apollo510b/main-source-cordio-sec-{slug}-0x{p['runtime_address']:08x}.bin"))
 regions.sort(key=lambda x:x["file_offset"]);final=max(x["file_offset"]+x["size"] for x in regions)
 if final!=provider["size"]:raise SystemExit(f"manifest tiling ends at {final}, provider has {provider['size']} bytes")
 override["regions"]=regions;m["package"].pop("expected_size",None);m["package"].pop("expected_sha256",None);base.MANIFEST.write_text(json.dumps(m,indent=2)+"\n")

def main():
 p=argparse.ArgumentParser();p.add_argument("action",choices=("prepare","promote","sync-manifest","pin-package"));a=p.parse_args().action
 if a=="prepare":base.prepare()
 elif a=="promote":base.promote()
 elif a=="sync-manifest":sync_manifest()
 else:base.pin_package()
if __name__=="__main__":main()
