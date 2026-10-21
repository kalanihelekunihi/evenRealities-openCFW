/* Apollo Main LVGL refresh timer 0x45360c..0x453778. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_display_current_44fa1a(void);
extern void audio_uart_lv_timer_pause(void *);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);
extern void audio_uart_page_43f66c(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_lv_refresh_collect_45377a(void);
extern void audio_uart_lv_refresh_layout_45383c(void);
extern void audio_uart_lv_refresh_render_4539b6(void);
extern void *audio_uart_font_path_node_append(void *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";
static const char function[] = "lv_display_refr_timer";

static uint32_t word(const uint8_t *base, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(base + offset);
}

static void put(uint8_t *base, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(base + offset) = value;
}

static uint8_t *pointer(const uint8_t *base, uint32_t offset)
{
    return (uint8_t *)(uintptr_t)word(base, offset);
}

static void clear(uint8_t *base, uint32_t count)
{
    for (uint32_t i = 0; i < count; ++i) base[i] = 0u;
}

void audio_uart_display_tick_45360c(void *timer)
{
    uint8_t *display;
    if (timer != 0) {
        display = pointer((const uint8_t *)timer, 0x0cu);
        put(audio_uart_display_lv_root, 0x10u, (uint32_t)(uintptr_t)display);
        audio_uart_lv_timer_pause(timer);
    } else {
        display = (uint8_t *)audio_uart_display_current_44fa1a();
        put(audio_uart_display_lv_root, 0x10u, (uint32_t)(uintptr_t)display);
    }
    display = pointer(audio_uart_display_lv_root, 0x10u);
    if (display == 0) {
        audio_uart_lvgl_log(2u, source, 0x174u, function,
                            "No display registered");
        return;
    }
    uint8_t *const draw = pointer(display, 0x24u);
    if (draw == 0 || word(draw, 0x10u) == 0u || word(draw, 0x0cu) == 0u) {
        audio_uart_lvgl_log(2u, source, 0x17bu, function, "No draw buffer");
        return;
    }
    (void)audio_uart_lv_display_event_44fdbe(display, 0x39u, 0);
    audio_uart_page_43f66c(pointer(display, 0x2c4u));
    if (pointer(display, 0x2ccu) != 0)
        audio_uart_page_43f66c(pointer(display, 0x2ccu));
    audio_uart_page_43f66c(pointer(display, 0x2c8u));
    audio_uart_page_43f66c(pointer(display, 0x2c0u));
    audio_uart_page_43f66c(pointer(display, 0x2bcu));
    if (pointer(display, 0x2c4u) == 0) {
        put(display, 0x260u, 0u);
        audio_uart_lvgl_log(2u, source, 0x18fu, function,
                            "there is no active screen");
    } else {
        audio_uart_lv_refresh_collect_45377a();
        audio_uart_lv_refresh_layout_45383c();
        audio_uart_lv_refresh_render_4539b6();
        if (word(display, 0x260u) != 0u) {
            if (word(display, 0x20u) != 0u && display[0x39u] == 1u) {
                for (uint32_t i = 0; i < word(display, 0x260u); ++i) {
                    if (display[0x240u + i] == 0u) {
                        void *const node = audio_uart_font_path_node_append(display + 0x268u);
                        (void)audio_uart_display_area_copy_439c04(
                            node, display + 0x40u + i * 0x10u, 0x10u);
                    }
                }
            }
            clear(display + 0x40u, 0x200u);
            clear(display + 0x240u, 0x20u);
            put(display, 0x260u, 0u);
        }
    }
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3au, 0);
}
