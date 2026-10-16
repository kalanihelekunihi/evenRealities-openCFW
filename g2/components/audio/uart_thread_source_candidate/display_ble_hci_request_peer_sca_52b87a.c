/* Cordio HciRequestPeerScaCmd 0x52b87a: 0x206d, two handle bytes. */
#include <stdint.h>

extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

void audio_ble_hci_request_peer_sca_52b87a(uint16_t handle)
{
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x206du, 2u);
    if (command == 0)
        return;
    command[3u] = (uint8_t)handle;
    command[4u] = (uint8_t)(handle >> 8u);
    audio_ble_hci_cmd_send(command);
}
