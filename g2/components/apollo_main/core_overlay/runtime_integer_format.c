/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 integer-formatting helper
 * at 0x00482518. The exact stock boundary, sole caller, context layout, and
 * behavioral evidence are recorded in EVIDENCE.md.
 */

typedef __UINT64_TYPE__ open_cfw_integer_format_u64;

#ifndef OPEN_CFW_INTEGER_FORMAT_POINTER_TYPE
#define OPEN_CFW_INTEGER_FORMAT_POINTER_TYPE unsigned char *
#endif

typedef OPEN_CFW_INTEGER_FORMAT_POINTER_TYPE
    open_cfw_integer_format_pointer;

struct open_cfw_integer_format_context {
    open_cfw_integer_format_u64 value;
    unsigned int reserved_08;
    open_cfw_integer_format_pointer digits;
    open_cfw_integer_format_pointer scratch;
    unsigned int prefix_length;
    unsigned int digit_length;
    unsigned int reserved_1c;
    unsigned int zero_padding;
    unsigned int reserved_24;
    unsigned int reserved_28;
    unsigned int reserved_2c;
    int precision;
    int field_width;
    unsigned short flags;
};

_Static_assert(
    __builtin_offsetof(struct open_cfw_integer_format_context, value) == 0x00,
    "integer-format value offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        reserved_08
    ) == 0x08,
    "integer-format reserved_08 offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_integer_format_context, digits) == 0x0c,
    "integer-format digit-pointer offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_integer_format_context, scratch) == 0x10,
    "integer-format scratch-pointer offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        prefix_length
    ) == 0x14,
    "integer-format prefix-length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        digit_length
    ) == 0x18,
    "integer-format digit-length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        zero_padding
    ) == 0x20,
    "integer-format zero-padding offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        precision
    ) == 0x30,
    "integer-format precision offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_integer_format_context,
        field_width
    ) == 0x34,
    "integer-format field-width offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_integer_format_context, flags) == 0x38,
    "integer-format flags offset changed"
);

#ifndef OPEN_CFW_INTEGER_FORMAT_POINTER_TO_BYTES
#define OPEN_CFW_INTEGER_FORMAT_POINTER_TO_BYTES(value) (value)
#endif

#ifndef OPEN_CFW_INTEGER_FORMAT_BYTES_TO_POINTER
#define OPEN_CFW_INTEGER_FORMAT_BYTES_TO_POINTER(value) (value)
#endif

#ifndef OPEN_CFW_INTEGER_FORMAT_POINTER_ADDRESS
#define OPEN_CFW_INTEGER_FORMAT_POINTER_ADDRESS(value) \
    ((unsigned int)(value))
#endif

#ifndef OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
#define OPEN_CFW_AEABI_DIVMOD_RESULT_DEFINED
struct open_cfw_aeabi_divmod_result {
    unsigned int quotient_low;
    unsigned int quotient_high;
    unsigned int remainder_low;
    unsigned int remainder_high;
};
#endif

#ifndef OPEN_CFW_INTEGER_FORMAT_DIVMOD
void open_cfw_aeabi_uldivmod_core(
    unsigned int dividend_low,
    unsigned int dividend_high,
    unsigned int divisor_low,
    unsigned int divisor_high,
    struct open_cfw_aeabi_divmod_result *result
);
#define OPEN_CFW_INTEGER_FORMAT_DIVMOD( \
    dividend_low, \
    dividend_high, \
    divisor_low, \
    divisor_high, \
    result \
) \
    open_cfw_aeabi_uldivmod_core( \
        (dividend_low), \
        (dividend_high), \
        (divisor_low), \
        (divisor_high), \
        (result) \
    )
#endif

#ifndef OPEN_CFW_INTEGER_FORMAT_ASCII_FOLD
unsigned int open_cfw_ascii_fold_lower(unsigned int value);
#define OPEN_CFW_INTEGER_FORMAT_ASCII_FOLD(value) \
    open_cfw_ascii_fold_lower(value)
#endif

static __attribute__((always_inline)) inline
open_cfw_integer_format_u64 open_cfw_integer_format_join(
    unsigned int low,
    unsigned int high
)
{
    return (
        ((open_cfw_integer_format_u64)high << 32U)
        | (open_cfw_integer_format_u64)low
    );
}

__attribute__((used, noinline))
void open_cfw_integer_format(
    struct open_cfw_integer_format_context *context,
    unsigned int specifier
)
{
    open_cfw_integer_format_u64 value = context->value;
    unsigned char *scratch =
        OPEN_CFW_INTEGER_FORMAT_POINTER_TO_BYTES(context->scratch);
    unsigned int base;
    unsigned int cursor = 60U;
    unsigned int digit_length;

    if (specifier == (unsigned int)'o') {
        base = 8U;
    }
    else if (
        OPEN_CFW_INTEGER_FORMAT_ASCII_FOLD(specifier)
        == (unsigned int)'x'
    ) {
        base = 16U;
    }
    else {
        base = 10U;
    }

    if (
        (
            specifier == (unsigned int)'d'
            || specifier == (unsigned int)'i'
        )
        && ((unsigned int)(value >> 32U) & 0x80000000U) != 0U
    ) {
        value = 0U - value;
    }

    if ((value == 0U) && (context->precision == 0)) {
        if ((base == 8U) && ((context->flags & 0x08U) != 0U)) {
            cursor = 59U;
            scratch[cursor] = (unsigned char)'0';
        }
    }
    else {
        do {
            struct open_cfw_aeabi_divmod_result result;
            unsigned int character;

            OPEN_CFW_INTEGER_FORMAT_DIVMOD(
                (unsigned int)value,
                (unsigned int)(value >> 32U),
                base,
                0U,
                &result
            );
            value = open_cfw_integer_format_join(
                result.quotient_low,
                result.quotient_high
            );
            character = result.remainder_low + (unsigned int)'0';
            cursor -= 1U;
            if ((character & 0xffU) >= (unsigned int)':') {
                character += (specifier & 0xffU) - 0x51U;
            }
            scratch[cursor] = (unsigned char)character;
        } while (
            value != 0U
            && OPEN_CFW_INTEGER_FORMAT_POINTER_ADDRESS(context->digits)
                < OPEN_CFW_INTEGER_FORMAT_POINTER_ADDRESS(
                    OPEN_CFW_INTEGER_FORMAT_BYTES_TO_POINTER(
                        scratch + cursor
                    )
                )
        );

        if (
            base == 8U
            && (context->flags & 0x08U) != 0U
            && scratch[cursor] != (unsigned char)'0'
        ) {
            cursor -= 1U;
            scratch[cursor] = (unsigned char)'0';
        }
    }

    digit_length = 60U - cursor;
    context->digit_length = digit_length;
    context->digits = OPEN_CFW_INTEGER_FORMAT_BYTES_TO_POINTER(
        scratch + cursor
    );

    if (context->precision > (int)digit_length) {
        context->zero_padding =
            (unsigned int)context->precision - digit_length;
        context->flags &= (unsigned short)0xffefU;
    }
    else if (
        context->precision < 0
        && ((unsigned char)context->flags & 0x14U) == 0x10U
    ) {
        unsigned int available = (unsigned int)context->field_width;

        available -= context->prefix_length;
        available -= context->zero_padding;
        available -= digit_length;
        if ((int)available > 0) {
            context->zero_padding = available;
        }
    }
}
