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

static uint16_t rd16(const uint8_t *p) {
    uint16_t value;
    __builtin_memcpy(&value, p, 2u);
    return value;
}
static uint32_t rd32(const uint8_t *p) {
    uint32_t value;
    __builtin_memcpy(&value, p, 4u);
    return value;
}
static void wr16(uint8_t *p, uint16_t value) {
    __builtin_memcpy(p, &value, 2u);
}
static void wr32(uint8_t *p, uint32_t value) {
    __builtin_memcpy(p, &value, 4u);
}

void audio_uart_lv_state_property_refresh_44bfae(void *object, uint32_t selector,
                                                   uint16_t previous, uint32_t next,
                                                   const void *transition) {
    uint8_t *const obj = (uint8_t *)object;
    const uint8_t *const entry = (const uint8_t *)transition;
    const uint32_t property = entry[8u];
    wr16(obj + 0x2au, (uint16_t)(rd16(obj + 0x2au) | 8u));
    wr16(obj + 0x28u, previous);
    const uint32_t old_value = audio_uart_lv_style_property_44bdea(object, selector, property);
    wr16(obj + 0x28u, (uint16_t)next);
    uint32_t new_value = audio_uart_lv_style_property_44bdea(object, selector, property);
    wr16(obj + 0x2au, (uint16_t)(rd16(obj + 0x2au) & ~8u));
    if (old_value == new_value) return;

    wr16(obj + 0x28u, previous);
    uint32_t start_value = audio_uart_lv_style_property_44bdea(object, selector, property);
    wr16(obj + 0x28u, (uint16_t)next);
    uint8_t *const style_entry = (uint8_t *)audio_uart_lv_transition_style_44c72c(object, selector);
    audio_uart_page_style_value_482868((void *)(uintptr_t)rd32(style_entry), property, start_value);
    audio_uart_page_style_refresh_44bc8c(object, rd32(entry + 4u), property);

    if (property == 0x0cu && (start_value == 0x7fffu || new_value == 0x7fffu)) {
        const int32_t half_width = audio_uart_lv_obj_width_43fd9e(object) / 2;
        const int32_t half_height = audio_uart_lv_obj_height_43fdda(object) / 2;
        const int32_t radius = (half_width < half_height ? half_width : half_height) + 1;
        if (start_value == 0x7fffu) start_value = (uint32_t)radius;
        if (new_value == 0x7fffu) new_value = (uint32_t)radius;
    }

    uint8_t *const node = (uint8_t *)audio_uart_lv_list_prepend_482b12(
        audio_uart_display_lv_root + 0x18u);
    if (node == 0) {
        audio_uart_lvgl_log(3u, style_path, 0x1c9u, "lv_obj_update_style",
                            "out of memory");
        __builtin_trap();
    }
    wr32(node, (uint32_t)(uintptr_t)object);
    node[4u] = (uint8_t)property;
    wr32(node + 8u, selector);
    wr32(node + 0x0cu, start_value);
    wr32(node + 0x10u, new_value);

    uint8_t animation[0x60u];
    audio_uart_lv_anim_init_4503d6(animation);
    wr32(animation, (uint32_t)(uintptr_t)node);
    wr32(animation + 4u, (uint32_t)(uintptr_t)audio_uart_lv_transition_exec_44cae0);
    wr32(animation + 0x0cu, (uint32_t)(uintptr_t)audio_uart_lv_transition_ready_44cc8c);
    wr32(animation + 0x10u, (uint32_t)(uintptr_t)audio_uart_lv_transition_delete_44ccd8);
    audio_uart_lv_anim_values_4506ce(animation, 0, 0xff);
    wr32(animation + 0x30u, rd16(entry));
    wr32(animation + 0x34u, (uint32_t)(-(int32_t)rd16(entry + 2u)));
    wr32(animation + 0x20u, rd32(entry + 0x0cu));
    animation[0x5cu] &= (uint8_t)~0x10u;
    wr32(animation + 0x1cu, rd32(entry + 0x10u));
    audio_uart_lv_anim_start_450408(animation);
}
