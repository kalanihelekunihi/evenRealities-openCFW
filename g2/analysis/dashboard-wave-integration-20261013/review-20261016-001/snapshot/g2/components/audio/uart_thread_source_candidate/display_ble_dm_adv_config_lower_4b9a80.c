/* Cordio legacy advertising configuration and LE parameter command. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint8_t audio_ble_dm_handler_state[];
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t opcode, uint16_t length);
extern void audio_ble_hci_cmd_send(void *command);

/* Stock dmLegAdvCb.advType byte at 0x20074fb3. */
uint8_t audio_ble_dm_leg_adv_type_20074fb3;

uint8_t audio_ble_dm_ll_addr_type_4d2a84(uint8_t address_type)
{
    if (audio_ble_dm_handler_state[0x16u] != 0u && address_type <= 1u) {
        return (uint8_t)(address_type + 2u);
    }
    return address_type;
}

void HciLeSetAdvParamCmd(uint16_t minimum, uint16_t maximum, uint8_t adv_type,
                         uint8_t own_address_type, uint8_t peer_address_type,
                         const uint8_t *peer_address, uint8_t channel_map,
                         uint8_t filter_policy)
{
    uint8_t *command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x2006u, 15u);
    if (command == 0) return;
    command[3u] = (uint8_t)minimum;
    command[4u] = (uint8_t)(minimum >> 8);
    command[5u] = (uint8_t)maximum;
    command[6u] = (uint8_t)(maximum >> 8);
    command[7u] = adv_type;
    command[8u] = own_address_type;
    command[9u] = peer_address_type;
    for (uint32_t i = 0; i < 6u; ++i) {
        command[10u + i] = peer_address == 0 ? 0u : peer_address[i];
    }
    command[16u] = channel_map;
    command[17u] = filter_policy;
    audio_ble_hci_cmd_send(command);
}

static uint16_t audio_ble_dm_load16(const uint8_t *bytes)
{
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

void audio_ble_dm_adv_config_lower_4b9a80(uint8_t type, uint8_t peer_type,
                                            const uint8_t *peer_address)
{
    HciLeSetAdvParamCmd(audio_ble_dm_load16(audio_ble_dm_adv_control + 0x10u),
                        audio_ble_dm_load16(audio_ble_dm_adv_control + 0x14u),
                        type,
                        audio_ble_dm_ll_addr_type_4d2a84(audio_ble_dm_handler_state[0x0eu]),
                        peer_type, peer_address,
                        audio_ble_dm_adv_control[0x1au],
                        audio_ble_dm_handler_state[0x11u]);
    audio_ble_dm_leg_adv_type_20074fb3 = type;
}
