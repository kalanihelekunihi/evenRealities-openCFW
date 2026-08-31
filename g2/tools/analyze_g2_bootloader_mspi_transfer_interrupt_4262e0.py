#!/usr/bin/env python3
"""Authenticate G2 MSPI blocking-transfer and interrupt source closure."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl
ROOT=Path(__file__).resolve().parents[1];B=0x410000;OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"research/admission/bootloader_mspi_transfer_interrupt_4262e0/runtime_bootloader_mspi_transfer_interrupt_candidate.c";HEADER=SOURCE.with_suffix(".h");FIXTURE=SOURCE.parent/"host_fixture.c";REMOVED_TRANSCRIPT=ROOT/"components/bootloader/core_overlay/runtime_mspi_transfer_interrupt_4262e0.c";BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-transfer-interrupt-4262e0.tsv";OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
SPANS={"open_cfw_bootloader_mspi_blocking_transfer_4262e0":(0x4262E0,0x42644C,"91c3b42f59f32e97e91133a7c66234488e6b0076c4dd4362a0ed7dd9d56492e3"),"open_cfw_bootloader_mspi_interrupt_enable_426450":(0x426450,0x426484,"ff601938062e67c168148c01471475c081038eb87938f8344c93afbf89f673e4"),"open_cfw_bootloader_mspi_interrupt_disable_426484":(0x426484,0x4264BA,"046eba05f4da245735e178e179220a0c666e75c2c377bf05f08fab8815900a40"),"open_cfw_bootloader_mspi_interrupt_status_get_4264ba":(0x4264BA,0x426506,"af49be2bc2098b45d294afc6ca8cc5f9f48eee343a0245cea95a9d832973c1c5")}
PINS={SOURCE:(1626,"c1936e16a49cadb67abeb93396f00b54f455844419523b38c6e9108d1f6cf381"),HEADER:(1516,"fc89ffb842dfa3aed6b04d369a7560406bc950414d6a0e5e76bb6711409f33b7"),FIXTURE:(1613,"078956d7b6d6c4f6605ed20591106f30df6ef2d9489a51db48797514aa404991"),BOUNDARY:(1869,"72f0e282e4e1a2e7c40e6071ad16d2e613112719da22fa62a3b6f709e8f8526c")};FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident");PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
class AuditError(RuntimeError):pass
def req(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(p,n):d,s=apollo_overlay.parse_elf32(p);x=apollo_overlay.section_named(s,".text."+n);b=d[int(x["offset"]):int(x["offset"])+int(x["size"])];r=sum(int(q["size"])//8 for q in s if int(q["type"])==9 and int(q["info"])==int(x["index"]));return b,r
def audit():
 req(not REMOVED_TRANSCRIPT.exists(),"raw executable transcript returned to public component source")
 for p,e in PINS.items():q=p.read_bytes();req((len(q),sha(q))==e,f"pin changed: {p.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();req(image[0x42644C-B:0x426450-B].hex()=="0000ff1f","gap changed")
 for n,(s,e,h) in SPANS.items():b=image[s-B:e-B];req((len(b),sha(b))==(e-s,h),f"stock {n} changed")
 req(tuple((a,decode_bl(image,a)) for a in (0x4263F6,0x42640C,0x426434))==((0x4263F6,0x423E8A),(0x42640C,0x423E40),(0x426434,0x41D246)),"transfer calls changed")
 profiles={}
 for pn,(cc,prefix) in PROFILES.items():
   v=subprocess.run([str(cc),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];req(v.startswith(prefix),"compiler changed");profiles[pn]={"version":v,"exact_target_object_asserted":False}
 leaves={x["function"]:x for x in json.loads(OVERLAY.read_text())["in_place_leaves"]}
 for n in SPANS:req(n not in leaves,f"deleted transcript remains production-routed: {n}")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];retained=next(x for x in regions if x["name"]=="bootloader_opaque_after_easylogger_transport");req((retained["target_address"],retained["size"],retained["address_status"])==(0x424A5A,6828,"official_blob"),"retained official MSPI boundary changed")
 with tempfile.TemporaryDirectory(prefix="open-cfw-transfer-int-component-") as td:subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 req(c["source_owned_bytes"]+c["opaque_base_bytes"]==147350,"conservation changed");req(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"semantic-candidate / production-retained-official-boundary / hardware-validation-blocked-by-unavailable-physical-evidence","profiles":profiles,"production":{"routed":False,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"boundary_status":"official_blob","next_frontier":0x426506},"bounded_mspi_code_closed":False,"candidate_semantics_closed":True,"adjacent_control":{"start":0x4251C0,"end":0x4262E0,"status":"official_blob"},"hardware_validation":"blocked by unavailable physical evidence","hardware_operations":[]}
def main():p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "MSPI transfer/interrupt: exact candidate; production retains authenticated official bytes");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"transfer/interrupt audit failed: {e}")
