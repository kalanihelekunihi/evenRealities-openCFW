#include <stdint.h>

extern uint8_t audio_ble_dm_privacy_state[];
extern uint8_t audio_ble_dm_conn_state_table_20067a30[];
extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);

/* Native 0x4d2aa8. Privacy state byte 0x16 is RAM 0x20073b8e. */
uint32_t audio_ble_pair_address_type_4d2aa8(uint32_t type)
{
    type = (uint8_t)type;
    if (audio_ble_dm_privacy_state[0x16u] != 0u) {
        if (type == 2u) return 0u;
        if (type == 3u) return 1u;
    }
    return type;
}

/* Native 0x4d294a. */
uint32_t audio_ble_pair_address_equal_4d294a(const void *row, const void *address)
{
    return g2_lfs_memcmp(row, address, 6u) == 0 ? 1u : 0u;
}

/* Native 0x47ad74: ten 200-byte AppDb rows, first matching row wins. */
uint32_t audio_ble_pair_record_find_47ad74(uint32_t type, const void *address)
{
    uint8_t match_type = (uint8_t)audio_ble_pair_address_type_4d2aa8((uint8_t)type);
    for (uint32_t index = 0u; index < 10u; ++index) {
        uint8_t *row = audio_ble_dm_conn_state_table_20067a30 + index * 200u;
        if (row[0x2fu] != 0u && row[6] == match_type &&
            audio_ble_pair_address_equal_4d294a(row, address) != 0u) {
            uint32_t stamp = ++audio_ble_pair_timestamp_counter_20074344;
            *(uint32_t *)(void *)(row + 0xc4u) = stamp;
            return (uint32_t)(uintptr_t)row;
        }
    }
    return 0u;
}
