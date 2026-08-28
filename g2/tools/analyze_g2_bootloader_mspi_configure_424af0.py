#!/usr/bin/env python3
"""Authenticate the G2 bootloader am_hal_mspi_configure source closure."""
from __future__ import annotations
import argparse, hashlib, json, struct, subprocess, tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl

ROOT=Path(__file__).resolve().parents[1];RUN_BASE=0x410000;ENTRY=0x424AF0;END=0x424BD4
STOCK_SHA="7e844f8b690703208e8e932371914cc19506c0d8adf682bfe03a28e55357ad8c"
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE=ROOT/"research/admission/bootloader_mspi_configure_424af0/runtime_bootloader_mspi_configure_candidate.c"
HEADER=SOURCE.with_suffix(".h");FIXTURE=SOURCE.parent/"host_fixture.c"
REMOVED_TRANSCRIPT=ROOT/"components/bootloader/core_overlay/runtime_mspi_configure_424af0.c"
BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-configure-424af0.tsv"
UPSTREAM=ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
PINS={SOURCE:(3108,"878b971854f3e4c9704c465e2624887e86797d0ccd1b1bb1a6b239adcaecf772"),HEADER:(925,"e4e23602893491fff99ec2fd13f04b4ae6386879af70ab36d639bfc593b8e2af"),FIXTURE:(2227,"7bcf6dafcc0a9105b48c155f0eacb9e4ff25f5ba52cae0f4d13a5fe8d4f93c72"),BOUNDARY:(2493,"26771781606a1420e4d004943f709ed314a56a34627b87320bd9fb286ce4beed"),UPSTREAM:(168473,"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident")
PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
class AuditError(RuntimeError):pass
def require(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(path):
 d,s=apollo_overlay.parse_elf32(path);x=apollo_overlay.section_named(s,".text.open_cfw_bootloader_mspi_configure_424af0");b=d[int(x["offset"]):int(x["offset"])+int(x["size"])];r=sum(int(q["size"])//8 for q in s if int(q["type"])==9 and int(q["info"])==int(x["index"]));return b,r
def audit():
 require(not REMOVED_TRANSCRIPT.exists(),"raw executable transcript returned to public component source")
 for p,e in PINS.items():
  q=p.read_bytes();require((len(q),sha(q))==e,f"input pin changed: {p.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();stock=image[ENTRY-RUN_BASE:END-RUN_BASE];require((len(stock),sha(stock))==(228,STOCK_SHA),"stock changed")
 callers=tuple(a for a in range(RUN_BASE,RUN_BASE+len(image)-3,2) if decode_bl(image,a)==ENTRY);require(callers==(0x4202EE,),"callers changed")
 require(image[0x424AEA-RUN_BASE:0x424AEC-RUN_BASE]==b"\0\0","predecessor alignment changed")
 for a,v in ((0x424AEC,0x2001CAA0),(0x4251AC,0x2001CAA0),(0x4251B0,0x01BEBEBE),(0x4251B4,0x20080000)):
  require(struct.unpack_from("<I",image,a-RUN_BASE)[0]==v,f"literal {a:#x} changed")
 up=UPSTREAM.read_text()
 for t in ("am_hal_mspi_configure","DEV0XIP_b.XIPEN0 = 0","DEV0SCRAMBLING = 0","ui32MaxPending","AM_HAL_MSPI_MAX_CQ_ENTRIES","bClkonD4"):
  require(t in up,f"upstream token changed: {t}")
 profiles={}
 with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-configure-audit-") as td:
  for name,(cc,prefix) in PROFILES.items():
   ver=subprocess.run([str(cc),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];require(ver.startswith(prefix),"compiler changed");rows={}
   for label,src in (("candidate",SOURCE),):
    out=Path(td)/(name+label+".o");subprocess.run([str(cc),*FLAGS,"-c",str(src),"-o",str(out)],check=True,capture_output=True,text=True);b,r=extract(out);require((len(b),sha(b),r)==(228,STOCK_SHA,0),f"{name} {label} changed");require(b==stock,f"{name} {label} not stock-exact");rows[label]=sha(b)
   profiles[name]={"version":ver,"objects":rows}
 cfg=json.loads(OVERLAY.read_text());require(all(x["function"]!="open_cfw_bootloader_mspi_configure_424af0" for x in cfg["in_place_leaves"]),"deleted transcript remains production-routed")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];retained=next(x for x in regions if x["name"]=="bootloader_opaque_after_easylogger_transport");require((retained["target_address"],retained["size"],retained["address_status"])==(0x424A5A,6828,"official_blob"),"retained official MSPI boundary changed");require(retained["target_address"]<=ENTRY and END<=retained["target_address"]+retained["size"],"configure span escaped retained official boundary")
 with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-configure-component-") as td:
  subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 require(c["source_owned_bytes"]+c["opaque_base_bytes"]==147296,"byte conservation changed");require(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"candidate-exact-dual-profile / production-retained-official-boundary / hardware-validation-deferred-by-project-direction","stock":{"start":ENTRY,"end":END,"bytes":228,"sha256":STOCK_SHA},"callers":list(callers),"profiles":profiles,"production":{"routed":False,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"boundary_status":"official_blob","next_frontier":END},"next_code_frontier":{"start":0x424BE4,"end":0x425066,"identity":"am_hal_mspi_device_configure","bytes":1154,"status":"official_blob"},"hardware_validation":"deferred by project direction","hardware_operations":[]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "Bootloader MSPI configure: exact candidate; production retains authenticated official bytes");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"MSPI configure audit failed: {e}")
