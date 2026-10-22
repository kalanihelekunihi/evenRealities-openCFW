/* quicklist_data_add_mult_items, native 0x58d668..0x58d9c0. */
#include <stdint.h>

extern uint8_t audio_quicklist_item_cache[0x1238];
extern uint32_t audio_quicklist_convert_pb(const void *pb_item, void *internal_item);
extern uint32_t audio_quicklist_tick_now(void);

static uint16_t read16(const uint8_t *data) {
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static uint32_t read32(const uint8_t *data) {
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
           ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

/* Stock 0x58D668 (quicklist_data_add_mult_items) */
uint32_t audio_quicklist_store_many(const void *pb_items) {
    if (pb_items == 0) return 2u;
    const uint8_t *source = (const uint8_t *)pb_items;
    uint32_t count = read16(source + 2u);
    if (count > 20u) count = 20u;
    if (source[1] == 0u) {
        for (uint32_t i = 0; i < 0x1238u; ++i) audio_quicklist_item_cache[i] = 0;
    } else if (read16(source + 2u) != 0u) {
        if (read32(source + 12u) == 0u) {
            for (uint32_t i = 0; i < 0x1238u; ++i) audio_quicklist_item_cache[i] = 0;
        }
        uint32_t old_valid = audio_quicklist_item_cache[0x1221u];
        if (old_valid + count > 20u) return 4u;
        for (uint32_t i = 0; i < count; ++i) {
            const uint8_t *item = source + 8u + i * 0xe8u;
            if (read32(item + 4u) < 20u) {
                uint8_t *target = audio_quicklist_item_cache + (i + old_valid) * 0xe8u;
                if ((uint8_t)audio_quicklist_convert_pb(item, target) == 0u)
                    audio_quicklist_item_cache[0xe4u + i * 0xe8u] = 1u;
            }
        }
    }
    audio_quicklist_item_cache[0x1220u] = source[1];
    audio_quicklist_item_cache[0x1221u] = (uint8_t)(audio_quicklist_item_cache[0x1221u] + count);
    audio_quicklist_item_cache[0x1222u] = source[0];
    uint32_t tick = audio_quicklist_tick_now();
    for (uint32_t i = 0; i < 4u; ++i) {
        audio_quicklist_item_cache[0x1228u + i] = (uint8_t)(tick >> (i * 8u));
        audio_quicklist_item_cache[0x122cu + i] = 0;
    }
    return audio_quicklist_item_cache[0x1221u] < audio_quicklist_item_cache[0x1220u] ? 1u : 0u;
}
