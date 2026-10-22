/* Cordio indication/notification setup, stock 0x53390e..0x533a40. */
#include <stdint.h>

extern void attL2cDataReq(uint8_t *, uint8_t, uint16_t, uint8_t *);
extern void WsfTimerStartSec(void *, uint32_t);
extern void audio_ble_att_exec_callback_4b5074(uint8_t, uint8_t,
                                                uint16_t, uint8_t, uint16_t);
extern void audio_ble_atts_exec_callback_533934(uint8_t, uint16_t, uint8_t);
extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];

extern uint16_t audio_ble_att_msg_param_4b50f0(uint8_t connection, uint8_t slot); /* opencfw U5: now provided by the Cordio unit */

void audio_ble_atts_set_pend_ntf_53390e(uint8_t *ccb, uint16_t handle)
{
    for (uint32_t index = 0u; index < 10u; ++index) {
        uint16_t *const pending =
            (uint16_t *)(void *)(ccb + 0x2au + index * 2u);
        if (*pending == 0u) {
            *pending = handle;
            return;
        }
    }
}

void audio_ble_atts_setup_msg_5339ac(uint8_t *ccb, uint8_t connection,
                                      uint8_t slot, void *packet_arg)
{
    uint8_t *const packet = (uint8_t *)packet_arg;
    const uint8_t opcode = packet[8];
    const uint16_t handle = *(const uint16_t *)(const void *)(packet + 2u);
    const uint16_t length = *(const uint16_t *)(const void *)packet;
    uint8_t *const main_ccb = (uint8_t *)(uintptr_t)
        *(const uint32_t *)(const void *)(ccb + 0x10u);
    attL2cDataReq(main_ccb, slot, length, packet);
    if (opcode == 0x1du) {
        *(uint16_t *)(void *)(ccb + 0x28u) = handle;
        *(uint16_t *)(void *)(ccb + 0x26u) = handle;
        ccb[0x0au] = 0x22u;
        *(uint16_t *)(void *)(ccb + 8u) =
            audio_ble_att_msg_param_4b50f0(ccb[0x24u], ccb[0x25u]);
        const uint8_t *const config = (const uint8_t *)(uintptr_t)
            *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
        WsfTimerStartSec(ccb, config[6]);
    } else if ((main_ccb[(uint32_t)slot * 4u + 2u] & 2u) == 0u) {
        if (opcode == 0x23u)
            audio_ble_att_exec_callback_4b5074(connection, 0x13u,
                                                handle, 0u, 0u);
        else
            audio_ble_atts_exec_callback_533934(connection, handle, 0u);
    } else {
        audio_ble_atts_set_pend_ntf_53390e(ccb, handle);
    }
}
