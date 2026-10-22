/* Cordio legacy advertising configuration and LE parameter command. */
#include <stdint.h>

extern uint8_t audio_ble_dm_adv_control[];
extern uint8_t audio_ble_dm_handler_state[];
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t opcode, uint16_t length);
extern void audio_ble_hci_cmd_send(void *command);

/* Stock dmLegAdvCb.advType byte at 0x20074fb3. */
uint8_t audio_ble_dm_leg_adv_type_20074fb3;

extern uint8_t audio_ble_dm_ll_addr_type_4d2a84(uint8_t address_type); /* opencfw U5: now provided by the Cordio unit */

extern void HciLeSetAdvParamCmd(uint16_t minimum, uint16_t maximum, uint8_t adv_type, uint8_t own_address_type, uint8_t peer_address_type, const uint8_t *peer_address, uint8_t channel_map, uint8_t filter_policy); /* opencfw U5: now provided by the Cordio unit */

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
