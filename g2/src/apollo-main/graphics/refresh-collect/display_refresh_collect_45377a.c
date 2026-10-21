/* Apollo Main LVGL refresh area coalescing, stock 0x45377a..0x453838. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern uint32_t audio_uart_lv_area_size_450b80(const void *);
extern void audio_uart_lv_area_copy_4530fc(int32_t *, const int32_t *);

static uint32_t read32(const uint8_t *base, uint32_t offset)
{
    return *(const uint32_t *)(const void *)(base + offset);
}

static int32_t maximum(int32_t a, int32_t b) { return a > b ? a : b; }
static int32_t minimum(int32_t a, int32_t b) { return a < b ? a : b; }

static uint32_t intersects(const int32_t *a, const int32_t *b)
{
    return b[2] >= a[0] && a[2] >= b[0] &&
           b[3] >= a[1] && a[3] >= b[1];
}

void audio_uart_lv_refresh_collect_45377a(void)
{
    uint8_t *const display = (uint8_t *)(uintptr_t)read32(
        audio_uart_display_lv_root, 0x10u);
    for (uint32_t i = 0; i < read32(display, 0x260u); ++i) {
        if (display[0x240u + i] != 0u) continue;
        for (uint32_t j = 0; j < read32(display, 0x260u); ++j) {
            if (display[0x240u + j] != 0u || i == j) continue;
            int32_t *const first = (int32_t *)(void *)(display + 0x40u + i * 16u);
            int32_t *const second = (int32_t *)(void *)(display + 0x40u + j * 16u);
            if (!intersects(first, second)) continue;
            int32_t union_area[4];
            union_area[0] = minimum(first[0], second[0]);
            union_area[1] = minimum(first[1], second[1]);
            union_area[2] = maximum(first[2], second[2]);
            union_area[3] = maximum(first[3], second[3]);
            const uint32_t union_size = audio_uart_lv_area_size_450b80(union_area);
            const uint32_t separate_size = audio_uart_lv_area_size_450b80(first) +
                                           audio_uart_lv_area_size_450b80(second);
            if (union_size < separate_size) {
                audio_uart_lv_area_copy_4530fc(first, union_area);
                display[0x240u + j] = 1u;
            }
        }
    }
}
