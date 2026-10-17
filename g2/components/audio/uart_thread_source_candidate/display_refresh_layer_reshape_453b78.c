/* Apollo Main LVGL refresh-layer draw-buffer reshape, 0x453b78..0x453bce. */
#include <stdint.h>

extern int32_t audio_uart_lv_area_height_4515a4(const void *);
extern int32_t audio_uart_lv_area_width_451598(const void *);
extern void *audio_uart_lv_draw_buf_reshape_48b196(void *, uint32_t,
                                                    uint32_t, uint32_t, uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";

void audio_uart_lv_layer_reshape_draw_buf_453b78(void *layer, uint32_t stride)
{
    const uint8_t *const bytes = (const uint8_t *)layer;
    const uint32_t height = (uint32_t)audio_uart_lv_area_height_4515a4(bytes + 4u);
    const uint32_t width = (uint32_t)audio_uart_lv_area_width_451598(bytes + 4u);
    void *const draw = (void *)(uintptr_t)
        *(const uint32_t *)(const void *)bytes;
    if (audio_uart_lv_draw_buf_reshape_48b196(draw, bytes[0x14u], width,
                                               height, stride) == 0) {
        audio_uart_lvgl_log(3u, source, 0x28du, "layer_reshape_draw_buf",
                            "Asserted at expression: %s (%s)",
                            "ret != NULL", "NULL pointer");
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
}
