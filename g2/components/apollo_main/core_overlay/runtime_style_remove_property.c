/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL style-property
 * removal routine at 0x004827B0...0x00482867.
 *
 * A mutable style with n properties owns one 5*n-byte allocation: n
 * consecutive 32-bit values followed by n one-byte property identifiers.
 * Removal allocates a new 5*(n-1)-byte block, copies every non-matching
 * entry in order, and releases the old block only after the copy completes.
 * The stock routine deliberately leaves the descriptor unchanged when the
 * allocation fails.
 *
 * Machine ABI: r0 style, r1 property, boolean result in r0. The stock
 * epilogue incidentally restores incoming r3 into caller-clobbered r1; none
 * of the three callers observes r1, while one caller consumes the r0 result.
 */

typedef unsigned int open_cfw_runtime_style_remove_word;
typedef unsigned int open_cfw_runtime_style_remove_pointer;

struct open_cfw_runtime_style_remove_descriptor {
    open_cfw_runtime_style_remove_pointer table;
    open_cfw_runtime_style_remove_word property_groups;
    unsigned char count_or_static;
    unsigned char reserved_09;
    unsigned char reserved_0a;
    unsigned char reserved_0b;
};

_Static_assert(
    sizeof(struct open_cfw_runtime_style_remove_descriptor) == 12U,
    "style-remove descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_remove_descriptor,
        table
    ) == 0x00U,
    "style-remove table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_remove_descriptor,
        count_or_static
    ) == 0x08U,
    "style-remove count offset changed"
);

enum {
    OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_LEVEL = 3U,
    OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_FILE = 0x006E8938U,
    OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_LINE = 0x00000117U,
    OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_FUNCTION = 0x0077943CU,
    OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_MESSAGE = 0x0075663CU
};

#ifndef OPEN_CFW_RUNTIME_STYLE_REMOVE_IS_STATIC
int open_cfw_runtime_lookup_is_static(const void *context);
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_IS_STATIC(style) \
    open_cfw_runtime_lookup_is_static((style))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_REMOVE_ALLOCATE
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_ALLOCATE(size) \
    ((open_cfw_runtime_style_remove_pointer)(__UINTPTR_TYPE__) \
        (((void *(*)(unsigned int))0x0044F719U)((size))))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE(allocation) \
    (((void (*)(void *))0x0044F759U)( \
        (void *)(__UINTPTR_TYPE__)(allocation) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES(value) \
    ((unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG
#define OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG( \
    level, file, line, function, message \
) \
    (((void (*)( \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int \
    ))0x0044D25DU)( \
        (level), (file), (line), (function), (message) \
    ))
#endif

__attribute__((used, noinline))
open_cfw_runtime_style_remove_word
open_cfw_runtime_style_remove_property(
    struct open_cfw_runtime_style_remove_descriptor *style,
    open_cfw_runtime_style_remove_word property
)
{
    open_cfw_runtime_style_remove_pointer old_table;
    open_cfw_runtime_style_remove_pointer new_table;
    unsigned char *old_bytes;
    unsigned char *new_bytes;
    unsigned char *old_properties;
    unsigned char *new_properties;
    open_cfw_runtime_style_remove_word old_count;
    open_cfw_runtime_style_remove_word new_count;
    open_cfw_runtime_style_remove_word source_index;
    open_cfw_runtime_style_remove_word destination_index;
    unsigned int normalized_property = (unsigned char)property;

    if (OPEN_CFW_RUNTIME_STYLE_REMOVE_IS_STATIC(style)) {
        OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG(
            OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_LEVEL,
            OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_FILE,
            OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_LINE,
            OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG_MESSAGE
        );
        return 0U;
    }

    old_count = style->count_or_static;
    if (old_count == 0U) {
        return 0U;
    }

    old_table = style->table;
    old_bytes = OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES(old_table);
    old_properties = old_bytes + old_count * 4U;
#pragma clang loop unroll(disable)
    for (
        source_index = 0U;
        source_index < old_count;
        source_index += 1U
    ) {
        if (old_properties[source_index] != normalized_property) {
            continue;
        }

        new_count = old_count - 1U;
        new_table = OPEN_CFW_RUNTIME_STYLE_REMOVE_ALLOCATE(
            new_count * 5U
        );
        if (new_table == 0U) {
            return 0U;
        }

        new_bytes = OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES(
            new_table
        );
        style->table = new_table;
        style->count_or_static = (unsigned char)new_count;
        new_properties = new_bytes + new_count * 4U;
        destination_index = 0U;
#pragma clang loop unroll(disable)
        for (
            source_index = 0U;
            source_index < old_count;
            source_index += 1U
        ) {
            if (old_properties[source_index] != normalized_property) {
                ((open_cfw_runtime_style_remove_word *)(void *)new_bytes)[
                    destination_index
                ] = (
                    (const open_cfw_runtime_style_remove_word *)
                    (const void *)old_bytes
                )[source_index];
                new_properties[destination_index] =
                    old_properties[source_index];
                destination_index += 1U;
            }
        }

        OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE(old_table);
        return 1U;
    }

    return 0U;
}

#undef OPEN_CFW_RUNTIME_STYLE_REMOVE_IS_STATIC
#undef OPEN_CFW_RUNTIME_STYLE_REMOVE_ALLOCATE
#undef OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE
#undef OPEN_CFW_RUNTIME_STYLE_REMOVE_POINTER_TO_BYTES
#undef OPEN_CFW_RUNTIME_STYLE_REMOVE_LOG
