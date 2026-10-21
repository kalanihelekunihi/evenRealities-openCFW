/* Apollo Main LVGL refresh-area scheduling, stock 0x453bce..0x453e10. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern void audio_uart_lv_layer_reshape_draw_buf_453b78(void *, uint32_t);
extern uint32_t audio_uart_lv_display_width_44fa7e(void *);
extern uint32_t audio_uart_lv_display_height_44faa8(void *);
extern uint32_t audio_uart_lv_area_height_4515a4(const void *);
extern uint32_t audio_uart_lv_area_size_450b80(const void *);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern void *audio_uart_lv_malloc(uint32_t);
extern void audio_uart_lv_heap_free(void *);
extern void audio_uart_lv_area_set_450b5c(void *, uint32_t, uint32_t,
                                          uint32_t, uint32_t);
extern void audio_uart_lv_render_layer_init_4847c4(void *, uint32_t,
                                                    uint32_t, const void *);
extern void audio_uart_lv_render_layer_453e10(void *);
extern void audio_uart_lv_render_wait_484622(void);
extern void audio_uart_lv_refresh_tasks_484548(void);
extern void audio_uart_lvgl_log(uint32_t, const char *, uint32_t,
                                const char *, const char *, ...);

static const char source[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\core\\lv_refr.c";

static uint32_t read32(const uint8_t *bytes, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(bytes + offset);
}

static void write32(uint8_t *bytes, uint32_t offset, uint32_t value)
{
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_refresh_area_453bce(const void *area, uint32_t offset)
{
    uint8_t *const display = (uint8_t *)(uintptr_t)
        read32(audio_uart_display_lv_root, 0x10u);
    uint8_t *const layer = (uint8_t *)(uintptr_t)read32(display, 0x2acu);
    uint8_t *const draw = (uint8_t *)(uintptr_t)read32(display, 0x24u);
    write32(layer, 0u, (uint32_t)(uintptr_t)draw);
    (void)audio_uart_display_area_copy_439c04(layer + 0x18u, area, 16u);
    (void)audio_uart_display_area_copy_439c04(layer + 0x28u, area, 16u);
    write32(layer, 0x40u, offset);

    const uint8_t mode = display[0x39u];
    if (mode == 2u || mode == 0u) {
        (void)audio_uart_display_area_copy_439c04(layer + 4u, area, 16u);
        audio_uart_lv_layer_reshape_draw_buf_453b78(
            layer, mode == 2u ? read32(draw, 8u) & 0xffffu : 0u);
    } else if (mode == 1u) {
        write32(layer, 4u, 0u);
        write32(layer, 8u, 0u);
        write32(layer, 0x0cu, audio_uart_lv_display_width_44fa7e(display) - 1u);
        write32(layer, 0x10u, audio_uart_lv_display_height_44faa8(display) - 1u);
        audio_uart_lv_layer_reshape_draw_buf_453b78(layer,
                                                      read32(draw, 8u) & 0xffffu);
    }

    uint32_t count = 1u;
    uint32_t rows = audio_uart_lv_area_height_4515a4(area);
    const uint32_t format = layer[0x14u];
    if (format < 7u || format >= 11u) {
        const uint32_t divisor = (read32(display, 0x38u) >> 17u) & 0xffu;
        const uint32_t bytes_per_chunk = read32(draw, 0x0cu) / divisor;
        const uint32_t pixels = audio_uart_lv_area_size_450b80(area);
        const uint32_t bytes_per_pixel =
            (audio_uart_lv_color_bpp_440f44(format) + 7u) / 8u;
        count = (bytes_per_chunk + bytes_per_pixel * pixels - 1u) /
            bytes_per_chunk;
        rows = audio_uart_lv_area_height_4515a4(area) / count;
    }

    if (count == 1u) {
        audio_uart_lv_render_layer_453e10(layer);
    } else {
        uint8_t *const children = (uint8_t *)audio_uart_lv_malloc(count * 0x58u);
        if (children == 0) {
            audio_uart_lvgl_log(3u, source, 0x2cau, "refr_area",
                                "Asserted at expression: %s (%s)",
                                "tile_layers != NULL", "Out of memory");
            for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
        }
        const uint32_t *const input = (const uint32_t *)area;
        for (uint32_t index = 0u; index < count; ++index) {
            uint32_t tile[4];
            audio_uart_lv_area_set_450b5c(tile, input[0],
                                            input[1] + rows * index,
                                            input[2],
                                            input[1] + rows * (index + 1u) - 1u);
            if (index == count - 1u) tile[3] = input[3];
            uint8_t *const child = children + index * 0x58u;
            audio_uart_lv_render_layer_init_4847c4(child, 0u, format, tile);
            (void)audio_uart_display_area_copy_439c04(child + 4u,
                                                        layer + 4u, 16u);
            write32(child, 0u, read32(layer, 0u));
            audio_uart_lv_render_layer_453e10(child);
        }
        for (uint32_t index = 0u; index < count; ++index) {
            uint8_t *const child = children + index * 0x58u;
            while (read32(child, 0x44u) != 0u) {
                audio_uart_lv_render_wait_484622();
                audio_uart_lv_refresh_tasks_484548();
            }
            uint8_t *link = layer;
            for (;;) {
                const uint32_t next = read32(link, 0x4cu);
                if (next == 0u) break;
                if (next == (uint32_t)(uintptr_t)child) {
                    write32(link, 0x4cu, read32(child, 0x4cu));
                    break;
                }
                link = (uint8_t *)(uintptr_t)next;
            }
            const uint32_t callback = read32(display, 0x2b4u);
            if (callback != 0u)
                ((void (*)(void *, void *))(uintptr_t)callback)(display, child);
        }
        audio_uart_lv_heap_free(children);
    }
    (void)audio_uart_display_area_copy_439c04(display + 0x30cu, area, 16u);
}
