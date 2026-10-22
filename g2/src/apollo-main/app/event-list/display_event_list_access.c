/* LV event list accessors at 0x450158, 0x450190 and 0x4501d2.
 * Native null assertions, descriptor invalidation, and deferred compaction. */
#include <stdint.h>

extern uint32_t audio_uart_lv_event_count_450388(void *);
extern void *audio_uart_lv_event_slot_450390(void *,uint32_t);
extern void audio_uart_lv_event_compact_450346(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_event.c";
static const char expression[]="list != NULL";
static const char message[]="NULL pointer";
static const char format[]="Asserted at expression: %s (%s)";




