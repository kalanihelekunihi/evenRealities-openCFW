/* Stock LVGL button fade Bezier path, 0x450688..0x45069f. */
#include <stdint.h>

extern int32_t audio_uart_lv_anim_bezier_450a04(void *, int32_t, int32_t,
                                                 int32_t, int32_t);

int32_t audio_uart_lv_anim_path_450688(void *descriptor) {
    return audio_uart_lv_anim_bezier_450a04(descriptor, 0x1ae, 0, 0x251, 0x400);
}
