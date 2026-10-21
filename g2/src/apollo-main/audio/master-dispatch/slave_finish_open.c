#include <stdint.h>

extern const uint8_t *audio_ble_comm_profile_slot;
extern uint8_t audio_ble_slave_open_flag_20074f93;
extern uint32_t audio_ble_pair_record_find_47ad74(uint32_t, const void *);
extern void audio_ble_subsystem_child_479418(void);
extern void audio_ble_slave_open_fallback_4b3606(const void *);
extern void audio_ble_slave_apply_record_52c244(uint32_t, const void *);
extern void audio_ble_pair_record_flags_47b40c(uint32_t, void *, uint32_t *);
extern void audio_ble_slave_apply_flags_52d370(uint32_t, uint32_t, uint32_t);
extern uint32_t AppDbCheckBonded(void);
extern uint32_t audio_ble_dm_sec_slave_req(uint8_t, uint8_t);

/* Native 0x4b3944. The record and policy providers retain separate contracts. */
void audio_ble_slave_finish_4b3944(const void *message, void *record)
{
    const uint8_t *msg = (const uint8_t *)message;
    uint8_t *row = (uint8_t *)record;
    row[6] = 0u;
    row[7] = 0u;
    uint32_t handle = audio_ble_pair_record_find_47ad74(msg[9], msg + 10u);
    *(uint32_t *)row = handle;
    if (handle == 0u && msg[9] == 1u && (msg[15] & 0xc0u) == 0x40u) {
        audio_ble_subsystem_child_479418();
        audio_ble_slave_open_fallback_4b3606(message);
    } else if (handle != 0u) {
        audio_ble_slave_open_flag_20074f93 = 1u;
        audio_ble_slave_apply_record_52c244(row[4], (const uint8_t *)(uintptr_t)handle + 0x6cu);
        uint32_t flags = 0u;
        uint32_t detail = 0u;
        audio_ble_pair_record_flags_47b40c(handle, &flags, &detail);
        audio_ble_slave_apply_flags_52d370(row[4], (uint8_t)flags, detail);
    }
    const uint8_t *profile = audio_ble_comm_profile_slot;
    if (profile[4] != 0u && AppDbCheckBonded() != 0u)
        (void)audio_ble_dm_sec_slave_req(msg[0], profile[0]);
}
