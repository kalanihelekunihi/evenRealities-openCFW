#include "native_gomore_accel_ring_score.h"
#include "native_float_to_signed.h"
#define FP __attribute__((noinline,noclone))
static FP float convert(uint32_t x) { return (float)(int32_t)x; }
static FP float multiply(float a, float b) { return a * b; }
static FP float madd(float acc, float a, float b) { return acc + a * b; }
static FP float divide(float a, float b) { return a / b; }
static FP float add(float a, float b) { return a + b; }
static float value(uint32_t bits)
{
    union {uint32_t bits; float value;} u = {.bits=bits};
    return u.value;
}
static int32_t sample(uint32_t at) { return *(volatile int16_t *)(uintptr_t)at; }
uint32_t r1_gomore_accel_ring_score_native(uint32_t a, uint32_t b, uint32_t c,
                                         uint32_t d, uint32_t e, uint32_t f,
                                         uint32_t length, uint32_t cursor,
                                         uint32_t window)
{
    if ((int32_t)(length - window) < 0) return UINT32_MAX;
    uint32_t sums[6] = {0, 0, 0, 0, 0, 0};
    for (uint32_t step = 1; (int32_t)step <= (int32_t)window; step++) {
        uint32_t position = cursor - step;
        if ((int32_t)position < 0) position += length;
        uint32_t offset = (uint32_t)(int32_t)(int8_t)position * 2u;
        sums[0] += (uint32_t)sample(a + offset);
        sums[1] += (uint32_t)sample(b + offset);
        sums[2] += (uint32_t)sample(c + offset);
        sums[3] += (uint32_t)sample(d + offset);
        sums[4] += (uint32_t)sample(e + offset);
        sums[5] += (uint32_t)sample(f + offset);
    }
    uint32_t maximum = sums[3], middle = sums[4], minimum = sums[5];
    if ((int32_t)maximum < (int32_t)middle) {
        uint32_t swap = maximum; maximum = middle; middle = swap;
    }
    if ((int32_t)middle < (int32_t)minimum) {
        uint32_t swap = middle; middle = minimum; minimum = swap;
    }
    if ((int32_t)maximum < (int32_t)middle) {
        uint32_t swap = maximum; maximum = middle; middle = swap;
    }
    /* Immutable typed coefficient words at stock 0xbd27c; bias at 0x56b98. */
    float score = 0.0f;
    if (window != 0) {
        score = multiply(value(0xba8e0d9f), convert(sums[0]));
        score = madd(score, convert(sums[1]), value(0x3c5d639e));
        score = madd(score, convert(sums[2]), value(0xba815ee5));
        score = madd(score, convert(maximum), value(0xbca9fb3c));
        score = madd(score, convert(middle), value(0xbc0befee));
        score = madd(score, convert(minimum), value(0x3c2c7c80));
        score = divide(score, convert(window));
    }
    score = add(score, value(0x3f8f797d));
    score = multiply(score, value(0x447a0000));
    int32_t result = (int32_t)r1_native_float_to_signed32(score);
    if (result > 32000) result = 32000;
    if (result < -32000) result = -32000;
    return (uint32_t)(int32_t)(int16_t)result;
}
