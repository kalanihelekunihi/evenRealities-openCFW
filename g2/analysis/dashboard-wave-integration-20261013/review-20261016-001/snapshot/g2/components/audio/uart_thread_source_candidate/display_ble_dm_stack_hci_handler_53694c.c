/* Native Cordio DM stack HCI dispatch at Apollo Main 0x53694c. */
#include <stdint.h>

extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern uint8_t audio_ble_dm_handler_state[];
extern void audio_ble_dm_stack_hci_scan_complete_5368b6(void *);
extern void WsfTimerStartMs(void *, uint32_t);
extern void WsfTimerStop(void *);
extern void audio_ble_dm_dev_pass_priv_4b2ea6(uint8_t, uint8_t, uint32_t, uint32_t);

void audio_ble_dm_stack_hci_handler_53694c(void *event_ptr)
{
    uint8_t *const event = (uint8_t *)event_ptr;
    uint8_t *const rows = audio_ble_dm_stack_rows_200738dc;
    if (event[2u] == 6u) {
        audio_ble_dm_stack_hci_scan_complete_5368b6(event);
        return;
    }
    if (event[2u] != 0x34u) return;

    if (rows[0x18u] == 1u) {
        if (event[3u] == 0u) {
            const uint16_t timeout = *(const uint16_t *)(const void *)(rows + 0x1au);
            if (timeout != 0u) {
                rows[0x0au] = 0x12u;
                WsfTimerStartMs(rows, timeout);
            }
            rows[0x18u] = 2u;
        } else {
            rows[0x18u] = 0u;
        }
        event[2u] = 0x24u;
    } else if (rows[0x18u] == 3u) {
        if (event[3u] == 0u) {
            WsfTimerStop(rows);
            rows[0x18u] = 0u;
        } else {
            rows[0x18u] = 2u;
        }
        event[2u] = 0x25u;
    }

    const uint8_t passed = event[2u] == 0x24u ? 0x0cu : 0x0du;
    audio_ble_dm_dev_pass_priv_4b2ea6(passed, event[2u], 0u, 0u);
    void (*callback)(void *) = *(void (**)(void *))(void *)(audio_ble_dm_handler_state + 8u);
    callback(event);
}
