/* Native SmpDmLescEnabled 0x537c30 and HciLeLtkReqNegReplCmd 0x52b2a4. */
#include <stdint.h>

extern uint8_t *smpCcbByConnId(uint8_t);
extern void *audio_ble_hci_cmd_alloc_52ae38(uint16_t, uint16_t);
extern void audio_ble_hci_cmd_send(void *);

uint8_t audio_ble_smp_lesc_enabled_537c30(uint8_t conn_id)
{
    uint8_t *const ccb = smpCcbByConnId(conn_id);
    if (ccb == 0) return 0u;
    uint8_t *const sc = *(uint8_t **)(void *)(ccb + 0x48u);
    return sc == 0 ? 0u : sc[0u];
}

void HciLeLtkReqNegReplCmd(uint16_t handle)
{
    uint8_t *const command = (uint8_t *)audio_ble_hci_cmd_alloc_52ae38(0x201bu, 2u);
    if (command == 0) return;
    command[3u] = (uint8_t)handle;
    command[4u] = (uint8_t)(handle >> 8);
    audio_ble_hci_cmd_send(command);
}
