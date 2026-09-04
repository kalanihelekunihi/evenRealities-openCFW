#!/usr/bin/env python3
"""Authenticate the G2 public am_hal_mspi_device_configure source closure."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
import apollo_overlay
from analyze_g2_bootloader_mspi_device_configure_424120 import decode_bl

ROOT=Path(__file__).resolve().parents[1];RUN_BASE=0x410000;ENTRY=0x424BE4;END=0x425066
COMPILED_SIZE=672;COMPILED_SHA="344f6705aac2638cd47e64b83a76058b16f00dc9640ccb6edd9ea9d52072cf56";UNRELOCATED_SHA="7dcafb51bf0566d580cd6de6f1d90e473d78da82db97bd6e12f15be0da2d9658"
STOCK_SHA="baf84c7a01d10528a6367c12651b215274674bbfe206d9d26edddda387d85658";REPLACED_STOCK_SHA="6bab21c83cc97181377b3cdc7a318e3a959326eb97946eae14e0278571365a94"
OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c";HEADER=SOURCE.with_suffix(".h");FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mspi_device_configure_public_host.c";BOUNDARY=ROOT/"tools/manifests/g2-bootloader-mspi-device-configure-public-424be4.tsv";UPSTREAM=ROOT/"third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c";OVERLAY=ROOT/"components/bootloader/core_overlay/overlay.json";MANIFEST=ROOT/"manifests/g2-2.2.6.10-core-source.json";BUILDER=ROOT/"components/bootloader/core_overlay/build_component.py"
PINS={SOURCE:(9044,"61d15896c3ab37265ba83b1de3b1312a7e7dd58ca847f7f991e840ebdd6f89c0"),HEADER:(2203,"f18e1f47bc57aa02f642fff57228f542ee709d9e266b294597e63397389cd49c"),FIXTURE:(3193,"f8e80e092bcd87f6610a6b452f8bd2e3a377ea55469deef3d7ee842f6a8a5f7f"),BOUNDARY:(2567,"861f4540491f9f817617be56e83f8b36296ba63cd1a671daaefb3599abf50aad"),UPSTREAM:(168473,"5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f")}
FLAGS=("-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-fno-jump-tables","-fno-vectorize","-fno-slp-vectorize","-mpure-code","-Wall","-Wextra","-Werror","-fno-ident")
PROFILES={"apple-clang":(Path("/usr/bin/clang"),"Apple clang version 21.0.0"),"linux-clang":(Path("/opt/homebrew/opt/llvm@22/bin/clang"),"Homebrew clang version 22.1.8")}
CALLS=((0x424C36,0x4249A0),(0x424C66,0x422364),(0x424C7A,0x4222F0),(0x424CA4,0x4249A0),(0x424D16,0x422364),(0x424D2A,0x4222F0),(0x424D8E,0x4249A0),(0x425012,0x424120),(0x425026,0x424A18))
RELOCATIONS=[
 {"offset":74,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mspi_clkgen_ctrl_4249a0","symbol_type":"STT_NOTYPE","target_address":0x4249A0},
 {"offset":164,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_clock_release_422364","symbol_type":"STT_NOTYPE","target_address":0x422364},
 {"offset":174,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_clock_request_4222f0","symbol_type":"STT_NOTYPE","target_address":0x4222F0},
 {"offset":210,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mspi_clkgen_ctrl_4249a0","symbol_type":"STT_NOTYPE","target_address":0x4249A0},
 {"offset":648,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mspi_device_configure_424120","symbol_type":"STT_NOTYPE","target_address":0x424120},
 {"offset":666,"type":"R_ARM_THM_CALL","symbol":"open_cfw_bootloader_mspi_xip_off_delay_424a18","symbol_type":"STT_NOTYPE","target_address":0x424A18},
]
class AuditError(RuntimeError):pass
def req(value,message):
 if not value:raise AuditError(message)
def sha(value):return hashlib.sha256(value).hexdigest()
def extract(path):
 return apollo_overlay.extract_in_place_function_section(path,"open_cfw_bootloader_mspi_device_configure_public_424be4",runtime_address=ENTRY,relocation_configs=RELOCATIONS,strict_relocation_contract=True,allow_discarded_alloc_sections=True)
def audit():
 for path,expected in PINS.items():
  payload=path.read_bytes();req((len(payload),sha(payload))==expected,f"input pin changed: {path.relative_to(ROOT)}")
 image=OFFICIAL.read_bytes();stock=image[ENTRY-RUN_BASE:END-RUN_BASE];req((len(stock),sha(stock))==(1154,STOCK_SHA),"stock changed");req(sha(stock[:COMPILED_SIZE])==REPLACED_STOCK_SHA,"replaced stock prefix changed")
 callers=tuple(address for address in range(RUN_BASE,RUN_BASE+len(image)-3,2) if decode_bl(image,address)==ENTRY);req(callers==(0x42032E,0x42033E,0x420E36),"callers changed");req(tuple((address,decode_bl(image,address)) for address,_ in CALLS)==CALLS,"stock call graph changed")
 upstream=UPSTREAM.read_text()
 for token in ("am_hal_mspi_device_configure","AM_HAL_MSPI_CLK_250MHZ","am_hal_clkmgr_clock_release","am_hal_clkmgr_clock_request","mspi_device_configure(pMSPIState)","mspi_get_xip_off_min_delay"):req(token in upstream,f"upstream token changed: {token}")
 profiles={}
 with tempfile.TemporaryDirectory(prefix="open-cfw-public-device-audit-") as temporary:
  for name,(compiler,prefix) in PROFILES.items():
   version=subprocess.run([str(compiler),"--version"],check=True,capture_output=True,text=True).stdout.splitlines()[0];req(version.startswith(prefix),f"{name} compiler changed");output=Path(temporary)/f"{name}.o";subprocess.run([str(compiler),*FLAGS,"-c",str(SOURCE),"-o",str(output)],check=True,capture_output=True,text=True);body,report=extract(output);req((len(body),sha(body),report["unrelocated_sha256"],report["relocation_count"])==(COMPILED_SIZE,COMPILED_SHA,UNRELOCATED_SHA,6),f"{name} object changed");profiles[name]={"version":version,"sha256":sha(body),"relocations":report["relocations"]}
 text=SOURCE.read_text();req(".byte" not in text and "__asm__" not in text,"structured source regressed to raw encoding")
 config=json.loads(OVERLAY.read_text());leaf={item["function"]:item for item in config["in_place_leaves"]}["open_cfw_bootloader_mspi_device_configure_public_424be4"];req((leaf["runtime_address"],leaf["expected"]["size"],leaf["expected"]["sha256"],leaf["expected"]["unrelocated_sha256"],leaf["relocations"])==(ENTRY,COMPILED_SIZE,COMPILED_SHA,UNRELOCATED_SHA,RELOCATIONS),"production route changed")
 regions=json.loads(MANIFEST.read_text())["component_overrides"]["apollo_bootloader"]["regions"];by_name={item["name"]:item for item in regions};literal=by_name["bootloader_mspi_device_config_literals_424bd4_opaque"];routed=by_name["bootloader_mspi_device_configure_public_424be4_source_in_place"];retained=by_name["bootloader_mspi_device_configure_public_unreachable_tail_424e84_425066_official"];req((literal["target_address"],literal["size"],literal["address_status"])==(0x424B88,92,"official_blob"),"predecessor literal boundary changed");req((routed["target_address"],routed["size"],routed["address_status"])==(ENTRY,COMPILED_SIZE,"source_compiled"),"source boundary changed");req((retained["target_address"],retained["size"],retained["address_status"])==(ENTRY+COMPILED_SIZE,482,"official_blob"),"retained unreachable-tail boundary changed")
 with tempfile.TemporaryDirectory(prefix="open-cfw-public-device-component-") as temporary:subprocess.run(["python3",str(BUILDER),"--output-dir",temporary],cwd=ROOT,check=True,capture_output=True,text=True);component=json.loads((Path(temporary)/"build-report.json").read_text())["component"]
 req(component["source_owned_bytes"]+component["opaque_base_bytes"]==146994,"byte conservation changed")
 return {"status":"structured-source-dual-profile / production-source-in-place / hardware-validation-blocked-by-unavailable-physical-evidence","stock":{"start":ENTRY,"end":END,"bytes":1154,"sha256":STOCK_SHA},"callers":list(callers),"calls":[list(item) for item in CALLS],"profiles":profiles,"production":{"routed":True,"compiled_bytes":COMPILED_SIZE,"compiled_sha256":COMPILED_SHA,"source_owned_bytes":component["source_owned_bytes"],"retained_official_bytes":component["opaque_base_bytes"],"boundary_status":"source_compiled","next_frontier":ENTRY+COMPILED_SIZE},"next_code_frontier":{"start":0x425066,"end":0x4250F0,"identity":"am_hal_mspi_enable","bytes":138,"source_compiled_bytes":128,"retained_unreachable_tail_bytes":10,"status":"source-compiled-with-retained-unreachable-tail"},"hardware_validation":"blocked by unavailable physical evidence","hardware_operations":[]}
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--json",action="store_true");result=audit();print(json.dumps(result,indent=2,sort_keys=True) if parser.parse_args().json else "Public MSPI device configuration: structured source routed in place");return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (AuditError,subprocess.CalledProcessError) as error:raise SystemExit(f"public device-configure audit failed: {error}")
