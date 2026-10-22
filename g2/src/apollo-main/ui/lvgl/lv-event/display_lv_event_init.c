/* Native LV transition/event initialization 0x4503a4. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[]; /* selected RAM0x2006f548 */
extern void audio_uart_lv_array_init_482b00(uint8_t *,uint32_t);
extern void audio_uart_lv_transition_timer_callback_450758(void *);
extern void *audio_uart_lv_timer_create_464466(void (*)(void *),uint32_t,void *);
extern void audio_uart_lv_transition_schedule_4509da(void); /* selected */


/* Native lv_timer_create464466..4644ee; actual helpers already selected.
 * Non-executable assertion literals authenticated from locked payload. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_prepend_482b12(uint32_t *);
extern uint32_t audio_uart_lv_tick(void);
extern void audio_uart_lv_timer_update_464696(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char timer_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_timer.c";
static const char timer_function[]="lv_timer_create";
static const char timer_format[]="Asserted at expression: %s (%s)";
static const char timer_expression[]="new_timer != NULL";
static const char timer_reason[]="Out of memory";
