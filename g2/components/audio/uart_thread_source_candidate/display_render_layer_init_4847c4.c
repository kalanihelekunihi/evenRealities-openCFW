/* Apollo Main LVGL layer base/init and display-list insertion, 0x4846de..0x484832. */
#include <stdint.h>

extern void *audio_uart_lv_refreshing_display_453604(void);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_draw.c";

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_render_layer_base_init_4846de(void *layer)
{
    if (layer == 0) {
        audio_uart_lvgl_log(3u, source, 0x17cu, "lv_layer_init",
                            "Asserted at expression: %s (%s)",
                            "layer != NULL", "NULL pointer");
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
    }
    uint8_t *const bytes = (uint8_t *)layer;
    for (uint32_t index = 0u; index < 0x58u; ++index) bytes[index] = 0u;
    bytes[0x38u] = 0xffu;
    write32(bytes, 0x39u, 0u);
}

void audio_uart_lv_render_layer_init_4847c4(void *layer, uint32_t parent,
                                              uint32_t format, const void *area)
{
    uint8_t *const bytes = (uint8_t *)layer;
    audio_uart_lv_render_layer_base_init_4846de(layer);
    uint8_t *const display = (uint8_t *)audio_uart_lv_refreshing_display_453604();
    write32(bytes, 0x48u, parent);
    (void)audio_uart_display_area_copy_439c04(bytes + 0x18u, area, 16u);
    (void)audio_uart_display_area_copy_439c04(bytes + 4u, area, 16u);
    (void)audio_uart_display_area_copy_439c04(bytes + 0x28u, area, 16u);
    bytes[0x14u] = (uint8_t)format;
    const uint32_t callback = read32(display, 0x2b0u);
    if (callback != 0u)
        ((void (*)(void *, void *))(uintptr_t)callback)(display, layer);
    const uint32_t head = read32(display, 0x2acu);
    if (head == 0u) {
        write32(display, 0x2acu, (uint32_t)(uintptr_t)layer);
    } else {
        uint8_t *link = (uint8_t *)(uintptr_t)head;
        while (read32(link, 0x4cu) != 0u)
            link = (uint8_t *)(uintptr_t)read32(link, 0x4cu);
        write32(link, 0x4cu, (uint32_t)(uintptr_t)layer);
    }
}
