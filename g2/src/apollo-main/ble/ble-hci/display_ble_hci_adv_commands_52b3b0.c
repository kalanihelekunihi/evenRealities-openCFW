/* Cordio LE legacy advertising commands at 0x52b3b0, 0x52b3d2, 0x52b554. */
#include <stdint.h>

extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t opcode, uint16_t length);
extern void audio_ble_hci_cmd_send(void *command);

void HciLeSetAdvEnableCmd(uint8_t enable)
{
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x200au, 1u);
    if (command != 0) {
        command[3u] = enable;
        audio_ble_hci_cmd_send(command);
    }
}

static void audio_ble_hci_set_adv_data(uint16_t opcode, uint8_t length,
                                        const uint8_t *data)
{
    /* The Cordio API requires length <= 31 before entering this routine. */
    if (length > 31u) return;
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(opcode, 32u);
    if (command != 0) {
        command[3u] = length;
        for (uint32_t i = 0; i < length; ++i) command[4u + i] = data[i];
        for (uint32_t i = length; i < 31u; ++i) command[4u + i] = 0u;
        audio_ble_hci_cmd_send(command);
    }
}

void HciLeSetAdvDataCmd(uint8_t length, const uint8_t *data)
{
    audio_ble_hci_set_adv_data(0x2008u, length, data);
}

void HciLeSetScanRespDataCmd(uint8_t length, const uint8_t *data)
{
    audio_ble_hci_set_adv_data(0x2009u, length, data);
}
