#!/usr/bin/env python3
"""Bind source-owned LV base descriptor, name, and callback relocations."""
import hashlib,json,subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile
ROOT=Path(__file__).resolve().parents[4];G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_lv_base_class_7564f8.c"
OUT=G2/"build/c-firmware/20261015/main-lv-base-class-7564f8"
BASE=G2/"build/c-firmware/20261015/main-lv-base-state-helpers/apollo-main-lv-base-state-helpers.o"
FACTORY=G2/"build/c-firmware/20261015/main-page-factory-43de82/receipt.json"
OWNED={"audio_uart_lv_base_class_7564f8","audio_uart_lv_base_class_name_78dc64"}
CALLBACKS={"audio_uart_lv_base_ctor_43e33e","audio_uart_lv_base_dtor_43e3de","audio_uart_lv_base_event_43e7d2"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,mode):return {s.split()[-1] for s in subprocess.check_output(["arm-none-eabi-nm",mode,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    obj=OUT/"display_lv_base_class_7564f8.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb","-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall","-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    factory=json.loads(FACTORY.read_text())
    if factory["status"]!="PASS_EXPERIMENTAL_MAIN_PAGE_FACTORY_43DE82_C" or factory["class_source_sha256"]!=sha(SOURCE):raise RuntimeError("factory class oracle changed")
    if symbols(obj,"--defined-only")!=OWNED or symbols(obj,"-u")!=CALLBACKS:raise RuntimeError("class symbol contract changed")
    with obj.open("rb") as stream:
        elf=ELFFile(stream);tab=elf.get_section_by_name(".symtab")
        names={i:s.name for i,s in enumerate(tab.iter_symbols())}
        class_symbol=tab.get_symbol_by_name("audio_uart_lv_base_class_7564f8")[0]
        offset=class_symbol["st_value"]
        rel=[]
        for section in elf.iter_sections():
            if section["sh_type"]=="SHT_REL":
                rel.extend((entry["r_offset"]-offset,names[entry["r_info_sym"]],entry["r_info_type"])
                           for entry in section.iter_relocations())
    expected={(4,"audio_uart_lv_base_ctor_43e33e",2),(8,"audio_uart_lv_base_dtor_43e3de",2),(12,"audio_uart_lv_base_event_43e7d2",2),(20,"audio_uart_lv_base_class_name_78dc64",2)}
    if set(rel)!=expected:raise RuntimeError(("class relocation contract changed",rel))
    linked=OUT/"apollo-main-lv-base-class-7564f8.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!={"audio_uart_lv_base_class_7564f8"} or after-before or len(before)!=242 or len(after)!=241 or not OWNED<=symbols(linked,"--defined-only"):raise RuntimeError("class linked contract changed")
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_LV_BASE_CLASS_C","source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),"object_sha256":sha(obj),"factory_oracle_sha256":factory["oracle_sha256"],"base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),"linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),"native_descriptor":"0x7564f8..0x75651b","native_name":"0x78dc64","descriptor_bytes":36,"callback_relocations":sorted([list(x) for x in rel]),"source_owned_symbols":sorted(OWNED),"unresolved_before":len(before),"unresolved_after":len(after),"imports_resolved":["audio_uart_lv_base_class_7564f8"],"imports_added":[],"source_complete":False,"full_payload_linked":False,"hardware_proof":False,"limits":["Descriptor and name are source-owned with four relocations; stock ROM placement and live class dispatch remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
