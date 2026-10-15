#include <stdint.h>

extern volatile uint8_t audio_ble_atts_ccc_runtime_20073b00[];
extern uint32_t audio_ble_atts_ccc_get_table_52bcea(uint8_t);

/* Native 0x52c664 reads 0x20073b14, offset 0x14 in ATT CCC runtime. */
uint8_t audio_ble_slave_ccc_count_52c664(void)
{
    return audio_ble_atts_ccc_runtime_20073b00[0x14u];
}

/* Native 0x52c60e writes one CCC value if the connection has a table. */
void audio_ble_slave_ccc_set_52c60e(uint8_t connection, uint8_t route,
                                     uint16_t value)
{
    uint32_t table = audio_ble_atts_ccc_get_table_52bcea(connection);
    if (table != 0u)
        *(volatile uint16_t *)(uintptr_t)(table + (uint32_t)route * 2u) = value;
}
