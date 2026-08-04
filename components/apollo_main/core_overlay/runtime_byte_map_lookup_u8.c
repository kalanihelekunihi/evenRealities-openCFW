/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 byte-map lookup adapter at
 * 0x00482946...0x0048294F. The public adapter explicitly normalizes its
 * full-width key argument before forwarding all three arguments and the
 * lookup result to the source-owned byte-map search helper at 0x00482716.
 */

#ifndef OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP
struct open_cfw_runtime_byte_map;
unsigned int open_cfw_runtime_byte_map_lookup(
    const struct open_cfw_runtime_byte_map *map,
    unsigned int key,
    unsigned int *result
);
#define OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP(map, key, result) \
    open_cfw_runtime_byte_map_lookup((map), (key), (result))
#endif

__attribute__((used, noinline))
unsigned int open_cfw_runtime_byte_map_lookup_u8(
    const void *map,
    unsigned int key,
    unsigned int *result
)
{
    return OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP(
        (const struct open_cfw_runtime_byte_map *)map,
        (unsigned char)key,
        result
    );
}

#undef OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP
