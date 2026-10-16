/* Native LVGL lv_label_set_text 0x49942e..0x49954c. */
#include <stdint.h>
#include <stddef.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, ...);
extern void audio_uart_page_event_prepare_49aacc(void *);
extern uint32_t audio_uart_page_text_length_49abd4(const char *);
extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_page_text_content_init_49abe0(void *, const char *);
extern void audio_uart_page_layout_update_49a602(void *);

static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\label\\lv_label.c";
static const char function[] = "lv_label_set_text";
static const char format[] = "Asserted at expression: %s (%s)";
static const char null_expression[] = "obj != NULL";
static const char null_reason[] = "NULL pointer";
static const char allocation_expression[] = "label->text != NULL";
static const char allocation_reason[] = "Out of memory";

static void fatal(uint32_t line, const char *expression, const char *reason) {
    audio_uart_lvgl_log(3u, path, line, function, format,
                        expression, reason);
    for (;;) {
        *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
}

const char *audio_uart_page_49942e(uint8_t *page, const char *text) {
    if (page == NULL)
        fatal(0x87u, null_expression, null_reason);
    const char *const requested = text;
    if (text == NULL)
        text = *(const char **)(void *)(page + 0x2cu);
    audio_uart_page_event_prepare_49aacc(page);
    const uint32_t needed = audio_uart_page_text_length_49abd4(text);
    char *const old_text = *(char **)(void *)(page + 0x2cu);
    const uint8_t is_static = (page[0x5cu] >> 4) & 1u;
    if (old_text == text && is_static == 0u) {
        char *replacement = (char *)audio_uart_lv_realloc_44f76a(old_text,
                                                                   needed);
        *(char **)(void *)(page + 0x2cu) = replacement;
        if (replacement == NULL)
            fatal(0x93u, allocation_expression, allocation_reason);
    } else {
        if (old_text != NULL && is_static == 0u) {
            audio_uart_lv_heap_free(old_text);
            *(char **)(void *)(page + 0x2cu) = NULL;
        }
        char *replacement = (char *)audio_uart_lv_malloc(needed);
        *(char **)(void *)(page + 0x2cu) = replacement;
        if (replacement == NULL)
            fatal(0xa3u, allocation_expression, allocation_reason);
        audio_uart_page_text_content_init_49abe0(page, text);
        page[0x5cu] &= (uint8_t)~0x10u;
    }
    audio_uart_page_layout_update_49a602(page);
    return requested;
}
