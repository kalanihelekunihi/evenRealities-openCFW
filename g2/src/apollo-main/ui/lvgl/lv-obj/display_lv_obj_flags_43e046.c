/* Apollo LV object state bit wrappers, native 0x43e046..0x43e0c7. */
#include <stdint.h>

extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                               const char *, const char *, ...);
extern void audio_uart_lv_obj_state_apply_43ebec(void *, uint32_t);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c";
static const char format[] = "Asserted at expression: %s (%s)";
static const char expression[] = "obj != NULL";
static const char message[] = "NULL pointer";
static const char add_name[] = "lv_obj_add_state";
static const char remove_name[] = "lv_obj_remove_state";




