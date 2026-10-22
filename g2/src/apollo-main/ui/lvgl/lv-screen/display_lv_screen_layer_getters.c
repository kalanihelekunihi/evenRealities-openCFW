/* Native display previous/top/system/bottom screen getters at
 * 0x44fc90/0x44fcbe/0x44fcfc/0x44fd38. */
#include <stdint.h>
extern void *audio_uart_display_default_get(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\display\\lv_display.c";
