/* Cordio attcProcMtuRsp at stock Main 0x4b527a. */
#include <stdint.h>

extern uint8_t audio_ble_att_cfg_ptr_200004b4[4];
extern uint16_t audio_ble_hci_max_rx_acl_len_530d4c(void);
extern void audio_ble_att_set_mtu_4b503c(uint8_t *, uint8_t, uint16_t, uint16_t);

void audio_attc_rsp_mtu_4b527a(uint8_t *ccb, uint16_t length,
                               const uint8_t *packet, void *event)
{
    (void)length;
    (void)event;
    uint16_t peer = (uint16_t)packet[9u] | ((uint16_t)packet[10u] << 8);
    if (peer < 247u)
        peer = 247u;
    const uint16_t acl = audio_ble_hci_max_rx_acl_len_530d4c();
    const int32_t maximum = (int32_t)acl - 4;
    const uint32_t config_address =
        *(const uint32_t *)(const void *)audio_ble_att_cfg_ptr_200004b4;
    const uint8_t *config = (const uint8_t *)(uintptr_t)config_address;
    const uint16_t configured =
        (uint16_t)config[4u] | ((uint16_t)config[5u] << 8);
    const uint16_t local = (int32_t)configured < maximum
        ? configured
        : (uint16_t)(audio_ble_hci_max_rx_acl_len_530d4c() - 4u);
    uint8_t *main_ccb = *(uint8_t **)ccb;
    audio_ble_att_set_mtu_4b503c(main_ccb, ccb[0x28u], peer, local);
}
