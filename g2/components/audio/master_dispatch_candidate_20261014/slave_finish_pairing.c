#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern void audio_ble_master_pair_state_47a49c(uint32_t, uint8_t);
extern void audio_ble_master_pair_event_4bb098(const void *, uint8_t);

/* Native 0x4b3aa8. Its 0x4b467c helper writes subsystem offset 0x54. */
void audio_ble_slave_finish_4b3aa8(const void *message, void *record)
{
    volatile uint8_t *row = (volatile uint8_t *)record;
    if (row[7] == 0u)
        return;
    row[5] = 1u;
    uint32_t handle = *(volatile uint32_t *)record;
    if (handle != 0u)
        audio_ble_master_pair_state_47a49c(handle, row[11]);
    audio_ble_subsystem_link_state_200719c8[0x54u] = 0u;
    if (audio_ble_subsystem_link_state_200719c8[0x5du] == 1u)
        row[9] = 1u;
    handle = *(volatile uint32_t *)record;
    if (handle != 0u)
        audio_ble_master_pair_event_4bb098(message, row[4]);
}
