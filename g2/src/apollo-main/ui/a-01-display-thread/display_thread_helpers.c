/* UI display-thread small helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\framework\sync\display_thread.c
 * (same translation unit as drivers/display/display-thread-core/display_thread_handlers.c).
 * Native 0x442618..0x44264d, 0x442d64..0x442d85, 0x44347a..0x4434cb,
 * 0x44368e..0x443727 and the TIMER0 ISR 0x44466c..0x444683 (vector slot 83 =
 * IRQ 67 TIMER0_IRQn). Literal pools 0x442cd4..0x442cdb, 0x443738..0x44374f,
 * 0x443768..0x4437d7, 0x4441e4..0x4441eb, 0x4443a0.
 *
 * TIMER0 is set up by audio_uart_display_setup1 (0x4446b4, app/setup/display_setup.c)
 * as the 1 ms LVGL tick: the ISR acknowledges the timer and calls lv_tick_inc(1). */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* Page-stack entry (layer byte at +0xb), shared with display_thread_handlers.c. */
typedef struct {
    uint32_t id;      /* +0x0 application / page id */
    void *screen;     /* +0x4 LVGL screen object */
    uint8_t pad[3];
    uint8_t layer;    /* +0xb 0 foreground, 1 background/menu */
} g2_ui_page_t;

/* UI registry row (RAM 0x20066230, 16 bytes each). */
typedef struct {
    uint32_t id;             /* +0x0 application id */
    uint32_t reserved_4;     /* +0x4 */
    void *handler;           /* +0x8 nonzero when the app is registered */
    const g2_ui_page_t *page;/* +0xc static page descriptor */
} g2_ui_registry_row_t;
_Static_assert(sizeof(g2_ui_registry_row_t) == 16u, "stock registry row stride is 16 bytes");

#define DISPLAY_LAYER_UNKNOWN 2u

extern volatile uint32_t audio_uart_user_registry_count; /* RAM 0x200744d4, *DAT_00442cd4 */
extern uint8_t audio_uart_user_registry_rows[];          /* RAM 0x20066230, DAT_00442cd8 */
extern uint8_t audio_uart_display_state[2];              /* RAM 0x20074f2c, [0] startup app type */
extern uint32_t audio_uart_display_active;               /* RAM 0x200744d8 */
extern uint32_t audio_uart_display_mode;                 /* RAM 0x200744dc */
extern uint32_t audio_uart_display_background;           /* RAM 0x200744e0 */

extern uint8_t onboarding_active_flag_467f08(void);      /* 0x467f08, byte RAM 0x2007501c */
extern uint32_t onboarding_should_run(void);             /* 0x468034 */
extern uint32_t get_silent_mode_ui_showing(void);        /* 0x469ae2 */
extern const char *display_context_language_460106(void); /* 0x460106, active context word 0 or NULL */
extern int32_t audio_uart_font_path_compare(const char *, const char *); /* 0x46cacc strcmp */
extern uint32_t am_hal_timer_interrupt_status_get_471e9e(bool enabled_only, uint32_t *status); /* 0x471e9e */
extern uint32_t am_hal_timer_interrupt_clear_471ebc(uint32_t mask); /* 0x471ebc */
extern void lv_tick_inc_473474(uint32_t period_ms);      /* 0x473474 */

static const char lang_de[] = "de"; /* ROM 0x44373c */
static const char lang_en_gb[] = "en-GB"; /* ROM 0x78d3cc */
static const char lang_fr[] = "fr"; /* ROM 0x443740 */
static const char lang_it[] = "it"; /* ROM 0x443744 */
static const char lang_es[] = "es"; /* ROM 0x443748 */
static const char lang_ja[] = "ja"; /* ROM 0x44374c */
static const char lang_zh_cn[] = "zh-CN"; /* ROM 0x78d3d4 */
static const char lang_zh_hk[] = "zh-HK"; /* ROM 0x78d3dc */

/* Layer of a registered app id, 2 when the id is unknown or unregistered. */
uint8_t display_registry_layer_get_442618(uint32_t id)
{
    const g2_ui_registry_row_t *rows = (const g2_ui_registry_row_t *)(void *)audio_uart_user_registry_rows;

    for (int32_t i = 0; i < (int32_t)audio_uart_user_registry_count; i++) {
        if (rows[i].id == id && rows[i].handler != NULL)
            return rows[i].page->layer;
    }
    return DISPLAY_LAYER_UNKNOWN;
}

/* Input is diverted while onboarding or the silent-mode UI owns the screen. */
uint32_t display_input_gated_442d64(void)
{
    if (onboarding_active_flag_467f08() == 1u || onboarding_should_run() == 1u ||
        get_silent_mode_ui_showing() == 1u)
        return 1u;
    return 0u;
}

uint8_t *display_startup_state_get_44347a(void)
{
    return audio_uart_display_state;
}

uint32_t display_background_app_running_44349c(void)
{
    return audio_uart_display_background != 0u ? 1u : 0u;
}

uint32_t display_foreground_app_running_4434b4(void)
{
    if (audio_uart_display_active != 0u && audio_uart_display_mode == 1u)
        return 1u;
    return 0u;
}

/* Active UI language code -> font/language index (unknown or none = 0). */
uint32_t display_language_index_44368e(void)
{
    const char *code = display_context_language_460106();

    if (code == NULL)
        return 0u;
    if (audio_uart_font_path_compare(code, lang_de) == 0)
        return 1u;
    if (audio_uart_font_path_compare(code, lang_en_gb) == 0)
        return 0u;
    if (audio_uart_font_path_compare(code, lang_fr) == 0)
        return 2u;
    if (audio_uart_font_path_compare(code, lang_it) == 0)
        return 4u;
    if (audio_uart_font_path_compare(code, lang_es) == 0)
        return 3u;
    if (audio_uart_font_path_compare(code, lang_ja) == 0)
        return 5u;
    if (audio_uart_font_path_compare(code, lang_zh_cn) == 0)
        return 6u;
    if (audio_uart_font_path_compare(code, lang_zh_hk) == 0)
        return 7u;
    return 0u;
}

/* TIMER0 (IRQ 67) handler: acknowledge every pending timer interrupt
 * (INTSTAT 0x40008064 -> INTCLR 0x40008068) and advance the LVGL tick. */
void am_timer00_isr_44466c(void)
{
    uint32_t status;

    (void)am_hal_timer_interrupt_status_get_471e9e(false, &status);
    (void)am_hal_timer_interrupt_clear_471ebc(status);
    lv_tick_inc_473474(1u);
}
