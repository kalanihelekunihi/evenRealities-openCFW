/* LVGL font bitmap callback wrapper, native 0x4d5612..0x4d5663. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
static const char bitmap_path[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\font\\lv_font.c";
static const char bitmap_function[]="lv_font_get_glyph_bitmap";
static const char bitmap_assert[]="Asserted at expression: %s (%s)";
static const char bitmap_expression[]="font_p != NULL";
static const char bitmap_null[]="NULL pointer";

uint32_t audio_uart_ambiq_glyph_bitmap_4d5612(uint32_t glyph,
                                                uint32_t user_data) {
    const uint8_t *g=(const uint8_t *)(uintptr_t)glyph;
    uint32_t font=*(const uint32_t *)g;
    if(font==0u) {
        audio_uart_lvgl_log(3u,bitmap_path,0x36u,bitmap_function,
                            bitmap_assert,bitmap_expression,bitmap_null);
        for(;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu=0u;
    }
    const uint8_t *f=(const uint8_t *)(uintptr_t)font;
    uint32_t address=*(const uint32_t *)(f+0x18u);
    if(address>=0x80000001u) g2_norflash_lock_46f65e();
    uint32_t (*callback)(uint32_t,uint32_t)=
        (uint32_t (*)(uint32_t,uint32_t))(uintptr_t)*(const uint32_t *)(f+4u);
    uint32_t bitmap=callback(glyph,user_data);
    address=*(const uint32_t *)(f+0x18u);
    if(address>=0x80000001u) g2_norflash_unlock_46f674();
    return bitmap;
}
