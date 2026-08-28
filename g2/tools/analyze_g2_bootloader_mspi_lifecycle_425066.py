#!/usr/bin/env python3
"""Authenticate G2 bootloader MSPI enable/disable/deinitialize closure."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl
ROOT=Path(__file__).resolve().parents[1];B=0x410000;OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"research/admission/bootloader_mspi_lifecycle_425066/runtime_bootloader_mspi_lifecycle_candidate.c";HEADER=SOURCE.with_suffix(".h");FIXTURE=SOURCE.parent/"host_fixture.c";REMOVED_TRANSCRIPT=ROOT/"components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c";BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-lifecycle-425066.tsv";UPSTREAM=ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c";OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
SPANS={"open_cfw_bootloader_mspi_enable_425066":(0x425066,0x4250F0,"3e8eafec68e5f33ec128fd64c1386692323e9b175993c267d6a2bb7ec3ac155c"),"open_cfw_bootloader_mspi_disable_4250f0":(0x4250F0,0x425166,"d99c52bed1418f48aab03ebc6fafc8faa36b93f3a980e0bbbacaa423aa7566bc"),"open_cfw_bootloader_mspi_deinitialize_42516c":(0x42516C,0x4251A4,"17e2e38a57e5a1669a591cf61ad92ff4b5ca8a1747673512410737ac452d689b")}
PINS={SOURCE:(1526,"1f836451ab83a17367d639bff89c0096d3cb4558ac094fa7090a1440bfd101b3"),HEADER:(1229,"879652bf84d77a7e8714e36650d5994c438c86170df81d182a6de01d456cecb7"),FIXTURE:(1497,"9cd37e2c4caee7d9c0cf3bfc68da82de0297dc933a4394f0f34efa5543fd7d79"),BOUNDARY:(2771,"56e43b632c9d231868fec474a6bbdd76d2ad90698553db03f8eb378c0d4e728c"),UPSTREAM:(168473,"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident");PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
class AuditError(RuntimeError):pass
def req(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(p,n):d,s=apollo_overlay.parse_elf32(p);x=apollo_overlay.section_named(s,".text."+n);b=d[int(x["offset"]):int(x["offset"])+int(x["size"])];r=sum(int(q["size"])//8 for q in s if int(q["type"])==9 and int(q["info"])==int(x["index"]));return b,r
def audit():
 req(not REMOVED_TRANSCRIPT.exists(),"raw executable transcript returned to public component source")
 for p,e in PINS.items():q=p.read_bytes();req((len(q),sha(q))==e,f"pin changed: {p.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();callers={0x425066:(0x420378,0x420E5A),0x4250F0:(0x420E10,0x42518E),0x42516C:(0x42031C,0x42036C,0x4203A6)}
 for n,(s,e,h) in SPANS.items():b=image[s-B:e-B];req((len(b),sha(b))==(e-s,h),f"stock {n} changed");req(tuple(a for a in range(B,B+len(image)-3,2) if decode_bl(image,a)==s)==callers[s],f"callers {n} changed")
 req(image[0x425166-B:0x42516C-B].hex()=="0000ffff0700","lifecycle gap changed")
 for a,t in ((0x42509C,0x423F28),(0x425132,0x423FAC),(0x42513C,0x423F54),(0x42515E,0x41D1C0),(0x42518E,0x4250F0)):req(decode_bl(image,a)==t,f"call edge {a:#x} changed")
 up=UPSTREAM.read_text()
 for t in ("am_hal_mspi_enable","am_hal_mspi_disable","am_hal_mspi_deinitialize","mspi_cq_init","mspi_cq_term","ui32XIPOffMinDelay"):req(t in up,f"upstream token changed: {t}")
 profiles={}
 for pn,(cc,prefix) in PROFILES.items():
   v=subprocess.run([str(cc),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];req(v.startswith(prefix),"compiler changed");profiles[pn]={"version":v,"exact_target_object_asserted":False}
 cfg=json.loads(OVERLAY.read_text());leaves={x["function"]:x for x in cfg["in_place_leaves"]}
 for n in SPANS:req(n not in leaves,f"deleted transcript remains production-routed: {n}")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];retained=next(x for x in regions if x["name"]=="bootloader_opaque_after_easylogger_transport");req((retained["target_address"],retained["size"],retained["address_status"])==(0x424A5A,6828,"official_blob"),"retained official MSPI boundary changed")
 with tempfile.TemporaryDirectory(prefix="open-cfw-lifecycle-component-") as td:subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 req(c["source_owned_bytes"]+c["opaque_base_bytes"]==147296,"conservation changed");req(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"semantic-candidate / production-retained-official-boundary / hardware-validation-deferred-by-project-direction","functions":{n:{"start":s,"end":e,"bytes":e-s,"sha256":h} for n,(s,e,h) in SPANS.items()},"profiles":profiles,"production":{"routed":False,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"boundary_status":"official_blob","next_frontier":0x4251A4},"successor":{"identity":"am_hal_mspi_control","status":"official_blob","start":0x4251C0,"end":0x4262E0,"retained_prefix_bytes":28},"hardware_validation":"deferred by project direction","hardware_operations":[]}
def main():p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "MSPI lifecycle: exact candidate; production retains authenticated official bytes");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"lifecycle audit failed: {e}")
