/*************************************************************************************************/
/*
 * Apache-2.0 Cordio HCI PHY command wrappers.
 *
 * Behavior and public ABI are from Packetcraft Cordio r20.05c
 * hci_cmd_phy.c.  Serialization is written explicitly so this maintained
 * translation unit has no dependency on Cordio's macro-only bstream header.
 */
/*************************************************************************************************/

#include "runtime_cordio_hci_cmd_phy.h"

#define OPEN_CFW_HCI_CMD_HEADER_BYTES       3u
#define OPEN_CFW_HCI_OPCODE_LE_READ_PHY     0x2030u
#define OPEN_CFW_HCI_OPCODE_LE_SET_DEF_PHY  0x2031u
#define OPEN_CFW_HCI_OPCODE_LE_SET_PHY      0x2032u

extern uint8_t *hciCmdAlloc(uint16_t opcode, uint8_t parameter_bytes);
extern void hciCmdSend(uint8_t *buffer);

static void open_cfw_hci_put_u16(uint8_t **cursor, uint16_t value)
{
    (*cursor)[0] = (uint8_t)value;
    (*cursor)[1] = (uint8_t)(value >> 8);
    *cursor += 2;
}

void HciLeReadPhyCmd(uint16_t handle)
{
    uint8_t *buffer = hciCmdAlloc(OPEN_CFW_HCI_OPCODE_LE_READ_PHY, 2u);
    uint8_t *cursor;

    if (buffer == (uint8_t *)0) {
        return;
    }
    cursor = buffer + OPEN_CFW_HCI_CMD_HEADER_BYTES;
    open_cfw_hci_put_u16(&cursor, handle);
    hciCmdSend(buffer);
}

void HciLeSetDefaultPhyCmd(uint8_t all_phys, uint8_t tx_phys, uint8_t rx_phys)
{
    uint8_t *buffer = hciCmdAlloc(OPEN_CFW_HCI_OPCODE_LE_SET_DEF_PHY, 3u);
    uint8_t *cursor;

    if (buffer == (uint8_t *)0) {
        return;
    }
    cursor = buffer + OPEN_CFW_HCI_CMD_HEADER_BYTES;
    *cursor++ = all_phys;
    *cursor++ = tx_phys;
    *cursor = rx_phys;
    hciCmdSend(buffer);
}

void HciLeSetPhyCmd(
    uint16_t handle,
    uint8_t all_phys,
    uint8_t tx_phys,
    uint8_t rx_phys,
    uint16_t phy_options)
{
    uint8_t *buffer = hciCmdAlloc(OPEN_CFW_HCI_OPCODE_LE_SET_PHY, 7u);
    uint8_t *cursor;

    if (buffer == (uint8_t *)0) {
        return;
    }
    cursor = buffer + OPEN_CFW_HCI_CMD_HEADER_BYTES;
    open_cfw_hci_put_u16(&cursor, handle);
    *cursor++ = all_phys;
    *cursor++ = tx_phys;
    *cursor++ = rx_phys;
    open_cfw_hci_put_u16(&cursor, phy_options);
    hciCmdSend(buffer);
}
