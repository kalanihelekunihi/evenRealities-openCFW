/* Apollo LVGL image alignment update 0x4992cc..0x499350.
 * Branches match pinned LVGL v9.3 update_align. */
#include <stdint.h>

extern void audio_uart_lv_image_set_rotation_4988dc(void *, int32_t);
extern void audio_uart_lv_image_set_pivot_498a14(void *, int32_t, int32_t);
extern void audio_uart_page_43f66c(void *);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void audio_uart_lv_image_scale_update_4991e0(void *, int32_t, int32_t);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8u) |
        ((uint32_t)p[2] << 16u) | ((uint32_t)p[3] << 24u);
}

void audio_uart_lv_image_update_align_4992cc(void *object) {
    const uint8_t *image = (const uint8_t *)object;
    uint32_t align = (get32(image + 0x58u) >> 8u) & 0xfu;
    if (align != 11u && align != 12u) return;
    audio_uart_lv_image_set_rotation_4988dc(object, 0);
    audio_uart_lv_image_set_pivot_498a14(object, 0, 0);
    if (align == 12u) {
        audio_uart_lv_image_scale_update_4991e0(object, 256, 256);
        return;
    }
    int32_t width = (int32_t)get32(image + 0x3cu);
    int32_t height = (int32_t)get32(image + 0x40u);
    if (width == 0 || height == 0) return;
    audio_uart_page_43f66c(object);
    int32_t scale_x = (int32_t)((uint32_t)audio_uart_lv_obj_width_43fd9e(object) << 8u) / width;
    int32_t scale_y = (int32_t)((uint32_t)audio_uart_lv_obj_height_43fdda(object) << 8u) / height;
    audio_uart_lv_image_scale_update_4991e0(object, scale_x, scale_y);
}
