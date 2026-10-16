/* Native HciLeLtkReqReplCmd at Apollo Main 0x52b2ce. */
#include <stdint.h>

extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

void HciLeLtkReqReplCmd(uint16_t handle, const uint8_t *key)
{
    uint8_t *const command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x201au, 18u);
    if (command == 0) return;
    command[3u] = (uint8_t)handle;
    command[4u] = (uint8_t)(handle >> 8);
    for (uint32_t i = 0; i < 16u; ++i) command[5u + i] = key[i];
    audio_ble_hci_cmd_send(command);
}
