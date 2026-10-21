/* Apollo Ambiq label glyph width/alignment gate at native 0x53faba. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);
static const char label_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_letter.c";
static const char label_function[]="is_width_aligned";
static const char label_error[]="Unsupported format!";
uint32_t audio_uart_ambiq_label_width_aligned_53faba(uint32_t width,
                                                       uint32_t format) {
    switch(format) {
    case 1u:return (width&7u)==0u;
    case 2u:return (width&3u)==0u;
    case 4u:return (width&1u)==0u;
    case 8u:return 1u;
    default:
        audio_uart_lvgl_log(3u,label_path,0x50u,label_function,label_error);
        return 0u;
    }
}
