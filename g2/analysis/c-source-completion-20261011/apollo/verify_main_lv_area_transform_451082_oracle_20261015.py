#!/usr/bin/env python3
"""Compare all Apollo area-alignment modes against stock Main."""
import hashlib,json,subprocess,tempfile
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn import arm_const as A

ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_area_transform_451082.c"
OUT=G2/"build/c-firmware/20261015/main-lv-area-transform-451082"
PAYLOAD_SHA="19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pack(values):return b"".join((x&0xffffffff).to_bytes(4,"little") for x in values)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    blob=(G2/"blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest()!=PAYLOAD_SHA:raise RuntimeError("Main payload changed")
    with tempfile.TemporaryDirectory() as directory:
        elf=Path(directory)/"test.elf"
        subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                        "-std=c11","-ffreestanding","-fno-builtin","-O2","-nostdlib",
                        "-Wl,-Ttext=0x100000","-Wl,-e,audio_uart_lv_area_transform_451082",
                        str(SOURCE),"-o",str(elf)],check=True)
        syms={p[2]:int(p[0],16) for line in subprocess.check_output(
            ["arm-none-eabi-nm",str(elf)],text=True).splitlines()
            if len(p:=line.split())==3}
        with elf.open("rb") as stream:
            segments=[(s["p_vaddr"],s.data()) for s in ELFFile(stream).iter_segments()
                      if s["p_type"]=="PT_LOAD"]
        def run(compiled,mode,parent_coords,child_coords,x,y):
            c=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
            c.mem_map(0x400000,0x400000);c.mem_write(0x438000,blob)
            c.mem_map(0x100000,0x100000)
            for address,data in segments:c.mem_write(address,data)
            c.mem_map(0x20000000,0x400000)
            parent,child=0x20010000,0x20011000
            c.mem_write(parent,pack(parent_coords));c.mem_write(child,pack(child_coords))
            c.reg_write(A.UC_ARM_REG_R0,parent)
            c.reg_write(A.UC_ARM_REG_R1,child)
            c.reg_write(A.UC_ARM_REG_R2,mode)
            c.reg_write(A.UC_ARM_REG_R3,x&0xffffffff)
            c.reg_write(A.UC_ARM_REG_SP,0x203ff000)
            c.mem_write(0x203ff000,pack((y,)))
            c.reg_write(A.UC_ARM_REG_LR,0x600001)
            entry=syms["audio_uart_lv_area_transform_451082"] if compiled else 0x451082
            c.emu_start(entry|1,0x600000,count=20000)
            return (c.reg_read(A.UC_ARM_REG_R0),bytes(c.mem_read(parent,16)),
                    bytes(c.mem_read(child,16)))
        geometries=[((10,20,109,69),(0,0,19,9),0,0),
                    ((-37,8,42,58),(-4,3,20,18),7,-5),
                    ((100,-100,133,-81),(5,-3,10,0),-11,13)]
        suite=[(mode,*geometry) for mode in range(256) for geometry in geometries]
        for case in suite:
            native,source=run(False,*case),run(True,*case)
            if native!=source:raise AssertionError((case,native,source))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_AREA_TRANSFORM_ORACLE",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "official_payload_sha256":PAYLOAD_SHA,
             "native_span":"0x451082..0x4513ad","cases":len(suite),
             "modes_tested":256,"geometries_per_mode":len(geometries),
             "limits":["All 8-bit mode values compared for three bounded geometries and signed offsets.",
                       "Extreme signed overflow and aliasing parent/child pointers are not covered."]}
    (OUT/"oracle.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(suite),sha(OUT/"oracle.json"))

if __name__=="__main__":main()
