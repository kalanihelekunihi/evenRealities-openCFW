/* Loaded image-B inverse RFFT split 0x1000f068..0x1000f0be.
 * The stock body uses C-SKY DSPv2 packed Q15 instructions; each is written
 * here as C on the two int16 lanes of a word, with the instruction's
 * saturation (semantics as XuanTie QEMU target/csky op_dspv2.c and
 * translate_v2.c). The pinned SDK scalar lowering differs by one Q15 count
 * in the full IMCRA oracle, so the stock lane sequence is kept as is.
 */
#include <stdint.h>

static inline __attribute__((always_inline)) int32_t lane_lo(uint32_t x)
{
    return (int16_t)(uint16_t)x;
}

static inline __attribute__((always_inline)) int32_t lane_hi(uint32_t x)
{
    return (int16_t)(uint16_t)(x >> 16);
}

static inline __attribute__((always_inline)) uint32_t lanes(int32_t hi, int32_t lo)
{
    return ((uint32_t)(uint16_t)hi << 16) | (uint16_t)lo;
}

static inline __attribute__((always_inline)) int32_t sat_s16(int32_t v)
{
    return v > INT16_MAX ? INT16_MAX : v < INT16_MIN ? INT16_MIN : v;
}

static inline __attribute__((always_inline)) uint32_t sat_s32(int64_t v)
{
    return (uint32_t)(int32_t)(v > INT32_MAX ? INT32_MAX : v < INT32_MIN ? INT32_MIN : v);
}

/* psub.16: lane-wise subtraction, wrapping. */
static inline __attribute__((always_inline)) uint32_t psub_16(uint32_t x, uint32_t y)
{
    return lanes(lane_hi(x) - lane_hi(y), lane_lo(x) - lane_lo(y));
}

/* pabs.s16.s: lane-wise |v|, saturating (-32768 -> 32767). */
static inline __attribute__((always_inline)) uint32_t pabs_s16_s(uint32_t x)
{
    const int32_t lo = lane_lo(x), hi = lane_hi(x);
    return lanes(sat_s16(hi < 0 ? -hi : hi), sat_s16(lo < 0 ? -lo : lo));
}

/* pneg.s16.s: lane-wise -v, saturating. */
static inline __attribute__((always_inline)) uint32_t pneg_s16_s(uint32_t x)
{
    return lanes(sat_s16(-lane_hi(x)), sat_s16(-lane_lo(x)));
}

/* pkg rz, rx, 0, ry, 16: {ry[31:16], rx[15:0]}. */
static inline __attribute__((always_inline)) uint32_t pkg_lo_hi(uint32_t x, uint32_t y)
{
    return (y & UINT32_C(0xffff0000)) | (x & 0xffffu);
}

/* pkghh: {ry[31:16], rx[31:16]}. */
static inline __attribute__((always_inline)) uint32_t pkghh(uint32_t x, uint32_t y)
{
    return (y & UINT32_C(0xffff0000)) | (x >> 16);
}

/* mulcs.s16: lo*lo - hi*hi, 32-bit wrapping (cannot overflow). */
static inline __attribute__((always_inline)) uint32_t mulcs_s16(uint32_t x, uint32_t y)
{
    return (uint32_t)(lane_lo(x) * lane_lo(y)) - (uint32_t)(lane_hi(x) * lane_hi(y));
}

/* mulcax.s16.s: saturate(hi(x)*lo(y) + lo(x)*hi(y)); only x = y =
 * 0x80008000 exceeds int32. */
static inline __attribute__((always_inline)) uint32_t mulcax_s16_s(uint32_t x, uint32_t y)
{
    return sat_s32((int64_t)lane_hi(x) * lane_lo(y) + (int64_t)lane_lo(x) * lane_hi(y));
}

/* mulaca.s16.s: saturate(z + (hi*hi + lo*lo)); the product sum is a 32-bit
 * value (it wraps only for x = y = 0x80008000), as the QEMU model. */
static inline __attribute__((always_inline)) uint32_t mulaca_s16_s(uint32_t z, uint32_t x, uint32_t y)
{
    const int32_t sum = (int32_t)((uint32_t)(lane_hi(x) * lane_hi(y)) +
                                  (uint32_t)(lane_lo(x) * lane_lo(y)));
    return sat_s32((int64_t)(int32_t)z + sum);
}

/* mulacsx.s16.s: saturate(z + (lo(x)*hi(y) - hi(x)*lo(y))). */
static inline __attribute__((always_inline)) uint32_t mulacsx_s16_s(uint32_t z, uint32_t x, uint32_t y)
{
    const int32_t diff = lane_lo(x) * lane_hi(y) - lane_hi(x) * lane_lo(y);
    return sat_s32((int64_t)(int32_t)z + diff);
}

void gx8002_image_b_split_rifft_q15_1000f068(
    const int16_t *source, uint32_t length, const int16_t *coefficient,
    int16_t *destination, uint32_t modifier)
{
    const uint32_t *left = (const uint32_t *)(const void *)source;
    const uint32_t *right = (const uint32_t *)(const void *)(source + 2u * length);
    uint32_t *output = (uint32_t *)(void *)destination;
    const uint32_t *table = (const uint32_t *)(const void *)coefficient;
    for (uint32_t i = 0; i < length; ++i) {
        const uint32_t a = *table;
        uint32_t b = psub_16(UINT32_C(0x8000), a);
        b = pkg_lo_hi(pabs_s16_s(b), b);
        const uint32_t input_left = *left++;
        const uint32_t input_right = *right--;
        uint32_t real = mulcs_s16(input_right, b);
        uint32_t imag = mulcax_s16_s(input_right, b);
        real = mulaca_s16_s(real, input_left, a);
        imag = pneg_s16_s(imag);
        imag = mulacsx_s16_s(imag, a, input_left);
        *output++ = pkghh(real, imag);
        table += modifier;
    }
}
