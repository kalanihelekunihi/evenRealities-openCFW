/* Native LVGL lv_obj_remove_event_cb 0x451862, including the null assert. */
#include <stdint.h>

extern uint32_t audio_uart_display_event_count_451790(void *);
extern void *audio_uart_display_event_at_4517d6(void *,uint32_t);
extern void audio_uart_display_event_remove_45181c(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...); /* 0x44d25c */

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_event.c";
static const char function[]="lv_obj_remove_event_cb";
static const char expression[]="obj != NULL";
static const char message[]="NULL pointer";
static const char format[]="Asserted at expression: %s (%s)";

