/* Cordio HCI LE create-connection command at stock Main 0x52afcc. */
#include <stdint.h>

extern uint8_t *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint8_t);
extern void audio_ble_copy_address6_4d293c(void *, const void *);
extern void audio_ble_hci_cmd_send(void *);

void audio_ble_hci_create_conn_52afcc(uint16_t scan_interval,
                                      uint16_t scan_window,
                                      uint8_t filter_policy,
                                      uint8_t peer_addr_type,
                                      const uint8_t *peer_address,
                                      uint8_t own_addr_type,
                                      const uint8_t *connection_spec)
{
    uint8_t *command = audio_ble_hci_cmd_alloc_52ae38(0x200du, 25u);
    if (command == 0)
        return;
    command[3] = (uint8_t)scan_interval;
    command[4] = (uint8_t)(scan_interval >> 8);
    command[5] = (uint8_t)scan_window;
    command[6] = (uint8_t)(scan_window >> 8);
    command[7] = filter_policy;
    command[8] = peer_addr_type;
    audio_ble_copy_address6_4d293c(command + 9u, peer_address);
    command[15] = own_addr_type;
    for (uint32_t i = 0u; i < 12u; ++i)
        command[16u + i] = connection_spec[i];
    audio_ble_hci_cmd_send(command);
}
