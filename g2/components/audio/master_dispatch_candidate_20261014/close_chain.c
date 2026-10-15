#include <stdint.h>

extern void audio_ble_master_close_child_479b74(uint32_t);
extern void audio_ble_master_close_child_47b730(uint32_t);

/* Native 0x47a47c. Preserve each byte write before the ordered calls. */
void audio_ble_master_child_47a47c(uint32_t handle)
{
    volatile uint8_t *record = (volatile uint8_t *)(uintptr_t)handle;
    record[0x2f] = 0u;
    record[0x30] = 0u;
    audio_ble_master_close_child_479b74(handle);
    audio_ble_master_close_child_47b730(handle);
}

/* Native 0x47a5c0. */
void audio_ble_master_child_47a5c0(uint32_t handle)
{
    volatile uint8_t *record = (volatile uint8_t *)(uintptr_t)handle;
    if (record[0x30] == 0u)
        audio_ble_master_child_47a47c(handle);
}
