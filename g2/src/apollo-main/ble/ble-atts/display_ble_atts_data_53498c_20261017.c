/* Cordio attsDataCback; stock Main 0x53498c. */
#include <stdint.h>
extern uint8_t *audio_ble_atts_ccb_by_handle_5351a8(uint16_t, uint8_t);
extern uint8_t audio_ble_atts_csf_act_client_state_52caa8(uint16_t, uint8_t, uint8_t *);
extern uint32_t audio_ble_atts_proc_table_2000045c[18];
extern void attsErrRsp(uint8_t *, uint8_t, uint8_t, uint16_t, uint8_t);
static const uint8_t minimum_pdu_length[18] = {
    0u, 3u, 5u, 7u, 5u, 3u, 5u, 5u, 5u,
    3u, 3u, 5u, 2u, 0u, 0u, 1u, 0u, 15u
};
static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}
void audio_ble_atts_data_53498c(uint16_t handle, uint16_t length, uint8_t *packet)
{
    uint8_t *ccb = audio_ble_atts_ccb_by_handle_5351a8(handle, 0u);
    if (ccb == 0u || length == 0u)
        return;
    const uint8_t opcode = packet[8u];
    uint8_t method;
    if (opcode < 0x13u || (opcode >= 0x16u && opcode < 0x1fu))
        method = (uint8_t)((opcode & 0xfeu) / 2u);
    else if (opcode == 0x52u)
        method = 10u;
    else if (opcode == 0x20u)
        method = 16u;
    else if (opcode == 0xd2u)
        method = 17u;
    else
        method = 0u;
    uint8_t *main_ccb = *(uint8_t **)(ccb + 0x10u);
    if ((main_ccb[2u] & 8u) != 0u && method != 15u)
        return;
    uint8_t error = audio_ble_atts_csf_act_client_state_52caa8(
        (uint16_t)(ccb[0x24u] - 1u), opcode, packet);
    uint16_t attribute_handle = 0u;
    if (error != 0u) {
        if (length < 3u)
            return;
        attribute_handle = read16(packet + 9u);
    } else {
        const uint32_t entry = audio_ble_atts_proc_table_2000045c[method];
        if (entry == 0u)
            error = 6u;
        else if (length < minimum_pdu_length[method])
            error = 4u;
        else {
            void (*handler)(uint8_t *, uint16_t, uint8_t *) =
                (void (*)(uint8_t *, uint16_t, uint8_t *))(uintptr_t)entry;
            handler(ccb, length, packet);
        }
    }
    if (error != 0u && opcode != 2u && opcode != 0x1eu &&
        (opcode & 0x40u) == 0u)
        attsErrRsp(main_ccb, 0u, opcode, attribute_handle, error);
}
