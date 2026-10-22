/* IAR DLIB / AEABI runtime leaves and the vector-table NMI default handler
 * from the low Apollo main image (no source path is retained for these).
 * Native rows: 0x4397a6, 0x439e90..0x439e9c, 0x43a110..0x43a1b0,
 * 0x43a5a0..0x43a5dc.
 *
 * Neighbouring rows that are not here: 0x438400..0x439b78 is Google liblc3
 * v1.1.3 (ltpf.c, bits.c; build it from upstream), and 0x439ce0..0x43a0ee,
 * 0x43a0f4, 0x43a1b0..0x43a59e and 0x43a5dc..0x43a690 belong to the closed
 * Nordic nrf_fuel_gauge library, which calls the helpers below.
 *
 * Integer only: the float/double parameters are moved as bit patterns. The
 * AEABI helper ABI is base AAPCS (float in r0, double in r0:r1 / r2:r3), so
 * the helpers carry pcs("aapcs") under the hard-float payload default. */
#include <stddef.h>
#include <stdint.h>

/* AEABI forward copy body 0x439be4 (app/byte-copy/byte_copy.c). */
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length);

typedef union { float f; uint32_t u; } p01_f32_bits_t;
typedef union { double d; uint64_t u; } p01_f64_bits_t;

/* Vector table slot 2 (ROM 0x438008 holds 0x4397a7): NMI default handler,
 * a single `b .`. */
void nmi_handler_4397a6(void)
{
    for (;;) {
    }
}

/* ISO memcpy: forwards to the AEABI copy body and returns the destination.
 * Used by nrf_fuel_gauge (e.g. 0x439d28, 0x43a1e4). */
void *memcpy_439e90(void *destination, const void *source, size_t length)
{
    audio_uart_checksum_copy(destination, source, (uint32_t)length);
    return destination;
}

/* __aeabi_f2d. Stock is `vmov s0,r0; vcvt.f64.f32 d0,s0; vmov r0,r1,d0`
 * (FPSCR default: no flush-to-zero, no default-NaN), reproduced here as
 * exact bit arithmetic: denormals are normalised, NaNs are quietened and
 * keep their payload. */
__attribute__((pcs("aapcs"))) double aeabi_f2d_43a110(float value)
{
    p01_f32_bits_t in = { .f = value };
    p01_f64_bits_t out;
    uint64_t sign = (uint64_t)(in.u >> 31) << 63;
    uint32_t exponent = (in.u >> 23) & 0xffu;
    uint32_t mantissa = in.u & 0x7fffffu;

    if (exponent == 0xffu) {
        out.u = sign | 0x7ff0000000000000ull | ((uint64_t)mantissa << 29);
        if (mantissa != 0u)
            out.u |= 0x0008000000000000ull;
    } else if (exponent != 0u) {
        out.u = sign | ((uint64_t)(exponent + 896u) << 52) | ((uint64_t)mantissa << 29);
    } else if (mantissa == 0u) {
        out.u = sign;
    } else {
        uint32_t e = 897u;
        while ((mantissa & 0x800000u) == 0u) {
            mantissa <<= 1;
            e--;
        }
        out.u = sign | ((uint64_t)e << 52) | ((uint64_t)(mantissa & 0x7fffffu) << 29);
    }
    return out.d;
}

/* IAR scatter-load decompressor (an __iar_lz77_init_single3-style handler),
 * referenced as 0x43a11f by rows 0x75d3e0/0x75d3f0/0x75d400 of the scatter
 * table and run by the loader at 0x5e42b4.
 * Record: +0 source offset relative to the record, +4 packed length << 1 |
 * static-base flag, +8 destination. Each token byte: bits 0-1 literal count
 * + 1 (0 => next byte + 3), bits 2-3 high offset byte (3 => explicit byte),
 * bits 4-7 match length - 2 (15 => next byte + 15). Returns the next record. */
typedef struct {
    int32_t source_offset;    /* +0 */
    uint32_t packed_length;   /* +4: length << 1 | r9-relative flag */
    uint32_t destination;     /* +8 */
} iar_lz77_record_t;
_Static_assert(sizeof(iar_lz77_record_t) == 12, "scatter record is three words");

const uint32_t *iar_lz77_init_single3_43a11e(const uint32_t *record)
{
    const iar_lz77_record_t *r = (const iar_lz77_record_t *)record;
    const uint8_t *src = (const uint8_t *)record + r->source_offset;
    const uint8_t *end = src + (r->packed_length >> 1);
    uint8_t *dst = (uint8_t *)(uintptr_t)r->destination;

    if (r->packed_length & 1u) {
        uintptr_t static_base;
        __asm volatile("mov %0, r9" : "=r"(static_base));
        dst += static_base;
    }

    while (src != end) {
        uint32_t token = *src++;
        uint32_t literals = token & 3u;
        uint32_t match;

        if (literals == 0u)
            literals = (uint32_t)*src++ + 3u;
        match = token >> 4;
        if (match == 15u)
            match = (uint32_t)*src++ + 15u;

        while (--literals != 0u)
            *dst++ = *src++;

        if (match != 0u) {
            uint32_t offset = *src++;
            uint32_t high = (token >> 2) & 3u;
            const uint8_t *back;

            if (high == 3u)
                high = *src++;
            back = dst - (offset + (high << 8));
            for (uint32_t i = 0u; i != match + 2u; i++)
                *dst++ = *back++;
        }
    }
    return record + 3;
}

/* __aeabi_dcmpun as linked: only the high words are inspected and the test is
 * (hi << 1) > 0xfff00000. It reports a NaN only when the top mantissa bit is
 * set together with another high-word mantissa bit; the default NaN
 * 0x7ff80000_00000000, signalling NaNs and NaNs whose payload is only in the
 * low word return 0. */
__attribute__((pcs("aapcs"))) int32_t aeabi_dcmpun_43a19c(double a, double b)
{
    p01_f64_bits_t x = { .d = a };
    p01_f64_bits_t y = { .d = b };

    if (((uint32_t)(x.u >> 32) << 1) > 0xfff00000u)
        return 1;
    return ((uint32_t)(y.u >> 32) << 1) > 0xfff00000u;
}

/* floorf core on the IEEE single bit pattern (r0 in, r0 out). */
uint32_t floorf_bits_43a5b0(uint32_t bits)
{
    int32_t e = (int32_t)((bits >> 23) & 0xffu) - 126;

    if (e <= 0) {
        /* |x| < 1: +0 and -0 unchanged, other negatives -1.0, positives +0. */
        uint32_t negative = bits & 0x80000000u;

        if ((bits << 1) != 0u)
            bits = 0xbf800000u;
        if (negative == 0u)
            bits = 0u;
        return bits;
    }
    if (e >= 24)
        return bits; /* integral, infinite or NaN */

    uint32_t mask = 0x00ffffffu >> (uint32_t)e;
    if ((int32_t)bits < 0)
        bits += mask;
    return bits & ~mask;
}

/* floorf (VFP entry: moves s0 to r0, calls the core, moves r0 back to s0).
 * Stock callers (liblc3 among them) pass x in s0: hard-float entry ABI. */
__attribute__((pcs("aapcs-vfp"))) float floorf_43a5a0(float value)
{
    p01_f32_bits_t v = { .f = value };

    v.u = floorf_bits_43a5b0(v.u);
    return v.f;
}
