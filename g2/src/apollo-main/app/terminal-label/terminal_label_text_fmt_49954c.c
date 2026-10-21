/* Stock LVGL lv_label_set_text_fmt, Apollo Main 0x49954c..0x499607. */
#include <stdint.h>
#include <stdarg.h>
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_page_invalidate_440656(void *);
extern void audio_uart_lv_heap_free(void *);
extern char *audio_uart_lv_label_vprintf_489ad2(const char *, va_list);
extern void audio_uart_page_layout_update_49a602(void *);
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\label\\lv_label.c";
static const char function[] = "lv_label_set_text_fmt";
static const char expression[] = "Asserted at expression: %s (%s)";
static const char null_pointer[] = "NULL pointer";
static const char object_not_null[] = "obj != NULL";
static const char format_not_null[] = "fmt != NULL";
static void fatal(uint32_t line, const char *which) {
    audio_uart_lvgl_log(3u, path, line, function, expression,
                        which, null_pointer);
    for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
}
uint32_t audio_lv_label_set_text_fmt_49954c(uint8_t *label,
                                               const char *format, ...) {
    if (label == 0) fatal(0xb1u, object_not_null);
    if (format == 0) fatal(0xb2u, format_not_null);
    audio_uart_page_invalidate_440656(label);
    uint32_t old = *(uint32_t *)(void *)(label + 0x2cu);
    if (old != 0u && ((label[0x5cu] >> 4u) & 1u) == 0u) {
        audio_uart_lv_heap_free((void *)(uintptr_t)old);
        *(uint32_t *)(void *)(label + 0x2cu) = 0u;
    }
    va_list args;
    va_start(args, format);
    char *new_text = audio_uart_lv_label_vprintf_489ad2(format, args);
    va_end(args);
    *(uint32_t *)(void *)(label + 0x2cu) = (uint32_t)(uintptr_t)new_text;
    label[0x5cu] &= (uint8_t)~0x10u;
    audio_uart_page_layout_update_49a602(label);
    return (uint32_t)(uintptr_t)label;
}
