/* Cordio dual-chip resolving-list and privacy-mode HCI commands, 0x52b744..0x52b84c. */
#include <stddef.h>
#include <stdint.h>

extern uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t length);
extern void hciCmdSend(uint8_t *command);
extern void *memcpy(void *dest, const void *src, size_t length);

void HciLeAddDeviceToResolvingListCmd(uint8_t type, const uint8_t *address,
                                      const uint8_t *peer_irk, const uint8_t *local_irk)
{
    uint8_t *const command = hciCmdAlloc(0x2027u, 39u);
    if (command != 0) {
        command[3u] = type;
        (void)memcpy(command + 4u, address, 6u);
        (void)memcpy(command + 10u, peer_irk, 16u);
        (void)memcpy(command + 26u, local_irk, 16u);
        hciCmdSend(command);
    }
}

void HciLeRemoveDeviceFromResolvingList(uint8_t type, const uint8_t *address)
{
    uint8_t *const command = hciCmdAlloc(0x2028u, 7u);
    if (command != 0) {
        command[3u] = type;
        (void)memcpy(command + 4u, address, 6u);
        hciCmdSend(command);
    }
}

void HciLeClearResolvingList(void)
{
    uint8_t *const command = hciCmdAlloc(0x2029u, 0u);
    if (command != 0) hciCmdSend(command);
}

void HciLeSetPrivacyModeCmd(uint8_t type, uint8_t *address, uint8_t mode)
{
    uint8_t *const command = hciCmdAlloc(0x204eu, 8u);
    if (command != 0) {
        command[3u] = type;
        (void)memcpy(command + 4u, address, 6u);
        command[10u] = mode;
        hciCmdSend(command);
    }
}
