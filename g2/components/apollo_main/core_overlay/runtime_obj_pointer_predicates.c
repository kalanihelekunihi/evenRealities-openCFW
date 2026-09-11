/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source recovery of two small `LVGL/src/core/lv_obj.c` helpers at
 * 0x0043E2BC...0x0043E2D4 and 0x0043E2D4...0x0043E2EA in G2 firmware
 * 2.2.6.10. The link-order census
 * (../../../tools/manifests/g2-lvgl-vendor-fork-census.tsv) brackets both
 * spans inside `lv_obj.c` with low confidence (a file-sandwich signal
 * only, no call-topology match), and no embedded diagnostic string names
 * either function; this file therefore documents recovered *behavior*,
 * not a claimed canonical LVGL symbol name.
 *
 * `open_cfw_runtime_obj_field_equals_or_null` (0x0043E2BC) is a null-safe
 * equality test against the first 32-bit field of its first argument.
 * Every observed caller (apollo-decomp-02.c) passes a fixed global as the
 * comparison value, consistent with a widget-class or type-tag identity
 * check.
 *
 * `open_cfw_runtime_obj_pointer_chain_contains` (0x0043E2D4) walks a
 * singly linked chain through the first pointer-sized field of each node,
 * starting one link past its first argument, and reports whether the
 * chain reaches the second argument before a NULL terminator. Every
 * observed caller (apollo-decomp-12.c) passes a fixed global as the
 * target, consistent with an `lv_obj_class_t` base-class ancestry check.
 *
 * The stock 32-bit target stores each chain link as a plain 32-bit
 * pointer value; this file walks the chain through genuine pointer types
 * rather than an explicit 32-bit integer cast so the same source is
 * correct on any host pointer width, not only on the 32-bit ARM target.
 */

typedef unsigned int open_cfw_runtime_pointer_word;

__attribute__((used, noinline))
int open_cfw_runtime_obj_field_equals_or_null(
    const open_cfw_runtime_pointer_word *first_field,
    open_cfw_runtime_pointer_word value
)
{
    if (first_field == (const open_cfw_runtime_pointer_word *)0) {
        return 0;
    }
    return *first_field == value;
}

__attribute__((used, noinline))
int open_cfw_runtime_obj_pointer_chain_contains(
    void *const *chain,
    const void *target
)
{
    const void *node = *chain;

    while (node != (const void *)0) {
        if (node == target) {
            return 1;
        }
        node = *(void *const *)node;
    }
    return 0;
}
