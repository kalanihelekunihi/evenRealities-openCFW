/* Cordio HCI LE Set Address Resolution Enable, native Thumb 0x52b7f6. */
#include <stdint.h>

extern uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t length);
extern void hciCmdSend(uint8_t *command);

void HciLeSetAddrResolutionEnable(uint8_t enable)
{
    uint8_t *const command = hciCmdAlloc(0x202du, 1u);
    if (command != 0) {
        command[3u] = enable;
        hciCmdSend(command);
    }
}
