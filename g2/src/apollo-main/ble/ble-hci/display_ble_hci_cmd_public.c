/* Native hciCmdAlloc 0x52ae38 and canonical hciCmdSend 0x52ae5e entry.
 * The send body is already source-defined as audio_ble_hci_cmd_send with
 * actual ARM C/native PASS5; this branch preserves its four entry registers. */
#include <stdint.h>
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void audio_ble_hci_cmd_send(void *message);
uint8_t *hciCmdAlloc(uint16_t opcode,uint8_t parameter_length)
{
    uint8_t *command=WsfMsgAlloc((uint16_t)(parameter_length+3u));
    if (!command) return 0;
    command[0u]=(uint8_t)opcode;
    command[1u]=(uint8_t)(opcode>>8u);
    command[2u]=parameter_length;
    return command;
}
__attribute__((naked)) void hciCmdSend(uint8_t *message __attribute__((unused)))
{
    __asm volatile("b audio_ble_hci_cmd_send");
}
