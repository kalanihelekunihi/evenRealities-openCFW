/* Apollo Main LVGL render-layer pass, stock 0x453e10..0x453f2e. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_display_pre_refresh_454692(void *);
extern uint32_t audio_uart_lv_color_has_alpha_440fc4(uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_ambiq_area_move_450bb2(void *, int32_t, int32_t);
extern void audio_uart_lv_draw_buf_clear_48ac40(void *, const void *);
extern void *audio_uart_display_active_screen_get(void *);
extern void *audio_uart_lv_display_bottom_layer_44fd38(void *);
extern void *audio_uart_lv_display_top_layer_44fcbe(void *);
extern void *audio_uart_lv_display_system_layer_44fcfc(void *);
extern void *audio_uart_lv_render_find_cover_453f2e(const void *, void *);
extern void audio_uart_lv_render_object_chain_453fce(void *, void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c";


static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_render_layer_reset_48471a(void *layer)
{
    if (layer == 0) {
        audio_uart_lvgl_log(3u, source, 0x183u, "lv_layer_reset",
                            "Asserted at expression: %s (%s)",
                            "layer != NULL", "NULL pointer");
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    uint8_t *const bytes = (uint8_t *)layer;
    bytes[0x38u] = 0xffu;
    write32(bytes, 0x39u, 0u);
}

