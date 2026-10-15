#!/usr/bin/env python3
"""Current-host touch C census; intentionally separate from the pinned builder."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOUCH = ROOT / "g2/components/touch"
OUT = ROOT / "g2/build/c-firmware/20261014/touch-current-census"
PRIOR_DIR = TOUCH / "source_candidate_20261010/build"
PRIOR = PRIOR_DIR / "receipt.json"
HISTORY = TOUCH / "reset_layout_candidate_20261010/reset_generated_lp_history_experimental.c"
RECEIPT = OUT / "touch-current-census-receipt.json"
RESET_NAMES = ("reset_sensor_descriptors.c", "reset_pin_config.c",
               "reset_generated_common_config.c", "reset_generated_internal_context.c",
               "reset_generated_widget_config.c", "reset_active_scan_context.c",
               "reset_base_frame_context.c", "reset_sensor_frames.c",
               "reset_capsense_context.c", "reset_pm_descriptor.c",
               "reset_common_context.c", "reset_widget_contexts.c",
               "reset_sensor_contexts.c", "reset_channel_pending.c",
               "reset_app_pm.c", "reset_position_history.c")
PROVIDER_NAMES = ("cy_scb_i2c", "cy_scb_common", "msclp", "syslib_asm",
                  "syslib_delay", "uidiv", "zero", "reset_data",
                  "crtbegin", "crtend")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prior = json.loads(PRIOR.read_text())
    assert prior["source_count"] == prior["compiled_count"] == 61
    assert prior["provider_object_count"] == len(PROVIDER_NAMES) == 10
    sources = sorted(p for p in TOUCH.glob("*_offline/*.c")
                     if p != TOUCH / "lp_history_offline/decoder.c")
    sources += [TOUCH / "reset_layout_candidate_20261010" / name for name in RESET_NAMES]
    assert len(sources) == 61
    previous_sources = {row["source"]: row["source_sha256"] for row in prior["records"]}
    for source in sources:
        assert previous_sources[str(source.relative_to(ROOT))] == sha(source)
    provider_objects = []
    for name, row in zip(PROVIDER_NAMES, prior["provider_records"]):
        obj = PRIOR_DIR / f"provider__{name}.o"
        assert sha(obj) == row["object_sha256"]
        assert sha(ROOT / row["source"]) == row["source_sha256"]
        provider_objects.append(obj)
    pdl = ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/mtb-pdl-cat2-35f1714623cfea682d5e285af80d50416b4c7bbc"
    includes = [*sorted(TOUCH.glob("*_offline")), pdl / "drivers/include",
                pdl / "devices/include",
                ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/core-lib-ca57d1e519e08badec6891d1776c7b4f05e09561/include",
                ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source/cmsis",
                ROOT / "g2/analysis/dependency-followup-2026-10-08/touch-source"]
    common = ["clang", "-target", "armv6m-none-eabi", "-mcpu=cortex-m0plus",
              "-mthumb", "-Og", "-ffreestanding", "-fno-builtin",
              "-ffunction-sections", "-fdata-sections", "-fno-common",
              "-DCY8C4046FNI_T412", *("-I" + str(p) for p in includes)]
    variants = {}
    for label, extra in (("default_enum", []), ("short_enum", ["-fshort-enums"])):
        directory = OUT / label
        directory.mkdir(exist_ok=True)
        objects = []
        for index, source in enumerate(sources):
            obj = directory / f"{index:03}-{source.parent.name}-{source.stem}.o"
            subprocess.run(common + extra + ["-c", str(source), "-o", str(obj)],
                           check=True, capture_output=True, text=True)
            objects.append(obj)
        hist = directory / "touch-lp-history-experimental.o"
        subprocess.run(common + extra + ["-c", str(HISTORY), "-o", str(hist)],
                       check=True, capture_output=True, text=True)
        listing = subprocess.check_output(["arm-none-eabi-nm", "-S", "-g",
                                           "--defined-only", str(hist)], text=True)
        assert "00000000 000001a8 B touch_generated_lp_history" in listing
        linked = directory / "touch-candidate.o"
        result = subprocess.run(["arm-none-eabi-ld", "-r", *map(str, objects),
                                 *map(str, provider_objects), str(hist), "-o",
                                 str(linked)], capture_output=True, text=True, check=True)
        listing = subprocess.check_output(["arm-none-eabi-nm", "-u", str(linked)], text=True)
        strong = [line.split()[-1] for line in listing.splitlines()
                  if line.split()[0] == "U"]
        weak = [line.split()[-1] for line in listing.splitlines()
                if line.split()[0] in ("w", "v")]
        assert not strong
        assert set(weak) == {"_ITM_deregisterTMCloneTable", "_ITM_registerTMCloneTable",
                             "__deregister_frame_info", "__register_frame_info"}
        variants[label] = {
            "objects_compiled": len(objects),
            "object_sha256": {str(p.relative_to(ROOT)): sha(p) for p in objects},
            "history_object": str(hist.relative_to(ROOT)),
            "history_object_sha256": sha(hist),
            "linked_object": str(linked.relative_to(ROOT)),
            "linked_object_sha256": sha(linked),
            "strong_unresolved": strong, "weak_unresolved": sorted(weak),
            "link_warnings": result.stderr.strip().splitlines(),
        }
    compiler = Path("/usr/bin/clang")
    receipt = {
        "status": "PASS_EXPERIMENTAL_TOUCH_C_SOURCE_CENSUS",
        "pinned_builder_receipt": str(PRIOR.relative_to(ROOT)),
        "pinned_builder_receipt_sha256": sha(PRIOR),
        "current_compiler": str(compiler), "current_compiler_sha256": sha(compiler),
        "pinned_compiler_sha256": "21df4f5520528e31b8632cfb3b4b57a3f2a33126693828bf69d1976f537aaec7",
        "pinned_compiler_match": sha(compiler) == "21df4f5520528e31b8632cfb3b4b57a3f2a33126693828bf69d1976f537aaec7",
        "selected_sources": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "provider_objects": {str(p.relative_to(ROOT)): sha(p) for p in provider_objects},
        "experimental_history_source": str(HISTORY.relative_to(ROOT)),
        "experimental_history_source_sha256": sha(HISTORY),
        "variants": variants,
        "whole_image_complete": False, "native_allocation_extent_proven": False,
        "hardware_proof": False,
        "gates": ["The original builder's compiler hash gate fails on this host and was not changed.",
                  "The previously pinned provider object set mixes enum ABIs; both local link variants emit ABI warnings.",
                  "The 424-byte LP history capacity is experimental: the native generated allocation extent and final RAM placement are unproved.",
                  "Relocatable object closure does not establish a linked image, original toolchain equivalence or hardware behavior."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], sha(RECEIPT))


if __name__ == "__main__":
    main()
