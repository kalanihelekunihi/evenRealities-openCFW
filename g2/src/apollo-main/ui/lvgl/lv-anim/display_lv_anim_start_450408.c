/* Apollo Main LVGL animation scheduler entry, native span 0x450408..0x4504ff. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void audio_uart_lv_anim_cancel_matching_450a74(void *);
extern void *audio_uart_lv_list_prepend_482b12(void *);
extern void *audio_uart_lv_grid_copy_454738(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_tick(void); /* native 0x473482 */
extern void audio_uart_lv_anim_normalize_450a3e(void *);
extern void audio_uart_lv_transition_schedule_4509da(void);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char scheduler_source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_anim.c";


