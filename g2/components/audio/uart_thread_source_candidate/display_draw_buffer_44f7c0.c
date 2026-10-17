/* Stock 0x44f7c0..0x44fa18. Pending callback/resource providers. */
#include <stdint.h>
#include <stddef.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_prepend_482b12(void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_array_init_482b00(uint8_t *, uint32_t);
extern uint32_t audio_uart_lv_tick(void);
extern void *audio_uart_lv_timer_create_464466(void (*)(void *), uint32_t, void *);
extern uint8_t audio_uart_page_instance_ready_48716c(void);
extern uint32_t audio_uart_page_488290(uint32_t);
extern void *audio_uart_page_487022(void *, uint32_t, uint32_t, uint32_t, const void *);
extern void *audio_uart_page_43de82(void *);
extern void audio_uart_lv_theme_refresh_44bc3a(void *);
extern void audio_uart_page_43dfa4(void *, uint32_t);
extern void audio_uart_page_44e368(void *, uint32_t);
extern void audio_uart_page_invalidate_440656(void *);
extern void audio_uart_lv_event_add_4500e4(void *, void (*)(void), uint32_t, void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_display_tick_45360c(void *);
extern const uint8_t audio_uart_display_page_style[]; /* stock 0x755610 */
extern uint32_t audio_uart_page_event_code_450286(const void *);
extern void audio_uart_lv_timer_resume_46453e(void *);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
static const char function[] = "lv_display_create";
static const char format[] = "Asserted at expression: %s (%s)";

static void fatal_null(uint32_t line, const char *expression)
{
    audio_uart_lvgl_log(3u, source, line, function, format,
                        expression, "NULL pointer");
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

static void zero_bytes(uint8_t *data, uint32_t count)
{
    for (uint32_t i = 0; i < count; ++i) data[i] = 0u;
}

/* Stock 0x44ffa0..0x44ffc8, the display refresh event callback. */
void audio_uart_display_event_44ffa0(void *event)
{
    if (audio_uart_page_event_code_450286(event) == 0x38u) {
        uint8_t *const display = *(uint8_t **)(void *)((uint8_t *)event + 4u);
        void *const timer = *(void **)(void *)(display + 0x304u);
        if (timer != 0) audio_uart_lv_timer_resume_46453e(timer);
    }
}

void *audio_uart_display_draw_buffer(uint32_t width, uint32_t height)
{
    uint8_t *const display = (uint8_t *)audio_uart_lv_list_prepend_482b12(
        audio_uart_display_lv_root + 4u);
    if (display == 0) fatal_null(0x41u, "disp != NULL");
    zero_bytes(display, 0x31cu);
    *(uint32_t *)(void *)(display + 0u) = width;
    *(uint32_t *)(void *)(display + 4u) = height;
    *(uint32_t *)(void *)(display + 8u) = UINT32_MAX;
    *(uint32_t *)(void *)(display + 12u) = UINT32_MAX;
    *(uint32_t *)(void *)(display + 24u) = 0x82u;
    *(uint32_t *)(void *)(display + 0x38u) = 1u << 17;
    display[0x3cu] = 6u;

    uint8_t *const layer = (uint8_t *)audio_uart_lv_malloc(0x58u);
    *(uint8_t **)(void *)(display + 0x2acu) = layer;
    if (layer == 0) fatal_null(0x58u, "disp->inv_areas != NULL");
    zero_bytes(layer, 0x58u);
    layer[0x38u] = 0xffu;
    /* The optional +0x2b0 callback is zero after the descriptor clear. */
    *(uint32_t *)(void *)(layer + 4u) = 0u;
    *(uint32_t *)(void *)(layer + 8u) = 0u;
    *(uint32_t *)(void *)(layer + 12u) = width - 1u;
    *(uint32_t *)(void *)(layer + 16u) = height - 1u;
    layer[0x14u] = display[0x3cu];
    *(uint32_t *)(void *)(display + 0x264u) = 1u;
    *(uint32_t *)(void *)(display + 0x308u) = audio_uart_lv_tick();
    audio_uart_lv_array_init_482b00(display + 0x268u, 0x10u);

    uint32_t *const active = (uint32_t *)(void *)(audio_uart_display_lv_root + 0x14u);
    const uint32_t previous = *active;
    *active = (uint32_t)(uintptr_t)display;
    void *const timer = audio_uart_lv_timer_create_464466(
        audio_uart_display_tick_45360c, 0x10u, display);
    *(void **)(void *)(display + 0x304u) = timer;
    if (timer == 0) fatal_null(0x6du, "disp->refr_timer != NULL");

    void *theme;
    if (audio_uart_page_instance_ready_48716c() == 0u) {
        const uint32_t background = audio_uart_page_488290(0u);
        const uint32_t foreground = audio_uart_page_488290(5u);
        theme = audio_uart_page_487022(display, foreground, background, 0u,
                                       audio_uart_display_page_style);
    } else {
        /* 0x487156 returns the cached page at lv state +0x178. */
        extern uint8_t audio_uart_display_lv_state[];
        theme = *(void **)(void *)(audio_uart_display_lv_state + 0x178u);
    }
    *(void **)(void *)(display + 0x300u) = theme;

    const uint32_t offsets[] = {0x2c8u, 0x2c4u, 0x2c0u, 0x2bcu};
    for (uint32_t i = 0u; i < 4u; ++i)
        *(void **)(void *)(display + offsets[i]) = audio_uart_page_43de82(0);
    const uint32_t styled[] = {0x2c8u, 0x2c0u, 0x2bcu};
    for (uint32_t i = 0u; i < 3u; ++i)
        audio_uart_lv_theme_refresh_44bc3a(
            *(void **)(void *)(display + styled[i]));
    audio_uart_page_43dfa4(*(void **)(void *)(display + 0x2c0u), 2u);
    audio_uart_page_43dfa4(*(void **)(void *)(display + 0x2bcu), 2u);
    for (uint32_t i = 0u; i < 3u; ++i)
        audio_uart_page_44e368(*(void **)(void *)(display + styled[i]), 0u);
    audio_uart_page_invalidate_440656(*(void **)(void *)(display + 0x2c4u));
    *active = previous != 0u ? previous : (uint32_t)(uintptr_t)display;
    audio_uart_lv_event_add_4500e4(display + 0x2e4u,
                                   (void (*)(void))audio_uart_display_event_44ffa0,
                                   0x38u, 0);
    *(uint32_t *)(void *)((uint8_t *)timer + 4u) =
        audio_uart_lv_tick() - *(uint32_t *)(void *)timer - 1u;
    return display;
}
