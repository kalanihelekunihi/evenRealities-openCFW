/* Native FT_Stroker_Cap round branch, 0x568870.  The arc emitter at
 * 0x56851e is a separate, typed source contract. */
#include <stdint.h>

typedef struct { int32_t x, y; } Vector;
extern int32_t audio_uart_font_stroker_arc_emit(void *border,
        const Vector *center, uint32_t radius, uint32_t angle,
        int32_t sweep); /* 0x56851e */
extern int32_t audio_uart_font_stroker_angle_diff(int32_t, int32_t); /* 0x52910e */

static uint32_t word(const void *p, uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p + offset);
}

int32_t audio_uart_font_stroker_round_cap(void *stroker, uint32_t side) {
    uint8_t *s = (uint8_t *)stroker;
    void *border = s + 0x34u + (side << 5);
    uint32_t start = 0x5a0000u - side * 0xb40000u;
    int32_t delta = audio_uart_font_stroker_angle_diff((int32_t)word(s, 0u),
                                                       (int32_t)word(s, 4u));
    if (delta == 0xb40000)
        delta = -(int32_t)start * 2;
    uint32_t angle = start + word(s, 0u);
    int32_t error = audio_uart_font_stroker_arc_emit(border,
            (const Vector *)(const void *)(s + 8u), word(s, 0x30u),
            angle, delta);
    s[0x34u + (side << 5) + 16u] = 0;
    return error;
}
