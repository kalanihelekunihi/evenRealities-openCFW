/* Dual-chip Cordio HCI lower providers from stock Main 0x530d3c and 0x52b0a4. */
#include <stdint.h>

extern uint8_t audio_ble_hci_controller_state_20071478[];
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint8_t);
extern void audio_ble_hci_cmd_send(void *);

uint64_t audio_ble_hci_get_le_supported_features_530d3c(void)
{
    const uint8_t *p = audio_ble_hci_controller_state_20071478 + 0x88u;
    uint64_t features = 0u;
    for (uint32_t i = 0u; i < 8u; ++i)
        features |= (uint64_t)p[i] << (i * 8u);
    return features & ~(uint64_t)2u;
}

void audio_ble_hci_create_conn_cancel_52b0a4(void)
{
    void *command = audio_ble_hci_cmd_alloc_52ae38(0x200eu, 0u);
    if (command != 0)
        audio_ble_hci_cmd_send(command);
}
