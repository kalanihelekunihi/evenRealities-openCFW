/* Nordic nrf_fuel_gauge (GCC-built in stock, 0x439fe4..0x43bfa8) uses fused VFMA, so this unit
 * keeps clang's default in-expression contraction; the g2-apollo-main profiles set -ffp-contract=off
 * because the IAR-built remainder of the image never emits VFMA. */
#pragma clang fp contract(on)
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
#include <stddef.h>

/* Freestanding: no libc string.h on the Apple-clang arm-none-eabi profile.
 * memcpy/memset are provided by the rest of the apollo-main link. */
void *memcpy(void *dst, const void *src, size_t n);
void *memset(void *dst, int c, size_t n);

#include "g2c_fuel_gauge_leaves.h"

extern float logf(float x);

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

/* VFP scalar ops that keep ARM NaN-payload propagation (quiet in place,
 * first multiply operand / addend rules of vsub/vdiv/vfma/vfms). Used so
 * interpolation does not collapse a signaling or payload NaN to 0x7FC00000. */
static float fg_vsub(float a, float b)
{
    float r;
    __asm__ __volatile__("vsub.f32 %0, %1, %2" : "=t"(r) : "t"(a), "t"(b));
    return r;
}

static float fg_vdiv(float a, float b)
{
    float r;
    __asm__ __volatile__("vdiv.f32 %0, %1, %2" : "=t"(r) : "t"(a), "t"(b));
    return r;
}

/* acc + a*b, typographic vfma.f32 acc, a, b — operand order matters for NaNs. */
static float fg_vfma(float acc, float a, float b)
{
    __asm__ __volatile__("vfma.f32 %0, %1, %2" : "+t"(acc) : "t"(a), "t"(b));
    return acc;
}

/* acc - a*b */
static float fg_vfms(float acc, float a, float b)
{
    __asm__ __volatile__("vfms.f32 %0, %1, %2" : "+t"(acc) : "t"(a), "t"(b));
    return acc;
}

static float fg_vadd(float a, float b)
{
    float r;
    __asm__ __volatile__("vadd.f32 %0, %1, %2" : "=t"(r) : "t"(a), "t"(b));
    return r;
}

static float fg_vmul(float a, float b)
{
    float r;
    __asm__ __volatile__("vmul.f32 %0, %1, %2" : "=t"(r) : "t"(a), "t"(b));
    return r;
}

static float fg_vabs(float a)
{
    float r;
    __asm__ __volatile__("vabs.f32 %0, %1" : "=t"(r) : "t"(a));
    return r;
}

static int32_t fg_vcvt_s32(float x)
{
    float tmp;
    int32_t i;
    __asm__ __volatile__("vcvt.s32.f32 %0, %1" : "=t"(tmp) : "t"(x));
    __asm__ __volatile__("vmov %0, %1" : "=r"(i) : "t"(tmp));
    return i;
}

static float fg_load_wrapped(const float *base, int32_t idx_cvt)
{
    uint32_t off = ((uint32_t)idx_cvt + 0x3FFFFFFFu) << 2;
    float v;
    memcpy(&v, (const uint8_t *)base + off, 4);
    return v;
}

/* 201-point table interpolator shared by fg_43bc84 / fg_43be18.
 * yA is the table scaled by k, yB is the unscaled table (43bc84:
 * r1=yA, r2=yB; 43be18 swaps them). dx = x[1]-x[0] is also used as
 * the last-interval width. Control flow follows typographic delayed
 * vmrs compares. VFP op order is preserved so NaN payloads propagate. */
static float __attribute__((noinline)) fg_high_end(float query, float k, float x200, float dx,
                         const float *yA, const float *yB)
{
    float s11 = yB[200], s12 = yA[200], s10 = yA[199], s13 = yB[199];
    float s14 = s11;
    float s15;
    s13 = fg_vfma(s13, s10, k);
    s14 = fg_vfma(s14, s12, k);
    s15 = fg_vsub(query, x200);
    s14 = fg_vsub(s14, s13);
    s15 = fg_vmul(s14, s15);
    s11 = fg_vadd(fg_vdiv(s15, dx), s11);
    return fg_vfma(s11, s12, k);
}

static float __attribute__((noinline)) fg_low_end(float query, float k, float x0, float dx,
                        const float *yA, const float *yB)
{
    float s12 = yB[0], s13 = yA[0], s14 = yB[1], s10 = yA[1];
    float s11 = s12;
    float s15;
    s14 = fg_vfma(s14, s10, k);
    s11 = fg_vfma(s11, s13, k);
    s15 = fg_vsub(query, x0);
    s14 = fg_vsub(s14, s11);
    s15 = fg_vmul(s15, s14);
    s12 = fg_vadd(fg_vdiv(s15, dx), s12);
    return fg_vfma(s12, s13, k);
}

static float __attribute__((noinline)) fg_interior201(float query, float k, float x0, float dx,
                            const float *yA, const float *yB)
{
    float t = fg_vdiv(fg_vsub(query, x0), dx);
    float floored = fg_43a5a0(t);
    float one = bits_f32(0x3F800000u);
    int32_t ia = fg_vcvt_s32(fg_vadd(floored, bits_f32(0x40000000u)));
    int32_t ib = fg_vcvt_s32(fg_vadd(floored, one));
    float t2 = fg_vdiv(fg_vsub(query, x0), dx);
    float frac = fg_vsub(t2, floored);
    float yA_a = fg_load_wrapped(yA, ia);
    float yB_a = fg_load_wrapped(yB, ia);
    float omf = fg_vsub(one, frac);
    float accB = fg_vmul(frac, yB_a);
    float yB_b = fg_load_wrapped(yB, ib);
    float yA_b = fg_load_wrapped(yA, ib);
    float accA = fg_vmul(frac, yA_a);
    accB = fg_vfma(accB, yB_b, omf);
    accA = fg_vfma(accA, yA_b, omf);
    return fg_vfma(accB, k, accA);
}

static float __attribute__((noinline)) fg_interp201(float query, float k, const float *x,
                          const float *yA, const float *yB)
{
    float x0 = x[0];
    float x200 = x[200];
    float dx = fg_vsub(x[1], x0);
    float s16 = bits_f32(0);
    int do_interior = 0;
    /* VFP vcmpe + integer branches:
     *   blt is N!=V (true LT or unordered), bmi is N (true LT only),
     *   bge is N==V (true GE, not unordered), bpl is N==0 (GE or unordered).
     * The typographic 0x30 blt therefore takes NaN query/x0 into path 0x15e,
     * where 0x16e bpl then selects the constant-0 result. */
    int c1_lt = (x0 < query);
    int c1_blt = c1_lt || f32_is_nan(x0) || f32_is_nan(query);
    int c2_lt = (query < x200);
    int c2_ge = (query >= x200);
    int c2_blt = c2_lt || f32_is_nan(query) || f32_is_nan(x200);

    if (c1_blt) {
        /* 0x30 blt taken: path 0x15e */
        if (c2_ge) {
            s16 = fg_high_end(query, k, x200, dx, yA, yB);
            if (c2_lt) {
                do_interior = 1;
            }
        } else if (!c1_lt) {
            /* 0x16e bpl: x0 >= query or unordered */
            s16 = bits_f32(0);
        } else if (c2_lt) {
            do_interior = 1;
        } else {
            /* x200 NaN with x0 < query: constant 0 */
            s16 = bits_f32(0);
        }
    } else {
        /* 0x34: x0 >= query (both ordered) */
        if (c2_blt) {
            s16 = fg_low_end(query, k, x0, dx, yA, yB);
            if (c1_lt && c2_lt) {
                do_interior = 1;
            }
        } else {
            s16 = fg_high_end(query, k, x200, dx, yA, yB);
            if (c1_lt && c2_lt) {
                do_interior = 1;
            }
        }
    }

    if (do_interior) {
        s16 = fg_interior201(query, k, x0, dx, yA, yB);
    }
    if (fg_43a0f4(query)) {
        return bits_f32(0);
    }
    return s16;
}

float fg_43bc84(float query, float k, const float *x, const float *y1, const float *y2)
{
    return fg_interp201(query, k, x, y1, y2);
}

float fg_43be18(float query, float k, const float *x, const float *y1, const float *y2)
{
    return fg_interp201(query, k, x, y2, y1);
}

/* Select the max-abs element of a short window, then either write
 * dst[i] = scale/src[i] at that index (others 0) or zero the whole
 * destination when |selected|*count*0x35A00000 >= |selected| (zero,
 * Inf, or a huge count). count==1 is the single-element scale/src[0]
 * path. count<=0 writes out={1,count} and does not touch dst. */
void fg_43bb14(const float *src, int count, float *dst, int32_t out[2], float scale)
{
    float raw[8];
    float abuf[8];
    int i, winner;
    float amax, thresh, selected;
    const float kthresh = bits_f32(0x35A00000u);

    if (count == 1) {
        out[0] = 1;
        out[1] = 1;
        dst[0] = fg_vdiv(scale, src[0]);
        return;
    }
    if (count <= 0) {
        out[0] = 1;
        out[1] = count;
        return;
    }

    /* typographic frame holds a handful of elements; callers use 2 or 3. */
    for (i = 0; i < count && i < 8; i++) {
        raw[i] = src[i];
        abuf[i] = fg_vabs(src[i]);
    }

    winner = 0;
    if (count >= 2 && abuf[1] > abuf[0]) {
        winner = 1;
    }
    if (count == 3) {
        if (winner == 0) {
            if (abuf[0] < abuf[2]) {
                winner = 2;
            }
        } else if (abuf[1] < abuf[2]) {
            winner = 2;
        }
    }

    selected = raw[winner];
    amax = fg_vabs(selected);
    thresh = fg_vmul(fg_vmul((float)count, kthresh), amax);
    out[0] = 1;
    out[1] = count;
    for (i = 0; i < count; i++) {
        dst[i] = bits_f32(0);
    }
    if (thresh >= amax) {
        return;
    }
    dst[winner] = fg_vdiv(scale, selected);
}

/* Clamp t into the 3-point x window, then either gather y samples at
 * knots that equal the clamped t, or two-channel-interpolate via
 * fg_439fe4 when t sits strictly between knots. count==3 copies six
 * packed y words; other small counts use the typographic split layout
 * (first half at mid[0], second half at mid[3]).
 * ABI: r0=count, r1=xwin[3], s0=t, r2=ysrc, r3=out_buf, [sp]=out_pair. */
void fg_439ce0(int count, const float *xwin, const float *ysrc,
               float *out_buf, int32_t *out_pair, float t_in)
{
    float mid[16];
    float tail[32];
    float t, hi;
    uint8_t flags[4];
    int32_t idxs[4];
    int neq, i;
    float interp[2];

    for (i = 0; i < 16; i++) {
        mid[i] = bits_f32(0);
    }

    if (count == 3) {
        memcpy(mid, ysrc, 6 * 4);
    } else if ((count << 24) < 0) {
        /* typographic copies 0x3fc bytes onto the stack. Not used by
         * the harness; keep a bounded prefix so C stays in-frame. */
        memcpy(tail, ysrc, 32 * 4);
        if (count > 0 && count < 16) {
            memcpy(mid, tail, (size_t)count * 4);
            memcpy(&mid[3], &tail[count], (size_t)count * 4);
        }
    } else {
        unsigned n2 = (unsigned)((count << 1) & 0xff);
        if (n2 != 0u) {
            unsigned ncopy = n2;
            if (ncopy > 32u) {
                ncopy = 32u;
            }
            memcpy(tail, ysrc, ncopy * 4u);
        }
        if (count != 0 && count < 16) {
            memcpy(mid, tail, (size_t)count * 4);
            memcpy(&mid[3], &tail[count], (size_t)count * 4);
        }
    }

    hi = fg_439e9c(xwin);
    t = fg_439efc(t_in, hi);
    t = fg_439f88(t, fg_439f24(xwin));

    flags[0] = (uint8_t)((xwin[0] == t) ? 1 : 0);
    flags[1] = (uint8_t)((xwin[1] == t) ? 1 : 0);
    flags[2] = (uint8_t)((xwin[2] == t) ? 1 : 0);
    neq = fg_439fb4(flags, idxs);

    if (neq == 0) {
        interp[0] = bits_f32(0);
        interp[1] = bits_f32(0);
        fg_439fe4(t, xwin, mid, interp);
        out_pair[0] = 1;
        out_pair[1] = 2;
        out_buf[0] = interp[0];
        out_buf[1] = interp[1];
        return;
    }

    out_pair[0] = neq;
    out_pair[1] = 2;
    if (neq <= 0) {
        return;
    }
    for (i = 0; i < neq; i++) {
        int idx = idxs[i]; /* 1-based */
        out_buf[i] = mid[idx - 1];
    }
    for (i = 0; i < neq; i++) {
        int idx = idxs[i];
        out_buf[neq + i] = mid[3 + (idx - 1)];
        /* typographic: [sp+32+idx*4] = mid at (32-24)/4 + idx = 2+idx
         * wait: mid[0] is sp+24, [sp+32+idx*4] = offset (8+idx*4) from mid
         * = mid[2+idx]. For idx=1 that is mid[3]. Yes mid[3+(idx-1)]. */
    }
}

/* Quadratic interpolation through (x[i], y[i]) at t. Swap the end points
 * when x[1] < x[0]. A 43a0f4 hit on any x[i] returns the incoming s16
 * (0 in a fresh VFP); a hit on t returns fg_aux[0] as float. Arithmetic
 * follows the typographic vsub/vdiv/vfms/vfma sequence so VFP NaN
 * payloads (including a quieted sNaN 0x7F800001 → 0x7FC00001) propagate. */
float fg_43a5dc(float t, const float x[3], const float y[3])
{
    float x0, x1, x2, y0, y1, y2;
    float dx10, dy10, dx21, dy21, dx20, dt;
    float s_left, s_right, curv, inner;
    int i;

    for (i = 0; i < 3; i++) {
        if (fg_43a0f4(x[i])) {
            return 0.0f; /* typographic returns stale s16; harness keeps s16=0 */
        }
    }

    x0 = x[0];
    x1 = x[1];
    x2 = x[2];
    y0 = y[0];
    y1 = y[1];
    y2 = y[2];
    if (x1 < x0) {
        x0 = x[2];
        y0 = y[2];
        x2 = x[0];
        y2 = y[0];
    }

    if (fg_43a0f4(t)) {
        return bits_f32(fg_aux[0]);
    }

    /* Same order as typographic 0x43A64E..0x43A686. */
    dx10 = fg_vsub(x1, x0);
    dy10 = fg_vsub(y1, y0);
    dx21 = fg_vsub(x2, x1);
    dy21 = fg_vsub(y2, y1);
    s_left = fg_vdiv(dy10, dx10);
    s_right = fg_vdiv(dy21, dx21);
    dx20 = fg_vsub(x2, x0);
    s_right = fg_vsub(s_right, s_left);
    curv = fg_vdiv(s_right, dx20);
    dt = fg_vsub(t, x0);
    inner = fg_vfms(s_left, dx10, curv);
    inner = fg_vfma(inner, curv, dt);
    return fg_vfma(y0, inner, dt);
}

/* Return 1 if n <= 0 or all of the first n bytes of s are nonzero; 0 if a
 * zero byte is found. Negative n is treated as empty (returns 1). */
int fg_43bfac(const uint8_t *s, int n)
{
    int i;
    if (n <= 0) {
        return 1;
    }
    for (i = 0; i < n; i++) {
        if (s[i] == 0) {
            return 0;
        }
    }
    return 1;
}

/* Two-channel quadratic interpolation at t through x[0..2]. y6 is
 * packed [y0[0], y1[0], y2[0], y0[1], y1[1], y2[1]]. A 43a0f4 hit on
 * x[i] returns without writing out; a hit on t writes fg_aux[0] to both
 * outputs. Endpoints swap when x[1] < x[0]. VFP op order preserved. */
void fg_439fe4(float t, const float x[3], const float y6[6], float out[2])
{
    float x0, x1, x2;
    float y00, y10, y20, y01, y11, y21;
    float dx10, dx21, dx20, dt;
    float s0, s1, s2, s3, c0, c1, i0, i1;
    int i;

    for (i = 0; i < 3; i++) {
        if (fg_43a0f4(x[i])) {
            return;
        }
    }

    x0 = x[0];
    x1 = x[1];
    x2 = x[2];
    y00 = y6[0];
    y10 = y6[1];
    y20 = y6[2];
    y01 = y6[3];
    y11 = y6[4];
    y21 = y6[5];
    if (x1 < x0) {
        float tmp;
        tmp = x0; x0 = x2; x2 = tmp;
        tmp = y00; y00 = y20; y20 = tmp;
        tmp = y01; y01 = y21; y21 = tmp;
    }

    if (fg_43a0f4(t)) {
        float z = bits_f32(fg_aux[0]);
        out[0] = z;
        out[1] = z;
        return;
    }

    dx10 = fg_vsub(x1, x0);
    dx21 = fg_vsub(x2, x1);
    /* typographic: dy00, dy01, dy10, dy11, then the four divs */
    s0 = fg_vsub(y10, y00); /* s15 = s25 - s16 */
    s2 = fg_vsub(y11, y01); /* s12 = s24 - s17 */
    s1 = fg_vsub(y20, y10); /* s21 = s21 - s25 */
    s3 = fg_vsub(y21, y11); /* s20 = s20 - s24 */
    s0 = fg_vdiv(s0, dx10); /* (y10-y00)/(x1-x0) */
    s1 = fg_vdiv(s1, dx21);
    s2 = fg_vdiv(s2, dx10);
    s3 = fg_vdiv(s3, dx21);
    s1 = fg_vsub(s1, s0);
    dx20 = fg_vsub(x2, x0);
    s3 = fg_vsub(s3, s2);
    c0 = fg_vdiv(s1, dx20);
    c1 = fg_vdiv(s3, dx20);
    dt = fg_vsub(t, x0);
    i0 = fg_vfms(s0, dx10, c0);
    i1 = fg_vfms(s2, dx10, c1);
    i0 = fg_vfma(i0, c0, dt);
    i1 = fg_vfma(i1, c1, dt);
    out[0] = fg_vfma(y00, i0, dt);
    out[1] = fg_vfma(y01, i1, dt);
}

static float fg_vnmul(float a, float b)
{
    float r;
    __asm__ __volatile__("vnmul.f32 %0, %1, %2" : "=t"(r) : "t"(a), "t"(b));
    return r;
}

static float fg_load_f32(const void *p)
{
    float v;
    memcpy(&v, p, 4);
    return v;
}

/* Scan flags the typographic way: decrement the remaining count first,
 * so only the first (n-1) flags are inspected when n>0. A zero flag
 * accepts mid[0]; exhausting the count returns the default. */
static int fg_ttf_accept_flags(const uint8_t *flags, int n)
{
    int left = (n < 0) ? 1 : (n + 1);
    left -= 1;
    if (left == 0) {
        return 0;
    }
    for (;;) {
        uint8_t f = *flags++;
        if (f == 0) {
            return 1;
        }
        left -= 1;
        if (left == 0) {
            return 0;
        }
    }
}

/* Mode-1 addend (1 - s[0x90]) / ((s[0x90] - s[0xA0]) / s[0x98]).
 * Returns 0 if typographic early-outs to fg_aux. */
static int fg_ttf_mode1_addend(const uint8_t *state, float *addend)
{
    float s13 = fg_load_f32(state + 0x90);
    float s15 = fg_load_f32(state + 0xA0);
    float s12 = fg_load_f32(state + 0x98);
    float s14, s18;
    s15 = fg_vsub(s13, s15);
    s14 = fg_vdiv(s15, s12);
    if (s14 < 0.0f) {
        return 0;
    }
    if (s14 == 0.0f) {
        return 0;
    }
    s15 = fg_vsub(bits_f32(0x3F800000u), s13);
    s18 = fg_vdiv(s15, s14);
    if (s18 < 0.0f) {
        return 0;
    }
    *addend = s18;
    return 1;
}

/* Time-to-full. r0=state, r1=mode (0=CV, 1=CC), r2=model, s0=term current
 * (the typographic 0x55F9A0 wrapper loads ext_block+0x10 into s0 and
 * tail-calls). Default return is fg_aux[0]. logf is the IAR DLIB body. */
float nrf_model_ttf_58eac4(void *state, int mode, const void *model, float term)
{
    const uint8_t *st = (const uint8_t *)state;
    const uint8_t *mod = (const uint8_t *)model;
    float def = bits_f32(fg_aux[0]);
    float v88 = fg_load_f32(st + 0x88);
    float v98, t, addend, lf;
    float out_buf[16];
    float mid[8];
    uint8_t flags[8];
    int32_t out_pair[2];
    int count, n, i;
    int have_mid;

    if (fg_43a0f4(v88)) {
        return def;
    }
    /* vcmpe #0 + blt (N!=V): continue if v88 < 0 or v88 is NaN. */
    if (!((v88 < 0.0f) || f32_is_nan(v88))) {
        return def;
    }
    v98 = fg_load_f32(st + 0x98);
    if (v98 == 0.0f) {
        return def;
    }

    count = (int)st[0xB4];
    t = fg_load_f32(st + 0x8C);
    for (i = 0; i < 16; i++) {
        out_buf[i] = bits_f32(0);
    }
    out_pair[0] = 0;
    out_pair[1] = 0;
    fg_439ce0(count,
              (const float *)(mod + 0x324),
              (const float *)(mod + 0x1584),
              out_buf, out_pair, t);
    n = out_pair[0];
    have_mid = 0;
    if (n > 0) {
        int lim = n;
        if (lim > 8) {
            lim = 8;
        }
        for (i = 0; i < lim; i++) {
            mid[i] = fg_vadd(out_buf[i], out_buf[n + i]);
        }
        have_mid = 1;
    }

    addend = bits_f32(0);
    if (n <= 0) {
        if (mode != 0) {
            if (!fg_ttf_mode1_addend(st, &addend)) {
                return def;
            }
        }
        (void)logf(fg_vdiv(term, v88));
        return def;
    }

    if (mode != 0) {
        if (!fg_ttf_mode1_addend(st, &addend)) {
            return def;
        }
    }

    lf = logf(fg_vdiv(term, v88));
    if (have_mid) {
        int lim = n;
        if (lim > 8) {
            lim = 8;
        }
        for (i = 0; i < lim; i++) {
            float s15 = fg_vnmul(mid[i], lf);
            mid[i] = s15;
            flags[i] = (uint8_t)((s15 < 0.0f) ? 1 : 0);
        }
    }
    if (!fg_ttf_accept_flags(flags, n)) {
        return def;
    }
    if (mode != 0) {
        return fg_vadd(addend, mid[0]);
    }
    return fg_vadd(mid[0], addend);
}

static void fg_store_f32(void *p, float v)
{
    memcpy(p, &v, 4);
}

static void fg_store_u32(void *p, uint32_t v)
{
    memcpy(p, &v, 4);
}

/* Clamp T into the model temps[3] window and record {hi,lo,count} the
 * typographic delayed-vmrs way (bge/bmi, not blt). */
static void fg_init_clamp_temps(const float *temps, float T,
                                float *out_T, float *out_hi, float *out_lo,
                                int *out_count)
{
    float t0 = temps[0], t1 = temps[1], t2 = temps[2];
    float s14 = t0, s13 = t1, s12, s15, s18 = T;
    int count;

    if (s14 >= s13) {
        /* 0x3da: t0 >= t1 (ordered). Count 1, T forced to t0. */
        s15 = s14;
        s18 = s14;
        count = 1;
        goto done;
    } else if (s14 < s13) {
        /* 0x2f6: true LT only. s12 = t1, lo stays t0. */
        s12 = s13;
    } else {
        /* unordered t0 vs t1: s12 = t0, ble taken, lo stays t0. */
        s12 = s14;
    }

    s15 = t2;
    if (s13 >= s15) {
        /* 0x3e6: t1 >= t2 (ordered). hi = s12, count 2. */
        s15 = s12;
        count = 2;
        goto clamp_win;
    }

    /* t1 < t2 or unordered */
    if (s12 < s15) {
        /* 0x346: s12 < t2, hi stays t2, count 3. bpl -> 0x100. */
        count = 3;
        if (!(s18 < s14)) {
            goto clamp_hi;
        }
        s18 = s14;
        goto done;
    }

    if (s14 > s15) {
        /* 0x3c8: lo > t2 (true GT). lo = t2, hi = s12, count 3. */
        s14 = s15;
        count = 3;
        s15 = s12;
        goto clamp_win;
    }

    /* 0xee: hi = s12, count 3 */
    s15 = s12;
    count = 3;

clamp_win:
    /* 0xf4: if T < lo, T = lo and skip hi clamp; else 0x100 vselgt. */
    if (s18 < s14) {
        s18 = s14;
        goto done;
    }
clamp_hi:
    if (s18 > s15) {
        s18 = s15;
    }
done:
    *out_T = s18;
    *out_hi = s15;
    *out_lo = s14;
    *out_count = count;
}

static float fg_init_low_end(float v, float T, float x0, float dx,
                             const uint8_t *model)
{
    float s12 = fg_load_f32(model + 0x1390); /* param_7[0] */
    float s13 = fg_load_f32(model + 0x11A8); /* param_6[0] */
    float s10 = fg_load_f32(model + 0x11AC); /* param_6[1] */
    float s15 = fg_load_f32(model + 0x1394); /* param_7[1] */
    float s11 = s12;
    float s14;
    s15 = fg_vfma(s15, T, s10);
    s11 = fg_vfma(s11, s13, T);
    s14 = fg_vsub(v, x0);
    s15 = fg_vsub(s15, s11);
    s15 = fg_vmul(s15, s14);
    s12 = fg_vadd(fg_vdiv(s15, dx), s12);
    return fg_vfma(s12, s13, T);
}

static float fg_init_high_end(float v, float T, float x_last, float dx,
                              const uint8_t *model)
{
    float s11 = fg_load_f32(model + 0x1574); /* param_7[121] */
    float s12 = fg_load_f32(model + 0x138C); /* param_6[121] */
    float s10 = fg_load_f32(model + 0x1388); /* param_6[120] */
    float s13 = fg_load_f32(model + 0x1570); /* param_7[120] */
    float s14 = s11;
    float s15;
    s13 = fg_vfma(s13, s10, T);
    s14 = fg_vfma(s14, s12, T);
    s15 = fg_vsub(v, x_last);
    s14 = fg_vsub(s14, s13);
    s15 = fg_vmul(s14, s15);
    s11 = fg_vadd(fg_vdiv(s15, dx), s11);
    return fg_vfma(s11, s12, T);
}

static float fg_init_interior(float v, float T, float x0, float dx,
                              const uint8_t *model)
{
    float t = fg_vdiv(fg_vsub(v, x0), dx);
    float floored = fg_43a5a0(t);
    float one = bits_f32(0x3F800000u);
    int32_t ia = fg_vcvt_s32(fg_vadd(floored, bits_f32(0x40000000u)));
    int32_t ib = fg_vcvt_s32(fg_vadd(floored, one));
    float t2 = fg_vdiv(fg_vsub(v, x0), dx);
    float frac = fg_vsub(t2, floored);
    const uint8_t *pa = model + 0x1000u + ((uint32_t)ia << 2);
    const uint8_t *pb = model + 0x1000u + ((uint32_t)ib << 2);
    float yB_hi = fg_load_f32(pa + 0x38C);
    float yA_hi = fg_load_f32(pa + 0x1A4);
    float omf = fg_vsub(one, frac);
    float accB = fg_vmul(frac, yB_hi);
    float yB_lo = fg_load_f32(pb + 0x38C);
    float yA_lo = fg_load_f32(pb + 0x1A4);
    float accA = fg_vmul(frac, yA_hi);
    accB = fg_vfma(accB, yB_lo, omf);
    accA = fg_vfma(accA, yA_lo, omf);
    return fg_vfma(accB, T, accA);
}

void nrf_model_init_43a1b0(float v, float i, float T, const void *opt,
                           const void *model, void *state, float *adjusted_v)
{
    uint8_t *st = (uint8_t *)state;
    const uint8_t *op = (const uint8_t *)opt;
    const uint8_t *mod = (const uint8_t *)model;
    const float *temps = (const float *)(mod + 0x324);
    const float *param2 = (const float *)(mod + 0x330);
    float aux0 = bits_f32(fg_aux[0]);
    float T_win, hi, lo, T_p9, p9, s16, x0, x_last, dx;
    int count, n, k, do_interior;
    uint8_t flags[4];
    int32_t idxs[4];
    float gathered[4];
    uint32_t zero = 0;

    fg_store_f32(st, bits_f32(0x3F800000u));
    fg_store_f32(st + 4, bits_f32(0x40000000u));
    memcpy(st + 8, op, 64);
    fg_store_u32(st + 0x48, (uint32_t)0); /* overwritten below from opt */
    memcpy(st + 0x48, op + 0x40, 4);
    memcpy(st + 0x4C, op + 0x44, 4);
    fg_store_f32(st + 0x50, bits_f32(0x40A00000u)); /* 5.0 */
    memcpy(st + 0x54, op + 0x48, 4);
    memcpy(st + 0x58, op + 0x4C, 4);
    memcpy(st + 0x5C, op + 0x50, 4);
    memcpy(st + 0x60, op + 0x54, 4);
    memcpy(st + 0x64, op + 0x58, 4);
    memcpy(st + 0x68, op + 0x5C, 4);
    memcpy(st + 0x6C, op + 0x60, 4);
    memcpy(st + 0x70, op + 0x64, 4);
    memcpy(st + 0x74, op + 0x68, 4);
    st[0x94] = 0;
    fg_store_u32(st + 0x78, zero);
    fg_store_u32(st + 0x7C, zero);
    fg_store_u32(st + 0x80, zero);
    fg_store_f32(st + 0x84, aux0);
    fg_store_f32(st + 0x88, aux0);
    fg_store_f32(st + 0x8C, aux0);
    fg_store_f32(st + 0x90, aux0);
    fg_store_u32(st + 0x98, zero);
    fg_store_f32(st + 0x9C, aux0);
    fg_store_f32(st + 0xA0, aux0);
    fg_store_f32(st + 0xA4, aux0);
    fg_store_f32(st + 0xA8, aux0);

    fg_init_clamp_temps(temps, T, &T_win, &hi, &lo, &count);
    st[0xB4] = (uint8_t)count;
    fg_store_f32(st + 0xAC, hi);
    fg_store_f32(st + 0xB0, lo);

    /* 439e9c-window clamp is only the param_9 query; voltage still uses T_win. */
    {
        float mx = fg_439e9c(temps);
        float t1 = fg_439efc(T_win, mx);
        float mn = fg_439f24(temps);
        T_p9 = fg_439f88(t1, mn);
    }

    flags[0] = (uint8_t)((temps[0] == T_p9) ? 1 : 0);
    flags[1] = (uint8_t)((temps[1] == T_p9) ? 1 : 0);
    flags[2] = (uint8_t)((temps[2] == T_p9) ? 1 : 0);
    n = fg_439fb4(flags, idxs);
    p9 = bits_f32(0);
    if (n == 0) {
        p9 = fg_43a5dc(T_p9, temps, (const float *)(mod + 0x1578));
    } else if (n > 0) {
        for (k = 0; k < n && k < 3; k++) {
            int idx = idxs[k];
            uint32_t off = ((uint32_t)(idx + 0x55D)) << 2;
            gathered[k] = fg_load_f32(mod + off);
        }
        p9 = gathered[0];
    }

    v = fg_vfma(v, i, p9); /* v + i * param_9 */
    fg_store_f32(st + 0xB8, bits_f32(0x40400000u)); /* 3.0 */

    x_last = param2[121];
    x0 = param2[0];
    dx = fg_vsub(param2[1], x0);

    s16 = bits_f32(0);
    do_interior = 0;
    if (x_last <= v) {
        /* 0x1e6 bls: last <= v (ordered) → high end */
        if (x0 < v) {
            /* 0x372: r2 = (last > v) ? 1 : 0 — false when last <= v */
            do_interior = (x_last > v) ? 1 : 0;
        }
        s16 = fg_init_high_end(v, T_win, x_last, dx, mod);
    } else {
        /* last > v or unordered last vs v */
        if (x0 < v) {
            /* 0x3a8 */
            do_interior = (x_last > v) ? 1 : 0;
            if (x0 == v) {
                s16 = fg_init_low_end(v, T_win, x0, dx, mod);
            } else {
                s16 = bits_f32(0);
            }
        } else if (f32_is_nan(x0) || f32_is_nan(v)) {
            /* 0x1f2 blt after bmi not taken: unordered first vs v */
            s16 = bits_f32(0);
            do_interior = 0;
        } else {
            /* first >= v: low end, r2 = 0 */
            s16 = fg_init_low_end(v, T_win, x0, dx, mod);
            do_interior = 0;
        }
    }

    if (do_interior) {
        s16 = fg_init_interior(v, T_win, x0, dx, mod);
    }
    if (fg_43a0f4(v)) {
        s16 = bits_f32(0);
    }

    fg_store_f32(st + 0xBC, bits_f32(0x40800000u)); /* 4.0 */
    fg_store_u32(st + 0xC0, zero);
    fg_store_u32(st + 0xC4, zero);
    fg_store_u32(st + 0xC8, zero);
    fg_store_f32(st + 0xCC, s16);
    fg_store_f32(st + 0xD0, p9);
    fg_store_f32(st + 0xD4, p9);
    fg_store_f32(st + 0xD8, p9);
    fg_store_f32(st + 0xDC, p9);
    if (adjusted_v) {
        *adjusted_v = v;
    }
}

extern float expf(float);
#include <arm_mve.h>

/* nrf_model_process_43a698 — typographic-faithful scalar C (MVE as 4-wide
 * elementwise ops and VLD4/VST4). Delayed-vmrs CFG; typographic VFP order. */

static float fg_vneg(float a)
{
    float r;
    __asm__ __volatile__("vneg.f32 %0, %1" : "=t"(r) : "t"(a));
    return r;
}

static float fg_vfnms(float acc, float a, float b)
{
    float r = acc;
    __asm__ __volatile__("vfnms.f32 %0, %1, %2" : "+t"(r) : "t"(a), "t"(b));
    return r;
}

typedef struct { float v[4]; } f32x4;

static f32x4 q_load(const void *p)
{
    f32x4 q;
    memcpy(&q, p, 16);
    return q;
}

static void q_store(void *p, f32x4 q)
{
    memcpy(p, &q, 16);
}

static f32x4 q_dup(float x)
{
    f32x4 q;
    q.v[0] = q.v[1] = q.v[2] = q.v[3] = x;
    return q;
}

static f32x4 q_mul(f32x4 a, f32x4 b)
{
    f32x4 r;
    float32x4_t va, vb, vr;
    memcpy(&va, &a, 16);
    memcpy(&vb, &b, 16);
    vr = vmulq_f32(va, vb);
    memcpy(&r, &vr, 16);
    return r;
}

static f32x4 q_add(f32x4 a, f32x4 b)
{
    f32x4 r;
    float32x4_t va, vb, vr;
    memcpy(&va, &a, 16);
    memcpy(&vb, &b, 16);
    vr = vaddq_f32(va, vb);
    memcpy(&r, &vr, 16);
    return r;
}

static f32x4 q_sub(f32x4 a, f32x4 b)
{
    f32x4 r;
    float32x4_t va, vb, vr;
    memcpy(&va, &a, 16);
    memcpy(&vb, &b, 16);
    vr = vsubq_f32(va, vb);
    memcpy(&r, &vr, 16);
    return r;
}

/* VLD4.32 / VST4.32 de/interleave of 16 floats. */
static void fg_vld4(const float *p, f32x4 *q0, f32x4 *q1, f32x4 *q2, f32x4 *q3)
{
    int i;
    for (i = 0; i < 4; i++) {
        q0->v[i] = p[4 * i + 0];
        q1->v[i] = p[4 * i + 1];
        q2->v[i] = p[4 * i + 2];
        q3->v[i] = p[4 * i + 3];
    }
}

static void fg_vst4(float *p, f32x4 q0, f32x4 q1, f32x4 q2, f32x4 q3)
{
    int i;
    for (i = 0; i < 4; i++) {
        p[4 * i + 0] = q0.v[i];
        p[4 * i + 1] = q1.v[i];
        p[4 * i + 2] = q2.v[i];
        p[4 * i + 3] = q3.v[i];
    }
}

static void fg_store_f32_at(void *p, float v)
{
    memcpy(p, &v, 4);
}

static uint32_t fg_load_u32(const void *p)
{
    uint32_t u;
    memcpy(&u, p, 4);
    return u;
}

static void fg_store_u32_at(void *p, uint32_t v)
{
    memcpy(p, &v, 4);
}




static void fg_temp_eq_flags(const float *temps, float t, uint8_t flags[3],
                             int32_t idxs[4], int32_t *n)
{
    flags[0] = (uint8_t)((temps[0] == t) ? 1 : 0);
    flags[1] = (uint8_t)((temps[1] == t) ? 1 : 0);
    flags[2] = (uint8_t)((temps[2] == t) ? 1 : 0);
    *n = fg_439fb4(flags, idxs);
}

/* Index into the small table that starts at state+0xBC. */
static float fg_state_tab(const uint8_t *st, int32_t idx)
{
    return fg_load_f32(st + 0xBC + ((uint32_t)idx << 2));
}

void nrf_model_process_43a698(float v, float i, float T, float dt,
                              void *state, const void *model, float *soc,
                              void *scratch, void *opt)
{
    uint8_t *st = (uint8_t *)state;
    const uint8_t *mod = (const uint8_t *)model;
    const float *temps = (const float *)(mod + 0x324);
    uint8_t frame[0x2C4] __attribute__((aligned(16)));
    uint8_t *sp = frame;
    uint8_t count = st[0xB4];
    float s16 = i, s17, s18, s19 = dt, s20, s21 = T;
    float s0, s1, s11, s12, s13, s14, s15, s24, s25, s26, s27, s28;
    int32_t n8, n3, n_ba6c[2], n_bb[2];
    int32_t idxs[8];
    uint8_t flags[4];
    f32x4 q5v;
    float r5f = 0;
    int32_t ia, ib, ic, k, n, r6v = 0;
    uint32_t u32;
    uint64_t u64;
    int r0i, r3i;
    float *f100, *f138, *f144, *f150, *f15c, *f168, *f178, *f188, *f198;
    float *f1b0, *f1c8, *f1e0, *f1f0, *f200, *f210, *f220, *f230, *f240, *f280;
    uint8_t *optb = (uint8_t *)opt;
    const float c_9999 = bits_f32(0x3F7FF972u);
    const float c_1em4 = bits_f32(0x38D1B717u);
    const float c_3600 = bits_f32(0x45610000u);
    const float c_m005 = bits_f32(0xBD4CCCCDu);
    const float c_105  = bits_f32(0x3F866666u);
    const float c_100  = bits_f32(0x42C80000u);
    const float c_099  = bits_f32(0x3F7D70A4u);
    const float one    = bits_f32(0x3F800000u);
    const float two    = bits_f32(0x40000000u);
    const float three  = bits_f32(0x40400000u);
    const float mone   = bits_f32(0xBF800000u);
    const float zero   = bits_f32(0);

    f100 = (float *)(sp + 0x100);
    f138 = (float *)(sp + 0x138);
    f144 = (float *)(sp + 0x144);
    f150 = (float *)(sp + 0x150);
    f15c = (float *)(sp + 0x15c);
    f168 = (float *)(sp + 0x168);
    f178 = (float *)(sp + 0x178);
    f188 = (float *)(sp + 0x188);
    f198 = (float *)(sp + 0x198);
    f1b0 = (float *)(sp + 0x1b0);
    f1c8 = (float *)(sp + 0x1c8);
    f1e0 = (float *)(sp + 0x1e0);
    f1f0 = (float *)(sp + 0x1f0);
    f200 = (float *)(sp + 0x200);
    f210 = (float *)(sp + 0x210);
    f220 = (float *)(sp + 0x220);
    f230 = (float *)(sp + 0x230);
    f240 = (float *)(sp + 0x240);
    f280 = (float *)(sp + 0x280);

    fg_store_f32_at(sp + 0x6C, v);
    s17 = fg_load_f32(st + 0xB0); /* lo */

    if (count != 1) {
        /* vcmpe T, lo; bpl -> 0xee8 */
        if (!(T < s17)) {
            goto L0ee8;
        }
    }

L003c:
    {
        float mx = fg_439e9c(temps);
        float t1 = fg_439efc(s17, mx);
        float mn = fg_439f24(temps);
        s18 = fg_439f88(t1, mn);
    }
    fg_temp_eq_flags(temps, s18, flags, idxs, &n);
    n8 = n;
    if (n8 == 0)
        goto L1166;
    if (n8 <= 0)
        goto L1260;

    /* Gather model+(idx+0x56b)*4+4 */
    for (k = 0; k < n8; k++) {
        uint32_t off = ((uint32_t)(idxs[k] + 0x56B) << 2) + 4;
        ((float *)(sp + 0x12C))[k] = fg_load_f32(mod + off);
    }
    fg_store_u32_at(sp + 0x64, (uint32_t)(uintptr_t)(sp + 0x12C));

L00e6:
    fg_439ce0((int)st[0xB4], temps, (const float *)(mod + 0x1584),
              f1c8, (int32_t *)(sp + 0x118), s17);
    fg_43ba6c(f1c8, (const int32_t *)(sp + 0x118), f1b0, n_ba6c);
    fg_store_u32_at(sp + 0x110, (uint32_t)n_ba6c[0]);
    fg_store_u32_at(sp + 0x114, (uint32_t)n_ba6c[1]);
    s20 = fg_vneg(s19);
    r3i = n_ba6c[0] << 1;
    if (r3i > 0) {
        for (k = 0; k < r3i; k++) {
            f1b0[k] = expf(fg_vdiv(s20, f1b0[k]));
        }
    }

    if (st[0xB4] == 3)
        goto L1100;

    /* zero 24 bytes at sp+0x198 */
    memset(sp + 0x198, 0, 24);
    /* lsls count, #24; bmi 0x11f6 */
    if ((int32_t)((uint32_t)st[0xB4] << 24) < 0)
        goto L11f6;
    r3i = (int)(((uint32_t)st[0xB4] << 1) & 0xFFu);
    if (r3i == 0)
        goto L01ca;
    {
        uint32_t nbytes = (uint32_t)r3i << 2;
        fg_memcpy(f1c8, mod + 0x159C, nbytes);
    }
    if (st[0xB4] == 0)
        goto L01ca;
    {
        int cnt = (int)st[0xB4];
        int i2;
        for (i2 = 0; i2 < cnt; i2++)
            f198[i2] = f1c8[i2];
        for (i2 = 0; i2 < cnt; i2++)
            ((float *)(sp + 0x1A4))[i2] = f1c8[cnt + i2];
    }

L01ca:
    fg_temp_eq_flags(temps, s18, flags, idxs, &n);
    if (n == 0)
        goto L1126;
    if (n <= 0)
        goto L1258;
    r6v = n << 2;
    /* gather sl[idx-1] into f1c8, then sl[idx+2] after */
    for (k = 0; k < n; k++)
        f1c8[k] = f198[idxs[k] - 1];
    for (k = 0; k < n; k++)
        f1c8[n + k] = f198[idxs[k] + 2];

L025c:
    fg_temp_eq_flags(temps, s18, flags, idxs, &n);
    n3 = n;
    fg_store_u32_at(sp + 0x60, (uint32_t)n3);
    if (n3 == 0)
        goto L1144;
    if (n3 <= 0)
        goto L1250;
    for (k = 0; k < n3; k++) {
        uint32_t off = ((uint32_t)(idxs[k] + 0x55D) << 2);
        f138[k] = fg_load_f32(mod + off);
    }
    fg_store_u32_at(sp + 0x68, (uint32_t)(uintptr_t)f138);

    /* r6v is a small byte offset set before 0x25c (n<<2 or 4). */
L02da:
    s18 = fg_load_f32(sp + (uint32_t)r6v + 0x1C8);
    if (n8 > 0) {
        float s64 = fg_load_f32(st + 0x64);
        float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
        for (k = 0; k < n8; k++)
            g[k] = fg_vmul(g[k], s64);
    }
    if (s16 < 0)
        goto L0fc6;

L0316:
    {
        float dv = fg_vabs(fg_vsub(fg_load_f32(sp + 0x6C), fg_load_f32(st + 0x80)));
        float di = fg_vabs(fg_vsub(fg_load_f32(st + 0x78), s16));
        u64 = fg_43a110(f32_bits(di));
        if (fg_43baf4((uint32_t)u64, (uint32_t)(u64 >> 32), 0xD2F1A9FCu, 0x3F70624Du) == 0)
            goto L0370;
        u64 = fg_43a110(f32_bits(dv));
        if (fg_43baf4((uint32_t)u64, (uint32_t)(u64 >> 32), 0xD2F1A9FCu, 0x3F70624Du) == 0)
            goto L0370;
        if (s21 < 0)
            goto L123c;
    }

L0370:
    fg_store_f32_at(sp + 0x84, fg_load_f32(st + 0xD0));

L037a:
    s14 = fg_vmul(fg_load_f32(st + 0xDC), c_9999);
    s15 = fg_vmul(fg_load_f32(st + 0xD8), c_9999);
    s12 = fg_load_f32(sp + 0x84);
    s14 = fg_vfma(s14, s12, c_1em4);
    s15 = fg_vfma(s15, s14, c_1em4);
    s11 = fg_load_f32(st + 0xB0);
    fg_store_f32_at(sp + 0x90, s15);
    /* vcmpe lo, T already issued; flags used at 0x3c0 */
    s15 = fg_vfnms(s15, s14, two);
    fg_store_f32_at(sp + 0x8C, s14);
    fg_store_f32_at(sp + 0x144, s15);
    if (!(s11 < s21)) {
        /* 0x3c2: vcmpe T, 0; blt (N!=V) 0x11e2 */
        if ((s21 < 0) || f32_is_nan(s21))
            goto L11e2;
    }
L03ce:
    n3 = (int32_t)fg_load_u32(sp + 0x60);
    fg_memcpy(sp + 0x144, (const void *)(uintptr_t)fg_load_u32(sp + 0x68),
              (size_t)((uint32_t)n3 << 2));
L03da:
    fg_memset(sp + 0x200, 0, 64);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    /* r1 = ia-1; r3 = ia + (ia-1)*4; store at 0xd4 */
    r3i = (int32_t)((uint32_t)ia + (((uint32_t)(ia - 1)) << 2));
    fg_store_u32_at(sp + 0xD4, (uint32_t)r3i);
    r3i = r3i - 1;
    fg_store_u32_at(sp + 0x94, (uint32_t)r3i);
    /* vstrw q2 {0,0,0,0} at sp+0x168; str 1.0 at [sp+0x2c0 + r3*4 - 192] */
    q_store(sp + 0x168, q_dup(zero));
    /* typographic: r2 still 1.0 from mov.w r2, #0x3f800000 at 0x3ea */
    fg_store_u32_at(sp + 0x2C0 + ((uint32_t)r3i << 2) - 192, 0x3F800000u);
    if (n8 > 0) {
        float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
        for (k = 0; k < n8; k++)
            g[k] = fg_vmul(g[k], c_3600);
    }


L0470:
    fg_43bb14((const float *)(uintptr_t)fg_load_u32(sp + 0x64),
              (int)n8, f150, n_bb, s20);
    {
        int32_t i0 = fg_vcvt_s32(fg_load_f32(st + 0));
        int32_t i1 = fg_vcvt_s32(fg_load_f32(st + 4));
        int32_t ibc = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        int32_t n0 = n_ba6c[0];
        float s10 = f1b0[0];
        float s11b = f1b0[n0];
        int32_t slv = i0, r7v = i1;
        int32_t lrv = slv - 1, ipv = r7v - 1;
        slv = slv + (lrv << 2);
        r7v = r7v + (ipv << 2);
        s0 = fg_vmul(fg_load_f32(st + 0x78), zero);
        slv = 0x2C0 + (slv << 2);
        r7v = 0x2C0 + (r7v << 2);
        s14 = fg_vsub(one, s10);
        s13 = f150[0];
        s15 = fg_vsub(one, s11b);
        fg_store_f32_at(sp + slv - 196, s10);
        fg_store_f32_at(sp + r7v - 196, s11b);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)lrv << 2), s14);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ipv << 2), s15);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ibc << 2) - 4, s13);
        fg_store_f32_at(sp + 0x194, s11b);
        s0 = fg_vmul(s0, s19);
    }
    fg_43bb14((const float *)(uintptr_t)fg_load_u32(sp + 0x64),
              (int)n8, f150, n_bb, s0);
    fg_43bc58(f150, (const int32_t *)(sp + 0x118), (float *)(sp + 0x120), n_ba6c);
    fg_store_u32_at(sp + 0x110, (uint32_t)n_ba6c[0]);
    fg_store_u32_at(sp + 0x114, (uint32_t)n_ba6c[1]);
    if (n_ba6c[1] > 0) {
        float *p = (float *)(sp + 0x120);
        for (k = 0; k < n_ba6c[1]; k++)
            p[k] = fg_vneg(p[k]);
        for (k = 0; k < n_ba6c[1]; k++)
            p[k] = expf(p[k]);
    }
    {
        f32x4 q2 = q_load(sp + 0x168);
        q_store(sp + 0x1E0, q2);
        q2 = q_mul(q2, q_dup(zero));
        q_store(sp + 0x1F0, q2);
        ia = fg_vcvt_s32(fg_load_f32(st + 0xB8));
        r3i = (int32_t)((uint32_t)ia + (((uint32_t)ia) << 2));
        fg_store_u32_at(sp + 0x2C0 + ((uint32_t)r3i << 2) - 212,
                        fg_load_u32(sp + 0x120));
        s0 = fg_load_f32(st + 0x78);
    }
    if (fg_43a0f4(s0) == 0)
        goto L0f5a;
    s24 = bits_f32(fg_aux[0]);
    fg_store_u32_at(sp + 0x88, (uint32_t)(uintptr_t)&fg_aux[0]);
    goto L05b6;

L0f5a:
    s15 = fg_load_f32(st + 0x78);
    if (s15 < 0) {
        s24 = mone;
        fg_store_u32_at(sp + 0x88, (uint32_t)(uintptr_t)&fg_aux[0]);
        goto L05b6;
    }
    if (s15 <= 0) {
        s24 = zero;
        fg_store_u32_at(sp + 0x88, (uint32_t)(uintptr_t)&fg_aux[0]);
        goto L05b6;
    }
    s24 = one;
    fg_store_u32_at(sp + 0x88, (uint32_t)(uintptr_t)&fg_aux[0]);

L05b6:
    s0 = zero;
    s0 = fg_vmul(s19, s0);
    fg_43bb14((const float *)(uintptr_t)fg_load_u32(sp + 0x64),
              (int)n8, f150, n_bb, s0);
    fg_43bc58(f150, (const int32_t *)(sp + 0x118),
              (float *)(uintptr_t)fg_load_u32(sp + 0x68), n_ba6c);
    fg_store_u32_at(sp + 0x110, (uint32_t)n_ba6c[0]);
    fg_store_u32_at(sp + 0x114, (uint32_t)n_ba6c[1]);
    /* typographic 0x5bc-0x5e4 pointer slots */
    fg_store_u32_at(sp + 0x70, (uint32_t)(uintptr_t)(sp + 0x240));
    fg_store_u32_at(sp + 0xCC, (uint32_t)(uintptr_t)(st + 0xD0));
    fg_store_u32_at(sp + 0x5C, (uint32_t)(uintptr_t)(st + 8));
    fg_store_u32_at(sp + 0x80, (uint32_t)(uintptr_t)(st + 0xC0));

    /* 0x5fa-0x7e0: scale tables and 4-iteration MVE mix. */
    {
        float sc0 = fg_load_f32(st + 0xC0);
        float sc1 = fg_load_f32(st + 0xC8);
        float sc2 = fg_load_f32(st + 0xCC);
        float i78 = fg_load_f32(st + 0x78);
        float s7 = fg_load_f32(st + 0xB8);
        float *yp = (float *)(uintptr_t)fg_load_u32(sp + 0x68);
        s15 = fg_vnmul(yp[0], ((float *)(sp + 0x120))[0]);
        s12 = fg_vsub(((float *)(sp + 0x120))[0], one);
        ia = fg_vcvt_s32(s7);
        fg_store_f32_at(sp + 0x2C0 + ((uint32_t)ia << 2) - 212, s12);
        s13 = fg_state_tab(st, ia);
        s14 = fg_vfma(one, s13, s24);
        s15 = fg_vmul(s15, s14);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ia << 2) - 4, s15);

        /* 4-wide mixes typographic 0x670-0x7e0, 4 dls iterations. */
        {
            f32x4 q5 = q_dup(sc0);
            f32x4 q0 = q_dup(sc1);
            f32x4 q2 = q_mul(q_dup(fg_load_f32(st + 0xC4)), q_load(sp + 0x210));
            f32x4 q1 = q_dup(sc2);
            f32x4 q3 = q_mul(q_dup(s24), q_load(sp + 0x1F0));
            f32x4 q6 = q_mul(q_dup(i78), q_load(sp + 0x1E0));
            q3 = q_add(q3, q6);
            q_store(sp + 0x178, q3);
            q5 = q_mul(q5, q_load(sp + 0x200));
            q0 = q_mul(q0, q_load(sp + 0x220));
            q2 = q_add(q2, q5);
            q2 = q_add(q2, q0);
            q1 = q_mul(q1, q_load(sp + 0x230));
            q2 = q_add(q2, q1);
            q_store(sp + 0x188, q2);
        }
        /* 4-iteration loop 0x718-0x7e0: s11=pb+pa into state+0xC0;
         * column stores of two 4-wide mixes to sp+0x280 then sp+0x240.
         * Does not write state+8; that happens at 0x912-0x922. */
        {
            float *pa = (float *)(sp + 0x178);
            float *pb = (float *)(sp + 0x188);
            float *dstc = (float *)(st + 0xC0);
            float *tile200 = (float *)(sp + 0x200);
            float *tile210 = (float *)(sp + 0x210);
            float *tile220 = (float *)(sp + 0x220);
            float *tile230 = (float *)(sp + 0x230);
            float *out240 = (float *)(sp + 0x240);
            float *out280 = (float *)(sp + 0x280);
            const float *p8 = (const float *)(st + 8);
            int iter;
            for (iter = 0; iter < 4; iter++) {
                f32x4 q0, q1, q2, q3, q4, q5, q6, q7, mix0, mix1;
                dstc[iter] = fg_vadd(pb[iter], pa[iter]);
                fg_vld4(p8, &q4, &q5, &q6, &q7);
                q3 = q_dup(tile200[iter]);
                q0 = q_dup(tile210[iter]);
                q1 = q_dup(tile220[iter]);
                q2 = q_dup(tile230[iter]);
                q0 = q_mul(q0, q5);
                q3 = q_mul(q3, q4);
                q1 = q_mul(q1, q6);
                q3 = q_add(q0, q3);
                q2 = q_mul(q2, q7);
                q3 = q_add(q3, q1);
                q3 = q_add(q3, q2);
                mix0 = q3;
                out280[iter] = mix0.v[0];
                out280[iter + 4] = mix0.v[1];
                out280[iter + 8] = mix0.v[2];
                out280[iter + 12] = mix0.v[3];
                q5 = q_dup(mix0.v[1]);
                q3 = q_mul(q5, q_load(tile210));
                q0 = q_dup(mix0.v[2]);
                q1 = q_mul(q_dup(mix0.v[0]), q_load(tile200));
                q2 = q_mul(q0, q_load(tile220));
                q3 = q_add(q3, q1);
                q0 = q_dup(mix0.v[3]);
                q3 = q_add(q3, q2);
                q2 = q_mul(q0, q_load(tile230));
                mix1 = q_add(q3, q2);
                out240[iter] = mix1.v[0];
                out240[iter + 4] = mix1.v[1];
                out240[iter + 8] = mix1.v[2];
                out240[iter + 12] = mix1.v[3];
            }
        }
    }
    /* 0x7e8: s0=-1, then 439f88(s0=-1, s1=state_tab[(int)state[0xB8]]) */
    s1 = fg_state_tab(st, fg_vcvt_s32(fg_load_f32(st + 0xB8)));
    s0 = fg_439f88(mone, s1);
    s15 = fg_439efc(one, s0);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xB8));
    fg_store_f32_at(st + 0xBC + ((uint32_t)ia << 2), s15);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s1 = fg_state_tab(st, ia);
    s0 = fg_439f88(c_m005, s1);
    s0 = fg_439efc(c_105, s0);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    fg_store_f32_at(st + 0xBC + ((uint32_t)ia << 2), s0);

    /* 0x868-0x926: scale f168 by state[0x4C], vst4 into sp+0x200, add into state+8. */
    {
        float k4c = fg_load_f32(st + 0x4C);
        f32x4 q5 = q_load(sp + 0x168);
        f32x4 q0 = q_mul(q_dup(fg_vmul(k4c, q5.v[0])), q5);
        f32x4 q1 = q_mul(q_dup(fg_vmul(k4c, q5.v[1])), q5);
        f32x4 q2 = q_mul(q_dup(fg_vmul(k4c, q5.v[2])), q5);
        f32x4 q3 = q_mul(q_dup(fg_vmul(k4c, q5.v[3])), q5);
        fg_vst4((float *)(sp + 0x200), q0, q1, q2, q3);
        {
            float *acc = (float *)(st + 8);
            float *addv = (float *)(sp + 0x200);
            float *src2 = (float *)(sp + 0x210); /* typographic r3 starts at fp=sp+0x200 after vst4 */
            /* typographic: r3=fp (sp+0x200), r1=sp+0x70, r2=state+8, 4x16B adds.
             * 0x910 ldr r1, [sp,#112] — set at 0x5c0 to sp+0x240, not 0x70 after reuse.
             * Then vldrw q3,[r1],#16; q2,[r3],#16; add; vstr [r2],#16. 4 iters.
             * If r1 is sp+0x240 this adds sp+0x240 into state+8, while r3 walks
             * the vst4 output at sp+0x200. Need the live r1. At 0x5c0 ip=sp+0x240
             * stored at 0x70. 0x910 uses that. */
            addv = (float *)(sp + 0x240);
            src2 = (float *)(sp + 0x200);
            for (k = 0; k < 16; k++)
                acc[k] = fg_vadd(addv[k], src2[k]);
        }
    }
    /* 0x92a: 43bc84(query=state_tab[(int)state[0xBC]], k=s17=lo/T,
     *         x=model (param start?), y1=model+0x518, y2=model+0x83c) */
    {
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        s0 = fg_43bc84(fg_state_tab(st, ia), s17,
                       (const float *)mod,
                       (const float *)(mod + 0x518),
                       (const float *)(mod + 0x83C));
        /* vfms with state[(int)state[4]] and state[(int)state[0]] tabs, and f1c8[0] */
        ib = fg_vcvt_s32(fg_load_f32(st + 4));
        ic = fg_vcvt_s32(fg_load_f32(st + 0));
        s0 = fg_vfms(s0, fg_state_tab(st, ib), s18);
        s0 = fg_vfms(s0, f1c8[0], fg_state_tab(st, ic));
        n3 = (int32_t)fg_load_u32(sp + 0x60);
        if (n3 > 0) {
            float *src = f144;
            float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
            for (k = 0; k < n3; k++) {
                float t = fg_vfms(s0, src[k], s16);
                g[k] = t;
            }
        }
    }
    /* 0x9a8: 43be18 similarly, y1=model+0xB60, y2=model+0xE84 */
    {
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        q_store(sp + 0x168, q_dup(zero));
        s0 = fg_43be18(fg_state_tab(st, ia), s17,
                       (const float *)mod,
                       (const float *)(mod + 0xB60),
                       (const float *)(mod + 0xE84));
        /* 0xa06.. stores into f168-indexed slots, then a reduction + loop
         * writing sl and 43bfac. */
        ib = fg_vcvt_s32(fg_load_f32(st + 0));
        ic = fg_vcvt_s32(fg_load_f32(st + 4));
        ia = fg_vcvt_s32(fg_load_f32(st + 0xB8));
        fg_store_f32_at(sp + 0x168 + ((uint32_t)(ia - 1) << 2), s0);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ib << 2) - 4, zero);
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ic << 2) - 4, fg_vneg(f1c8[0]));
        fg_store_f32_at(sp + 0x168 + ((uint32_t)ia << 2) - 4, fg_vneg(s18));
    }

    /* Reduce f168 and mix with state+8 via vld4, then 43bfac. */
    {
        float acc = fg_load_f32(st + 0x48);
        /* typographic 0xb16 dls 4: for each of 4 rows at state+8 */
        uint8_t *row = st + 8;
        float *outp = (float *)(sp + 0x188);
        /* s18 accumulated as sum of products + acc */
        float s18a = acc;
        /* A compact equivalent of the 0xb1e-0xb56 body: 4 iterations of
         * row-dot with f168's 4 values, div by running sum, store to sl. */
        float w0 = fg_load_f32(sp + 0x168);
        float w1 = fg_load_f32(sp + 0x16C);
        float w2 = fg_load_f32(sp + 0x170);
        float w3 = fg_load_f32(sp + 0x174);
        s18a = acc; /* typographic adds s18 after first reduction; init from state[0x48] at 0xa72 */
        /* 0xae2-0xb1a first reduces q3 lanes + s20=0 into s18, then loop. */
        {
            /* Build 4-wide products of f168 broadcasts vs vld4(state+8). */
            f32x4 qa, qb, qc, qd, qw0, qw1, qw2, qw3, qs;
            fg_vld4((const float *)(st + 8), &qa, &qb, &qc, &qd);
            qw0 = q_mul(q_dup(w0), qa);
            qw1 = q_mul(q_dup(w1), qb);
            qw2 = q_mul(q_dup(w2), qc);
            qw3 = q_mul(q_dup(w3), qd);
            qs = q_add(q_add(qw0, qw1), q_add(qw2, qw3));
            qs = q_mul(qs, q_load(sp + 0x168));
            /* horizontal add + 0 into s15, then s18 = s15 + state[0x48] */
            /* typographic: s6=q0+s20(0); s7=q1+s6; s15=q2+s7; s15+=q3; s18+=s15 */
            s15 = fg_vadd(qs.v[1], fg_vadd(qs.v[0], zero));
            s15 = fg_vadd(qs.v[2], s15);
            s15 = fg_vadd(s15, qs.v[3]);
            s18a = fg_vadd(s15, acc);
        }
        /* typographic 0xb2e: s15 = w1*b; vfma(w0,a); vfma(w2,c); vfma(w3,d) */
        for (k = 0; k < 4; k++) {
            float a = fg_load_f32(st + 8 + k);
            float b = fg_load_f32(st + 8 + 16 + k);
            float c = fg_load_f32(st + 8 + 32 + k);
            float d = fg_load_f32(st + 8 + 48 + k);
            s15 = fg_vmul(w1, b);
            s15 = fg_vfma(s15, w0, a);
            s15 = fg_vfma(s15, w2, c);
            s15 = fg_vfma(s15, w3, d);
            outp[k] = fg_vdiv(s15, s18a);
        }
        s18 = s18a;
        s14 = fg_vmul(s18, c_100);
        n3 = (int32_t)fg_load_u32(sp + 0x60);
        if (n3 > 0) {
            float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
            float *p9 = (float *)(uintptr_t)fg_load_u32(sp + 0x68);
            float *dest = p9;
            float vv = fg_load_f32(sp + 0x6C);
            for (k = 0; k < n3; k++) {
                float t = fg_vsub(vv, g[k]);
                *dest++ = t; /* store first; next mul reloads p9[0] */
                s15 = fg_vmul(t, p9[0]);
                flags[k] = (uint8_t)((s15 > s14) ? 1 : 0);
            }
        }
        r0i = fg_43bfac(flags, n3);
        if (r0i == 0)
            goto L0f50;
        /* 0xbb6: q5 = 0, r5 = 0, store zeros over sp+0x188, fall into 0xbc6 */
        q5v = q_dup(zero);
        q_store(sp + 0x188, q5v);
        r5f = zero; /* typographic movs r5, #0 */
        goto L0bc6;
    }

L0f50:
    /* typographic: q5 = load(sp+0x188), r5 = [sp,#0x194], b 0xbc6 */
    q5v = q_load(sp + 0x188);
    r5f = fg_load_f32(sp + 0x194); /* typographic ldr r5, [sp,#0x194] */

L0bc6:
    /* 0xbc6-0xbe0: state+0xC0 += vdup(*[sp,#0x68]) * q5 */
    {
        uint8_t *yp = (uint8_t *)(uintptr_t)fg_load_u32(sp + 0x68);
        uint8_t *c0p = (uint8_t *)(uintptr_t)fg_load_u32(sp + 0x80);
        f32x4 q3, q2;
        q3 = q_load(c0p);
        q2 = q_mul(q_dup(fg_load_f32(yp)), q5v);
        q3 = q_add(q3, q2);
        q_store(c0p, q3);
    }
    /* 0xbe2-0xc9e: 439f88/439efc clamps into state tab */
    s0 = fg_439f88(mone, fg_state_tab(st, fg_vcvt_s32(fg_load_f32(st + 0xB8))));
    s15 = fg_439efc(one, s0);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xB8));
    fg_store_f32_at(st + 0xBC + ((uint32_t)ia << 2), s15);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s0 = fg_439f88(zero, fg_state_tab(st, ia));
    s0 = fg_439efc(one, s0);
    /* r6 was captured before 439efc from vcvt(state[0xBC]) */
    fg_store_f32_at(st + 0xBC + ((uint32_t)ia << 2), s0);

    /* 0xc56-0xd14: (q5*s18) broadcasts times sp+0x188, subtract from
     * vld4(state+8), vst4 back. Then 0xd18 cbz r7 skips 0xd38. */
    {
        f32x4 q188, qa, qb, qc, qd, t1, t0, t2, t3;
        float sc0 = fg_vmul(q5v.v[0], s18);
        float sc1 = fg_vmul(q5v.v[1], s18);
        float sc2 = fg_vmul(q5v.v[2], s18);
        float sc3 = fg_vmul(q5v.v[3], s18);
        q188 = q_load(sp + 0x188);
        t1 = q_mul(q_dup(sc1), q188);
        t0 = q_mul(q_dup(sc0), q188);
        t2 = q_mul(q_dup(sc2), q188);
        t3 = q_mul(q_dup(sc3), q188);
        fg_vld4((const float *)(st + 8), &qa, &qb, &qc, &qd);
        qa = q_sub(qa, t0);
        qb = q_sub(qb, t1);
        qc = q_sub(qc, t2);
        qd = q_sub(qd, t3);
        fg_vst4((float *)(st + 8), qa, qb, qc, qd);
    }
    if (r0i != 0) {
        int32_t off = (int32_t)fg_load_u32(sp + 0xD4);
        s14 = fg_load_f32(st + 0x50);
        s15 = fg_vmul(fg_load_f32(st + ((uint32_t)off << 2) + 4), s14);
        fg_store_f32_at(st + ((uint32_t)off << 2) + 4, s15);
    }

L0d4e:
    /* SOC / scratch / opt write-out and state tail (0xd4e-0xee4). */
    s15 = fg_state_tab(st, fg_vcvt_s32(fg_load_f32(st + 0xBC)));
    s1 = fg_load_f32(st + 0x90);
    s15 = fg_vsub(s15, s1);
    /* delayed flags: vcmpe i,0 issued before the sub is used at 0xd74 ble */
    if (!(s16 <= 0)) {
        if (s15 > 0)
            fg_store_f32_at(st + 0xBC + ((uint32_t)fg_vcvt_s32(fg_load_f32(st + 0xBC)) << 2), s1);
    }
    if (s16 < 0)
        goto L0f7c;
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC)) - 1;
    goto L0d92;

L0f7c:
    if (s15 < 0) {
        fg_store_f32_at(st + 0xBC + ((uint32_t)fg_vcvt_s32(fg_load_f32(st + 0xBC)) << 2), s1);
        /* then 0x1268 -> 0xf8c */
    }
    {
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        s0 = fg_439f88(zero, fg_state_tab(st, ia));
        s0 = fg_439efc(c_099, s0);
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        fg_store_f32_at(st + 0xBC + ((uint32_t)ia << 2), s0);
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC)) - 1;
    }

L0d92:
    fg_store_f32_at(st + 0x78, s16);
    {
        uint32_t word = fg_load_u32(st + ((uint32_t)ia << 2) + 0xC0);
        if (soc)
            fg_store_u32_at(soc, word);
        r3i = (int32_t)fg_load_u32(sp + 0x94);
        s0 = fg_4397a8(fg_load_f32(st + ((uint32_t)r3i << 2) + 8));
        s0 = fg_vmul(s0, three);
        if (scratch)
            fg_store_f32_at(scratch, s0);
        fg_store_f32_at(st + 0x80, fg_load_f32(sp + 0x6C));
        /* pack 16 bytes at sp+0xf8: s14 from 0x84, word from 0x144, 0x90, 0x8c */
        fg_store_f32_at(sp + 0xF8, fg_load_f32(sp + 0x84));
        fg_store_u32_at(sp + 0xFC, fg_load_u32(sp + 0x144));
        fg_store_f32_at(sp + 0x100, fg_load_f32(sp + 0x90));
        fg_store_f32_at(sp + 0x104, fg_load_f32(sp + 0x8C));
        /* typographic stores that q to [sp+0xcc] which was state+0xD0 */
        memcpy(st + 0xD0, sp + 0xF8, 16);
    }
    if (fg_43a0f4(fg_load_f32(st + 0x88)) == 0)
        goto L1188;
L0dfe:
    fg_store_u32_at(st + 0x98, 0);
    st[0x94] = 0;
    s0 = s16;
    if (fg_43a0f4(s0) == 0)
        goto L0efe;
    s18 = bits_f32(fg_aux[0]); /* r3 at 0x88 is fg_aux */
    if (s18 != mone)
        goto L0f08;
    goto L0e2c;

L0efe:
    if (s16 < 0)
        goto L0e2c;
    goto L0f08;

L0e2c:
    s18 = bits_f32(fg_aux[0]);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    fg_store_f32_at(st + 0x9C, s18);
    fg_store_u32_at(st + 0xA0, fg_load_u32(st + 0xBC + ((uint32_t)ia << 2)));
    if (st[0x94] == 0)
        goto L0f44;
    goto L0e54;

L0f08:
    {
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        uint32_t tab = fg_load_u32(st + 0xBC + ((uint32_t)ia << 2));
        /* write {tab, s18, s18, s18} at state+0x9C */
        fg_store_u32_at(st + 0x9C, tab);
        fg_store_f32_at(st + 0xA0, s18);
        fg_store_f32_at(st + 0xA4, s18);
        fg_store_f32_at(st + 0xA8, s18);
        if (st[0x94] != 0)
            goto L0e54;
    }

L0f44:
    s15 = fg_vadd(s19, fg_load_f32(st + 0x98));
    goto L0e66;

L0e54:
    s15 = s19;
    st[0x94] = 0;
    fg_store_u32_at(st + 0x9C, fg_load_u32(st + 0x90));

L0e66:
    fg_store_f32_at(st + 0x98, s15);
    fg_store_f32_at(st + 0x84, s18);
    if (s16 > 0 && s19 > 0)
        goto L106a;

L0e86:
    s15 = fg_load_f32(st + 0x98); /* typographic uses the s15 already in the reg at 0xe88 vcmpe s15,0 — that's the value just stored */
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s14 = fg_state_tab(st, ia);
    /* delayed ble on s15 ? 0  (s15 is dt or dt+old) */
    if (!(s15 <= 0)) {
        if (s19 > 0)
            goto L10ae;
    }

L0eb2:
    fg_store_f32_at(st + 0x88, s16);
    fg_store_f32_at(st + 0x90, s14);
    fg_store_f32_at(st + 0x8C, s17);
    {
        float pack[4];
        float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
        pack[0] = g ? g[0] : zero;
        pack[1] = f144[0];
        pack[2] = r5f; /* typographic r5 from 0xF50 [sp,#0x194] or 0 from 0xBB6 */
        pack[3] = s17;
        if (opt)
            memcpy(opt, pack, 16);
    }
    return;

L106a:
    if (fg_43a0f4(fg_load_f32(st + 0x90)) != 0)
        goto L1218;
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s14 = fg_state_tab(st, ia);
    s13 = fg_load_f32(st + 0x90);
    if (s14 <= s13)
        goto L1362;
    goto L109c;

L1218:
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s14 = fg_state_tab(st, ia);
    goto L109c;

L109c:
    s15 = fg_load_f32(st + 0x98);
    if (s15 <= 0)
        goto L0eb2;
L10ae:
    s13 = fg_load_f32(st + 0x68);
    if (!(s13 < s15))
        goto L0eb2;
    s12 = fg_load_f32(st + 0x90);
    s13 = fg_vsub(s14, fg_load_f32(st + 0x9C));
    s20 = fg_vdiv(s13, s15);
    if (s12 > s14)
        goto L12a8;
    goto L10dc;

L12a8:
    if (fg_43a0f4(s18) != 0)
        goto L10dc;
    s0 = fg_vabs(fg_vdiv(s18, s20));
    if (s0 < fg_load_f32(st + 0x6C))
        goto L13b8;
    st[0x94] = 1;
    goto L10dc;

L13b8:
    s0 = fg_vabs(fg_vdiv(s20, s18));
    if (!(s0 < fg_load_f32(st + 0x6C)))
        st[0x94] = 1;
    goto L10dc;

L10dc:
    if (s20 < 0)
        goto L12f8;
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s14 = fg_state_tab(st, ia);
    goto L0eb2;

L12f8:
    /* CC/CV style TTF-like update of 0xA4 / 0x84 / 0xA8 */
    s15 = fg_vneg(fg_load_f32(st + 0x90));
    s18 = fg_vdiv(s15, s20);
    s0 = fg_load_f32(st + 0xA4);
    if (fg_43a0f4(s0) == 0)
        s11 = fg_load_f32(st + 0xA4);
    else
        s11 = s18;
    s12 = fg_vdiv(s19, fg_load_f32(st + 0x54));
    s15 = fg_vsub(one, s12);
    s15 = fg_vmul(s15, s11);
    s15 = fg_vfma(s15, s18, s12);
    if (s15 < zero)
        s15 = zero;
    fg_store_f32_at(st + 0xA4, s15);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    fg_store_f32_at(st + 0x84, s15);
    s14 = fg_state_tab(st, ia);
    goto L0eb2;

L1362:
    s14 = fg_vsub(s14, s13);
    s20 = fg_vdiv(s14, s19);
    s0 = fg_load_f32(st + 0xA8);
    if (fg_43a0f4(s0) == 0)
        s13 = fg_load_f32(st + 0xA8);
    else
        s13 = s20;
    s14 = fg_vdiv(s19, fg_load_f32(st + 0x58));
    s18 = fg_vsub(one, s14);
    s18 = fg_vmul(s18, s13);
    s18 = fg_vfma(s18, s20, s14);
    fg_store_f32_at(st + 0xA8, s18);
    ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
    s14 = fg_state_tab(st, ia);
    goto L109c;

L1188:
    s0 = fg_load_f32(st + 0x88);
    if (fg_43a0f4(s0) == 0)
        goto L11fe;
    s20 = bits_f32(fg_aux[0]);
    if (s20 == mone)
        goto L127a;
    goto L11a8;

L11fe:
    s15 = fg_load_f32(st + 0x88);
    if (s15 < 0)
        goto L127a;
    if (s15 <= 0) {
        s20 = zero;
        goto L11a8;
    }
    s20 = one;
    goto L11a8;

L11a8:
    if (fg_43a0f4(s16) == 0)
        goto L126e;
    s18 = bits_f32(fg_aux[0]);
    if (s18 != mone)
        goto L0e4a;
    goto L11ca;

L126e:
    if (!(s16 < 0))
        goto L11da;
    goto L11ca;

L11ca:
    if (s20 != mone)
        goto L0dfe;
    s18 = bits_f32(fg_aux[0]);
    goto L0e4a;

L11da:
    s18 = bits_f32(fg_aux[0]);
    goto L0e4a;

L127a:
    if (fg_43a0f4(s16) == 0)
        goto L12d8;
    s20 = bits_f32(fg_aux[0]);
    if (s20 == mone)
        goto L11a8;
    goto L0dfe;

L12d8:
    if (!(s16 < 0))
        goto L0dfe;
    if (fg_43a0f4(s16) == 0)
        goto L11da;
    s20 = mone;
    goto L11b4;

L11b4:
    s18 = bits_f32(fg_aux[0]);
    if (s18 != mone)
        goto L0e4a;
    goto L11ca;

L0e4a:
    if (st[0x94] == 0)
        goto L0f44;
    goto L0e54;

L0ee8:
    s17 = fg_load_f32(st + 0xAC);
    if (!(s17 < T))
        s17 = T;
    goto L003c;

L0fc6:
    {
        ia = fg_vcvt_s32(fg_load_f32(st + 0xBC));
        s14 = fg_load_f32(st + 0xBC); /* keep as s14 for later vcvt reuse */
        s15 = fg_state_tab(st, ia);
        s13 = fg_load_f32(st + 0x70);
        if (!(s15 < s13))
            goto L1020;
        if (n8 <= 0)
            goto L0316;
        {
            float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
            float s5c = fg_load_f32(st + 0x5C);
            for (k = 0; k < n8; k++)
                g[k] = fg_vmul(g[k], s5c);
        }
        ia = fg_vcvt_s32(s14);
        s15 = fg_state_tab(st, ia);
    }
L1020:
    if (!(s15 < c_099))
        goto L0316;
    s14 = fg_load_f32(st + 0x74);
    if (!(s14 < s15))
        goto L0316;
    if (n8 <= 0)
        goto L0316;
    {
        float *g = (float *)(uintptr_t)fg_load_u32(sp + 0x64);
        float s60 = fg_load_f32(st + 0x60);
        for (k = 0; k < n8; k++)
            g[k] = fg_vmul(g[k], s60);
    }
    goto L0316;

L1100:
    fg_memcpy(f198, mod + 0x159C, 24);
    goto L01ca;

L1126:
    fg_439fe4(s18, temps, f198, f280);
    f1c8[0] = f280[0];
    f1c8[1] = f280[1];
    r6v = 4;
    goto L025c;

L1144:
    s0 = fg_43a5dc(s18, temps, (const float *)(mod + 0x1578));
    f138[0] = s0;
    fg_store_u32_at(sp + 0x68, (uint32_t)(uintptr_t)f138);
    fg_store_u32_at(sp + 0x60, 1);
    goto L02da;

L1166:
    s0 = fg_43a5dc(s18, temps, (const float *)(mod + 0x15B4));
    ((float *)(sp + 0x12C))[0] = s0;
    fg_store_u32_at(sp + 0x64, (uint32_t)(uintptr_t)(sp + 0x12C));
    n8 = 1;
    goto L00e6;

L11e2:
    fg_store_u32_at(sp + 0x60, 1);
    goto L03da;

L11f6:
    r3i = 0x3FC / 4; /* mov r2, #0x3fc then memcpy nbytes = r2 from 0x176? */
    /* 0x11f6 mov r2, #0x3fc; b 0x176 which is lsls r2, r3, #2 already done
     * — it REPLACES the memcpy size with 0x3FC. */
    fg_memcpy(f1c8, mod + 0x159C, 0x3FC);
    if (st[0xB4] == 0)
        goto L01ca;
    {
        int cnt = (int)st[0xB4];
        int i2;
        for (i2 = 0; i2 < cnt; i2++)
            f198[i2] = f1c8[i2];
        for (i2 = 0; i2 < cnt; i2++)
            ((float *)(sp + 0x1A4))[i2] = f1c8[cnt + i2];
    }
    goto L01ca;

L123c:
    {
        float dv = fg_vabs(fg_vsub(fg_load_f32(sp + 0x6C), fg_load_f32(st + 0x80)));
        float di = fg_vabs(fg_vsub(fg_load_f32(st + 0x78), s16));
        fg_store_f32_at(sp + 0x84, fg_vdiv(dv, di));
        goto L037a;
    }

L1250:
    fg_store_u32_at(sp + 0x68, (uint32_t)(uintptr_t)f138);
    goto L02da;

L1258:
    r6v = n << 2;
    goto L025c;

L1260:
    fg_store_u32_at(sp + 0x64, (uint32_t)(uintptr_t)(sp + 0x12C));
    goto L00e6;
}
