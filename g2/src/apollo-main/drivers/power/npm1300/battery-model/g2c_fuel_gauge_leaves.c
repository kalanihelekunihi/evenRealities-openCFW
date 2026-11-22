/* Idiomatic scalar-float C for nrf_fuel_gauge leaf callees.
 *
 * Decompiled from stock 2.2.6.10 Thumb at the typographic labels in
 * g2c_fuel_gauge_cores.S (objdump of the relocated bodies). Semantics are
 * the stock ones, including NaN and signed-zero corners that differ from
 * libc fminf/fmaxf/floorf/isnanf. ABIs match the call sites:
 *   fg_43a110 / fg_43a19c / fg_43a5b0 use integer registers (soft-float
 *   style); the rest use hard-float AAPCS (s0/s1 in, s0 or r0 out).
 *
 * No fg_call trampoline, no register VM.
 */
#include <stdint.h>
#include <string.h>

#include "g2c_fuel_gauge_leaves.h"

static uint32_t f32_bits(float x)
{
    uint32_t u;
    memcpy(&u, &x, sizeof(u));
    return u;
}

static float bits_f32(uint32_t u)
{
    float x;
    memcpy(&x, &u, sizeof(x));
    return x;
}

/* VFP vcmp Vs-bit: any IEEE-754 binary32 NaN (quiet or signaling). */
static int f32_is_nan(float x)
{
    return (f32_bits(x) & 0x7FFFFFFFu) > 0x7F800000u;
}

/* fg_43a110: r0 holds f32 bits, returns f64 bits in r0:r1 (uint64).
 * Bit layout matches vcvt.f64.f32, including NaN payload (mantissa << 29)
 * and normalized denormals. */
uint64_t fg_43a110(uint32_t bits)
{
    uint32_t sign = bits >> 31;
    uint32_t exp = (bits >> 23) & 0xFFu;
    uint32_t man = bits & 0x7FFFFFu;
    uint32_t exp64;
    uint64_t man64;

    if (exp == 0u) {
        if (man == 0u) {
            exp64 = 0u;
            man64 = 0u;
        } else {
            int e = 1023 - 127 + 1; /* biased exp of 2^{-126} before normalize */
            while ((man & 0x800000u) == 0u) {
                man <<= 1;
                e--;
            }
            man &= 0x7FFFFFu;
            exp64 = (uint32_t)e;
            man64 = (uint64_t)man << 29;
        }
    } else if (exp == 255u) {
        exp64 = 0x7FFu;
        man64 = (uint64_t)man << 29;
        if (man != 0u) {
            /* vcvt.f64.f32 quiets signaling NaNs (sets the top mantissa bit). */
            man64 |= (1ULL << 51);
        }
    } else {
        exp64 = exp - 127u + 1023u;
        man64 = (uint64_t)man << 29;
    }

    return ((uint64_t)sign << 63) | ((uint64_t)exp64 << 52) | man64;
}

/* Returns 1 if either double's high word has (hi<<1) + 0x100000 giving
 * unsigned HI (C=1, Z=0): a qNaN whose high-word mantissa is richer than
 * the canonical 0x7FF80000 pattern. Low words are ignored. Not isfinite
 * and not a full isnan. */
int fg_43a19c(uint32_t lo0, uint32_t hi0, uint32_t lo1, uint32_t hi1)
{
    (void)lo0;
    (void)lo1;
    /* CMN #0x100000, hi<<1 is HI iff (hi<<1) > 0xFFF00000 (wrap to 0 is LS). */
    if ((hi0 << 1) > 0xFFF00000u) {
        return 1;
    }
    if ((hi1 << 1) > 0xFFF00000u) {
        return 1;
    }
    return 0;
}

/* Promote s0 to double (same as 43a110) and apply 43a19c to that value
 * twice; canonicalize a nonzero result to 1. */
int fg_43a0f4(float x)
{
    uint64_t d = fg_43a110(f32_bits(x));
    uint32_t lo = (uint32_t)d;
    uint32_t hi = (uint32_t)(d >> 32);
    int r = fg_43a19c(lo, hi, lo, hi);
    return (r != 0) ? 1 : 0;
}

/* Min-like of (a, b). If b is NaN, keep a. If a is +0 and b is ±0, return b
 * (preserves b's signed zero). Otherwise return the lesser; a NaN in a is
 * kept because unordered compare is not LT. */
float fg_439efc(float a, float b)
{
    if (f32_is_nan(b)) {
        return a;
    }
    if (f32_bits(a) == 0u && b == 0.0f) {
        return b;
    }
    /* vcmp s1,s0 + IT LT: N!=V is also true for unordered (a is NaN). */
    if (f32_is_nan(a) || b < a) {
        return b;
    }
    return a;
}

/* Max-like of (a, b). If b is NaN, keep a. If b is ±0 and a is +0, return a.
 * Otherwise return the greater; a NaN in a is kept (unordered is not LT). */
float fg_439f88(float a, float b)
{
    uint32_t abits = f32_bits(a);
    if (f32_is_nan(b)) {
        return a;
    }
    /* When b is ±0, cmn on a's bits is taken: both +0 and -0 set Z and
     * branch to the CS tail. +0 (C clear) keeps a; -0 (C set) takes b. */
    if (b == 0.0f && (abits & 0x7FFFFFFFu) == 0u) {
        return (abits >= 0x80000000u) ? b : a;
    }
    /* vcmp s0,s1 + IT LT: unordered (a is NaN) also selects b. */
    if (f32_is_nan(a) || a < b) {
        return b;
    }
    return a;
}

/* Integer-bit floor toward -inf, preserving signed zero. |x| < 1 maps
 * positives (and +0) to +0 and negatives (except -0) to -1.0f. Inf and NaN bits are returned unchanged. */
uint32_t fg_43a5b0(uint32_t bits)
{
    int exp_rel = (int)((bits >> 23) & 0xFFu) - 126;

    if (exp_rel <= 0) {
        uint32_t out = bits;
        /* cmn r0,r0 is Z for both +0 and -0 (0x80000000+0x80000000 wraps to 0). */
        if ((bits & 0x7FFFFFFFu) != 0u) {
            out = 0xBF800000u; /* -1.0f */
        }
        if (bits < 0x80000000u) { /* CMN C clear: bit 31 clear */
            out = 0u;
        }
        return out;
    }
    if (exp_rel >= 24) {
        return bits;
    }
    {
        uint32_t mask = 0x00FFFFFFu >> (unsigned)exp_rel;
        if ((int32_t)bits < 0) {
            bits += mask;
        }
        bits &= ~mask;
        return bits;
    }
}

float fg_43a5a0(float x)
{
    return bits_f32(fg_43a5b0(f32_bits(x)));
}

/* Copy a two-float TTE parameter pair into model state at +0x48 / +0x4c
 * (TTE cache lives at +0x84 in the same 0xE8-byte state block). */
void nrf_model_tte_params_58eab0(void *state, const float params[2])
{
    float *dst = (float *)((uint8_t *)state + 0x48);
    dst[0] = params[0];
    dst[1] = params[1];
}

#include <stddef.h>
#include <string.h>

extern uint32_t fg_aux[16];
extern uint32_t fg_iar_err[8];

/* ---- memcpy / memset: standard C, not the typographic IAR bodies.
 * Stock IAR memcpy is a forward copy (no overlap path). fg_memset is
 * the standard (dst, c, n) wrapper around an IAR (dst, n, c) inner.
 * Both return dst. Call sites use non-overlapping regions. */

void *fg_memcpy(void *dst, const void *src, size_t n)
{
    return memcpy(dst, src, n);
}

void *fg_memset(void *dst, int c, size_t n)
{
    return memset(dst, c, n);
}

/* IAR error helper used by the negative-sqrt path: store 0x21 at fg_iar_err[0]. */
void fg_439ca4(void)
{
    fg_iar_err[0] = 0x21u;
}

/* Hardware sqrt of a nonnegative s0. If s0 < 0 (not NaN, not -0), store the
 * IAR error code and return qNaN 0x7FFFFFFF. */
float fg_4397a8(float x)
{
    if (x < 0.0f) {
        fg_439ca4();
        return bits_f32(0x7FFFFFFFu);
    }
    return __builtin_sqrtf(x);
}

/* Max of a 3-float window, skipping leading values that trip fg_43a0f4.
 * VSELGT: a later value wins only when it is strictly greater (unordered
 * leaves the running max). If all three trip the predicate, return a[0]. */
float fg_439e9c(const float a[3])
{
    if (!fg_43a0f4(a[0])) {
        float m = a[0];
        if (a[1] > m) {
            m = a[1];
        }
        if (a[2] > m) {
            m = a[2];
        }
        return m;
    }
    if (!fg_43a0f4(a[1])) {
        float m = a[1];
        if (a[2] > m) {
            m = a[2];
        }
        return m;
    }
    if (!fg_43a0f4(a[2])) {
        return a[2];
    }
    return a[0];
}

/* Min of a 3-float window, same predicate skip as fg_439e9c. IT MI takes
 * the later value only when it is strictly less (unordered keeps the min). */
float fg_439f24(const float a[3])
{
    if (!fg_43a0f4(a[0])) {
        float m = a[0];
        if (a[1] < m) {
            m = a[1];
        }
        if (a[2] < m) {
            m = a[2];
        }
        return m;
    }
    if (!fg_43a0f4(a[1])) {
        float m = a[1];
        if (a[2] < m) {
            m = a[2];
        }
        return m;
    }
    if (!fg_43a0f4(a[2])) {
        return a[2];
    }
    return a[0];
}

/* Scan the first three bytes of s. Write 1-based indices of nonzero bytes
 * into out[] and return how many were stored (0..3). */
int fg_439fb4(const uint8_t *s, int32_t *out)
{
    int stored = 0;
    int i;
    for (i = 0; i < 3; i++) {
        if (s[i] != 0) {
            out[stored] = i + 1;
            stored++;
            if (stored > 2) {
                return stored;
            }
        }
    }
    return stored;
}

/* fabs of 2*count floats. out[0] = count, out[1] = 2. */
void fg_43ba6c(const float *src, const int32_t *count_ptr, float *dst, int32_t out[2])
{
    int32_t count = count_ptr[0];
    int32_t n = count * 2;
    int32_t i;
    out[0] = count;
    out[1] = 2;
    if (n <= 0) {
        return;
    }
    for (i = 0; i < n; i++) {
        dst[i] = bits_f32(f32_bits(src[i]) & 0x7FFFFFFFu);
    }
}

/* fabs of p[1] floats. out[0] = 1, out[1] = p[1]. */
void fg_43bc58(const float *src, const int32_t *p, float *dst, int32_t out[2])
{
    int32_t n = p[1];
    int32_t i;
    out[0] = 1;
    out[1] = n;
    if (n <= 0) {
        return;
    }
    for (i = 0; i < n; i++) {
        dst[i] = bits_f32(f32_bits(src[i]) & 0x7FFFFFFFu);
    }
}

/* Integer-ABI predicate on two doubles in (lo0,hi0) and (lo1,hi1).
 * This is fg_43c0b0's NZCV, reduced by the wrapper's sbcs/negs to !C. */
int fg_43baf4(uint32_t lo0, uint32_t hi0, uint32_t lo1, uint32_t hi1)
{
    uint32_t or_hi = hi0 | hi1;
    uint32_t acc = lo0 | (or_hi << 1);
    int c_or = (int)(or_hi >> 31); /* C after orrs ip, r0, (r1|r3)<<1 */
    int z_or;
    acc |= lo1;
    z_or = (acc == 0);

    if (!c_or) {
        /* Both high words have bit 31 clear. */
        uint64_t sum = (uint64_t)0x200000u + (uint64_t)(hi0 << 1);
        int c0 = (int)(sum >> 32);
        int z0 = ((uint32_t)sum == 0u);
        int c;
        if (c0 && !z0) {
            c = 1; /* hi0 is a NaN-ish pattern: HI */
        } else if (hi1 == hi0) {
            c = (lo1 >= lo0);
        } else {
            c = (hi1 >= hi0);
        }
        return c ? 0 : 1;
    }
    if (z_or) {
        /* ±0 vs ±0 (magnitude zero, at least one minus sign). C stays 1. */
        return 0;
    }
    {
        uint64_t sum = (uint64_t)0x200000u + (uint64_t)(hi0 << 1);
        int c0 = (int)(sum >> 32);
        int z0 = ((uint32_t)sum == 0u);
        int ls0 = (!c0) || z0;
        int c;
        if (!ls0) {
            return 0; /* hi0 NaN-ish, C=1 */
        }
        /* Second cmn (hi1). If it is HI (hi1 is Inf/NaN with mantissa),
         * keep those flags (C=1) — empirically required for -qNaN vs a
         * nonnegative first operand on this path. */
        {
            uint64_t sum1 = (uint64_t)0x200000u + (uint64_t)(hi1 << 1);
            int c1 = (int)(sum1 >> 32);
            int z1 = ((uint32_t)sum1 == 0u);
            int ls1 = (!c1) || z1;
            if (!ls1) {
                return 0;
            }
        }
        if (hi0 == hi1) {
            c = (lo0 >= lo1);
        } else {
            c = (hi0 >= hi1);
        }
        return c ? 0 : 1;
    }
}
