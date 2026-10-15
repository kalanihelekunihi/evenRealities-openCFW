#include <stdint.h>

extern void audio_ble_master_pair_state_47a49c(uint32_t, uint8_t);
extern void audio_ble_master_pair_event_4bb098(const void *, uint8_t);

/* Native 0x5038da. The pending flag is cleared on every path. */
void audio_ble_master_event_5038da(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    volatile uint8_t *row = (volatile uint8_t *)record;
    if ((bytes[4] & 1u) != 0u) {
        row[5] = 1u;
        uint32_t handle = *(volatile uint32_t *)record;
        if (handle != 0u)
            audio_ble_master_pair_state_47a49c(handle, row[11]);
        handle = *(volatile uint32_t *)record;
        if (handle != 0u)
            audio_ble_master_pair_event_4bb098(message, row[4]);
    }
    row[8] = 0u;
}
