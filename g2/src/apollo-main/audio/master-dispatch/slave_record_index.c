#include <stdint.h>

extern uint8_t audio_ble_dm_conn_rows_200712a4[];

/* Native 0x4b6ed8: read dmCb.conn[id] byte at offset 0x13. The native
 * expression also addresses RAM before conn[0] when id is zero. */
uint32_t audio_ble_slave_record_kind_4b6ed8(uint32_t connection)
{
    connection = (uint8_t)connection;
    uintptr_t address = (uintptr_t)audio_ble_dm_conn_rows_200712a4
                      + (uint32_t)connection * 0x30u - 0x1du;
    return *(const volatile uint8_t *)address;
}

/* Native 0x4b6eea: return the pointer to dmCb.conn[id]. */
uint32_t audio_ble_slave_record_key_4b6eea(uint32_t connection)
{
    connection = (uint8_t)connection;
    uintptr_t address = (uintptr_t)audio_ble_dm_conn_rows_200712a4
                      + (uint32_t)connection * 0x30u - 0x30u;
    return (uint32_t)address;
}
