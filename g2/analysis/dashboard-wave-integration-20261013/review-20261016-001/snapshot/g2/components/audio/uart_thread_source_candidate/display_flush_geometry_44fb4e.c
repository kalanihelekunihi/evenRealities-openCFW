/* Apollo Main display flush area copy, geometry and ready accessors.
 * Native spans 0x439c04, 0x44fa1a, 0x44fad2, 0x44fb10,
 * 0x44fb4e, 0x44fb9a, 0x44fc42. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];

static uint32_t get32(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}

void *audio_uart_display_area_copy_439c04(void *out, const void *in, uint32_t count) {
    uint8_t *dst = (uint8_t *)out;
    const uint8_t *src = (const uint8_t *)in;
    for (uint32_t index = 0; index < count; ++index) dst[index] = src[index];
    return out;
}

void *audio_uart_display_current_44fa1a(void) {
    return (void *)(uintptr_t)get32(audio_uart_display_lv_state, 0x14u);
}

int32_t audio_uart_display_area_width_44fad2(void *display) {
    uint8_t *item = (uint8_t *)(display != 0 ? display : audio_uart_display_current_44fa1a());
    if (item == 0) return 0;
    uint32_t mode = item[0x2fcu] & 7u;
    if (mode == 1u || mode == 3u) {
        int32_t candidate = (int32_t)get32(item, 0x0cu);
        return candidate < 1 ? (int32_t)get32(item, 4u) : candidate;
    }
    int32_t candidate = (int32_t)get32(item, 8u);
    return candidate < 1 ? (int32_t)get32(item, 0u) : candidate;
}

int32_t audio_uart_display_area_height_44fb10(void *display) {
    uint8_t *item = (uint8_t *)(display != 0 ? display : audio_uart_display_current_44fa1a());
    if (item == 0) return 0;
    uint32_t mode = item[0x2fcu] & 7u;
    if (mode == 1u || mode == 3u) {
        int32_t candidate = (int32_t)get32(item, 8u);
        return candidate < 1 ? (int32_t)get32(item, 0u) : candidate;
    }
    int32_t candidate = (int32_t)get32(item, 0x0cu);
    return candidate < 1 ? (int32_t)get32(item, 4u) : candidate;
}

int32_t audio_uart_display_area_x_44fb4e(void *display) {
    uint8_t *item = (uint8_t *)(display != 0 ? display : audio_uart_display_current_44fa1a());
    if (item == 0) return 0;
    uint32_t mode = item[0x2fcu] & 7u;
    if (mode == 1u) return (int32_t)get32(item, 0x14u);
    if (mode == 3u) return audio_uart_display_area_width_44fad2(item) -
                           (int32_t)get32(item, 0x14u);
    if (mode == 2u) return audio_uart_display_area_width_44fad2(item) -
                           (int32_t)get32(item, 0x10u);
    return (int32_t)get32(item, 0x10u);
}

int32_t audio_uart_display_area_y_44fb9a(void *display) {
    uint8_t *item = (uint8_t *)(display != 0 ? display : audio_uart_display_current_44fa1a());
    if (item == 0) return 0;
    uint32_t mode = item[0x2fcu] & 7u;
    if (mode == 1u) return (int32_t)get32(item, 0x10u);
    if (mode == 3u) return audio_uart_display_area_height_44fb10(item) -
                           (int32_t)get32(item, 0x10u);
    if (mode == 2u) return audio_uart_display_area_height_44fb10(item) -
                           (int32_t)get32(item, 0x14u);
    return (int32_t)get32(item, 0x14u);
}

uint32_t audio_uart_display_flush_ready_44fc42(const void *display) {
    return get32((const uint8_t *)display, 0x34u) != 0u;
}
