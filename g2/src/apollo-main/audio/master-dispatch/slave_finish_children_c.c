#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern void audio_ble_master_child_47a5c0(uint32_t);
extern int32_t g2_lfs_memcmp(const void *, const void *, uint32_t);
extern uint32_t audio_ble_pair_record_find_47add4(uint32_t, const void *);
extern void audio_ble_slave_resolve_4b36b2(void *);

static const uint8_t empty_address[8] = {0};
extern uint8_t audio_ble_slave_open_flag_20074f93; /* opencfw U5: now provided by the Cordio unit */

/* Native 0x4b39de. */
void audio_ble_slave_finish_4b39de(const void *message, void *record)
{
    (void)message;
    uint32_t handle = *(const uint32_t *)record;
    if (handle != 0u)
        audio_ble_master_child_47a5c0(handle);
    audio_ble_slave_open_flag_20074f93 = 0u;
}

/* Native 0x4b3b4c. 0x20071a34 aliases subsystem offset 0x6c. */
void audio_ble_slave_finish_4b3b4c(const void *message, void *record)
{
    const uint8_t *bytes = (const uint8_t *)message;
    uint32_t *handle = (uint32_t *)record;
    if (*handle == 0u) {
        uint16_t address_type = (uint16_t)bytes[14] | ((uint16_t)bytes[15] << 8);
        if (address_type == 0u &&
            g2_lfs_memcmp(bytes + 6u, empty_address, 8u) == 0) {
            if (audio_ble_subsystem_link_state_200719c8[0x74u] != 0u) {
                audio_ble_subsystem_link_state_200719c8[0x6cu] = 1u;
                return;
            }
        } else {
            *handle = audio_ble_pair_record_find_47add4(address_type, bytes + 6u);
            if (*handle != 0u)
                audio_ble_subsystem_link_state_200719c8[0x74u] = 0u;
        }
    }
    audio_ble_slave_resolve_4b36b2(record);
}
