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

static void null_assert(const char *function,uint32_t line)
{
    audio_uart_lvgl_log(3u,source,line,function,format,expression,message);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}

uint32_t audio_uart_display_event_list_count_450158(void *list)
{
    if (list==0) null_assert("lv_event_get_count",159u);
    return audio_uart_lv_event_count_450388(list);
}

void *audio_uart_display_event_list_at_450190(void *list,uint32_t index)
{
    if (list==0) null_assert("lv_event_get_dsc",165u);
    void *slot=audio_uart_lv_event_slot_450390(list,index);
    return slot ? *(void **)slot : 0;
}

uint32_t audio_uart_display_event_list_remove_4501d2(void *list,uint32_t index)
{
    if (list==0) null_assert("lv_event_remove",185u);
    uint8_t *descriptor=audio_uart_display_event_list_at_450190(list,index);
    if (descriptor==0) return 0u;
    ((uint8_t *)list)[20u]|=2u;
    *(uint32_t *)(void *)(descriptor+8u)|=0x10000u;
    audio_uart_lv_event_compact_450346(list);
    return 1u;
}
