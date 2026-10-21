/* Cordio dmConnOpen at stock Main 0x536a28. */
#include <stdint.h>

extern uint8_t audio_ble_dm_conn_rows_200712a4[];
extern uint8_t audio_ble_dm_handler_state[];
extern uint32_t audio_ble_dm_scan_phy_index_4d2b3e(uint8_t);
extern uint32_t audio_ble_dm_ll_addr_type_4d2a84(uint8_t);
extern void audio_ble_hci_create_conn_52afcc(uint16_t, uint16_t, uint8_t,
                                              uint8_t, const uint8_t *, uint8_t,
                                              const uint8_t *);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t, uint8_t,
                                                uint32_t, uint32_t);

static uint16_t le16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}

void audio_ble_dm_conn_open_536a28(uint8_t init_phys, uint8_t addr_type,
                                    const uint8_t *peer_address)
{
    (void)init_phys; /* Stock selects the LE 1M scan PHY unconditionally. */
    uint8_t index = (uint8_t)audio_ble_dm_scan_phy_index_4d2b3e(1u);
    uint8_t own_addr_type = (uint8_t)audio_ble_dm_ll_addr_type_4d2a84(
        audio_ble_dm_handler_state[13]);
    const uint8_t *state = audio_ble_dm_conn_rows_200712a4;
    audio_ble_hci_create_conn_52afcc(le16(state + 0xbcu + 2u * index),
                                      le16(state + 0xc0u + 2u * index),
                                      audio_ble_dm_handler_state[20],
                                      addr_type, peer_address, own_addr_type,
                                      state + 0xa4u + 12u * index);
    audio_ble_dm_dev_pass_priv_4b2ea6(14u, 0u, 0u, 0u);
}
