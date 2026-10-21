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

static uint16_t get16(const uint8_t *p) {
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8u));
}

static void null_assert(const char *name, uint32_t line) {
    audio_uart_lvgl_log(3u, source, line, name, format, expression, message);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_lv_obj_flag_set_43e046(void *object, uint32_t flags) {
    if (object == 0) null_assert(add_name, 0x132u);
    uint16_t before = get16((const uint8_t *)object + 0x28u);
    uint16_t after = (uint16_t)(before | flags);
    if (after != before) audio_uart_lv_obj_state_apply_43ebec(object, after);
}

void audio_uart_lv_obj_flag_clear_43e086(void *object, uint32_t flags) {
    if (object == 0) null_assert(remove_name, 0x13cu);
    uint16_t before = get16((const uint8_t *)object + 0x28u);
    uint16_t after = (uint16_t)(before & ~flags);
    if (after != before) audio_uart_lv_obj_state_apply_43ebec(object, after);
}
