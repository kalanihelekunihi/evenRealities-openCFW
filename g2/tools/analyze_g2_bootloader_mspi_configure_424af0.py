#!/usr/bin/env python3
"""Authenticate the G2 bootloader am_hal_mspi_configure source closure."""
from __future__ import annotations
import argparse, hashlib, json, struct, subprocess, tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl

ROOT=Path(__file__).resolve().parents[1];RUN_BASE=0x410000;ENTRY=0x424AF0;END=0x424BD4
STOCK_SHA="7e844f8b690703208e8e932371914cc19506c0d8adf682bfe03a28e55357ad8c"
COMPILED_SIZE=152;COMPILED_SHA="f48e9bead432163e13d495026fb798ea87c640638ea6ec79bfa179a3d766bad1";REPLACED_STOCK_SHA="2b81ab47153b316f2a0d1803cdf2a36eda6c7d4aa57125c878f6d8d032836862"
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mspi_configure_424af0.c"
HEADER=ROOT/"components/bootloader/core_overlay/runtime_mspi_configure_424af0.h";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mspi_configure_host.c"
BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-configure-424af0.tsv"
UPSTREAM=ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c"
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
PINS={SOURCE:(3980,"f05aebfb3914e67a37a692216df76b57842a49e2851dfdac12cefa1c66c827ec"),HEADER:(1356,"f5bcdaab84d4d7c09be0879513c79efb2ed9b27bc1684f7adf8521cbf38113dd"),FIXTURE:(3876,"05194a6c572e4999baf5a4d28409806c89c2a9b5af422a50ccf6448809f1f038"),BOUNDARY:(2515,"ee81be0373cc88119ede9f11c4474161c3de60662dfb8020cd2b4473d6e9036c"),UPSTREAM:(168473,"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fno-jump-tables","-fno-vectorize","-fno-slp-vectorize","-mpure-code","-Wall","-Wextra","-Werror","-fno-ident")
PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
class AuditError(RuntimeError):pass
def require(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(path):
 d,s=apollo_overlay.parse_elf32(path);x=apollo_overlay.section_named(s,".text.open_cfw_bootloader_mspi_configure_424af0");b=d[int(x["offset"]):int(x["offset"])+int(x["size"])];r=sum(int(q["size"])//8 for q in s if int(q["type"])==9 and int(q["info"])==int(x["index"]));return b,r
def audit():
 for p,e in PINS.items():
  q=p.read_bytes();require((len(q),sha(q))==e,f"input pin changed: {p.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();stock=image[ENTRY-RUN_BASE:END-RUN_BASE];require((len(stock),sha(stock))==(228,STOCK_SHA),"stock changed")
 require(sha(stock[:COMPILED_SIZE])==REPLACED_STOCK_SHA,"replaced stock prefix changed")
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
   for label,src in (("structured",SOURCE),):
    out=Path(td)/(name+label+".o");subprocess.run([str(cc),*FLAGS,"-c",str(src),"-o",str(out)],check=True,capture_output=True,text=True);b,r=extract(out);require((len(b),sha(b),r)==(COMPILED_SIZE,COMPILED_SHA,0),f"{name} {label} changed");rows[label]=sha(b)
   profiles[name]={"version":ver,"objects":rows}
 cfg=json.loads(OVERLAY.read_text());text=SOURCE.read_text();require(".byte" not in text and "__asm__" not in text,"structured configure source regressed to raw encoding");leaves={x["function"]:x for x in cfg["in_place_leaves"]};leaf=leaves["open_cfw_bootloader_mspi_configure_424af0"];require((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["relocations"])==(ENTRY,COMPILED_SIZE,COMPILED_SHA,[]),"configure route changed")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];by_name={x["name"]:x for x in regions};routed=by_name["bootloader_mspi_configure_424af0_source_in_place"];require((routed["target_address"],routed["size"],routed["address_status"])==(ENTRY,COMPILED_SIZE,"source_compiled"),"source configure boundary changed");retained=by_name["bootloader_opaque_after_easylogger_transport"];require((retained["target_address"],retained["size"],retained["address_status"])==(ENTRY+COMPILED_SIZE,6526,"official_blob"),"retained official MSPI boundary changed")
 with tempfile.TemporaryDirectory(prefix="open-cfw-mspi-configure-component-") as td:
  subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 require(c["source_owned_bytes"]+c["opaque_base_bytes"]==146994,"byte conservation changed");require(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence","stock":{"start":ENTRY,"end":END,"bytes":228,"sha256":STOCK_SHA},"callers":list(callers),"profiles":profiles,"production":{"routed":True,"compiled_bytes":COMPILED_SIZE,"compiled_sha256":COMPILED_SHA,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"boundary_status":"source_compiled","next_frontier":ENTRY+COMPILED_SIZE},"next_code_frontier":{"start":0x424BE4,"end":0x425066,"identity":"am_hal_mspi_device_configure","bytes":1154,"status":"official_blob"},"hardware_validation":"blocked by unavailable physical evidence","hardware_operations":[]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "Bootloader MSPI configure: structured source routed in place");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"MSPI configure audit failed: {e}")
