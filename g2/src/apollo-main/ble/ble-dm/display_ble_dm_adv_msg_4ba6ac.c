#include <stdint.h>

/* Cordio legacy advertising action order, stock table at 0x75f550. */
typedef void (*audio_dm_adv_action_t)(void *message);

extern uint8_t audio_ble_dm_adv_control[];
extern void HciLeSetAdvEnableCmd(uint8_t enable);
extern void audio_ble_dm_adv_config_lower_4b9a80(uint8_t type,
                                                  uint8_t peer_type,
                                                  const uint8_t *peer_address);
extern void HciLeSetAdvDataCmd(uint8_t length, const uint8_t *data);
extern void HciLeSetScanRespDataCmd(uint8_t length, const uint8_t *data);

static uint16_t audio_dm_adv_load16(const uint8_t *bytes)
{
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

static void audio_dm_adv_store16(uint8_t *bytes, uint16_t value)
{
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8);
}

void audio_ble_dm_adv_remove_set_4ba33c(void *message) { (void)message; }
void audio_ble_dm_adv_clear_sets_4ba33e(void *message) { (void)message; }
void audio_ble_dm_adv_set_rand_addr_4ba340(void *message) { (void)message; }

void audio_ble_dm_adv_config_4b9ac0(void *message)
{
    if (audio_ble_dm_adv_control[0x1du] == 0u &&
        audio_ble_dm_adv_control[0x18u] != 1u &&
        audio_ble_dm_adv_control[0x18u] != 4u) {
        const uint8_t *bytes = (const uint8_t *)message;
        audio_ble_dm_adv_config_lower_4b9a80(bytes[5u], bytes[6u], bytes + 7u);
    }
}

void audio_ble_dm_adv_set_data_4b9d24(void *message)
{
    if (audio_ble_dm_adv_control[0x1du] == 0u) {
        const uint8_t *bytes = (const uint8_t *)message;
        if (bytes[6u] == 0u) {
            HciLeSetAdvDataCmd(bytes[7u], bytes + 8u);
        } else {
            HciLeSetScanRespDataCmd(bytes[7u], bytes + 8u);
        }
    }
}

void audio_ble_dm_adv_start_4b9e88(void *message)
{
    if (audio_ble_dm_adv_control[0x1du] == 0u &&
        audio_ble_dm_adv_control[0x18u] != 1u &&
        audio_ble_dm_adv_control[0x18u] != 4u) {
        const uint8_t *bytes = (const uint8_t *)message;
        audio_ble_dm_adv_control[0x1du] = 3u;
        audio_dm_adv_store16(audio_ble_dm_adv_control + 0x20u,
                             audio_dm_adv_load16(bytes + 8u));
        HciLeSetAdvEnableCmd(1u);
    }
}

void audio_ble_dm_adv_stop_4ba0f4(void *message)
{
    (void)message;
    if (audio_ble_dm_adv_control[0x1du] == 1u &&
        audio_ble_dm_adv_control[0x18u] != 1u &&
        audio_ble_dm_adv_control[0x18u] != 4u) {
        audio_ble_dm_adv_control[0x1du] = 5u;
        HciLeSetAdvEnableCmd(0u);
    }
}

void audio_ble_dm_adv_timeout_4ba342(void *message)
{
    (void)message;
    if (audio_ble_dm_adv_control[0x1du] == 1u) {
        audio_ble_dm_adv_control[0x1du] = 5u;
        HciLeSetAdvEnableCmd(0u);
    }
}

const audio_dm_adv_action_t audio_ble_dm_adv_actions_75f550[8] = {
    audio_ble_dm_adv_config_4b9ac0,
    audio_ble_dm_adv_set_data_4b9d24,
    audio_ble_dm_adv_start_4b9e88,
    audio_ble_dm_adv_stop_4ba0f4,
    audio_ble_dm_adv_remove_set_4ba33c,
    audio_ble_dm_adv_clear_sets_4ba33e,
    audio_ble_dm_adv_set_rand_addr_4ba340,
    audio_ble_dm_adv_timeout_4ba342,
};

void audio_ble_dm_adv_msg_handler_4ba6ac(void *message)
{
    const uint8_t *bytes = (const uint8_t *)message;
    audio_ble_dm_adv_actions_75f550[bytes[2] & 7u](message);
}
