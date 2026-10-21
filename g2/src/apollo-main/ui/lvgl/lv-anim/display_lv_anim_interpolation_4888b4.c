/* Apollo Main LVGL linear interpolation and Bezier path, 0x4888b4/0x450a04. */
#include <stdint.h>

extern int32_t audio_uart_lv_anim_bezier_curve_48869a(int32_t, int32_t,
                                                       int32_t, int32_t, int32_t);

int32_t audio_uart_lv_anim_interpolate_4888b4(int32_t position, int32_t start,
                                               int32_t end, int32_t from,
                                               int32_t to) {
    if (end >= start) {
        if (position >= end) return to;
        if (position <= start) return from;
    } else {
        if (position <= end) return to;
        if (position >= start) return from;
    }
    const int32_t range = (int32_t)((uint32_t)end - (uint32_t)start);
    const int32_t rise = (int32_t)((uint32_t)to - (uint32_t)from);
    const int32_t step = (int32_t)((uint32_t)position - (uint32_t)start);
    const int32_t product = (int32_t)((uint32_t)rise * (uint32_t)step);
    const int32_t quotient = (product == INT32_MIN && range == -1)
        ? INT32_MIN : product / range;
    return (int32_t)((uint32_t)from + (uint32_t)quotient);
}

int32_t audio_uart_lv_anim_bezier_450a04(void *descriptor, int32_t c1,
                                          int32_t c2, int32_t c3, int32_t c4) {
    const uint8_t *const bytes = (const uint8_t *)descriptor;
    const int32_t elapsed = *(const int32_t *)(const void *)(bytes + 0x34u);
    const int32_t duration = *(const int32_t *)(const void *)(bytes + 0x30u);
    const int32_t progress = audio_uart_lv_anim_interpolate_4888b4(
        elapsed, 0, duration, 0, 0x400);
    const int32_t curved = audio_uart_lv_anim_bezier_curve_48869a(
        progress, c1, c2, c3, c4);
    const int32_t from = *(const int32_t *)(const void *)(bytes + 0x24u);
    const int32_t to = *(const int32_t *)(const void *)(bytes + 0x2cu);
    const uint32_t delta = (uint32_t)to - (uint32_t)from;
    const int32_t scaled = (int32_t)(delta * (uint32_t)curved);
    return (int32_t)((uint32_t)from + (uint32_t)(scaled >> 10));
}
