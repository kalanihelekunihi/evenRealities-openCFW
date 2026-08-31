#!/usr/bin/env python3
"""Authenticate the G2 bootloader mspi_clkgen_ctrl source closure."""
from __future__ import annotations
import argparse, hashlib, json, struct, subprocess, tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl

ROOT=Path(__file__).resolve().parents[1]; RUN_BASE=0x410000
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE=ROOT/"research/admission/bootloader_mspi_clkgen_ctrl_4249a0/runtime_bootloader_mspi_clkgen_ctrl_candidate.c"
HEADER=SOURCE.with_suffix(".h");FIXTURE=SOURCE.parent/"host_fixture.c"
PRODUCTION=ROOT/"components/bootloader/core_overlay/runtime_mspi_clkgen_ctrl_4249a0.c"
XIP_SOURCE=SOURCE.parent/"runtime_bootloader_mspi_xip_off_delay_candidate.c"
XIP_PRODUCTION=ROOT/"components/bootloader/core_overlay/runtime_mspi_xip_off_delay_424a18.c"
BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-clkgen-ctrl-4249a0.tsv"
OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json"
MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json"
BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
ENTRY=0x4249A0;END=0x424A18
STOCK_SHA="86e27ef6ed8e0e1ba9c0f2ba553376ae57fcf0154bba95f37d1eb4a6ef7c3dd0"
RAW_SHA="43c19e55e5d8b9810f0cf96b81554a3f4cc62f980a8047468a2ad8645d064909"
CALLERS=(0x424C36,0x424CA4,0x424D8E,0x42590C,0x4259DE,0x426886,0x426A1E,0x426BE4)
RELOCS=((10,"open_cfw_bootloader_critical_save_41b8ec",0x41B8EC),(84,"open_cfw_bootloader_retained_delay_us_41d1c0",0x41D1C0))
PINS={SOURCE:(2715,"909aa5b18001aa05c7ed64cdcd3fbd70b1fa6c02e19ac92c404c955a7d5010b5"),HEADER:(1288,"76f87a812e401ff0b5da73024ce7b8792f49e762e04aa1e95ed5e5b577741c69"),FIXTURE:(1947,"ee0694436d49743f6da7cc3fdb000d7d68e06d93920f4b47ee2b8bcc2840fe06"),PRODUCTION:(1107,"2b7f364930310395ee2b3c3d8f7c786029591d0328caa099373cc0359ab1f8e4"),XIP_SOURCE:(1159,"9a5aec4286a22fa910d3c86e3ee4960e967e47e08978d126c023014b2cfe9449"),XIP_PRODUCTION:(904,"06bc26a164c241543c6c44284edfe103daf5314cca64c517fb9b12a7cdd9d525"),BOUNDARY:(1810,"d91523e1019540e14baf0f611c626baf3a035285b5bc13348dac9e072e5b0ebd")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident")
PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
class AuditError(RuntimeError):pass
def req(x,m):
 if not x:raise AuditError(m)
def sha(x):return hashlib.sha256(x).hexdigest()
def extract(p):
 d,s=apollo_overlay.parse_elf32(p);x=apollo_overlay.section_named(s,".text.open_cfw_bootloader_mspi_clkgen_ctrl_4249a0");body=d[int(x["offset"]):int(x["offset"])+int(x["size"])];sym=apollo_overlay.section_named(s,".symtab");st=s[int(sym["link"])];strings=d[int(st["offset"]):int(st["offset"])+int(st["size"])];names=[]
 for i in range(int(sym["size"])//16):
  f=struct.unpack_from("<IIIBBH",d,int(sym["offset"])+i*16);names.append(apollo_overlay.elf_string(strings,f[0],"symbol"))
 rel=[]
 for q in s:
  if int(q["type"])==9 and int(q["info"])==int(x["index"]):
   for i in range(int(q["size"])//8):
    o,v=struct.unpack_from("<II",d,int(q["offset"])+i*8);rel.append((o,v&255,names[v>>8]))
 return body,rel
def audit():
 for p,e in PINS.items():q=p.read_bytes();req((len(q),sha(q))==e,f"pin changed: {p}")
 image=OFFICIAL.read_bytes();stock=image[ENTRY-RUN_BASE:END-RUN_BASE];req((len(stock),sha(stock))==(120,STOCK_SHA),"stock changed")
 callers=tuple(a for a in range(RUN_BASE,RUN_BASE+len(image)-3,2) if decode_bl(image,a)==ENTRY);req(callers==CALLERS,"callers changed")
 req(struct.unpack_from("<I",image,0x4251A8-RUN_BASE)[0]==0x40004110,"register literal changed")
 profiles={}
 with tempfile.TemporaryDirectory(prefix="open-cfw-clkgen-audit-") as td:
  for name,(cc,prefix) in PROFILES.items():
   ver=subprocess.run([str(cc),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];req(ver.startswith(prefix),"compiler changed");out=Path(td)/(name+".o");subprocess.run([str(cc),*FLAGS,"-c",str(SOURCE),"-o",str(out)],check=True,capture_output=True,text=True);body,rel=extract(out);req((len(body),sha(body))==(120,RAW_SHA),"raw body changed");req(rel==[(o,10,s) for o,s,_ in RELOCS],"relocations changed");linked=bytearray(body)
   for o,_,t in RELOCS:linked[o:o+4]=apollo_overlay.encode_thumb_branch(ENTRY+o,t,link=True)
   req(bytes(linked)==stock,"linked body changed");profiles[name]={"version":ver,"sha256":sha(linked)}
   xipout=Path(td)/(name+"-xip.o");subprocess.run([str(cc),*FLAGS,"-c",str(XIP_SOURCE),"-o",str(xipout)],check=True,capture_output=True,text=True);xd,xs=apollo_overlay.parse_elf32(xipout);xx=apollo_overlay.section_named(xs,".text.open_cfw_bootloader_mspi_xip_off_delay_424a18");xb=xd[int(xx["offset"]):int(xx["offset"])+int(xx["size"])];req((len(xb),sha(xb))==(66,"cee39c273a2725778729f4b8182d878ba06d55ec3a614cf1b2289990b6a4ceac"),"xip delay body changed")
 cfg=json.loads(OVERLAY.read_text());leaf=next(x for x in cfg["in_place_leaves"] if x["function"]=="open_cfw_bootloader_mspi_clkgen_ctrl_4249a0");req((leaf["runtime_address"],leaf["expected"]["sha256"])==(ENTRY,STOCK_SHA),"overlay changed")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];by_name={x["name"]:x for x in regions};expected={"bootloader_mspi_clkgen_ctrl_4249a0_source_in_place":(ENTRY,120,"source_compiled"),"bootloader_mspi_xip_off_delay_424a18_source_in_place":(0x424A18,66,"source_compiled"),"bootloader_opaque_after_easylogger_transport":(0x424A5A,6828,"official_blob")}
 for key,value in expected.items():req(key in by_name,f"region disappeared: {key}");row=by_name[key];req((row["target_address"],row["size"],row["address_status"])==value,f"region changed: {key}")
 successor=by_name["bootloader_opaque_after_easylogger_transport"]
 with tempfile.TemporaryDirectory(prefix="open-cfw-clkgen-component-") as td:subprocess.run(["python3",str(BUILDER),"--output-dir",td],cwd=ROOT,check=True,capture_output=True,text=True);c=json.loads((Path(td)/"build-report.json").read_text())["component"]
 req(c["source_owned_bytes"]+c["opaque_base_bytes"]+c["generated_patch_site_bytes"]+c["generated_alignment_bytes"]==c["size"],"accounting changed")
 req(c["source_owned_in_place_bytes"]<=c["source_owned_bytes"],"in-place accounting changed")
 return {"status":"production-routed-exact-dual-profile-source / hardware-validation-blocked-by-unavailable-physical-evidence","callers":list(callers),"profiles":profiles,"production":{"routed":True,"source_owned_bytes":c["source_owned_bytes"],"retained_official_bytes":c["opaque_base_bytes"],"next_frontier":successor["target_address"]},"next_frontier":{"start":0x424A5A,"end":0x424AEA,"identity":"am_hal_mspi_initialize","bytes":144},"hardware_validation":"blocked by unavailable physical evidence","hardware_operations":[]}
def main():
 p=argparse.ArgumentParser();p.add_argument("--json",action="store_true");r=audit();print(json.dumps(r,indent=2,sort_keys=True) if p.parse_args().json else "Bootloader clock/XIP-delay: exact production source; hardware validation blocked by unavailable physical evidence");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as e:raise SystemExit(f"clkgen audit failed: {e}")
