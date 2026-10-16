#!/usr/bin/env python3
"""Bind seven bounded calibration RAM cells into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/hub_calibration_ram_slots.c"
BASE=G2/"build/c-firmware/20261015/main-lv-label-text-helpers-49abd4/apollo-main-lv-label-text-helpers-49abd4.o"
OUT=G2/"build/c-firmware/20261015/main-hub-calibration-ram-slots"
IMAGE=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SLOTS={
    "audio_uart_calibration_snapshot_200749a8":(0x200749a8,0x4a7750,4),
    "audio_uart_calibration_success_primary_200749ac":(0x200749ac,0x4a7754,4),
    "audio_uart_calibration_success_secondary_200749b0":(0x200749b0,0x4a7760,4),
    "audio_uart_calibration_panel_left_200749b4":(0x200749b4,0x4a7768,4),
    "audio_uart_calibration_panel_right_200749b8":(0x200749b8,0x4a776c,4),
    "audio_uart_calibration_panel_mark_200749bc":(0x200749bc,0x4a7770,4),
    "audio_uart_calibration_status_2007501c":(0x2007501c,0x467fec,1),
}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path,flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g",flag,str(path)],text=True).splitlines()}

def main():
    if hashlib.sha256(IMAGE).hexdigest()!=IMAGE_SHA:
        raise RuntimeError("Official Main payload changed")
    for name,(address,literal,_) in SLOTS.items():
        actual=int.from_bytes(IMAGE[literal-0x438000:literal-0x438000+4],"little")
        if actual!=address:
            raise RuntimeError(f"Calibration literal changed: {name}")
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"hub_calibration_ram_slots.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2",
                    "-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=set(SLOTS) or symbols(obj,"-u"):
        raise RuntimeError("Calibration slot symbol contract changed")
    rows={parts[-1]:parts for line in subprocess.check_output(
        ["arm-none-eabi-nm","-g","-S",str(obj)],text=True).splitlines()
        if len(parts:=line.split())==4 and parts[-1] in SLOTS}
    if set(rows)!=set(SLOTS) or any(int(rows[name][1],16)!=size
                                    for name,(_,_,size) in SLOTS.items()):
        raise RuntimeError("Calibration slot extents changed")
    before=symbols(BASE,"-u")
    if len(before)!=221 or not set(SLOTS)<=before:
        raise RuntimeError("Calibration slot base contract changed")
    linked=OUT/"apollo-main-hub-calibration-ram-slots.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    after=symbols(linked,"-u")
    if before-after!=set(SLOTS) or after-before or len(after)!=214:
        raise RuntimeError("Calibration slot link delta changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_HUB_CALIBRATION_RAM_SLOTS_C",
             "official_payload_sha256":IMAGE_SHA,
             "native_literals":{name:{"ram":hex(address),"literal":hex(literal),
                                      "observed_bytes":size}
                                for name,(address,literal,size) in SLOTS.items()},
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object":str(obj.relative_to(ROOT)),"object_sha256":sha(obj),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "source_owned_symbols":sorted(SLOTS),"imports_resolved":sorted(SLOTS),
             "imports_added":[],"unresolved_before":221,"unresolved_after":214,
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["Six four-byte pointer cells and one byte status cell are source-owned. Native startup values, final RAM placement and hardware behavior remain unverified."]}
    path=OUT/"receipt.json"
    path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],221,214,sha(path))

if __name__=="__main__":main()
