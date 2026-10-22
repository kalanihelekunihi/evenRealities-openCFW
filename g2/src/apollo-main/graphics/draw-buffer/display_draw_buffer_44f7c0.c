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



/* Stock 0x44ffa0..0x44ffc8, the display refresh event callback. */
void audio_uart_display_event_44ffa0(void *event)
{
    if (audio_uart_page_event_code_450286(event) == 0x38u) {
        uint8_t *const display = *(uint8_t **)(void *)((uint8_t *)event + 4u);
        void *const timer = *(void **)(void *)(display + 0x304u);
        if (timer != 0) audio_uart_lv_timer_resume_46453e(timer);
    }
}

