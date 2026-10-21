#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern const uint8_t *audio_ble_comm_profile_slot;
extern uint32_t audio_ble_slave_record_key_4b6eea(uint32_t);
extern uint32_t audio_ble_slave_record_kind_4b6ed8(uint32_t);
extern uint32_t audio_ble_pair_record_create_47a71c(uint8_t, uint32_t, uint32_t);
extern void audio_ble_slave_set_features_52bacc(uint32_t, uint32_t, uint32_t,
                                                 uint32_t, uint32_t);

/* Native 0x4b39f6. Subsystem offset 0x54 is RAM 0x20071a1c. */
void audio_ble_slave_finish_4b39f6(const void *message, void *record)
{
    const uint8_t *msg = (const uint8_t *)message;
    uint8_t *row = (uint8_t *)record;
    audio_ble_subsystem_link_state_200719c8[0x54u] = 1u;
    row[7] = (uint8_t)((msg[4] & 1u) & (audio_ble_comm_profile_slot[0] & 1u));
    if (row[7] != 0u && *(uint32_t *)row == 0u) {
        uint32_t key = audio_ble_slave_record_key_4b6eea(row[4]);
        uint8_t kind = (uint8_t)audio_ble_slave_record_kind_4b6ed8(row[4]);
        *(uint32_t *)row = audio_ble_pair_record_create_47a71c(kind, key, 0u);
    }
    row[11] = 0u;
    uint8_t supported = audio_ble_comm_profile_slot[2];
    uint8_t flags = audio_ble_comm_profile_slot[1];
    if (audio_ble_slave_record_kind_4b6ed8(row[4]) == 1u)
        flags |= 2u;
    audio_ble_slave_set_features_52bacc(row[4], audio_ble_comm_profile_slot[3],
                                        audio_ble_comm_profile_slot[0],
                                        (uint8_t)(flags & msg[6]),
                                        (uint8_t)(supported & msg[7]));
}
