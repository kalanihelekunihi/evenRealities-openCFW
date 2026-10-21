/* quicklist_data_add_item at native 0x58d51c..0x58d668. */
#include <stdint.h>

extern uint32_t audio_quicklist_convert_pb(const void *pb_item, void *internal_item);
extern uint32_t audio_quicklist_tick_now(void);

/* Stock item cache 0x20101a1c..0x20102c54. Startup/layout qualification open. */
uint8_t audio_quicklist_item_cache[0x1238];

uint32_t audio_quicklist_store_one(const void *pb_item) {
    if (pb_item == 0) return 2u;
    for (uint32_t i = 0; i < 0x1220u; ++i) audio_quicklist_item_cache[i] = 0;
    uint32_t result = (uint8_t)audio_quicklist_convert_pb(pb_item, audio_quicklist_item_cache);
    if (result != 0u) return result;
    audio_quicklist_item_cache[0xe4u] = 1u;
    audio_quicklist_item_cache[0x1220u] = 1u;
    audio_quicklist_item_cache[0x1221u] = 1u;
    audio_quicklist_item_cache[0x1222u] = 3u;
    uint32_t tick = audio_quicklist_tick_now();
    for (uint32_t i = 0; i < 4u; ++i) {
        audio_quicklist_item_cache[0x1228u + i] = (uint8_t)(tick >> (8u * i));
        audio_quicklist_item_cache[0x122cu + i] = 0;
    }
    return 0u;
}
