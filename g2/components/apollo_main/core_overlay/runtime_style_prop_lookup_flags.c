/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL style-property flag
 * lookup at 0x00482A6A...0x00482AB1.
 *
 * The stock function normalizes its property argument to one byte. Property
 * 0xff means "any" and returns all six behavior flags; property zero is
 * invalid and returns no flags. Properties 1...137 index the pinned built-in
 * table below. Properties 138...254 index the optional custom-property table
 * held in the LVGL global state at 0x2006F548: its 32-bit size is at +0x28
 * and its 32-bit table pointer is at +0x30.
 */

typedef unsigned int open_cfw_runtime_style_prop_word;
typedef unsigned int open_cfw_runtime_style_prop_pointer;

_Static_assert(
    sizeof(open_cfw_runtime_style_prop_word) == 4U,
    "style-property word width changed"
);
_Static_assert(
    sizeof(open_cfw_runtime_style_prop_pointer) == 4U,
    "style-property pointer width changed"
);

enum {
    OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT = 138U,
    OPEN_CFW_RUNTIME_STYLE_PROP_ANY = 0xffU,
    OPEN_CFW_RUNTIME_STYLE_PROP_ALL_FLAGS = 0x3fU
};

static const unsigned char open_cfw_runtime_style_prop_builtin_flags[
    OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT
] = {
    0x00U, 0x04U, 0x04U, 0x02U, 0x04U, 0x04U, 0x04U, 0x04U,
    0x04U, 0x04U, 0x04U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x06U, 0x06U, 0x06U, 0x06U, 0x06U, 0x06U, 0x04U, 0x00U,
    0x06U, 0x06U, 0x06U, 0x06U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x05U,
    0x02U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x04U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x02U, 0x00U, 0x02U, 0x02U, 0x02U, 0x00U, 0x02U, 0x00U,
    0x02U, 0x02U, 0x02U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x02U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x02U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U, 0x00U,
    0x01U, 0x01U, 0x05U, 0x05U, 0x05U, 0x01U, 0x05U, 0x00U,
    0x00U, 0x00U, 0x00U, 0x10U, 0x01U, 0x01U, 0x00U, 0x00U,
    0x00U, 0x10U, 0x22U, 0x22U, 0x0cU, 0x0cU, 0x32U, 0x32U,
    0x32U, 0x00U, 0x00U, 0x32U, 0x32U, 0x10U, 0x00U, 0x00U,
    0x00U, 0x00U, 0x04U, 0x04U, 0x04U, 0x04U, 0x04U, 0x04U,
    0x04U, 0x04U, 0x04U, 0x04U, 0x04U, 0x04U, 0x04U, 0x04U,
    0x04U, 0x00U
};

_Static_assert(
    sizeof(open_cfw_runtime_style_prop_builtin_flags)
        == OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT,
    "style-property built-in table size changed"
);

#ifndef OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_SIZE
#define OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_SIZE() \
    (*(const volatile open_cfw_runtime_style_prop_word *) \
        (__UINTPTR_TYPE__)0x2006F570U)
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER
#define OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER() \
    (*(const volatile open_cfw_runtime_style_prop_pointer *) \
        (__UINTPTR_TYPE__)0x2006F578U)
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_PROP_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_STYLE_PROP_POINTER_TO_BYTES(value) \
    ((const unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

__attribute__((used, noinline))
unsigned char open_cfw_runtime_style_prop_lookup_flags(
    open_cfw_runtime_style_prop_word property
)
{
    unsigned char normalized = (unsigned char)property;
    open_cfw_runtime_style_prop_pointer custom_table;

    if (normalized == OPEN_CFW_RUNTIME_STYLE_PROP_ANY) {
        return OPEN_CFW_RUNTIME_STYLE_PROP_ALL_FLAGS;
    }
    if (normalized == 0U) {
        return 0U;
    }
    if (normalized < OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT) {
        return open_cfw_runtime_style_prop_builtin_flags[normalized];
    }

    normalized = (unsigned char)(
        normalized - OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT
    );
    custom_table = OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER();
    if (
        custom_table != 0U
        && normalized < OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_SIZE()
    ) {
        custom_table = OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER();
        return OPEN_CFW_RUNTIME_STYLE_PROP_POINTER_TO_BYTES(custom_table)[
            normalized
        ];
    }

    return 0U;
}

#undef OPEN_CFW_RUNTIME_STYLE_PROP_POINTER_TO_BYTES
#undef OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_POINTER
#undef OPEN_CFW_RUNTIME_STYLE_PROP_CUSTOM_TABLE_SIZE
