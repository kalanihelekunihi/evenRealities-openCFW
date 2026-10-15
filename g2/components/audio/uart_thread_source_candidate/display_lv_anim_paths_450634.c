/* Apollo Main animation paths 0x450634..0x450659 and 0x450672..0x450687. */
#include <stdint.h>

extern int32_t audio_uart_lv_anim_interpolate_4888b4(int32_t, int32_t, int32_t,
                                                       int32_t, int32_t);
extern int32_t audio_uart_lv_anim_bezier_450a04(void *, int32_t, int32_t,
                                                 int32_t, int32_t);

int32_t audio_uart_lv_anim_default_path_450634(void *descriptor) {
    const uint8_t *const bytes = (const uint8_t *)descriptor;
    const int32_t elapsed = *(const int32_t *)(const void *)(bytes + 0x34u);
    const int32_t duration = *(const int32_t *)(const void *)(bytes + 0x30u);
    const int32_t progress = audio_uart_lv_anim_interpolate_4888b4(
        elapsed, 0, duration, 0, 0x400);
    const int32_t start = *(const int32_t *)(const void *)(bytes + 0x24u);
    const int32_t end = *(const int32_t *)(const void *)(bytes + 0x2cu);
    const uint32_t delta = (uint32_t)end - (uint32_t)start;
    const int32_t scaled = (int32_t)(delta * (uint32_t)progress);
    return (int32_t)((uint32_t)start + (uint32_t)(scaled >> 10));
}

int32_t audio_uart_lv_anim_path_450672(void *descriptor) {
    return audio_uart_lv_anim_bezier_450a04(descriptor, 0, 0, 0x251, 0x400);
}
