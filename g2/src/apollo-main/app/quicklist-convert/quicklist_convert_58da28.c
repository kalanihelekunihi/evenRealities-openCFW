/* quicklist_data_convert_from_pb, native 0x58da28..0x58daca. */
#include <stdint.h>

uint32_t audio_quicklist_convert_pb(const void *pb_item, void *internal_item) {
    if (pb_item == 0 || internal_item == 0) return 2u;
    const uint8_t *source = (const uint8_t *)pb_item;
    uint8_t *target = (uint8_t *)internal_item;
    for (uint32_t i = 0; i < 0xe8u; ++i) target[i] = 0;
    for (uint32_t i = 0; i < 12u; ++i) target[i] = source[i];
    for (uint32_t i = 16u; i < 24u; ++i) target[i] = source[i];
    target[24] = source[0xe5u];
    uint32_t count = (uint32_t)source[24] | ((uint32_t)source[25] << 8);
    if (count > 200u) count = 200u;
    target[0xe2u] = (uint8_t)count;
    target[0xe3u] = (uint8_t)(count >> 8);
    for (uint32_t i = 0; i < count; ++i) target[25u + i] = source[26u + i];
    target[25u + count] = 0;
    return 0u;
}
