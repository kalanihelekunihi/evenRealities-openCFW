/* Apollo FreeType outline-font capability at native 0x529ca4. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
static const char outline_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c";
static const char outline_function[]="lv_freetype_is_outline_font";
static const char outline_assert[]="Asserted at expression: %s (%s)";
static const char outline_expr[]="font != NULL";
static const char outline_null[]="NULL pointer";
uint32_t audio_uart_ambiq_outline_available_529ca4(const void *font) {
    if(font==0) {
        audio_uart_lvgl_log(3u,outline_path,104u,outline_function,
                            outline_assert,outline_expr,outline_null);
        for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
    }
    const uint8_t *descriptor=(const uint8_t *)(uintptr_t)
        *(const uint32_t *)((const uint8_t *)font+0x18u);
    if(*(const uint32_t *)(const void *)descriptor!=0x5f5f4654u) return 0u;
    return descriptor[0x2du]==1u;
}
