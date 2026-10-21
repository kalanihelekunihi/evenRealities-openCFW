/* Apollo FreeType outline scale accessor, native 0x529bfe..0x529ca3. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
static const char outline_scale_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\libs\\freetype\\lv_freetype_outline.c";
static const char outline_scale_function[]="lv_freetype_outline_get_scale";
static const char outline_scale_assert_fmt[]="Asserted at expression: %s (%s)";
static const char outline_scale_invalid_fmt[]="Asserted at expression: %s Invalid font descriptor: 0x%x";
static const char outline_scale_null_pointer[]="NULL pointer";
static const char outline_scale_font_expr[]="font != NULL";
static const char outline_scale_descriptor_expr[]="dsc != NULL";
static const char outline_scale_magic_expr[]="LV_FREETYPE_FONT_DSC_HAS_MAGIC_NUM(dsc)";
static void outline_scale_fail(void) {
    for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
}
uint32_t audio_uart_ambiq_font_units_529bfe(const void *font) {
    if(font==0) {
        audio_uart_lvgl_log(3u,outline_scale_path,95u,outline_scale_function,outline_scale_assert_fmt,outline_scale_font_expr,outline_scale_null_pointer);
        outline_scale_fail();
    }
    const uint8_t *descriptor=(const uint8_t *)(uintptr_t)
        *(const uint32_t *)((const uint8_t *)font+0x18u);
    if(descriptor==0) {
        audio_uart_lvgl_log(3u,outline_scale_path,97u,outline_scale_function,outline_scale_assert_fmt,outline_scale_descriptor_expr,outline_scale_null_pointer);
        outline_scale_fail();
    }
    uint32_t magic=*(const uint32_t *)descriptor;
    if(magic!=0x5f5f4654u) {
        audio_uart_lvgl_log(3u,outline_scale_path,97u,outline_scale_function,outline_scale_invalid_fmt,outline_scale_magic_expr,magic);
        outline_scale_fail();
    }
    uint32_t numerator=*(const uint32_t *)(descriptor+0x28u)<<6;
    const uint8_t *face=(const uint8_t *)(uintptr_t)
        *(const uint32_t *)(descriptor+0x34u);
    uint32_t denominator=*(const uint32_t *)(face+8u);
    uint32_t quotient;
    __asm__ volatile("udiv %0, %1, %2" : "=r"(quotient)
                     : "r"(numerator),"r"(denominator));
    return quotient;
}
