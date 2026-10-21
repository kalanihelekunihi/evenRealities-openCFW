#include <stdint.h>

extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern uint8_t audio_ble_slave_open_flag_20074f93;
extern uint8_t audio_ble_slave_ccc_count_52c664(void);
extern void audio_ble_slave_ccc_set_52c60e(uint8_t, uint8_t, uint16_t);

/* Native 0x4b3aec. CCC values start at offset 0x6c in the linked record. */
void audio_ble_slave_finish_4b3aec(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    volatile uint8_t *row = (volatile uint8_t *)record;
    if (row[6] != 0u && bytes[4] != 0u) {
        row[5] = 1u;
        row[6] = 0u;
    }
    if (audio_ble_slave_open_flag_20074f93 == 0u)
        return;
    uint8_t connection = bytes[0];
    const uint8_t *slot = audio_ble_discovery_connection_records_200717b0 +
                          ((uint32_t)connection - 1u) * 0x30u;
    uint32_t handle = *(const uint32_t *)(const void *)slot;
    const uint16_t *ccc = (const uint16_t *)(uintptr_t)(handle + 0x6cu);
    for (uint32_t i = 0u; (uint8_t)i < audio_ble_slave_ccc_count_52c664(); ++i) {
        uint16_t value = ccc[i];
        if (value != 0u)
            audio_ble_slave_ccc_set_52c60e(connection, (uint8_t)i, value);
    }
}
