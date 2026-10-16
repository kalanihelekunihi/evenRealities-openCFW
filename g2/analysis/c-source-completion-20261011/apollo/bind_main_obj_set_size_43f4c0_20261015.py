#!/usr/bin/env python3
"""Bind native-checked LV size setters and style wrappers into Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_obj_set_size_43f4c0.c"
ORACLE = G2 / "build/c-firmware/20261015/main-obj-set-size-43f4c0/oracle-receipt.json"
BASE = G2 / "build/c-firmware/20261015/main-lv-style-lookup-482716/apollo-main-lv-style-lookup-482716.o"
OUT = G2 / "build/c-firmware/20261015/main-obj-set-size-43f4c0"
OWNED = {"audio_uart_page_43f4c0", "audio_uart_page_43f506",
         "audio_uart_page_43f568", "audio_uart_page_441164", "audio_uart_page_44118e"}
RESOLVED = {"audio_uart_page_43f4c0", "audio_uart_page_43f506",
            "audio_uart_page_43f568"}
CHILDREN = {"audio_uart_lvgl_log", "audio_uart_page_style_get_44beaa",
            "audio_uart_page_style_apply_44be4c"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def symbols(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_NATIVE_MAIN_OBJ_SET_SIZE_43F4C0" or \
       oracle["cases"] != 62 or oracle["source_sha256"] != sha(SOURCE) or \
       set(oracle["source_owned_symbols"]) != OWNED or \
       oracle["native_body_sha256"] != {
           "audio_uart_page_43f4c0": "1258e9bbe9c2b2bfb71fdb97341d9d7386f0abd175cb244ab693cc8b7cd4b652",
           "audio_uart_page_43f506": "80b3551e5004e2906368646e44e3cf3f4368db8c71278ad96bd4e00313e2b936",
           "audio_uart_page_43f568": "3b4a83b0c22894cb71d868387e2473e20883de9270761ef4c54ce084a84ebf3f",
           "audio_uart_page_441164": "dfae41b44b846301235271942e5ff864eae436df249b34a6966d0749e23aa495",
           "audio_uart_page_44118e": "75f58c772500c63334a65bd89b41060b1fade822792432bf61d8dad408dd0730"}:
        raise RuntimeError("Native LV size evidence changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "display_lv_obj_set_size_43f4c0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE),
                    "-o", str(obj)], check=True)
    if symbols(obj, "--defined-only") != OWNED or symbols(obj, "-u") != CHILDREN:
        raise RuntimeError("LV size object symbol contract changed")
    before = symbols(BASE, "-u")
    if len(before) != 228 or not RESOLVED <= before or \
       not CHILDREN <= symbols(BASE, "--defined-only"):
        raise RuntimeError("LV size base contract changed")
    linked = OUT / "apollo-main-obj-set-size-43f4c0.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = symbols(linked, "-u")
    if before - after != RESOLVED or after - before or len(after) != 225:
        raise RuntimeError("LV size link delta changed")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_OBJ_SET_SIZE_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle": str(ORACLE.relative_to(ROOT)), "oracle_sha256": sha(ORACLE),
               "oracle_cases": oracle["cases"],
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "source_owned_symbols": sorted(OWNED),
               "imports_resolved": sorted(RESOLVED), "imports_added": [],
               "unresolved_before": len(before), "unresolved_after": len(after),
               "source_complete": False, "full_payload_linked": False,
               "hardware_proof": False,
               "limits": ["Three LV size entry points have controlled native coverage only.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))

if __name__ == "__main__":
    main()
