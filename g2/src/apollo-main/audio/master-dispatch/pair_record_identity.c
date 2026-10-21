#include <stdint.h>

extern uint8_t audio_ble_dm_conn_state_table_20067a30[];
extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);

/* Native 0x47add4: locate the first occupied AppDb row matching an
 * identity address type and its eight-byte address. */
uint32_t audio_ble_pair_record_find_47add4(uint32_t type, const void *address)
{
    uint16_t sought = (uint16_t)type;
    for (uint32_t index = 0u; index < 10u; ++index) {
        uint8_t *row = audio_ble_dm_conn_state_table_20067a30 + index * 200u;
        uint16_t row_type = (uint16_t)row[0x4cu]
                          | ((uint16_t)row[0x4du] << 8u);
        if (row[0x2fu] != 0u && row_type == sought &&
            g2_lfs_memcmp(row + 0x44u, address, 8u) == 0) {
            uint32_t stamp = ++audio_ble_pair_timestamp_counter_20074344;
            *(uint32_t *)(void *)(row + 0xc4u) = stamp;
            return (uint32_t)(uintptr_t)row;
        }
    }
    return 0u;
}
