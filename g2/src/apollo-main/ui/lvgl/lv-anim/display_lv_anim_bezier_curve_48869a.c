/* Apollo Main fixed-point Bezier solver, native spans 0x488686/0x48869a. */
#include <stdint.h>

extern int64_t audio_uart_lv_div64_47cc1c(int64_t numerator, int64_t denominator);

static int32_t add32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a + (uint32_t)b);
}
static int32_t sub32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a - (uint32_t)b);
}
static int32_t mul32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a * (uint32_t)b);
}
static int32_t abs32(int32_t value) {
    return value < 0 ? sub32(0, value) : value;
}

int32_t audio_uart_lv_anim_polynomial_488686(int32_t t, int32_t a,
                                               int32_t b, int32_t c) {
    const int32_t inner = add32(b, mul32(t, a) >> 10);
    const int32_t middle = add32(c, mul32(t, inner) >> 10);
    return mul32(t, middle) >> 10;
}

int32_t audio_uart_lv_anim_bezier_curve_48869a(int32_t progress,
                                                 int32_t x1, int32_t y1,
                                                 int32_t x2, int32_t y2) {
    if (progress == 0 || progress == 0x400) return progress;
    const int32_t bx = mul32(3, x1);
    const int32_t cx = sub32(mul32(3, sub32(x2, x1)), bx);
    const int32_t ax = sub32(sub32(0x400, bx), cx);
    const int32_t by = mul32(3, y1);
    const int32_t cy = sub32(mul32(3, sub32(y2, y1)), by);
    const int32_t ay = sub32(sub32(0x400, by), cy);
    int32_t t = progress;
    for (int32_t count = 0; count < 8; ++count) {
        const int32_t error = sub32(audio_uart_lv_anim_polynomial_488686(t, ax, cx, bx), progress);
        if (abs32(error) < 2) goto result;
        const int32_t triple = mul32(3, mul32(ax, t)) >> 10;
        const int32_t derivative = add32(bx, mul32(t, add32(triple, mul32(2, cx))) >> 10);
        if (abs32(derivative) < 2) break;
        const int32_t step = (int32_t)audio_uart_lv_div64_47cc1c(
            (int64_t)error * 0x400, (int64_t)derivative);
        if (step == 0) break;
        t = sub32(t, step);
    }
    {
        int32_t low = 0;
        int32_t high = 0x400;
        t = progress;
        if (t < low) t = low;
        if (t > high) t = high;
        while (low < high) {
            const int32_t estimate = audio_uart_lv_anim_polynomial_488686(t, ax, cx, bx);
            if (abs32(sub32(estimate, progress)) < 2) break;
            if (estimate < progress) low = t;
            else high = t;
            const int32_t half = sub32(high, low) / 2;
            t = add32(low, half);
            if (t == low) break;
        }
    }
result:
    return audio_uart_lv_anim_polynomial_488686(t, ay, cy, by);
}
