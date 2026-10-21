#include <stdint.h>

extern void audio_ble_slave_disconnect_event(uint8_t);

/* Native 0x50390c: clear pending connection state before dispatching close. */
void audio_ble_master_event_50390c(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    volatile uint8_t *row = (volatile uint8_t *)record;
    uint16_t connection = (uint16_t)bytes[0] | (uint16_t)((uint16_t)bytes[1] << 8);
    row[8] = 0u;
    audio_ble_slave_disconnect_event((uint8_t)connection);
}

/* Native 0x50391c: a successful event turns the active row into a
 * connected, non-pending state. The other cases leave the row untouched. */
void audio_ble_master_event_50391c(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    volatile uint8_t *row = (volatile uint8_t *)record;
    if (row[6] != 0u && bytes[4] != 0u) {
        row[5] = 1u;
        row[6] = 0u;
        row[8] = 0u;
    }
}

