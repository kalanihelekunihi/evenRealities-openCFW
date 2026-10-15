#include <stdint.h>

extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern uint8_t audio_ble_discovery_connection_records_200717b0[];
extern void audio_ble_subsystem_child_479418(void);
extern uint32_t audio_ble_pair_record_next_47a630(uint32_t);
extern uint32_t audio_ble_link_mask_select_47ae78(uint32_t, uint8_t, uint8_t *);
extern uint32_t audio_ble_slave_record_key_4b6eea(uint32_t);
extern void audio_ble_slave_resolution_request_4d27f6(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "app_slave";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_slave.c";
static const char function[] = "appSlaveResolveAddr";
static const char busy[] = "appSlaveResolveAddr: Address resolution already in progress, ignoring";
static const char compact[] =
    "[app_slave]appSlaveResolveAddr: Address resolution already in progress, ignoring";

/* Native 0x4b3606. State +0x70 is the current AppDb row and +0x74 is
 * the outstanding-resolution flag. */
void audio_ble_slave_open_fallback_4b3606(const void *message)
{
    const uint8_t *msg = (const uint8_t *)message;
    uint32_t message_id = (uint32_t)msg[0] | ((uint32_t)msg[1] << 8u);
    if (audio_ble_subsystem_link_state_200719c8[0x74u] != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x166u, busy);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u, compact, compact);
        return;
    }
    audio_ble_subsystem_child_479418();
    uint32_t row = audio_ble_pair_record_next_47a630(0u);
    *(uint32_t *)(void *)(audio_ble_subsystem_link_state_200719c8 + 0x70u) = row;
    while (row != 0u) {
        uint32_t link = audio_ble_link_mask_select_47ae78(row, 4u, 0);
        if (link != 0u) {
            uintptr_t connection_row =
                (uintptr_t)audio_ble_discovery_connection_records_200717b0
                + message_id * 0x30u - 0x30u;
            uint8_t connection = *(const volatile uint8_t *)(connection_row + 4u);
            uint32_t key = audio_ble_slave_record_key_4b6eea(connection);
            audio_ble_slave_resolution_request_4d27f6(key, link, message_id);
            audio_ble_subsystem_link_state_200719c8[0x74u] = 1u;
            break;
        }
        row = audio_ble_pair_record_next_47a630(row);
        *(uint32_t *)(void *)(audio_ble_subsystem_link_state_200719c8 + 0x70u) = row;
    }
}
