/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL style-property
 * default dispatcher at 0x0048297C...0x00482A59.
 *
 * The stock ABI returns one 32-bit word in r0. For defaults constructed as
 * three-byte LVGL color/value objects, only bits 23:0 are written and bits
 * 31:24 retain their value from incoming r1. The second source parameter
 * intentionally captures that otherwise undocumented register carrier so
 * entry-patched binary callers observe the exact stock result.
 */

typedef unsigned int open_cfw_runtime_style_default_word;

_Static_assert(
    sizeof(open_cfw_runtime_style_default_word) == 4U,
    "style-default word width changed"
);

enum {
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_COLOR_ADDRESS = 0x0078F278U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_100_A_ADDRESS = 0x0078F27CU,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_FF_A_ADDRESS = 0x0078F280U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_FF_B_ADDRESS = 0x0078F284U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_0F_ADDRESS = 0x0078F288U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_POINTER_ADDRESS = 0x0078F28CU,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_MASK_ADDRESS = 0x0078F290U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_100_B_ADDRESS = 0x0078F294U,
    OPEN_CFW_RUNTIME_STYLE_DEFAULT_ZERO_ADDRESS = 0x0078F298U
};

#ifndef OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD
#define OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(address) \
    (*(const volatile open_cfw_runtime_style_default_word *) \
        (__UINTPTR_TYPE__)(address))
#endif

static open_cfw_runtime_style_default_word
open_cfw_runtime_style_default_three_byte(
    open_cfw_runtime_style_default_word low_value,
    open_cfw_runtime_style_default_word incoming_r1
)
{
    return (
        (incoming_r1 & 0xFF000000U)
        | (low_value & 0x00FFFFFFU)
    );
}

/*
 * Machine ABI:
 *   r0 property, r1 high-byte carrier, result in r0.
 *
 * Only r0 is part of the source-level LVGL call. Encoding r1 explicitly is
 * required because the stock compiler used the top byte of its saved r1 as
 * padding when returning a three-byte value.
 */
__attribute__((used, noinline))
open_cfw_runtime_style_default_word open_cfw_runtime_style_default_value(
    open_cfw_runtime_style_default_word property,
    open_cfw_runtime_style_default_word incoming_r1
)
{
    open_cfw_runtime_style_default_word default_color =
        OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_COLOR_ADDRESS
        );
    unsigned int normalized = (unsigned char)property;

    if (normalized == 5U || normalized == 7U) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_MASK_ADDRESS
        );
    }
    if (normalized == 0x1CU) {
        return open_cfw_runtime_style_default_three_byte(
            default_color,
            incoming_r1
        );
    }
    if (normalized == 0x22U) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_FF_B_ADDRESS
        );
    }
    if (
        normalized == 0x23U
        || normalized == 0x31U
        || normalized == 0x39U
        || normalized == 0x3DU
        || normalized == 0x45U
        || normalized == 0x4CU
        || normalized == 0x52U
        || normalized == 0x58U
        || normalized == 0x78U
    ) {
        return open_cfw_runtime_style_default_three_byte(0U, incoming_r1);
    }
    if (
        normalized == 0x24U
        || normalized == 0x25U
        || normalized == 0x29U
        || normalized == 0x32U
        || normalized == 0x3AU
        || normalized == 0x3EU
        || normalized == 0x44U
        || normalized == 0x4DU
        || normalized == 0x53U
        || normalized == 0x59U
        || normalized == 0x62U
        || normalized == 0x63U
    ) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_FF_A_ADDRESS
        );
    }
    if (normalized == 0x34U) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_0F_ADDRESS
        );
    }
    if (normalized == 0x5AU) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_POINTER_ADDRESS
        );
    }
    if (normalized == 0x6EU || normalized == 0x6FU) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_100_A_ADDRESS
        );
    }
    if (normalized == 0x76U) {
        return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
            OPEN_CFW_RUNTIME_STYLE_DEFAULT_100_B_ADDRESS
        );
    }

    return OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(
        OPEN_CFW_RUNTIME_STYLE_DEFAULT_ZERO_ADDRESS
    );
}

#undef OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD
