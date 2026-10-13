#include <stdint.h>

typedef int32_t (*ft_sort_compare)(const void *, const void *);

/* Complete native bodies 0x5677a8..0x56798c, excluding the sort core. */
void audio_uart_ft_sort_swap_5677a8(uint8_t *a, uint8_t *b, uint32_t width)
{
    if (width < 64u) {
        while (width-- != 0u) {
            uint8_t value = *a;
            *a++ = *b;
            *b++ = value;
        }
        return;
    }
    do {
        uint32_t length = width > 128u ? 128u : width;
        uint8_t scratch[128];
        for (uint32_t i = 0; i < length; ++i) scratch[i] = a[i];
        for (uint32_t i = 0; i < length; ++i) a[i] = b[i];
        for (uint32_t i = 0; i < length; ++i) b[i] = scratch[i];
        a += length;
        b += length;
        width -= length;
    } while (width != 0u);
}

void audio_uart_ft_sort_rotate_5677fe(uint8_t *a, uint8_t *b, uint8_t *c, uint32_t width)
{
    if (width < 64u) {
        while (width-- != 0u) {
            uint8_t value = *a;
            *a++ = *c;
            *c++ = *b;
            *b++ = value;
        }
        return;
    }
    do {
        uint32_t length = width > 128u ? 128u : width;
        uint8_t scratch[128];
        for (uint32_t i = 0; i < length; ++i) scratch[i] = a[i];
        for (uint32_t i = 0; i < length; ++i) a[i] = c[i];
        for (uint32_t i = 0; i < length; ++i) c[i] = b[i];
        for (uint32_t i = 0; i < length; ++i) b[i] = scratch[i];
        a += length;
        b += length;
        c += length;
        width -= length;
    } while (width != 0u);
}

void audio_uart_ft_sort_insert_56786c(uint8_t *a, uint8_t *b, uint32_t width)
{
    uint32_t remaining = width;
    while (remaining != 0u) {
        uint32_t length = remaining > 128u ? 128u : remaining;
        uint8_t scratch[128];
        for (uint32_t i = 0; i < length; ++i) scratch[i] = b[width - length + i];
        uint32_t move = (uint32_t)(b - a) + width - length;
        for (uint32_t i = move; i != 0u; --i) a[length + i - 1u] = a[i - 1u];
        for (uint32_t i = 0; i < length; ++i) a[i] = scratch[i];
        remaining -= length;
    }
}

void audio_uart_ft_sort_median_5678b6(uint8_t *a, uint8_t *b, uint8_t *c,
                                       uint32_t width, ft_sort_compare compare)
{
    if (compare(b, a) < 0) audio_uart_ft_sort_swap_5677a8(a, b, width);
    if (compare(c, b) < 0) audio_uart_ft_sort_swap_5677a8(b, c, width);
    if (compare(b, a) < 0) audio_uart_ft_sort_swap_5677a8(a, b, width);
}

uint32_t audio_uart_ft_sort_heap_sift_567906(uint8_t *base, uint32_t start,
                                             uint32_t count, uint32_t width,
                                             ft_sort_compare compare)
{
    uint32_t index = start;
    uint8_t *cursor = base + width * index;
    for (;;) {
        uint32_t child = index * 2u + 2u;
        if (child > count) break;
        uint8_t *candidate = base + width * child;
        if (child == count || compare(candidate, candidate - width) < 0) {
            --child;
            candidate -= width;
        }
        audio_uart_ft_sort_swap_5677a8(cursor, candidate, width);
        index = child;
        cursor = candidate;
    }
    while (index > start) {
        index = (index - 1u) >> 1;
        uint8_t *parent = base + width * index;
        if (compare(cursor, parent) <= 0) break;
        audio_uart_ft_sort_swap_5677a8(parent, cursor, width);
        cursor = parent;
    }
    return start;
}
