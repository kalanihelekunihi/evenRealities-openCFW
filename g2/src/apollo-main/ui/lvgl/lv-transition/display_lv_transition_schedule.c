/* Native LVGL transition timer selection 0x4509da and resume/update
 * descendants 0x46453e/0x464696; product LV root is live RAM. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_first(void *); /* selected 0x482cd8 */
extern void audio_uart_lv_timer_pause(void *); /* selected 0x46450c */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
