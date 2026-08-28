/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 LVGL style-property
 * setter at 0x00482868...0x00482945.
 *
 * A mutable style with n properties owns one 5*n-byte allocation: n
 * consecutive 32-bit values followed by n one-byte property identifiers.
 * Existing properties are searched from the last entry toward the first.
 * Appending grows the allocation in place or by relocation, shifts the
 * packed property identifiers four bytes upward, then appends the new value
 * and property. Reallocation failure leaves the descriptor unchanged.
 *
 * Machine ABI: r0 style, r1 property, r2 value. The semantic return type is
 * void. The stock epilogue incidentally restores the incoming r1 and r2
 * stack saves into caller-clobbered r0 and r1; all 50 direct callers discard
 * those values.
 */

typedef unsigned int open_cfw_runtime_style_set_word;
typedef unsigned int open_cfw_runtime_style_set_pointer;

struct open_cfw_runtime_style_set_descriptor {
    open_cfw_runtime_style_set_pointer table;
    open_cfw_runtime_style_set_word property_groups;
    unsigned char count_or_static;
    unsigned char reserved_09;
    unsigned char reserved_0a;
    unsigned char reserved_0b;
};

_Static_assert(
    sizeof(open_cfw_runtime_style_set_word) == 4U,
    "style-set word width changed"
);
_Static_assert(
    sizeof(struct open_cfw_runtime_style_set_descriptor) == 12U,
    "style-set descriptor size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_set_descriptor,
        table
    ) == 0x00U,
    "style-set table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_set_descriptor,
        property_groups
    ) == 0x04U,
    "style-set property-group offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_style_set_descriptor,
        count_or_static
    ) == 0x08U,
    "style-set count offset changed"
);

enum {
    OPEN_CFW_RUNTIME_STYLE_SET_LOG_LEVEL = 3U,
    OPEN_CFW_RUNTIME_STYLE_SET_LOG_FILE = 0x006E8938U,
    OPEN_CFW_RUNTIME_STYLE_SET_STATIC_LINE = 0x0000014CU,
    OPEN_CFW_RUNTIME_STYLE_SET_INVALID_LINE = 0x00000150U,
    OPEN_CFW_RUNTIME_STYLE_SET_LOG_FUNCTION = 0x0078114CU,
    OPEN_CFW_RUNTIME_STYLE_SET_STATIC_MESSAGE = 0x0074B0CCU,
    OPEN_CFW_RUNTIME_STYLE_SET_ASSERT_FORMAT = 0x0076DE3CU,
    OPEN_CFW_RUNTIME_STYLE_SET_ASSERT_EXPRESSION = 0x0076DE58U
};

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_IS_STATIC
int open_cfw_runtime_lookup_is_static(const void *context);
#define OPEN_CFW_RUNTIME_STYLE_SET_IS_STATIC(style) \
    open_cfw_runtime_lookup_is_static((style))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_REALLOCATE
#define OPEN_CFW_RUNTIME_STYLE_SET_REALLOCATE(allocation, size) \
    ((open_cfw_runtime_style_set_pointer)(__UINTPTR_TYPE__) \
        (((void *(*)(void *, unsigned int))0x0044F76BU)( \
            (void *)(__UINTPTR_TYPE__)(allocation), \
            (size) \
        )))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES(value) \
    ((unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_BUCKET_INDEX
unsigned char open_cfw_runtime_lookup_bucket_index(unsigned char key);
#define OPEN_CFW_RUNTIME_STYLE_SET_BUCKET_INDEX(property) \
    open_cfw_runtime_lookup_bucket_index((property))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_LOG_CONSTANT
#define OPEN_CFW_RUNTIME_STYLE_SET_LOG_CONSTANT( \
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

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_LOG_ASSERT
#define OPEN_CFW_RUNTIME_STYLE_SET_LOG_ASSERT( \
    level, file, line, function, format, expression \
) \
    (((void (*)( \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int, \
        unsigned int \
    ))0x0044D25DU)( \
        (level), \
        (file), \
        (line), \
        (function), \
        (format), \
        (expression) \
    ))
#endif

#ifndef OPEN_CFW_RUNTIME_STYLE_SET_FATAL
#define OPEN_CFW_RUNTIME_STYLE_SET_FATAL() \
    do { \
        for (;;) { \
            *(volatile open_cfw_runtime_style_set_word *) \
                (__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
        } \
    } while (0)
#endif

__attribute__((used, noinline))
void open_cfw_runtime_style_set_property(
    struct open_cfw_runtime_style_set_descriptor *style,
    open_cfw_runtime_style_set_word property,
    open_cfw_runtime_style_set_word value
)
{
    open_cfw_runtime_style_set_pointer new_table;
    unsigned char *table_bytes;
    unsigned char *old_properties;
    open_cfw_runtime_style_set_word count;
    open_cfw_runtime_style_set_word index;
    unsigned char normalized_property;
    unsigned char bucket_index;

    if (OPEN_CFW_RUNTIME_STYLE_SET_IS_STATIC(style)) {
        OPEN_CFW_RUNTIME_STYLE_SET_LOG_CONSTANT(
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_LEVEL,
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_FILE,
            OPEN_CFW_RUNTIME_STYLE_SET_STATIC_LINE,
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_STYLE_SET_STATIC_MESSAGE
        );
        return;
    }

    normalized_property = (unsigned char)property;
    if (normalized_property == 0U) {
        OPEN_CFW_RUNTIME_STYLE_SET_LOG_ASSERT(
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_LEVEL,
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_FILE,
            OPEN_CFW_RUNTIME_STYLE_SET_INVALID_LINE,
            OPEN_CFW_RUNTIME_STYLE_SET_LOG_FUNCTION,
            OPEN_CFW_RUNTIME_STYLE_SET_ASSERT_FORMAT,
            OPEN_CFW_RUNTIME_STYLE_SET_ASSERT_EXPRESSION
        );
        OPEN_CFW_RUNTIME_STYLE_SET_FATAL();
        return;
    }

    count = style->count_or_static;
    if (style->table != 0U) {
        table_bytes = OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES(
            style->table
        );
        old_properties = table_bytes + count * 4U;
        index = count;
#pragma clang loop unroll(disable)
        while (index != 0U) {
            index -= 1U;
            if (old_properties[index] == normalized_property) {
                ((open_cfw_runtime_style_set_word *)(void *)table_bytes)[
                    index
                ] = value;
                return;
            }
        }
    }

    new_table = OPEN_CFW_RUNTIME_STYLE_SET_REALLOCATE(
        style->table,
        (count + 1U) * 5U
    );
    if (new_table == 0U) {
        return;
    }

    style->table = new_table;
    table_bytes = OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES(new_table);
    old_properties = table_bytes + count * 4U;
    index = count;
#pragma clang loop unroll(disable)
    while (index != 0U) {
        index -= 1U;
        old_properties[index + 4U] = old_properties[index];
    }

    count += 1U;
    style->count_or_static = (unsigned char)count;
    table_bytes[count * 4U + count - 1U] = normalized_property;
    ((open_cfw_runtime_style_set_word *)(void *)table_bytes)[
        count - 1U
    ] = value;

    bucket_index = OPEN_CFW_RUNTIME_STYLE_SET_BUCKET_INDEX(
        normalized_property
    );
    style->property_groups |= 1U << bucket_index;
}

#undef OPEN_CFW_RUNTIME_STYLE_SET_IS_STATIC
#undef OPEN_CFW_RUNTIME_STYLE_SET_REALLOCATE
#undef OPEN_CFW_RUNTIME_STYLE_SET_POINTER_TO_BYTES
#undef OPEN_CFW_RUNTIME_STYLE_SET_BUCKET_INDEX
#undef OPEN_CFW_RUNTIME_STYLE_SET_LOG_CONSTANT
#undef OPEN_CFW_RUNTIME_STYLE_SET_LOG_ASSERT
#undef OPEN_CFW_RUNTIME_STYLE_SET_FATAL
