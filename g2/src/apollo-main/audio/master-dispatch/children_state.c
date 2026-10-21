#include <stdint.h>

extern void audio_ble_connection_state_set_47b4ce(uint32_t, uint8_t);

/* Native 0x503880 and 0x50389e pass the row's connection handle through
 * the existing source-backed state setter. The former guards a null row;
 * the latter is called only after the parent selected a valid row. */
void audio_ble_master_event_503880(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    if (bytes[3] == 0u && record != 0) {
        uint32_t handle = *(volatile uint32_t *)record;
        if (handle != 0u)
            audio_ble_connection_state_set_47b4ce(handle, 1u);
    }
}

void audio_ble_master_event_50389e(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    if (bytes[3] == 0u) {
        uint32_t handle = *(volatile uint32_t *)record;
        if (handle != 0u)
            audio_ble_connection_state_set_47b4ce(handle, 0u);
    }
}
