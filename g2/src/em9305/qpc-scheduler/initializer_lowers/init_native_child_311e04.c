#include <stdint.h>

/* Native 0x311e04..0x311e5c: natural logarithm of an unsigned integer in
 * single precision. With e = log2p0(x) (APEX floor-log2 extension) the
 * mantissa m = x / 2^e is in [1, 2); ln(x) = e * ln 2 + P(m), where P is
 * the stock quartic, evaluated in the stock order on the FPU (profile
 * g2-em9305-2, -mfpu=fpus). Stock divides by (float)(1 << e) with fsdiv;
 * that quotient is exact, so the C multiplies by the exact float 2^-e
 * instead (bit-identical result, no soft-float division). */
#ifdef OPENCFW_QEMU_SOFT_LOG2P0
/* Test-harness only: QEMU-ARC lacks the APEX log2p0 extension; model it
 * as floor(log2(x)) with 0 for x = 0 (the harness applies the same model
 * to the stock side). */
static inline uint32_t opencfw_em9305_log2p0(uint32_t value)
{
    uint32_t result = 0u;
    while ((value >>= 1) != 0u)
        result++;
    return result;
}
#else
__asm__(".extInstruction log2p0,7,1,SUFFIX_NONE,SYNTAX_2OP");
static inline uint32_t opencfw_em9305_log2p0(uint32_t value)
{
    uint32_t result;
    __asm__ volatile("log2p0 %0,%1" : "=r"(result) : "r"(value));
    return result;
}
#endif

float opencfw_em9305_child_311e04(uint32_t value)
{
    uint32_t exponent = opencfw_em9305_log2p0(value);
    union { uint32_t bits; float value; } scale = { (127u - (exponent & 31u)) << 23 };
    float mantissa = (float)value * scale.value;
    float log_scale = (float)exponent * 0x1.62e43p-1f;  /* ln 2, 0x3f317218 */
    float p = mantissa * -0x1.cf6dacp-5f;             /* 0xbd67b6d6 */
    p = p + 0x1.c9e97p-2f;                            /* 0x3ee4f4b8 */
    p = mantissa * p;
    p = p + -0x1.784f16p+0f;                          /* 0xbfbc278b */
    p = mantissa * p;
    p = p + 0x1.691d2ap+1f;                           /* 0x40348e95 */
    p = mantissa * p;
    p = p + -0x1.bde634p+0f;                          /* 0xbfdef31a */
    return log_scale + p;
}
