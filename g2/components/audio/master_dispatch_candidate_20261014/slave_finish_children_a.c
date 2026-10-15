#include <stdint.h>

extern void audio_ble_master_child_47aed4(uint32_t, const void *);

/* Native 0x4b3a86. */
void audio_ble_slave_finish_4b3a86(const void *message, void *record)
{
    volatile uint8_t *row = (volatile uint8_t *)record;
    if (row[7] == 0u)
        return;
    uint32_t handle = *(volatile uint32_t *)record;
    if (handle == 0u)
        return;
    row[11] = (uint8_t)(row[11] | ((const uint8_t *)message)[30]);
    audio_ble_master_child_47aed4(handle, message);
}

/* Native 0x4b3aea is bx lr. */
void audio_ble_slave_finish_4b3aea(const void *message, void *record)
{
    (void)message;
    (void)record;
}
