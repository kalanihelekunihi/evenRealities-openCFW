/* Apollo Main generic pair search 0x52a284..0x52a2d5. */
#include <stdint.h>

typedef int32_t (*pair_compare_fn)(const void *, const void *);

void *audio_uart_lv_font_pair_search_52a284(const void *key,
                                            const void *base,
                                            uint32_t count,
                                            uint32_t size,
                                            pair_compare_fn compare) {
    const uint8_t *start = (const uint8_t *)base;
    while (count != 0u) {
        const uint8_t *middle = start + size * (count >> 1u);
        int32_t result = compare(key, middle);
        if (result <= 0) {
            if (result == 0) return (void *)middle;
            count >>= 1u;
        } else {
            count = (count >> 1u) - ((count & 1u) ^ 1u);
            start = middle + size;
        }
    }
    return 0;
}
