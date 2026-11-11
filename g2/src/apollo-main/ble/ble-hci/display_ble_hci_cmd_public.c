/* Native canonical hciCmdSend 0x52ae5e entry. The send body is
 * audio_ble_hci_cmd_send_body in display_ble_hci_cmd_send.c (sources.json
 * aliases audio_ble_hci_cmd_send -> hciCmdSend). The stock entry left the
 * caller's R1-R3 in place; the body ignores R1/R3 and uses R2 only as the high
 * word of its return value, which no hciCmdSend caller reads. */
#include <stdint.h>
extern uint64_t audio_ble_hci_cmd_send_body(void *,uint32_t,uint32_t,uint32_t);
void hciCmdSend(uint8_t *message)
{
    (void)audio_ble_hci_cmd_send_body(message,0u,0u,0u);
}
