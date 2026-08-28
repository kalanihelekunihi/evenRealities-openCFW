#!/usr/bin/env python3
"""Authenticate public am_hal_mspi_device_configure in the G2 bootloader."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl
ROOT=Path(__file__).resolve().parents[1];B=0x410000;ENTRY=0x424BE4;END=0x425066;SHA="baf84c7a01d10528a6367c12651b215274674bbfe206d9d26edddda387d85658"
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"research/admission/bootloader_mspi_device_configure_public_424be4/runtime_bootloader_mspi_device_configure_public_candidate.c";HEADER=SOURCE.with_suffix(".h");FIXTURE=SOURCE.parent/"host_fixture.c";REMOVED_TRANSCRIPT=ROOT/"components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c";BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-device-configure-public-424be4.tsv";UPSTREAM=ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c";OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
PINS={SOURCE:(2117,"f4c72a1b0751be9126ca19ca40795de73b38c624f7b9724606c49c71a9717af0"),HEADER:(1357,"9542865973dca6e1dec52c92fdb44c49eba78fef5b9dfea421052011e60ab7cd"),FIXTURE:(1427,"9e29f3b028bd7b4f4baa579768097631d67806f9e715c181a9060e5e66c83e80"),BOUNDARY:(2545,"0eb41b766c08f6740dd08ae307766e1eeec6f1c55bd039b5bbf7f208f008a184"),UPSTREAM:(168473,"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident");PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
CALLS=((0x424C36,0x4249A0),(0x424C66,0x422364),(0x424C7A,0x4222F0),(0x424CA4,0x4249A0),(0x424D16,0x422364),(0x424D2A,0x4222F0),(0x424D8E,0x4249A0),(0x425012,0x424120),(0x425026,0x424A18))
class AuditError(RuntimeError):pass
def req(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(p):
 d,s=apollo_overlay.parse_elf32(p);x=apollo_overlay.section_named(s,".text.open_cfw_bootloader_mspi_device_configure_public_424be4");b=d[int(x["offset"]):int(x["offset"])+int(x["size"])];r=sum(int(q["size"])//8 for q in s if int(q["type"])==9 and int(q["info"])==int(x["index"]));return b,r
def audit():
 req(not REMOVED_TRANSCRIPT.exists(),"raw executable transcript returned to public component source")
 for p,e in PINS.items():q=p.read_bytes();req((len(q),sha(q))==e,f"pin changed: {p.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();stock=image[ENTRY-B:END-B];req((len(stock),sha(stock))==(1154,SHA),"stock changed");callers=tuple(a for a in range(B,B+len(image)-3,2) if decode_bl(image,a)==ENTRY);req(callers==(0x42032E,0x42033E,0x420E36),"callers changed");req(tuple((a,decode_bl(image,a)) for a,_ in CALLS)==CALLS,"call graph changed")
 up=UPSTREAM.read_text()
 for t in ("am_hal_mspi_device_configure","AM_HAL_MSPI_CLK_250MHZ","am_hal_clkmgr_clock_release","am_hal_clkmgr_clock_request","mspi_device_configure(pMSPIState)","mspi_get_xip_off_min_delay"):
  req(t in up,f"upstream token changed: {t}")
 profiles={}
 for n,(cc,prefix) in PROFILES.items():
   v=subprocess.run([str(cc),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];req(v.startswith(prefix),"compiler changed");profiles[n]={"version":v,"exact_target_object_asserted":False}
 cfg=json.loads(OVERLAY.read_text());req(all(x["function"]!="open_cfw_bootloader_mspi_device_configure_public_424be4" for x in cfg["in_place_leaves"]),"deleted transcript remains production-routed")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];retained=next(x for x in regions if x["name"]=="bootloader_opaque_after_easylogger_transport");req((retained["target_address"],retained["size"],retained["address_status"])==(0x424A5A,6828,"official_blob"),"retained official MSPI boundary changed");req(retained["target_address"]<=ENTRY and END<=retained["target_address"]+retained["size"],"public configure span escaped retained official boundary")
 with tempfile.TemporaryDirectory(prefix="open-cfw-public-device-component-") as td:subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 req(c["source_owned_bytes"]+c["opaque_base_bytes"]==147296,"conservation changed");req(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"semantic-candidate / production-retained-official-boundary / hardware-validation-deferred-by-project-direction","stock":{"start":ENTRY,"end":END,"bytes":1154,"sha256":SHA},"callers":list(callers),"calls":[list(x) for x in CALLS],"profiles":profiles,"production":{"routed":False,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"boundary_status":"official_blob","next_frontier":END},"next_frontier":{"start":0x425066,"end":0x4250F0,"identity":"am_hal_mspi_enable","bytes":138,"status":"official_blob"},"hardware_validation":"deferred by project direction","hardware_operations":[]}
def main():p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "Public MSPI device configuration: exact candidate; production retains authenticated official bytes");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"public device-configure audit failed: {e}")
