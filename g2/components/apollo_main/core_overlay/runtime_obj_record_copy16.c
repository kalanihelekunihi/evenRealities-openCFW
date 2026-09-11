/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of a small `LVGL/src/core/lv_obj.c`-linked
 * 16-byte record copy at 0x0043EE94...0x0043EEA6 in G2 firmware 2.2.6.10.
 * The link-order census
 * (../../../tools/manifests/g2-lvgl-vendor-fork-census.tsv) brackets this
 * span inside lvgl-core module object code with low confidence (a
 * link-order signal only); no embedded diagnostic string names it and no
 * caller in the recovered corpus was resolved to a specific LVGL source
 * line, so this file documents recovered *behavior* -- an unconditional
 * four-word (16-byte) record copy, matching the shape of an
 * `lv_area_t`/`lv_style_value_t`-sized aggregate assignment -- not a
 * claimed canonical LVGL symbol name.
 */

typedef unsigned int open_cfw_runtime_word;

__attribute__((used, noinline))
void open_cfw_runtime_obj_copy_record16(
    open_cfw_runtime_word destination[4],
    const open_cfw_runtime_word source[4]
)
{
    destination[0] = source[0];
    destination[1] = source[1];
    destination[2] = source[2];
    destination[3] = source[3];
}
