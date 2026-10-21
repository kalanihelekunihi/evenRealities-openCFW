/* Cordio dmConnReset at Apollo Main 0x4b67ec. The CCB block must extend
 * through offset 0xc3; reset writes the two PHY defaults there. */
#include <stdint.h>

extern uint8_t audio_dm_connection_records[];
extern uint8_t audio_ble_dm_handler_state[];
extern void audio_ble_dm_conn_hci_handler_4b68a4(void *);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);

__attribute__((used))
const uint8_t audio_ble_dm_conn_spec_defaults_78a814[12] = {
    0x18u, 0x00u, 0x28u, 0x00u, 0x00u, 0x00u,
    0xd0u, 0x07u, 0x00u, 0x00u, 0x00u, 0x00u,
};

void audio_ble_dm_conn_reset_4b67ec(void)
{
    uint8_t event[9];
    event[4] = 0u;
    event[3] = 0u;
    event[8] = 0x16u;
    for (uint32_t i = 0u; i < 3u; ++i) {
        const uint8_t *row = audio_dm_connection_records + i * 0x30u;
        if (row[0x16u] != 0u) {
            event[0] = row[0x0cu];
            event[1] = row[0x0du];
            event[6] = event[0];
            event[7] = event[1];
            event[2] = 3u;
            audio_ble_dm_conn_hci_handler_4b68a4(event);
        }
    }
    for (uint32_t i = 0u; i < 2u; ++i) {
        uint8_t *base = audio_dm_connection_records;
        base[0xbcu + i * 2u] = 0x60u;
        base[0xbdu + i * 2u] = 0u;
        base[0xc0u + i * 2u] = 0x30u;
        base[0xc1u + i * 2u] = 0u;
        (void)audio_queue_copy_bytes(base + 0xa4u + i * 12u,
                                     audio_ble_dm_conn_spec_defaults_78a814, 12u);
    }
    audio_ble_dm_handler_state[0x14u] = 0u;
    audio_ble_dm_handler_state[0x0du] = 0u;
}
