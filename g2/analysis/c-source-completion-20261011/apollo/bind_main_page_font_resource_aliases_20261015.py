#!/usr/bin/env python3
"""Reuse previously bound NOR flash guards for the font glyph descriptor."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
G2=ROOT/"g2"
SOURCE=G2/"components/audio/uart_thread_source_candidate/display_page_font_resource_aliases.c"
OUT=G2/"build/c-firmware/20261015/main-page-font-resource-aliases"
BASE=G2/"build/c-firmware/20261015/main-page-font-glyph-describe-4d56c0/apollo-main-page-font-glyph-describe-4d56c0.o"
PROVENANCE=G2/"build/c-firmware/norflash-aliases-round1039/receipt.json"
RESOLVED={"audio_uart_font_resource_enter_46f65e","audio_uart_font_resource_leave_46f674"}
PROVIDERS={"g2_norflash_lock_46f65e","g2_norflash_unlock_46f674"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def symbols(p,option):return {s.split()[-1] for s in subprocess.check_output(
    ["arm-none-eabi-nm",option,str(p)],text=True).splitlines()}
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    prior=json.loads(PROVENANCE.read_text())
    if prior["status"]!="PASS_NORFLASH_SOURCE_ALIAS_BINDING" or \
            prior["provider_pairs"].get("g2_norflash_lock_46f65e")!="audio_uart_ring_config_lock" or \
            prior["provider_pairs"].get("g2_norflash_unlock_46f674")!="audio_uart_ring_config_unlock":
        raise RuntimeError("NOR guard provenance changed")
    prior_source=G2/prior["source"]
    if sha(prior_source)!=prior["source_sha256"]:
        raise RuntimeError("NOR guard alias source changed")
    if not PROVIDERS <= symbols(BASE,"--defined-only"):
        raise RuntimeError("NOR guard providers absent from Main")
    obj=OUT/"display_page_font_resource_aliases.o"
    subprocess.run(["clang","--target=arm-none-eabi","-mcpu=cortex-m4","-mthumb",
                    "-std=c11","-ffreestanding","-fno-builtin","-O2","-Wall",
                    "-Wextra","-Werror","-c",str(SOURCE),"-o",str(obj)],check=True)
    if symbols(obj,"--defined-only")!=RESOLVED or symbols(obj,"-u")!=PROVIDERS:
        raise RuntimeError("font resource alias object changed")
    linked=OUT/"apollo-main-page-font-resource-aliases.o"
    subprocess.run(["arm-none-eabi-ld","-r",str(BASE),str(obj),"-o",str(linked)],check=True)
    before,after=symbols(BASE,"-u"),symbols(linked,"-u")
    if before-after!=RESOLVED or after-before or len(before)!=238 or len(after)!=236:
        raise RuntimeError(("font resource alias import contract changed",before-after,after-before,len(before),len(after)))
    receipt={"status":"PASS_EXPERIMENTAL_MAIN_PAGE_FONT_RESOURCE_ALIASES_C",
             "source":str(SOURCE.relative_to(ROOT)),"source_sha256":sha(SOURCE),
             "object_sha256":sha(obj),"provenance_receipt":str(PROVENANCE.relative_to(ROOT)),
             "provenance_receipt_sha256":sha(PROVENANCE),
             "base_object":str(BASE.relative_to(ROOT)),"base_sha256":sha(BASE),
             "linked_object":str(linked.relative_to(ROOT)),"linked_sha256":sha(linked),
             "unresolved_before":len(before),"unresolved_after":len(after),
             "imports_resolved":sorted(RESOLVED),"imports_added":[],
             "source_complete":False,"full_payload_linked":False,"hardware_proof":False,
             "limits":["This binds existing source-owned NOR guard providers by symbol identity; live mutex, flash power, and hardware behavior remain open."]}
    path=OUT/"receipt.json";path.write_text(json.dumps(receipt,indent=2)+"\n")
    print(receipt["status"],len(before),len(after),sha(path))
if __name__=="__main__":main()
