#include <stdint.h>

/* Apollo Main 0x503c32. The connection rows begin at native RAM
 * 0x200717b0 and are 0x30 bytes each. Storage ownership remains external. */
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern void audio_ble_master_event_5037ea(const void *, void *);
extern void audio_ble_master_event_503810(const void *, void *);
extern void audio_ble_master_event_5038da(const void *, void *);
extern void audio_ble_master_event_50390c(const void *, void *);
extern void audio_ble_master_event_50391c(const void *, void *);
extern void audio_ble_master_event_5038b8(const void *, void *);
extern void audio_ble_master_event_503820(const void *, void *);
extern void audio_ble_master_event_503880(const void *, void *);
extern void audio_ble_master_event_50389e(const void *, void *);
extern void audio_ble_slave_disconnect_event(uint8_t);
extern uint32_t audio_ble_hci_driver_radio_boot(uint8_t);
extern void audio_ble_dm_device_reset(void);

void audio_ble_comm_master_dispatch_b(void *message)
{
    const uint8_t *bytes = (const uint8_t *)message;
    uint16_t connection = (uint16_t)bytes[0] | (uint16_t)((uint16_t)bytes[1] << 8);
    uint8_t event = bytes[2];
    void *row = 0;
    if (event != 0x3fu && event != 0x79u && connection >= 1u && connection <= 3u)
        row = &audio_ble_discovery_connection_records_200717b0[(connection - 1u) * 0x30u];

    switch (event) {
    case 0x27u: if (row) audio_ble_master_event_5037ea(message, row); break;
    case 0x28u: if (row) audio_ble_master_event_503810(message, row); break;
    case 0x2au: if (row) audio_ble_master_event_5038da(message, row); break;
    case 0x2bu: if (row) audio_ble_master_event_50390c(message, row); break;
    case 0x2cu: if (row) audio_ble_master_event_50391c(message, row); break;
    case 0x2du: audio_ble_slave_disconnect_event((uint8_t)connection); break;
    case 0x2fu: if (row) audio_ble_master_event_5038b8(message, row); break;
    case 0x32u: if (row) audio_ble_master_event_503820(message, row); break;
    case 0x3au: if (row) audio_ble_master_event_503880(message, row); break;
    case 0x3bu: if (row) audio_ble_master_event_50389e(message, row); break;
    case 0x3fu: break; /* Native initializes row to null for this event. */
    case 0x79u:
        (void)audio_ble_hci_driver_radio_boot(0u);
        audio_ble_dm_device_reset();
        break;
    default: break;
    }
}
