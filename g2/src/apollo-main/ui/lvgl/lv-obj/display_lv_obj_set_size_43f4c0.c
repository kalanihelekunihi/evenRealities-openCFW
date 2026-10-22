/* LVGL lv_obj_set_size/width/height and size-style setters in Apollo Main. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, ...);
extern uint32_t audio_uart_page_style_get_44beaa(uint32_t, uint32_t,
                                                  uint32_t *, uint32_t);
extern void audio_uart_page_style_apply_44be4c(void *, uint8_t,
                                                uint32_t, uint32_t);

static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj_pos.c";
static const char asserted[] = "Asserted at expression: %s (%s)";
static const char expression[] = "obj != NULL";
static const char reason[] = "NULL pointer";






