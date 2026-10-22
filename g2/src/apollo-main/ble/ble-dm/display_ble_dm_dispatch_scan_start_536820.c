/* Cordio DM scan-start dispatch 0x536820 and LE scan parameters 0x52b50a. */
#include <stdint.h>

extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern uint8_t audio_ble_dm_handler_state[];
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

extern void audio_ble_hci_le_set_scan_params_52b50a(uint8_t type, uint16_t interval, uint16_t window, uint8_t own_addr, uint8_t filter_policy); /* opencfw U5: now provided by the Cordio unit */

void audio_ble_dm_dispatch_536820(void *message_ptr)
{
    uint8_t *const message = (uint8_t *)message_ptr;
    uint8_t *const rows = audio_ble_dm_stack_rows_200738dc;
    if (rows[0x18u] != 0u) return;

    uint8_t own_addr = audio_ble_dm_handler_state[0x0fu];
    if (audio_ble_dm_handler_state[0x16u] != 0u) {
        if (own_addr == 0u) own_addr = 2u;
        else if (own_addr == 1u) own_addr = 3u;
    }
    const uint16_t interval = *(const uint16_t *)(const void *)(rows + 0x10u);
    const uint16_t window = *(const uint16_t *)(const void *)(rows + 0x14u);
    audio_ble_hci_le_set_scan_params_52b50a(message[5u], interval, window,
                                             own_addr, audio_ble_dm_handler_state[0x13u]);
    const uint8_t mode = message[7u];
    rows[0x1du] = mode == 1u ? 1u : mode == 2u ? 3u : 0u;
    rows[0x1cu] = 0u;
    *(uint16_t *)(void *)(rows + 0x1au) = *(const uint16_t *)(const void *)(message + 8u);
    rows[0x18u] = 1u;
    /* Native scan start passes event byte 12 to HciLeSetScanEnableCmd. */
    uint8_t *const command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x200cu, 2u);
    if (command != 0) {
        command[3u] = 1u;
        command[4u] = message[0x0cu];
        audio_ble_hci_cmd_send(command);
    }
}
