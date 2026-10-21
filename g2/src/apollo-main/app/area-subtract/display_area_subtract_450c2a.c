/* Apollo Main LVGL redraw-area subtraction, stock 0x450c2a..0x450d8a. */
#include <stdint.h>

static uint32_t overlaps(const int32_t *a, const int32_t *b)
{
    return b[2] >= a[0] && a[2] >= b[0] &&
           b[3] >= a[1] && a[3] >= b[1];
}

static uint32_t contains(const int32_t *outer, const int32_t *inner)
{
    return inner[0] >= outer[0] && inner[1] >= outer[1] &&
           inner[2] <= outer[2] && inner[3] <= outer[3];
}

static int32_t maximum(int32_t a, int32_t b) { return a > b ? a : b; }
static int32_t minimum(int32_t a, int32_t b) { return a < b ? a : b; }

static void write_area(int32_t *out, uint32_t index, int32_t x1, int32_t y1,
                       int32_t x2, int32_t y2)
{
    int32_t *const slot = out + 4u * (uint32_t)(uint8_t)index;
    slot[0] = x1;
    slot[1] = y1;
    slot[2] = x2;
    slot[3] = y2;
}

int32_t audio_uart_lv_area_subtract_450c2a(int32_t *out, const int32_t *a,
                                             const int32_t *b)
{
    if (!overlaps(a, b)) return -1;
    if (contains(b, a)) return 0;

    uint32_t count = 0u;
    const int32_t top_height = (int32_t)((uint32_t)b[1] - (uint32_t)a[1]);
    if (top_height >= 1) {
        write_area(out, count++, a[0], a[1], a[2],
                   (int32_t)((uint32_t)b[1] - 1u));
    }

    const int32_t bottom_height = (int32_t)((uint32_t)a[3] - (uint32_t)b[3]);
    if (bottom_height >= 1 && b[3] < a[3]) {
        write_area(out, count++, a[0], (int32_t)((uint32_t)b[3] + 1u),
                   a[2], a[3]);
    }

    const int32_t middle_top = maximum(a[1], b[1]);
    const int32_t middle_bottom = minimum(a[3], b[3]);
    const int32_t middle_span =
        (int32_t)((uint32_t)middle_bottom - (uint32_t)middle_top);
    const int32_t left_width = (int32_t)((uint32_t)b[0] - (uint32_t)a[0]);
    if (left_width >= 1 && middle_span >= 1) {
        write_area(out, count++, a[0], middle_top,
                   (int32_t)((uint32_t)b[0] - 1u), middle_bottom);
    }

    const int32_t right_width = (int32_t)((uint32_t)a[2] - (uint32_t)b[2]);
    if (right_width >= 1) {
        write_area(out, count++, (int32_t)((uint32_t)b[2] + 1u),
                   middle_top, a[2], middle_bottom);
    }
    return (int32_t)(int8_t)count;
}
