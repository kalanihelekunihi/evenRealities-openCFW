#include <stdint.h>

/* These two callees are retained by their authenticated Main addresses.
 * Their bodies are separate source contracts. */
extern void audio_ble_master_child_47a5c0(uint32_t);
extern void audio_ble_master_child_47aed4(uint32_t, const void *);

/* Native 0x503810. */
void audio_ble_master_event_503810(const void *message, void *record)
{
    (void)message;
    uint32_t handle = *(volatile uint32_t *)record;
    if (handle != 0u)
        audio_ble_master_child_47a5c0(handle);
}

/* Native 0x5038b8. The row flag must be written before the child call. */
void audio_ble_master_event_5038b8(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    volatile uint8_t *row = (volatile uint8_t *)record;
    if (row[7] != 0u) {
        uint32_t handle = *(volatile uint32_t *)record;
        if (handle != 0u) {
            row[11] = (uint8_t)(row[11] | bytes[30]);
            audio_ble_master_child_47aed4(handle, message);
        }
    }
}
