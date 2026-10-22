/* Native LV filesystem driver construct/register 0x4c7064/0x4c706e. */
#include <stdint.h>
#include <stddef.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *memset(void *,int,size_t);
extern void *audio_uart_lv_list_prepend_482b12(uint32_t *); /* selected */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_fs.c";
static const char function[]="lv_fs_drv_register";
static const char format[]="Asserted at expression: %s (%s)";
static const char expression[]="new_drv != NULL";
static const char message[]="Out of memory";


