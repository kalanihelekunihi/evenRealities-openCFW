#include <stdint.h>

extern uint8_t audio_ble_dm_conn_state_table_20067a30[];

/* Native 0x47a630. The native continuation checks up to nine following
 * rows from the supplied pointer; it does not clamp to the table end. */
uint32_t audio_ble_pair_record_next_47a630(uint32_t current)
{
    uintptr_t row = current == 0u
                  ? (uintptr_t)audio_ble_dm_conn_state_table_20067a30
                  : (uintptr_t)current + 200u;
    uint32_t remaining = current == 0u ? 10u : 9u;
    while (remaining-- != 0u) {
        if (*(const volatile uint8_t *)(row + 0x2fu) != 0u)
            return (uint32_t)row;
        row += 200u;
    }
    return 0u;
}
