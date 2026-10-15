/* Apollo LV event extent helper, native 0x452c66..0x452d41. */
#include <stdint.h>

extern int32_t audio_uart_lv_compass_part_452450(void *, uint32_t);
extern uint32_t audio_uart_lv_compass_part_452498(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_45246e(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_45245a(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_452464(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_452410(void *, uint32_t);
extern uint32_t audio_uart_lv_compass_part_45243a(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_452446(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_4522d4(void *, uint32_t);
extern int32_t audio_uart_lv_compass_part_4522de(void *, uint32_t);

static int32_t add32(int32_t a, int32_t b) {
    return (int32_t)((uint32_t)a + (uint32_t)b);
}
static int32_t abs32(int32_t a) {
    return a < 1 ? (int32_t)(0u - (uint32_t)a) : a;
}

uint32_t audio_uart_lv_compass_452c66(void *object, uint32_t selector) {
    int32_t extent = 0;
    int32_t first = audio_uart_lv_compass_part_452450(object, selector);
    if (first != 0 && (uint8_t)audio_uart_lv_compass_part_452498(object, selector) > 2u) {
        int32_t offset = audio_uart_lv_compass_part_45246e(object, selector);
        int32_t x = audio_uart_lv_compass_part_45245a(object, selector);
        int32_t y = audio_uart_lv_compass_part_452464(object, selector);
        int32_t magnitude = abs32(x) > abs32(y) ? abs32(x) : abs32(y);
        int32_t candidate = add32(add32(add32(first / 2, 1), offset), magnitude);
        if (candidate >= 0) extent = candidate;
    }
    int32_t second = audio_uart_lv_compass_part_452410(object, selector);
    if (second != 0 && (uint8_t)audio_uart_lv_compass_part_45243a(object, selector) > 2u) {
        int32_t offset = audio_uart_lv_compass_part_452446(object, selector);
        int32_t candidate = add32(second, offset);
        if (candidate >= extent) extent = candidate;
    }
    int32_t low = audio_uart_lv_compass_part_4522d4(object, selector);
    int32_t high = audio_uart_lv_compass_part_4522de(object, selector);
    int32_t base = low > high ? low : high;
    if (base > 0) extent = add32(extent, base);
    return (uint32_t)extent;
}
