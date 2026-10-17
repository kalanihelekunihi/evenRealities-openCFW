/* Apollo Main LVGL maximum refresh stripe height, 0x4544ae..0x454572. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_font_bitmap_stride(uint32_t, uint8_t);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";
static const char function[] = "get_max_row";

uint32_t audio_uart_lv_refresh_chunk_height_4544ae(void *display,
                                                     uint32_t width,
                                                     uint32_t height)
{
    const uint8_t *const bytes = (const uint8_t *)display;
    const uint8_t format = bytes[0x3cu];
    const uint32_t stride = audio_uart_font_bitmap_stride(width, format);
    uint32_t reserved = 0u;
    if (format == 7u) reserved = 2u;
    else if (format == 8u) reserved = 4u;
    else if (format == 9u) reserved = 16u;
    else if (format == 10u) reserved = 256u;
    reserved *= 4u;
    if (stride == 0u) {
        audio_uart_lvgl_log(2u, source, 0x4c9u, function,
                            "Invalid stride. Value is 0");
        return 0u;
    }
    const uint8_t *const draw = (const uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(bytes + 0x24u);
    uint32_t max_rows =
        (*(const uint32_t *)(const void *)(draw + 0x0cu) - reserved) / stride;
    if ((int32_t)height < (int32_t)max_rows) max_rows = height;
    uint32_t rows = max_rows;
    uint32_t rounded_rows = 0u;
    for (;;) {
        int32_t area[4] = {0, 0, 0, (int32_t)(rows - 1u)};
        void *const current = (void *)(uintptr_t)
            *(const uint32_t *)(const void *)(audio_uart_display_lv_root + 0x10u);
        (void)audio_uart_lv_display_event_44fdbe(current, 0x35u, area);
        if ((int32_t)max_rows >= (int32_t)audio_uart_lv_area_height_4515a4(area)) {
            rounded_rows = (uint32_t)area[3] + 1u;
            break;
        }
        --rows;
        if ((int32_t)rows < 1) break;
    }
    if ((int32_t)rows >= 1) return rounded_rows;
    audio_uart_lvgl_log(2u, source, 0x4e5u, function,
                        "Can't set draw_buf height using the round function. (Wrong round_cb or too small draw_buf)");
    return 0u;
}
