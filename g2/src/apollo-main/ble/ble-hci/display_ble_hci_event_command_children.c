/* Native hciEvtProcessCmdStatus 0x56b150 and hciCoreNumCmplPkts 0x530c08. */
#include <stdint.h>
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live 0x20073870 */
extern uint8_t audio_ble_hci_controller_state_20071478[]; /* live 0x20071478 */
extern uint8_t *audio_ble_hci_conn_by_handle(uint16_t); /* selected 0x52a704 */
extern void audio_ble_hci_cmd_status_failure(uint32_t,uint32_t); /* 0x56b100 */
extern void audio_ble_hci_cmd_receive_complete(uint32_t); /* 0x52aef8 */
extern void audio_ble_hci_tx_ready(uint8_t); /* 0x52a79e */

static uint16_t rd16(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
void audio_ble_hci_event_cmd_status(const void *parameters) {
    const uint8_t *p=(const uint8_t *)parameters;
    if(p[0]!=0u)audio_ble_hci_cmd_status_failure(p[0],rd16(p+2u));
    audio_ble_hci_cmd_receive_complete(p[1]);
}
