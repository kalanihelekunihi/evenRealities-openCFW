#include <stdint.h>

extern void audio_ble_connection_state_set_47b4ce(uint32_t, uint8_t);
extern uint8_t audio_ble_dm_privacy_state[];

/* Native 0x20075020. Its absolute placement remains a linker gate. */
uint8_t audio_ble_slave_status_20075020;

/* Native 0x4b3bb4. */
void audio_ble_slave_finish_4b3bb4(const void *message, void *record)
{
    if (((const uint8_t *)message)[3] != 0u || record == 0)
        return;
    uint32_t handle = *(const uint32_t *)record;
    if (handle != 0u)
        audio_ble_connection_state_set_47b4ce(handle, 1u);
}

/* Native 0x4b3bd2; the parent dispatcher supplies a nonnull row. */
void audio_ble_slave_finish_4b3bd2(const void *message, void *record)
{
    if (((const uint8_t *)message)[3] != 0u)
        return;
    uint32_t handle = *(const uint32_t *)record;
    if (handle != 0u)
        audio_ble_connection_state_set_47b4ce(handle, 0u);
}

/* Native 0x4b3ba0 through its two one-byte accessors 0x4d2a7e/0x52dc24. */
void audio_ble_slave_finish_4b3ba0(const void *message, void *record)
{
    (void)record;
    if (((const uint8_t *)message)[3] == 0u)
        audio_ble_slave_status_20075020 = audio_ble_dm_privacy_state[0x16u];
}
