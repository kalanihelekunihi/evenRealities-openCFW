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

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

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

void audio_uart_lv_render_layer_453e10(void *layer_arg)
{
    uint8_t *const layer = (uint8_t *)layer_arg;
    audio_uart_lv_render_layer_reset_48471a(layer);
    uint8_t *const display = (uint8_t *)(uintptr_t)
        read32(audio_uart_display_lv_root, 0x10u);
    if (read32(display, 0x20u) == 0u)
        audio_uart_lv_display_pre_refresh_454692(display);
    if (audio_uart_lv_color_has_alpha_440fc4(display[0x3cu]) != 0u) {
        int32_t clear_area[4];
        (void)audio_uart_display_area_copy_439c04(clear_area,
                                                    layer + 0x18u, 16u);
        audio_uart_ambiq_area_move_450bb2(clear_area,
                                            -(int32_t)read32(layer, 4u),
                                            -(int32_t)read32(layer, 8u));
        audio_uart_lv_draw_buf_clear_48ac40(
            (void *)(uintptr_t)read32(layer, 0u), clear_area);
    }
    void *const active = audio_uart_display_active_screen_get(display);
    void *active_cover = audio_uart_lv_render_find_cover_453f2e(
        layer + 0x18u, active);
    void *previous_cover = 0;
    if (read32(display, 0x2ccu) != 0u)
        previous_cover = audio_uart_lv_render_find_cover_453f2e(
            layer + 0x18u, (void *)(uintptr_t)read32(display, 0x2ccu));
    if (active_cover == 0 && previous_cover == 0)
        audio_uart_lv_render_object_chain_453fce(
            layer, audio_uart_lv_display_bottom_layer_44fd38(display));
    if ((display[0x2d8u] & 1u) != 0u) {
        if (active_cover == 0)
            active_cover = (void *)(uintptr_t)read32(display, 0x2c4u);
        audio_uart_lv_render_object_chain_453fce(layer, active_cover);
        if (read32(display, 0x2ccu) != 0u) {
            if (previous_cover == 0)
                previous_cover = (void *)(uintptr_t)read32(display, 0x2ccu);
            audio_uart_lv_render_object_chain_453fce(layer, previous_cover);
        }
    } else {
        if (read32(display, 0x2ccu) != 0u) {
            if (previous_cover == 0)
                previous_cover = (void *)(uintptr_t)read32(display, 0x2ccu);
            audio_uart_lv_render_object_chain_453fce(layer, previous_cover);
        }
        if (active_cover == 0)
            active_cover = (void *)(uintptr_t)read32(display, 0x2c4u);
        audio_uart_lv_render_object_chain_453fce(layer, active_cover);
    }
    audio_uart_lv_render_object_chain_453fce(
        layer, audio_uart_lv_display_top_layer_44fcbe(display));
    audio_uart_lv_render_object_chain_453fce(
        layer, audio_uart_lv_display_system_layer_44fcfc(display));
}
