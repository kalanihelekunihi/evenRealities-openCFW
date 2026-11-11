/* SPDX-License-Identifier: MIT
 * C forms of C-SKY V2 register-shift instructions, for code whose shift
 * count can leave 0..31. The CK804 lsl/lsr/rotl use Ry[5:0] and give 0 when
 * that is above 31 (XuanTie QEMU target/csky translate_v2.c lsl/lsr/rotl);
 * plain C shifts by 32 or more are undefined. always_inline keeps them out
 * of any section of their own (stage-1 code must stay in STAGE1).
 */
#ifndef OPENCFW_CODEC_CSKY_OPS_H
#define OPENCFW_CODEC_CSKY_OPS_H
#include <stdint.h>

static inline __attribute__((always_inline)) uint32_t
csky_lsl(uint32_t value, uint32_t count)
{
    count &= 63u;
    return count > 31u ? 0u : value << count;
}

static inline __attribute__((always_inline)) uint32_t
csky_lsr(uint32_t value, uint32_t count)
{
    count &= 63u;
    return count > 31u ? 0u : value >> count;
}

static inline __attribute__((always_inline)) uint32_t
csky_rotl(uint32_t value, uint32_t count)
{
    count &= 63u;
    if (count > 31u)
        return 0u;
    return count == 0u ? value : (value << count) | (value >> (32u - count));
}

/* A word pointer the compiler cannot prove null. Stock code really loads
 * and stores near address 0 on some invalid-input paths; a plain C null
 * dereference would let the compiler delete it or insert a trap. */
static inline __attribute__((always_inline)) volatile uint32_t *
csky_word_ptr(uintptr_t address)
{
    volatile uintptr_t opaque = address;
    return (volatile uint32_t *)opaque;
}

#endif
