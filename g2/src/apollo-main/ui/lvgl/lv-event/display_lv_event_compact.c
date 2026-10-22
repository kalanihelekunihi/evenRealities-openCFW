/* Native event-array compaction 0x4502e0/0x450346 and clear 0x488478.
 * The resize lower remains an explicit LV array allocator operation. */
#include <stdint.h>
extern uint32_t audio_uart_lv_event_count_450388(void *);
extern void *audio_uart_lv_event_slot_450390(void *,uint32_t);
extern uint32_t audio_uart_lv_event_descriptor_invalid_45037e(void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void *audio_uart_lv_realloc_44f76a(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
