/* Apollo Main per-property animated state refresh, 0x44bfae..0x44c14d. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[]; /* native RAM 0x2006f548 */
extern uint32_t audio_uart_lv_style_property_44bdea(void *, uint32_t, uint32_t);
extern void *audio_uart_lv_transition_style_44c72c(void *, uint32_t);
extern void audio_uart_page_style_value_482868(void *, uint32_t, uint32_t);
extern void audio_uart_page_style_refresh_44bc8c(void *, uint32_t, uint32_t);
extern int32_t audio_uart_lv_obj_width_43fd9e(void *);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);
extern void *audio_uart_lv_list_prepend_482b12(void *);
extern void audio_uart_lv_anim_init_4503d6(void *);
extern void audio_uart_lv_anim_values_4506ce(void *, int32_t, int32_t);
extern void *audio_uart_lv_anim_start_450408(void *);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                               const char *, const char *, ...);

/* Callback bodies are separate native spans and remain explicit providers. */
extern void audio_uart_lv_transition_exec_44cae0(void *, uint32_t);
extern void audio_uart_lv_transition_ready_44cc8c(void *);
extern void audio_uart_lv_transition_delete_44ccd8(void *);

static const char style_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_style.c";


