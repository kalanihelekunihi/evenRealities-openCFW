/* Native HciLeReadRemoteFeatCmd 0x52b352, attributed Cordio hci_cmd.c. */
#include <stdint.h>

extern uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t parameter_length);
extern void hciCmdSend(uint8_t *command);

void HciLeReadRemoteFeatCmd(uint16_t handle)
{
    uint8_t *command = hciCmdAlloc(0x2016u, 2u);
    if (command == 0) return;
    command[3u] = (uint8_t)handle;
    command[4u] = (uint8_t)(handle >> 8u);
    hciCmdSend(command);
}
