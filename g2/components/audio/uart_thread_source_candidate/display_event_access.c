/* Native LVGL object-event wrappers 0x451790/0x4517d6/0x45181c. */
#include <stdint.h>

extern uint32_t audio_uart_display_event_list_count_450158(void *);
extern void *audio_uart_display_event_list_at_450190(void *,uint32_t);
extern uint32_t audio_uart_display_event_list_remove_4501d2(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_event.c";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
static const char format[]="Asserted at expression: %s (%s)";
static const char count_function[]="lv_obj_get_event_count";
static const char at_function[]="lv_obj_get_event_dsc";
static const char remove_function[]="lv_obj_remove_event";

static void null_assert(const char *function,uint32_t line)
{
    audio_uart_lvgl_log(3u,source,line,function,format,expression,message);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
}
static void *event_list(void *object)
{
    uint32_t address=*(uint32_t *)((uint8_t *)object+8u);
    return (void *)(uintptr_t)(address+8u);
}

uint32_t audio_uart_display_event_count_451790(void *object)
{
    if (object==0) null_assert(count_function,0x6eu);
    if (*(uint32_t *)((uint8_t *)object+8u)==0u) return 0u;
    return audio_uart_display_event_list_count_450158(event_list(object));
}

void *audio_uart_display_event_at_4517d6(void *object,uint32_t index)
{
    if (object==0) null_assert(at_function,0x75u);
    if (*(uint32_t *)((uint8_t *)object+8u)==0u) return 0;
    return audio_uart_display_event_list_at_450190(event_list(object),index);
}

void audio_uart_display_event_remove_45181c(void *object,uint32_t index)
{
    if (object==0) null_assert(remove_function,0x7cu);
    if (*(uint32_t *)((uint8_t *)object+8u)==0u) return;
    audio_uart_display_event_list_remove_4501d2(event_list(object),index);
}
