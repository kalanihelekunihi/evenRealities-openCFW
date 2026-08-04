/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Bounded source replacement for the G2 2.2.6.10 byte-keyed map lookup at
 * 0x00482716. Its two table layouts, wrapper ABI, sole direct dependency,
 * adjacent boundaries, and complete branch/pointer topology are pinned by
 * the standalone host test.
 */

typedef unsigned int open_cfw_runtime_byte_map_word;
typedef unsigned int open_cfw_runtime_byte_map_pointer;

struct open_cfw_runtime_byte_map {
    open_cfw_runtime_byte_map_pointer table;
    open_cfw_runtime_byte_map_word reserved_04;
    unsigned char count_or_sentinel;
    unsigned char reserved_09;
    unsigned char reserved_0a;
    unsigned char reserved_0b;
};

_Static_assert(
    sizeof(open_cfw_runtime_byte_map_word) == 4U,
    "byte-map word width changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_runtime_byte_map, table) == 0x00U,
    "byte-map table offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_byte_map,
        count_or_sentinel
    ) == 0x08U,
    "byte-map count offset changed"
);

#ifndef OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES
#define OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES(value) \
    ((const unsigned char *)(__UINTPTR_TYPE__)(value))
#endif

#ifndef OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD
#define OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD(source) \
    (*(const open_cfw_runtime_byte_map_word *)(const void *)(source))
#endif

__attribute__((used, noinline))
open_cfw_runtime_byte_map_word open_cfw_runtime_byte_map_lookup(
    const struct open_cfw_runtime_byte_map *map,
    open_cfw_runtime_byte_map_word key,
    open_cfw_runtime_byte_map_word *result
)
{
    const unsigned char *table;
    open_cfw_runtime_byte_map_word index;
    unsigned int normalized_key = (unsigned char)key;

    if (map->count_or_sentinel == 0xffU) {
        table = OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES(map->table);
#pragma clang loop unroll(disable)
        for (index = 0U; table[index * 8U] != 0U; index += 1U) {
            if (table[index * 8U] == normalized_key) {
                *result = OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD(
                    table + index * 8U + 4U
                );
                return 1U;
            }
        }
        return 0U;
    }

    if (map->count_or_sentinel == 0U) {
        return 0U;
    }

    table = OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES(map->table);
#pragma clang loop unroll(disable)
    for (index = 0U; index < map->count_or_sentinel; index += 1U) {
        if (
            table[
                (open_cfw_runtime_byte_map_word)map->count_or_sentinel * 4U
                + index
            ] == normalized_key
        ) {
            *result = OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD(
                table + index * 4U
            );
            return 1U;
        }
    }

    return 0U;
}

#undef OPEN_CFW_RUNTIME_BYTE_MAP_POINTER_TO_BYTES
#undef OPEN_CFW_RUNTIME_BYTE_MAP_LOAD_WORD
