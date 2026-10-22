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




