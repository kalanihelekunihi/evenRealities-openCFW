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
