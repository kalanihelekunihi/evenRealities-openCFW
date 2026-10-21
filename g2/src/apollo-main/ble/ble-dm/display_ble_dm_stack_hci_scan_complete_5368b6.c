/* Cordio scan report filter at 0x5368b6 and AD-type walker at 0x4d2a06. */
#include <stdint.h>

extern uint8_t audio_ble_dm_stack_rows_200738dc[];
extern uint8_t audio_ble_dm_handler_state[];

uint8_t *audio_ble_dm_find_ad_type_4d2a06(uint8_t type, uint16_t remaining,
                                            uint8_t *fields)
{
    while (remaining != 0u) {
        const uint8_t length = fields[0u];
        if (length == 0u || length >= remaining) return 0;
        if (fields[1u] == type) return fields;
        remaining = (uint16_t)(remaining - length - 1u);
        fields += (uint32_t)length + 1u;
    }
    return 0;
}

void audio_ble_dm_stack_hci_scan_complete_5368b6(void *event_ptr)
{
    uint8_t *const event = (uint8_t *)event_ptr;
    uint8_t *const rows = audio_ble_dm_stack_rows_200738dc;
    if (rows[0x18u] != 2u) return;
    uint8_t suppress = 0u;
    if (rows[0x1du] != 0u) {
        if (event[0x0au] == 4u) {
            if (rows[0x1cu] != 0u) {
                suppress = 1u;
                rows[0x1cu] = 0u;
            }
        } else {
            uint8_t *const fields = *(uint8_t **)(void *)(event + 4u);
            uint8_t *const ad = audio_ble_dm_find_ad_type_4d2a06(1u, event[8u], fields);
            if (ad == 0 || (ad[2u] & rows[0x1du]) == 0u) {
                suppress = 1u;
                rows[0x1cu] = 1u;
            }
        }
    }
    if (suppress == 0u) {
        event[2u] = 0x26u;
        void (*callback)(void *) = *(void (**)(void *))(void *)(audio_ble_dm_handler_state + 8u);
        callback(event);
    }
}
