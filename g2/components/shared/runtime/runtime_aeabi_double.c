/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Freestanding ARM EABI double helpers for Apollo510/Cortex-M55.  The
 * firmware ABI passes binary64 values through core-register pairs; these
 * routines move the exact words into FPv5-D16 registers, perform the IEEE-754
 * operation in hardware, and move the result words back.  No compiler runtime
 * or C floating operation is used in the target bodies.
 */

#include "runtime_aeabi_double.h"

typedef union open_cfw_aeabi_double_words {
    double value;
    struct {
        unsigned int low;
        unsigned int high;
    } words;
} open_cfw_aeabi_double_words;

typedef union open_cfw_aeabi_float_word {
    float value;
    unsigned int word;
} open_cfw_aeabi_float_word;

#if defined(__arm__) || defined(__thumb__)
#define OPEN_CFW_AEABI_SOFT_PCS __attribute__((pcs("aapcs")))

#define OPEN_CFW_AEABI_DOUBLE_BINARY(name, instruction) \
    OPEN_CFW_AEABI_SOFT_PCS \
    __attribute__((used, noinline)) \
    double name(double left, double right) \
    { \
        open_cfw_aeabi_double_words a = { .value = left }; \
        open_cfw_aeabi_double_words b = { .value = right }; \
        open_cfw_aeabi_double_words result; \
        __asm__ volatile( \
            ".fpu fpv5-d16\n\t" \
            "vmov d0, %2, %3\n\t" \
            "vmov d1, %4, %5\n\t" \
            instruction " d0, d0, d1\n\t" \
            "vmov %0, %1, d0" \
            : "=r"(result.words.low), "=r"(result.words.high) \
            : "r"(a.words.low), "r"(a.words.high), \
              "r"(b.words.low), "r"(b.words.high) \
            : "d0", "d1" \
        ); \
        return result.value; \
    }

OPEN_CFW_AEABI_DOUBLE_BINARY(__aeabi_dadd, "vadd.f64")
OPEN_CFW_AEABI_DOUBLE_BINARY(__aeabi_dmul, "vmul.f64")
OPEN_CFW_AEABI_DOUBLE_BINARY(__aeabi_ddiv, "vdiv.f64")

OPEN_CFW_AEABI_SOFT_PCS
__attribute__((used, noinline))
double __aeabi_ui2d(unsigned int value)
{
    open_cfw_aeabi_double_words result;

    __asm__ volatile(
        ".fpu fpv5-d16\n\t"
        "vmov s0, %2\n\t"
        "vcvt.f64.u32 d0, s0\n\t"
        "vmov %0, %1, d0"
        : "=r"(result.words.low), "=r"(result.words.high)
        : "r"(value)
        : "d0"
    );
    return result.value;
}

OPEN_CFW_AEABI_SOFT_PCS
__attribute__((used, noinline))
float __aeabi_d2f(double value)
{
    open_cfw_aeabi_double_words source = { .value = value };
    open_cfw_aeabi_float_word result;

    __asm__ volatile(
        ".fpu fpv5-d16\n\t"
        "vmov d0, %1, %2\n\t"
        "vcvt.f32.f64 s0, d0\n\t"
        "vmov %0, s0"
        : "=r"(result.word)
        : "r"(source.words.low), "r"(source.words.high)
        : "d0"
    );
    return result.value;
}

#undef OPEN_CFW_AEABI_DOUBLE_BINARY
#undef OPEN_CFW_AEABI_SOFT_PCS
#else
double __aeabi_dadd(double left, double right) { return left + right; }
double __aeabi_dmul(double left, double right) { return left * right; }
double __aeabi_ddiv(double left, double right) { return left / right; }
double __aeabi_ui2d(unsigned int value) { return (double)value; }
float __aeabi_d2f(double value) { return (float)value; }
#endif
