#!/usr/bin/env python3
"""Compose source-backed LVGL label path; retain the global-layout gate."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261014/main-norflash-recorded-aliases/apollo-main-norflash-bound.o"
LABEL = G2 / "build/c-firmware/root-main-lvgl-label-source-round813"
PROVIDERS = G2 / "build/c-firmware/root-main-lvgl-label-providers-round814"
AMBIQ = G2 / "components/main/ambiq_buffer_handlers_candidate_20261014"
DRAW = G2 / "build/c-firmware/20261014/main-root-dependencies/ambiq-current/draw_label.o"
DRAW_RECEIPT = G2 / "build/c-firmware/20261014/main-root-dependencies/ambiq-graph-current-receipt.json"
LVGL = ROOT / "third-party/upstream/lvgl"
OUT = G2 / "build/c-firmware/20261014/main-lvgl-label-graph"
LOCAL_STEMS = ("label_pixel", "glyph_bitmap", "image_options_init",
               "label_fill_rectangle", "label_glyph_blit", "label_rect_copy",
               "label_vector_dispatch", "label_width_aligned",
               "label_vector_draw", "label_outline_available",
               "font_outline_scale", "vector_path_state", "vector_shape_matrix")
GPU = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/gpu_blit.c"
GLOBAL = G2 / "components/main/lvgl_global_candidate_20261014/global.c"
GLOBAL_RECEIPT = PROVIDERS / "round817-receipt.json"
LVGL_PROVIDERS = {
    "misc/lv_area.c": ("lv_area_is_out", "lv_point_set"),
    "misc/lv_color.c": ("lv_color_black", "lv_color_make"),
    "misc/lv_math.c": ("lv_trigo_sin",),
    "font/lv_font.c": ("lv_font_get_glyph_dsc", "lv_font_get_glyph_width",
                       "lv_font_get_line_height", "lv_font_glyph_release_draw_data"),
    "draw/lv_draw_rect.c": ("lv_draw_fill_dsc_init",),
    "draw/lv_draw_buf.c": ("lv_draw_buf_create_ex", "lv_draw_buf_destroy"),
    "stdlib/builtin/lv_string_builtin.c": ("lv_memcpy", "lv_memset"),
    "misc/lv_text.c": ("lv_text_encoded_get_char_id",
                       "lv_text_encoded_letter_next_2", "lv_text_get_next_line",
                       "lv_text_get_size", "lv_text_get_width_with_flags",
                       "lv_text_unicode_to_encoded"),
}
LVGL_FLAGS = ["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
              "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-DLV_CONF_SKIP",
              "-DLV_USE_THEME_DEFAULT=0", "-DLV_USE_THEME_SIMPLE=0",
              "-DLV_USE_THEME_MONO=0", "-ffunction-sections", "-fdata-sections",
              "-I" + str(G2 / "components/bootloader/filesystem/freestanding_include"),
              "-I" + str(G2 / "analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include"),
              "-I" + str(LVGL)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def defined_values(path):
    rows = subprocess.check_output(["arm-none-eabi-nm", "-g", "--defined-only",
                                    str(path)], text=True)
    return {parts[2]: parts[0] for row in rows.splitlines()
            if len(parts := row.split()) == 3}


def main():
    source_audit = json.loads((LABEL / "link-audit.json").read_text())
    provider_audit = json.loads((PROVIDERS / "link-audit.json").read_text())
    draw_audit = json.loads(DRAW_RECEIPT.read_text())
    global_evidence = json.loads(GLOBAL_RECEIPT.read_text())
    if global_evidence["native_literal_value"] != "0x2006f548" or \
       global_evidence["native_literal_address"] != "0x0047364c":
        raise RuntimeError("native LVGL global address evidence changed")
    native_elf = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
    literal = subprocess.check_output(["arm-none-eabi-objdump", "-s",
                                      "--start-address=0x47364c", "--stop-address=0x473650",
                                      str(native_elf)], text=True)
    if "47364c 48f50620" not in literal:
        raise RuntimeError("native LVGL global literal changed")
    commit = subprocess.check_output(["git", "-C", str(LVGL), "rev-parse", "HEAD"],
                                     text=True).strip()
    if commit != source_audit["upstream_commit"] or commit != provider_audit["upstream_commit"]:
        raise RuntimeError("pinned LVGL revision changed")
    if sha(LVGL / "src/draw/lv_draw_label.c") != source_audit["upstream_source_sha256"]:
        raise RuntimeError("LVGL label source drift")
    if sha(LABEL / "lv_draw_label_upstream.o") != source_audit["upstream_object_sha256"]:
        raise RuntimeError("LVGL label object drift")
    if sha(AMBIQ / "lvgl_label_aliases.c") != source_audit["alias_source_sha256"] or \
       sha(LABEL / "lvgl_label_aliases.o") != source_audit["alias_object_sha256"]:
        raise RuntimeError("LVGL adapter drift")
    draw_row = next(row for row in draw_audit["source_units"]
                    if row["object"] == str(DRAW.relative_to(ROOT)))
    if sha(AMBIQ / "draw_label.c") != draw_row["source_sha256"] or \
       sha(DRAW) != draw_row["object_sha256"]:
        raise RuntimeError("Ambiq draw-label drift")
    OUT.mkdir(parents=True, exist_ok=True)
    probe = G2 / "analysis/c-source-completion-20261011/m0/root-main-display-driver-event-loop-round607/lvgl_label_source_round813/global_layout_probe_round816.c"
    subprocess.run(LVGL_FLAGS + ["-c", str(probe), "-o", str(OUT / "lvgl_global_layout.o")], check=True)
    raw = OUT / "lv_draw_label_raw.o"
    label_obj = OUT / "lv_draw_label_profile.o"
    subprocess.run(LVGL_FLAGS + ["-Dlv_draw_label_iterate_characters=audio_uart_lv_draw_label_48a0be",
                                 "-Dlv_draw_unit_draw_letter=audio_uart_lv_draw_unit_draw_letter_48a77e",
                                 "-c", str(LVGL / "src/draw/lv_draw_label.c"), "-o", str(raw)], check=True)
    subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections", "-e",
                    "audio_uart_lv_draw_label_48a0be", str(raw), "-o", str(label_obj)], check=True)
    subprocess.run(["arm-none-eabi-objcopy", "--strip-unneeded", str(label_obj)], check=True)
    alias_obj = OUT / "lvgl_label_aliases.o"
    subprocess.run(LVGL_FLAGS + ["-c", str(AMBIQ / "lvgl_label_aliases.c"),
                                 "-o", str(alias_obj)], check=True)
    objects = [DRAW, label_obj, alias_obj]
    for index, (relative, source_hash) in enumerate(provider_audit["provider_sources_sha256"].items()):
        src = LVGL / "src" / relative
        if sha(src) != source_hash or relative not in LVGL_PROVIDERS:
            raise RuntimeError(f"LVGL provider drift: {relative}")
        raw_obj = OUT / f"lvgl_{index}_raw.o"
        obj = OUT / f"lvgl_{index}_selected.o"
        subprocess.run(LVGL_FLAGS + ["-c", str(src), "-o", str(raw_obj)], check=True)
        subprocess.run(["arm-none-eabi-ld", "-r", "--gc-sections",
                        *(item for symbol in LVGL_PROVIDERS[relative]
                          for item in ("-u", symbol)), str(raw_obj), "-o", str(obj)], check=True)
        subprocess.run(["arm-none-eabi-objcopy", "--strip-unneeded", str(obj)], check=True)
        if not set(LVGL_PROVIDERS[relative]) <= names(obj, "-g", "--defined-only"):
            raise RuntimeError(f"LVGL profile provider missing roots: {relative}")
        objects.append(obj)
    memory = OUT / "lvgl_memory_aliases.o"
    if sha(AMBIQ / "lvgl_memory_aliases.c") != provider_audit["memory_alias_source_sha256"]:
        raise RuntimeError("LVGL allocator adapter drift")
    subprocess.run(LVGL_FLAGS + ["-c", str(AMBIQ / "lvgl_memory_aliases.c"),
                                 "-o", str(memory)], check=True)
    objects.append(memory)
    global_obj = OUT / "lvgl_global.o"
    subprocess.run(LVGL_FLAGS + ["-c", str(GLOBAL), "-o", str(global_obj)], check=True)
    if names(global_obj, "-g", "--defined-only") != {"lv_global"}:
        raise RuntimeError("source-owned LVGL global definition changed")
    sections = subprocess.check_output(["arm-none-eabi-readelf", "-SW", str(global_obj)], text=True)
    if not re.search(r"\.bss\.opencfw_lv_global\s+NOBITS\s+\S+\s+\S+\s+0001ec\s", sections):
        raise RuntimeError("LVGL global section extent changed")
    for obj in (BASE, label_obj, global_obj):
        attributes = subprocess.check_output(["arm-none-eabi-readelf", "-A", str(obj)], text=True)
        if "Tag_ABI_enum_size: int" not in attributes:
            raise RuntimeError(f"mixed enum ABI: {obj}")
    objects.append(global_obj)
    for stem in LOCAL_STEMS:
        obj = OUT / f"{stem}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(AMBIQ / f"{stem}.c"),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    gpu_obj = OUT / "gpu_blit.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(GPU),
                    "-o", str(gpu_obj)], check=True)
    objects.append(gpu_obj)
    before = names(BASE, "-u")
    defined = names(BASE, "-g", "--defined-only")
    for obj in objects:
        current = names(obj, "-g", "--defined-only")
        if current & defined:
            raise RuntimeError(f"duplicate source symbol in {obj}: {current & defined}")
        defined |= current
    linked = OUT / "apollo-main-lvgl-label.o"
    if "audio_uart_display_lv_root" not in before:
        raise RuntimeError("display LVGL root import changed")
    link = subprocess.run(["arm-none-eabi-ld", "-r", str(BASE),
                           *(str(obj) for obj in objects),
                           "--defsym=audio_uart_display_lv_root=lv_global",
                           "-o", str(linked)], text=True, capture_output=True, check=True)
    if link.stderr:
        raise RuntimeError(f"LVGL profile linker warning: {link.stderr}")
    after = names(linked, "-u")
    if len(before) != 482 or after - before != {
            "audio_uart_ambiq_vector_shape_draw_5202ec"} or \
       before - after != {"audio_uart_ambiq_draw_label_53faa6",
                          "audio_uart_display_lv_root"}:
        raise RuntimeError("unexpected label graph import delta")
    symbol_values = defined_values(linked)
    if symbol_values.get("audio_uart_display_lv_root") != symbol_values.get("lv_global"):
        raise RuntimeError("display/global source storage alias differs")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_LVGL_LABEL_C_GRAPH",
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "upstream_submodule": str(LVGL.relative_to(ROOT)), "upstream_commit": commit,
        "source_audit": str((LABEL / "link-audit.json").relative_to(ROOT)),
        "source_audit_sha256": sha(LABEL / "link-audit.json"),
        "provider_audit": str((PROVIDERS / "link-audit.json").relative_to(ROOT)),
        "provider_audit_sha256": sha(PROVIDERS / "link-audit.json"),
        "global_address_receipt": str(GLOBAL_RECEIPT.relative_to(ROOT)),
        "global_address_receipt_sha256": sha(GLOBAL_RECEIPT),
        "lvgl_profile": {"short_enums": False, "LV_USE_THEME_DEFAULT": 0,
                         "LV_USE_THEME_SIMPLE": 0, "LV_USE_THEME_MONO": 0,
                         "global_layout_probe": str(probe.relative_to(ROOT)),
                         "global_layout_probe_sha256": sha(probe)},
        "global_source": str(GLOBAL.relative_to(ROOT)),
        "global_source_sha256": sha(GLOBAL),
        "global_object": str(global_obj.relative_to(ROOT)),
        "global_object_sha256": sha(global_obj),
        "source_units": [{"source": str((AMBIQ / f"{stem}.c").relative_to(ROOT)),
                          "source_sha256": sha(AMBIQ / f"{stem}.c"),
                          "object": str((OUT / f"{stem}.o").relative_to(ROOT)),
                          "object_sha256": sha(OUT / f"{stem}.o")}
                         for stem in LOCAL_STEMS] +
                        [{"source": str(GPU.relative_to(ROOT)), "source_sha256": sha(GPU),
                          "object": str(gpu_obj.relative_to(ROOT)), "object_sha256": sha(gpu_obj)}],
        "selected_objects": [{"path": str(obj.relative_to(ROOT)), "sha256": sha(obj)}
                             for obj in objects],
        "bounded_oracles_observed": [
            {"path": relative, "sha256": sha(ROOT / relative), "status": status}
            for relative, status in (
                ("g2/analysis/c-source-completion-20261011/peripherals/verify_ambiq_draw_label_dispatch_native_20261014.py",
                 "PASS_AMBIQ_DRAW_LABEL_DISPATCH_NATIVE 256"),
                ("g2/analysis/c-source-completion-20261011/peripherals/verify_glyph_bitmap_round812.py",
                 "PASS_NATIVE_GLYPH_BITMAP_VALID 24"))],
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["LVGL source storage matches the candidate 492-byte profile; final placement at 0x2006f548 and startup ownership remain open.",
                   "Native vector-shape draw at 0x5202ec remains an unimplemented C provider.",
                   "Two bounded renderer checks were rerun with temporary pyelftools and Unicorn; they do not cover the full connected graph.",
                   "The rebuilt LVGL objects share Main's 32-bit enum ABI, but this source profile is not fully proven as stock.",
                   "Full native renderer equivalence remains a gate.",
                   "Main placement and hardware boot remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
