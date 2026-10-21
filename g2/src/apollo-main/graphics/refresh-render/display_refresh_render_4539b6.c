/* Apollo Main LVGL refresh render loop, stock 0x4539b6..0x453b74. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_display_event_44fdbe(void *, uint32_t, void *);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_uart_lv_area_width_451598(const void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_lv_refresh_chunk_height_4544ae(void *, uint32_t,
                                                            uint32_t);
extern void audio_uart_lv_refresh_area_453bce(const void *, uint32_t);
extern void audio_uart_lv_display_flush_454574(void *);

static uint32_t read32(const uint8_t *base, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(base + offset);
}

static void write32(uint8_t *base, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(base + offset) = value;
}

void audio_uart_lv_refresh_render_4539b6(void)
{
    uint8_t *const display = (uint8_t *)(uintptr_t)read32(
        audio_uart_display_lv_root, 0x10u);
    const uint32_t count = read32(display, 0x260u);
    if (count == 0u) return;

    uint32_t last = 0u;
    for (int32_t index = (int32_t)(count - 1u); index >= 0; --index) {
        if (display[0x240u + (uint32_t)index] == 0u) {
            last = (uint32_t)index;
            break;
        }
    }
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3bu, 0);
    write32(display, 0x38u,
            (read32(display, 0x38u) & ~3u) | 0x02000000u);

    for (uint32_t index = 0u; (int32_t)index < (int32_t)count; ++index) {
        if (display[0x240u + index] != 0u) continue;
        if (index == last) write32(display, 0x38u, read32(display, 0x38u) | 1u);
        write32(display, 0x38u, read32(display, 0x38u) & ~2u);

        int32_t area[4];
        (void)audio_uart_display_area_copy_439c04(
            area, display + 0x40u + index * 16u, 16u);
        const uint8_t mode = display[0x39u];
        if (mode == 1u || mode == 2u) {
            write32(display, 0x38u, read32(display, 0x38u) | 2u);
            audio_uart_lv_refresh_area_453bce(area, 0u);
            audio_uart_lv_display_flush_454574(display);
        } else if (mode == 0u) {
            const uint32_t width = audio_uart_lv_area_width_451598(area);
            const uint32_t height = audio_uart_lv_area_height_4515a4(area);
            const uint32_t chunk = audio_uart_lv_refresh_chunk_height_4544ae(
                display, width, height);
            int32_t stripe[4] = {area[0], area[1], area[2], area[3]};
            uint32_t rendered = 0u;
            uint32_t y = (uint32_t)area[1];
            for (;;) {
                stripe[1] = (int32_t)y;
                uint32_t end = y + chunk - 1u;
                if ((int32_t)end > area[3]) end = (uint32_t)area[3];
                stripe[3] = (int32_t)end;
                if (stripe[3] == area[3])
                    write32(display, 0x38u, read32(display, 0x38u) | 2u);
                audio_uart_lv_refresh_area_453bce(stripe, rendered);
                rendered += audio_uart_lv_area_height_4515a4(stripe);
                audio_uart_lv_display_flush_454574(display);
                y += chunk;
                if ((int32_t)(y + chunk - 1u) <= area[3]) continue;
                if ((int32_t)end != area[3]) {
                    stripe[1] = (int32_t)y;
                    stripe[3] = area[3];
                    write32(display, 0x38u, read32(display, 0x38u) | 2u);
                    audio_uart_lv_refresh_area_453bce(stripe, rendered);
                    rendered += audio_uart_lv_area_height_4515a4(stripe);
                    audio_uart_lv_display_flush_454574(display);
                }
                break;
            }
        }
    }
    (void)audio_uart_lv_display_event_44fdbe(display, 0x3cu, 0);
    write32(display, 0x38u, read32(display, 0x38u) & ~0x02000000u);
}
