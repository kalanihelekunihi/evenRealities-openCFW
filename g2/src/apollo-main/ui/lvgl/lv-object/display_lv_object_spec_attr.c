/* Native lv_obj_allocate_spec_attr 0x43e1fa. Full allocation and original
 * assertion paths; existing spec attributes are left intact. */
#include <stdint.h>
extern void *audio_uart_lv_heap_alloc(uint32_t); /* selected zeroed 0x44f730 */
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c";
