/*
 * SPDX-License-Identifier: MIT
 *
 * Source recovery of the G2 2.2.6.10 mpaland/printf fixed-point floating
 * converter at 0x00483350...0x00483611. Conversion semantics derive from
 * mpaland/printf commit d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e.
 *
 * The Apollo510 target supports double-precision VFP, but the overlay's
 * otherwise soft-float Clang target would lower ordinary C double arithmetic
 * to unresolved __aeabi helpers. The small wrappers below express the stock
 * VFP operations explicitly, keeping the recovered function source-owned and
 * relocation-free except for its source-owned _out_rev dependency.
 */

typedef __UINT32_TYPE__ open_cfw_runtime_ftoa_word;
typedef __UINT64_TYPE__ open_cfw_runtime_ftoa_bits;

#ifndef OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
#define OPEN_CFW_RUNTIME_NTOA_OUTPUT_FN_DEFINED
typedef void (*open_cfw_runtime_ntoa_output_fn)(
    char,
    void *,
    unsigned int,
    unsigned int
);
#endif

#ifndef OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#define OPEN_CFW_RUNTIME_FLOAT_ABI_DEFINED
#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_RUNTIME_FLOAT_ABI __attribute__((pcs("aapcs-vfp")))
#else
#define OPEN_CFW_RUNTIME_FLOAT_ABI
#endif
#endif

enum {
    OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE = 32U,
    OPEN_CFW_RUNTIME_FTOA_DEFAULT_PRECISION = 6U,
    OPEN_CFW_RUNTIME_FTOA_FLAG_ZERO_PAD = 1U << 0U,
    OPEN_CFW_RUNTIME_FTOA_FLAG_LEFT = 1U << 1U,
    OPEN_CFW_RUNTIME_FTOA_FLAG_PLUS = 1U << 2U,
    OPEN_CFW_RUNTIME_FTOA_FLAG_SPACE = 1U << 3U,
    OPEN_CFW_RUNTIME_FTOA_FLAG_PRECISION = 1U << 10U
};

static const double open_cfw_runtime_ftoa_pow10[] = {
    1.0,
    10.0,
    100.0,
    1000.0,
    10000.0,
    100000.0,
    1000000.0,
    10000000.0,
    100000000.0,
    1000000000.0
};

#ifndef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE
open_cfw_runtime_ftoa_word open_cfw_runtime_format_out_reverse(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_ftoa_word index,
    open_cfw_runtime_ftoa_word maximum_length,
    const char *reverse_buffer,
    open_cfw_runtime_ftoa_word length,
    open_cfw_runtime_ftoa_word width,
    open_cfw_runtime_ftoa_word flags
);
#define OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    reverse_buffer, \
    length, \
    width, \
    flags \
) \
    open_cfw_runtime_format_out_reverse( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (reverse_buffer), \
        (length), \
        (width), \
        (flags) \
    )
#endif

#ifndef OPEN_CFW_RUNTIME_FTOA_ETOA
OPEN_CFW_RUNTIME_FLOAT_ABI
open_cfw_runtime_ftoa_word open_cfw_runtime_etoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_ftoa_word index,
    open_cfw_runtime_ftoa_word maximum_length,
    double value,
    open_cfw_runtime_ftoa_word precision,
    open_cfw_runtime_ftoa_word width,
    open_cfw_runtime_ftoa_word flags
);
#define OPEN_CFW_RUNTIME_FTOA_ETOA( \
    output, \
    buffer, \
    index, \
    maximum_length, \
    value, \
    precision, \
    width, \
    flags \
) \
    open_cfw_runtime_etoa( \
        (output), \
        (buffer), \
        (index), \
        (maximum_length), \
        (value), \
        (precision), \
        (width), \
        (flags) \
    )
#endif

static __attribute__((always_inline)) inline
open_cfw_runtime_ftoa_bits open_cfw_runtime_ftoa_to_bits(double value)
{
    union {
        double floating;
        open_cfw_runtime_ftoa_bits bits;
    } representation;

    representation.floating = value;
    return representation.bits;
}

static __attribute__((always_inline)) inline double
open_cfw_runtime_ftoa_from_bits(open_cfw_runtime_ftoa_bits bits)
{
    union {
        double floating;
        open_cfw_runtime_ftoa_bits bits;
    } representation;

    representation.bits = bits;
    return representation.floating;
}

#if defined(__arm__) || defined(__thumb__)
static __attribute__((always_inline)) inline double
open_cfw_runtime_ftoa_subtract(double left, double right)
{
    double result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vsub.f64 %P0, %P1, %P2"
        : "=w"(result)
        : "w"(left), "w"(right)
    );
    return result;
}

static __attribute__((always_inline)) inline double
open_cfw_runtime_ftoa_multiply(double left, double right)
{
    double result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vmul.f64 %P0, %P1, %P2"
        : "=w"(result)
        : "w"(left), "w"(right)
    );
    return result;
}

static __attribute__((always_inline)) inline double
open_cfw_runtime_ftoa_signed_to_double(int value)
{
    double result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vmov s15, %1\n\t"
        "vcvt.f64.s32 %P0, s15"
        : "=w"(result)
        : "r"(value)
        : "s15"
    );
    return result;
}

static __attribute__((always_inline)) inline double
open_cfw_runtime_ftoa_unsigned_to_double(
    open_cfw_runtime_ftoa_word value
)
{
    double result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vmov s15, %1\n\t"
        "vcvt.f64.u32 %P0, s15"
        : "=w"(result)
        : "r"(value)
        : "s15"
    );
    return result;
}

static __attribute__((always_inline)) inline int
open_cfw_runtime_ftoa_double_to_signed(double value)
{
    int result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vcvt.s32.f64 s15, %P1\n\t"
        "vmov %0, s15"
        : "=r"(result)
        : "w"(value)
        : "s15"
    );
    return result;
}

static __attribute__((always_inline)) inline
open_cfw_runtime_ftoa_word open_cfw_runtime_ftoa_double_to_unsigned(
    double value
)
{
    open_cfw_runtime_ftoa_word result;

    __asm__ volatile (
        ".fpu fpv5-d16\n\t"
        "vcvt.u32.f64 s15, %P1\n\t"
        "vmov %0, s15"
        : "=r"(result)
        : "w"(value)
        : "s15"
    );
    return result;
}
#else
static double open_cfw_runtime_ftoa_subtract(double left, double right)
{
    return left - right;
}

static double open_cfw_runtime_ftoa_multiply(double left, double right)
{
    return left * right;
}

static double open_cfw_runtime_ftoa_signed_to_double(int value)
{
    return (double)value;
}

static double open_cfw_runtime_ftoa_unsigned_to_double(
    open_cfw_runtime_ftoa_word value
)
{
    return (double)value;
}

static int open_cfw_runtime_ftoa_double_to_signed(double value)
{
    return (int)value;
}

static open_cfw_runtime_ftoa_word
open_cfw_runtime_ftoa_double_to_unsigned(double value)
{
    return (open_cfw_runtime_ftoa_word)value;
}
#endif

__attribute__((used, noinline, minsize))
OPEN_CFW_RUNTIME_FLOAT_ABI
open_cfw_runtime_ftoa_word open_cfw_runtime_ftoa(
    open_cfw_runtime_ntoa_output_fn output,
    void *buffer,
    open_cfw_runtime_ftoa_word index,
    open_cfw_runtime_ftoa_word maximum_length,
    double value,
    open_cfw_runtime_ftoa_word precision,
    open_cfw_runtime_ftoa_word width,
    open_cfw_runtime_ftoa_word flags
)
{
    char reverse_buffer[OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE];
    open_cfw_runtime_ftoa_word length = 0U;
    open_cfw_runtime_ftoa_bits value_bits =
        open_cfw_runtime_ftoa_to_bits(value);
    open_cfw_runtime_ftoa_bits magnitude_bits =
        value_bits & 0x7FFFFFFFFFFFFFFFULL;
    _Bool negative = 0;
    int whole;
    double temporary;
    open_cfw_runtime_ftoa_word fraction;
    double difference;

    if (
        magnitude_bits > 0x7FF0000000000000ULL
    ) {
        return OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE(
            output,
            buffer,
            index,
            maximum_length,
            "nan",
            3U,
            width,
            flags
        );
    }
    if (value_bits == 0xFFF0000000000000ULL) {
        return OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE(
            output,
            buffer,
            index,
            maximum_length,
            "fni-",
            4U,
            width,
            flags
        );
    }
    if (value_bits == 0x7FF0000000000000ULL) {
        const char *infinity =
            (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_PLUS) != 0U
            ? "fni+"
            : "fni";
        open_cfw_runtime_ftoa_word infinity_length =
            (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_PLUS) != 0U ? 4U : 3U;

        return OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE(
            output,
            buffer,
            index,
            maximum_length,
            infinity,
            infinity_length,
            width,
            flags
        );
    }

    if (magnitude_bits > 0x41CDCD6500000000ULL) {
        return OPEN_CFW_RUNTIME_FTOA_ETOA(
            output,
            buffer,
            index,
            maximum_length,
            value,
            precision,
            width,
            flags
        );
    }

    if (
        (value_bits & 0x8000000000000000ULL) != 0U
        && magnitude_bits != 0U
    ) {
        negative = 1;
        value = open_cfw_runtime_ftoa_from_bits(magnitude_bits);
    }
    else if (magnitude_bits == 0U) {
        /*
         * C comparisons leave -0.0 non-negative, but its later arithmetic
         * compares as zero rather than as a large unsigned bit pattern.
         */
        value = open_cfw_runtime_ftoa_from_bits(0U);
    }

    if (
        (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_PRECISION) == 0U
    ) {
        precision = OPEN_CFW_RUNTIME_FTOA_DEFAULT_PRECISION;
    }
    while (
        length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE
        && precision > 9U
    ) {
        reverse_buffer[length] = '0';
        length += 1U;
        precision -= 1U;
    }

    whole = open_cfw_runtime_ftoa_double_to_signed(value);
    temporary = open_cfw_runtime_ftoa_multiply(
        open_cfw_runtime_ftoa_subtract(
            value,
            open_cfw_runtime_ftoa_signed_to_double(whole)
        ),
        open_cfw_runtime_ftoa_pow10[precision]
    );
    fraction = open_cfw_runtime_ftoa_double_to_unsigned(temporary);
    difference = open_cfw_runtime_ftoa_subtract(
        temporary,
        open_cfw_runtime_ftoa_unsigned_to_double(fraction)
    );

    if (
        open_cfw_runtime_ftoa_to_bits(difference)
        > 0x3FE0000000000000ULL
    ) {
        open_cfw_runtime_ftoa_word fraction_limit = 1U;
        open_cfw_runtime_ftoa_word iterator;

        fraction += 1U;
        for (iterator = 0U; iterator < precision; iterator += 1U) {
            fraction_limit *= 10U;
        }
        if (fraction >= fraction_limit) {
            fraction = 0U;
            whole += 1;
        }
    }
    else if (
        open_cfw_runtime_ftoa_to_bits(difference)
        == 0x3FE0000000000000ULL
        && (fraction == 0U || (fraction & 1U) != 0U)
    ) {
        fraction += 1U;
    }

    if (precision == 0U) {
        difference = open_cfw_runtime_ftoa_subtract(
            value,
            open_cfw_runtime_ftoa_signed_to_double(whole)
        );
        if (
            open_cfw_runtime_ftoa_to_bits(difference)
                == 0x3FE0000000000000ULL
            && (whole & 1) != 0
        ) {
            whole += 1;
        }
    }
    else {
        open_cfw_runtime_ftoa_word count = precision;

        while (length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE) {
            count -= 1U;
            reverse_buffer[length] = (char)('0' + (fraction % 10U));
            length += 1U;
            fraction /= 10U;
            if (fraction == 0U) {
                break;
            }
        }
        while (
            length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE
            && count-- > 0U
        ) {
            reverse_buffer[length] = '0';
            length += 1U;
        }
        if (length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE) {
            reverse_buffer[length] = '.';
            length += 1U;
        }
    }

    while (length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE) {
        reverse_buffer[length] = (char)('0' + (whole % 10));
        length += 1U;
        whole /= 10;
        if (whole == 0) {
            break;
        }
    }

    if (
        (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_LEFT) == 0U
        && (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_ZERO_PAD) != 0U
    ) {
        if (
            width != 0U
            && (
                negative != 0
                || (
                    flags
                    & (
                        OPEN_CFW_RUNTIME_FTOA_FLAG_PLUS
                        | OPEN_CFW_RUNTIME_FTOA_FLAG_SPACE
                    )
                ) != 0U
            )
        ) {
            width -= 1U;
        }
        while (
            length < width
            && length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE
        ) {
            reverse_buffer[length] = '0';
            length += 1U;
        }
    }

    if (length < OPEN_CFW_RUNTIME_FTOA_BUFFER_SIZE) {
        if (negative != 0) {
            reverse_buffer[length] = '-';
            length += 1U;
        }
        else if ((flags & OPEN_CFW_RUNTIME_FTOA_FLAG_PLUS) != 0U) {
            reverse_buffer[length] = '+';
            length += 1U;
        }
        else if (
            (flags & OPEN_CFW_RUNTIME_FTOA_FLAG_SPACE) != 0U
        ) {
            reverse_buffer[length] = ' ';
            length += 1U;
        }
    }

    return OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE(
        output,
        buffer,
        index,
        maximum_length,
        reverse_buffer,
        length,
        width,
        flags
    );
}

#undef OPEN_CFW_RUNTIME_FTOA_ETOA
#undef OPEN_CFW_RUNTIME_FORMAT_OUT_REVERSE
