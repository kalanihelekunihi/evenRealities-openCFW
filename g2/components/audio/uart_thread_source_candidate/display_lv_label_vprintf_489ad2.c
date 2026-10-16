/* Two-pass LVGL formatted-text allocator, stock 0x489ad2..0x489b3b. */
#include <stdint.h>
#include <stdarg.h>
extern uint32_t audio_uart_lv_vsnprintf_483fea(char *, uint32_t,
                                                const char *, va_list);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_text.c";
static const char function[] = "lv_text_set_text_vfmt";
static const char assertion[] = "Asserted at expression: %s (%s)";
static const char allocation_expression[] = "text != NULL";
static const char allocation_reason[] = "Out of memory";
char *audio_uart_lv_label_vprintf_489ad2(const char *format, va_list args) {
    uint32_t length = audio_uart_lv_vsnprintf_483fea((char *)0, 0u,
                                                       format, args);
    char *buffer = (char *)audio_uart_lv_malloc(length + 1u);
    if (buffer == 0) {
        audio_uart_lvgl_log(3u, path, 0x20fu, function, assertion,
                            allocation_expression, allocation_reason);
        for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
    }
    (void)audio_uart_lv_vsnprintf_483fea(buffer, length + 1u,
                                           format, args);
    return buffer;
}
