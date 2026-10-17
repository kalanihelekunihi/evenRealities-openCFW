/* Cordio attcConnCback; stock Main 0x53135a. */
#include <stdint.h>
extern uint8_t audio_ble_attc_state[];
extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern uint8_t DmConnRole(uint8_t);
extern uint16_t audio_ble_hci_max_rx_acl_len_530d4c(void);
extern void audio_ble_attc_mtu_request(uint8_t, uint16_t);
extern void audio_ble_attc_req_clear_531af2(uint8_t, uint8_t *, uint8_t);
extern void audio_ble_attc_write_cmd_callback_530de6(uint8_t, uint8_t *, uint8_t);
extern void WsfTimerStop(void *);
static uint16_t read16(const uint8_t *p)
{
    return (uint16_t)p[0] | ((uint16_t)p[1] << 8);
}
void audio_ble_attc_conn_53135a(uint8_t *ccb, const uint8_t *event)
{
    const uint8_t connection = ccb[0x0eu];
    if (event[2u] == 0x27u) {
        if (DmConnRole(connection) == 0u) {
            const uint16_t rx_len = audio_ble_hci_max_rx_acl_len_530d4c();
            const uint32_t cfg_address =
                *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
            const uint16_t configured = read16((const uint8_t *)(uintptr_t)cfg_address + 4u);
            const uint16_t transport = (uint16_t)(rx_len - 4u);
            const uint16_t local = configured < transport ? configured :
                (uint16_t)(audio_ble_hci_max_rx_acl_len_530d4c() - 4u);
            if (local != 0xf7u)
                audio_ble_attc_mtu_request(connection, local);
        }
        return;
    }
    if (event[2u] != 0x28u)
        return;
    const uint8_t status = (uint8_t)((event[3u] == 0u ? event[8u] : event[3u]) - 0x60u);
    uint8_t *on_deck = audio_ble_attc_state + 0x180u + (uint32_t)connection * 12u;
    if (on_deck[2u] != 0u)
        audio_ble_attc_req_clear_531af2(connection, on_deck, status);
    for (uint8_t slot = 0u; slot < 3u; ++slot) {
        uint8_t *client = (uint8_t *)(uintptr_t)
            ((uintptr_t)audio_ble_attc_state + (uint32_t)connection * 0x84u +
             (uint32_t)slot * 0x2cu - 0x84u);
        if (client[6u] != 0u) {
            WsfTimerStop(client + 0x18u);
            audio_ble_attc_req_clear_531af2(client[0x29u], client + 4u, status);
        }
        ccb[(uint32_t)slot * 4u + 2u] &= (uint8_t)~0x12u;
        uint8_t *sign = *(uint8_t **)(audio_ble_attc_state + 0x1b0u);
        if (sign != 0u) {
            void (*callback)(uint8_t *, uint8_t) =
                *(void (**)(uint8_t *, uint8_t))(sign + 4u);
            callback(client, status);
        }
        audio_ble_attc_write_cmd_callback_530de6(connection, client, status);
    }
}
