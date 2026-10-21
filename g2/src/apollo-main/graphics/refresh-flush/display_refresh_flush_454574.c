/* Apollo Main LVGL display flush 0x454574..0x454610 and callback bridge
 * 0x454648..0x454690. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_thread_sync_wait_4d46e8(void *);
extern void audio_uart_lv_refresh_tasks_484548(void);
extern void audio_uart_lv_display_pre_refresh_454692(void *);
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_display_flush_event_454648(void *display,
                                                const int32_t *area,
                                                void *buffer_data)
{
    uint8_t *const bytes = (uint8_t *)display;
    int32_t adjusted[4];
    const uint32_t x = read32(bytes, 0x10u);
    const uint32_t y = read32(bytes, 0x14u);
    adjusted[0] = (int32_t)(x + (uint32_t)area[0]);
    adjusted[1] = (int32_t)(y + (uint32_t)area[1]);
    adjusted[2] = (int32_t)(x + (uint32_t)area[2]);
    adjusted[3] = (int32_t)(y + (uint32_t)area[3]);
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3du, adjusted);
    const uint32_t callback = read32(bytes, 0x28u);
    ((void (*)(void *, const int32_t *, void *))(uintptr_t)callback)(
        display, adjusted, buffer_data);
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3eu, adjusted);
}

void audio_uart_lv_display_flush_454574(void *display)
{
    uint8_t *const bytes = (uint8_t *)display;
    uint8_t *const layer = (uint8_t *)(uintptr_t)read32(bytes, 0x2acu);
    while (read32(layer, 0x44u) != 0u) {
        (void)audio_uart_lv_thread_sync_wait_4d46e8(
            audio_uart_display_lv_root + 0x148u);
        audio_uart_lv_refresh_tasks_484548();
    }
    if (read32(bytes, 0x20u) != 0u) {
        void *const current = (void *)(uintptr_t)read32(
            audio_uart_display_lv_root, 0x10u);
        audio_uart_lv_display_pre_refresh_454692(current);
    }
    write32(bytes, 0x30u, 1u);
    const uint32_t flags = read32(bytes, 0x38u);
    const uint32_t last = (flags & 3u) == 3u ? 1u : 0u;
    write32(bytes, 0x34u, last);
    if (read32(bytes, 0x28u) != 0u) {
        uint8_t *const draw = (uint8_t *)(uintptr_t)read32(layer, 0u);
        void *const data = (void *)(uintptr_t)read32(draw, 0x10u);
        audio_uart_lv_display_flush_event_454648(
            display, (const int32_t *)(const void *)(bytes + 0x30cu), data);
    }
    if (read32(bytes, 0x20u) == 0u) return;
    if (bytes[0x39u] == 1u && last == 0u) return;
    write32(bytes, 0x24u,
            read32(bytes, 0x24u) == read32(bytes, 0x1cu) ?
                read32(bytes, 0x20u) : read32(bytes, 0x1cu));
}
