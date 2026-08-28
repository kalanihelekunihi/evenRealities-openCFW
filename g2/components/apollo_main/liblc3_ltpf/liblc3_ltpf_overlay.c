/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Production translation unit for the bounded Google liblc3 LTPF-analysis
 * replacement.  The maintained upstream implementation is included without
 * copying or rewriting its algorithm.  Public functions outside the analysis
 * subsystem are given internal linkage so the compiler can prove that they do
 * not enter this overlay.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_LIBLC3_RUNTIME_ONLY

#define memmove open_cfw_liblc3_memmove
#define sqrtf open_cfw_liblc3_sqrtf_nonnegative

#define lc3_ltpf_synthesize \
    __attribute__((internal_linkage, unused)) lc3_ltpf_synthesize
#define lc3_ltpf_disable \
    __attribute__((internal_linkage, unused)) lc3_ltpf_disable
#define lc3_ltpf_get_nbits \
    __attribute__((internal_linkage, unused)) lc3_ltpf_get_nbits
#define lc3_ltpf_put_data \
    __attribute__((internal_linkage, unused)) lc3_ltpf_put_data
#define lc3_ltpf_get_data \
    __attribute__((internal_linkage, unused)) lc3_ltpf_get_data

#include "../../../third_party/liblc3/src/ltpf.c"

#endif

/*
 * Source-owned runtime closure used only by this LTPF-analysis overlay.  The
 * square-root boundary is deliberately narrower than a general libm sqrtf:
 * LTPF passes the product of two self-dot-products, which is nonnegative.
 * Negative inputs fail closed to a quiet NaN and are never supported ingress
 * from the admitted stock caller.
 */
void *open_cfw_liblc3_memmove(void *destination, const void *source, size_t n)
{
    unsigned char *dst = (unsigned char *)destination;
    const unsigned char *src = (const unsigned char *)source;

    if (dst == src || n == 0U) {
        return destination;
    }

    if ((uintptr_t)dst < (uintptr_t)src) {
        for (size_t i = 0U; i < n; ++i) {
            dst[i] = src[i];
        }
    } else {
        for (size_t i = n; i != 0U; --i) {
            dst[i - 1U] = src[i - 1U];
        }
    }

    return destination;
}

float open_cfw_liblc3_sqrtf_nonnegative(float value)
{
    float result;

    if (!(value >= 0.0f)) {
        union {
            uint32_t word;
            float scalar;
        } quiet_nan = { UINT32_C(0x7fc00000) };
        return quiet_nan.scalar;
    }

#if defined(__arm__) || defined(__thumb__)
    __asm__("vsqrt.f32 %0, %1" : "=t"(result) : "t"(value));
#else
    result = __builtin_sqrtf(value);
#endif
    return result;
}
