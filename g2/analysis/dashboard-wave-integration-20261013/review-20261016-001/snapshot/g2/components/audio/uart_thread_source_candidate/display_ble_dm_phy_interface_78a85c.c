/* Cordio PHY interface at 0x78a85c and its HCI handler at 0x4c5734.
 * Native CCB offsets and callback slot are measured against the pinned image. */
#include <stdint.h>

extern void audio_ble_dm_empty_reset_4d29be(void);
extern void audio_ble_dm_empty_handler_4d29c0(void *);
extern uint8_t *audio_ble_dm_conn_ccb_by_handle_4b601c(uint16_t);
extern uint8_t audio_dm_connection_records[];

typedef void (*audio_ble_dm_event_callback)(void *);

void audio_ble_dm_phy_hci_handler_4c5734(void *event_ptr)
{
    const uint8_t *const event = (const uint8_t *)event_ptr;
    uint8_t indication[10];
    uint8_t *ccb;
    const uint8_t kind = event[2u];
    if (kind == 0x2au) {
        indication[0] = 0u;
        indication[1] = 0u;
        indication[2] = 0x45u;
        indication[3] = event[4u];
        indication[4] = indication[3];
    } else {
        ccb = audio_ble_dm_conn_ccb_by_handle_4b601c(
            *(const uint16_t *)(const void *)event);
        if (ccb == 0 || (kind != 0x29u && kind != 0x2bu)) return;
        indication[0] = ccb[0x10u];
        indication[1] = 0u;
        indication[2] = (kind == 0x29u) ? 0x44u : 0x46u;
        indication[3] = event[4u];
        indication[4] = indication[3];
        *(uint16_t *)(void *)(indication + 6u) =
            *(const uint16_t *)(const void *)(ccb + 0x0cu);
        indication[8] = event[8u];
        indication[9] = event[9u];
    }
    (*(audio_ble_dm_event_callback *)(void *)(audio_dm_connection_records + 0x9cu))(indication);
}

typedef void (*audio_ble_dm_phy_fn)(void *);
_Static_assert(sizeof(audio_ble_dm_phy_fn) == 4u, "Thumb pointer ABI");
const audio_ble_dm_phy_fn audio_ble_dm_phy_table[3]
    __attribute__((used, aligned(4))) = {
        (audio_ble_dm_phy_fn)audio_ble_dm_empty_reset_4d29be,
        audio_ble_dm_phy_hci_handler_4c5734,
        audio_ble_dm_empty_handler_4d29c0,
    };
