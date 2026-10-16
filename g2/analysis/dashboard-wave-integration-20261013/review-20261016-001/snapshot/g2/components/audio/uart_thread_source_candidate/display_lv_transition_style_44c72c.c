/* Apollo Main transition style lookup, native 0x44c72c..0x44c827.
 * Object records are eight bytes; bit 25 marks the transition overlay. */
#include <stdint.h>

extern void *audio_uart_lv_realloc_44f76a(void *, uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                               const char *, const char *, ...);

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

void *audio_uart_lv_transition_style_44c72c(void *object, uint32_t selector) {
    uint8_t *const obj = (uint8_t *)object;
    uint16_t flags = rd16(obj + 0x2au);
    uint32_t count = (flags & 0x03ffu) >> 4u;
    uint8_t *entries = (uint8_t *)(uintptr_t)rd32(obj + 0x0cu);
    for (uint32_t i = 0; i < count; ++i) {
        const uint32_t tag = rd32(entries + i * 8u + 4u);
        if ((tag & 0x02000000u) != 0u &&
            (tag & 0x00ffffffu) == selector)
            return entries + i * 8u;
    }

    const uint32_t next = (count + 1u) & 0x3fu;
    flags = (uint16_t)((flags & 0xfc0fu) | (next << 4u));
    wr16(obj + 0x2au, flags);
    if (next == 0u) {
        audio_uart_lvgl_log(3u, style_path, 0x2e8u, "get_trans_style",
                            "Asserted at expression: %s", "obj->style_cnt != 0");
        __builtin_trap();
    }
    entries = (uint8_t *)audio_uart_lv_realloc_44f76a(entries, next * 8u);
    wr32(obj + 0x0cu, (uint32_t)(uintptr_t)entries);
    /* Native insertion shifts every existing record right by one slot. */
    for (uint32_t i = next - 1u; i != 0u; --i)
        __builtin_memcpy(entries + i * 8u, entries + (i - 1u) * 8u, 8u);
    audio_uart_buffer_zero(entries, 8u, 0u);
    uint8_t *const style = (uint8_t *)audio_uart_lv_malloc(12u);
    wr32(entries, (uint32_t)(uintptr_t)style);
    audio_uart_buffer_zero(style, 12u, 0u);
    wr32(entries + 4u, 0x02000000u | (selector & 0x00ffffffu));
    return entries;
}
