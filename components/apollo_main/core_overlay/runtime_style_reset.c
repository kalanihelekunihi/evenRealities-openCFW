/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 style reset routine at
 * 0x00482796...0x004827AF.
 *
 * Byte offset 8 is either a mutable-table entry count or the 0xff marker for
 * a static table. Mutable-table storage is released through the retained
 * allocator wrapper at 0x0044F758 before the full 12-byte descriptor is
 * zeroed. Static storage is never released.
 */

typedef unsigned int open_cfw_runtime_style_reset_word;
typedef unsigned int open_cfw_runtime_style_reset_pointer;

struct open_cfw_runtime_style_reset_descriptor {
    open_cfw_runtime_style_reset_pointer table;
    open_cfw_runtime_style_reset_word property_groups;
    unsigned char count_or_static;
    unsigned char reserved_09;
    unsigned char reserved_0a;
    unsigned char reserved_0b;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_style_reset_descriptor) == 12U,
    "style descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_reset_descriptor,
        table
    ) == 0x00U,
    "style table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_reset_descriptor,
        count_or_static
    ) == 0x08U,
    "style count offset changed"
);

#ifndef OPEN_CFW_RUNTIME_STYLE_RESET_FREE
#define OPEN_CFW_RUNTIME_STYLE_RESET_FREE(allocation) \
    (((void (*)(void *))0x0044F759U)((allocation)))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO
void *open_cfw_runtime_memory_zero(void *destination, unsigned int size);
#define OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO(destination, size) \
    open_cfw_runtime_memory_zero((destination), (size))
#endif

__attribute__((used, noinline))
void open_cfw_runtime_style_reset(void *style_pointer)
{
    struct open_cfw_runtime_style_reset_descriptor *style =
        (struct open_cfw_runtime_style_reset_descriptor *)style_pointer;

    if (style->count_or_static != 0xFFU) {
        OPEN_CFW_RUNTIME_STYLE_RESET_FREE(
            (void *)(__UINTPTR_TYPE__)style->table
        );
    }
    OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO(style, sizeof(*style));
}

#undef OPEN_CFW_RUNTIME_STYLE_RESET_FREE
#undef OPEN_CFW_RUNTIME_STYLE_RESET_MEMORY_ZERO
