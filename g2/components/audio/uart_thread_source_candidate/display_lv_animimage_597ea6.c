/* LVGL animimage setters/start, Apollo Main 0x597ea6..0x597f81. */
#include <stdint.h>
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);
extern void audio_uart_lv_anim_values_4506ce(void *, uint32_t);
extern void audio_uart_lv_anim_start_450408(void *);
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\widgets\\animimage\\lv_animimage.c";
static const char expression[] = "Asserted at expression: %s (%s)";
static const char object_not_null[] = "obj != NULL";
static const char null_pointer[] = "NULL pointer";
static const char set_src[] = "lv_animimg_set_src";
static const char start[] = "lv_animimg_start";
static const char set_duration[] = "lv_animimg_set_duration";
static const char set_repeat_count[] = "lv_animimg_set_repeat_count";
static void fatal(uint32_t line, const char *function) {
    audio_uart_lvgl_log(3u, path, line, function, expression,
                        object_not_null, null_pointer);
    for (;;) *(volatile uint32_t *)(uintptr_t)0xffffffffu = 0u;
}
void audio_lv_label_style_call_597ea6(uint8_t *object, const void *sources,
                                       uint32_t count) {
    if (object == 0) fatal(0x6cu, set_src);
    *(uint32_t *)(void *)(object + 0xbcu) = (uint32_t)(uintptr_t)sources;
    object[0xc0u] = (uint8_t)count;
    audio_uart_lv_anim_values_4506ce(object + 0x5cu, 0u);
}
void audio_lv_label_style_call_597ee0(uint8_t *object) {
    if (object == 0) fatal(0x75u, start);
    audio_uart_lv_anim_start_450408(object + 0x5cu);
}
void audio_lv_label_style_call_597f10(uint8_t *object, uint32_t duration) {
    if (object == 0) fatal(0x80u, set_duration);
    *(uint32_t *)(void *)(object + 0x8cu) = duration;
    *(uint32_t *)(void *)(object + 0x94u) = duration;
}
void audio_lv_label_style_call_597f52(uint8_t *object, uint32_t repeat_count) {
    if (object == 0) fatal(0x88u, set_repeat_count);
    *(uint32_t *)(void *)(object + 0xa0u) = repeat_count;
}
