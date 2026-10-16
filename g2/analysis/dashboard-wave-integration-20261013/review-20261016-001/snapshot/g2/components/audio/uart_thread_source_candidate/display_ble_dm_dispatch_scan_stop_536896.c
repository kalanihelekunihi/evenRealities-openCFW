/* Cordio DM scan-stop dispatch 0x536896 and HCI command 0x52b4e2. */
#include <stdint.h>

extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

void audio_ble_hci_le_set_scan_enable_off_52b4e2(uint8_t enable, uint8_t filter_duplicates)
{
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x200cu, 2u);
    if (command == 0) return;
    command[3u] = enable;
    command[4u] = filter_duplicates;
    audio_ble_hci_cmd_send(command);
}

void audio_ble_dm_dispatch_536896(void *message)
{
    (void)message;
    if (audio_ble_dm_stack_rows_200738dc[0x18u] == 2u) {
        audio_ble_dm_stack_rows_200738dc[0x18u] = 3u;
        audio_ble_hci_le_set_scan_enable_off_52b4e2(0u, 0u);
    }
}
