/* Cordio HCI LE Set Random Address command, native Main 0x52b4ba. */
#include <stdint.h>
extern uint8_t *hciCmdAlloc(uint16_t opcode,uint8_t length);
extern void hciCmdSend(uint8_t *command);
void HciLeSetRandAddrCmd(const uint8_t *address)
{
    uint8_t *command=hciCmdAlloc(0x2005u,6u);
    if (!command) return;
    for (uint8_t i=0u;i<6u;i++) command[3u+i]=address[i];
    hciCmdSend(command);
}
