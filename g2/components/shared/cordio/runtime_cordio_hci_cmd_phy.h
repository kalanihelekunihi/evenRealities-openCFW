#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_CMD_PHY_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_CMD_PHY_H

#include <stdint.h>

void HciLeReadPhyCmd(uint16_t handle);
void HciLeSetDefaultPhyCmd(uint8_t all_phys, uint8_t tx_phys, uint8_t rx_phys);
void HciLeSetPhyCmd(
    uint16_t handle,
    uint8_t all_phys,
    uint8_t tx_phys,
    uint8_t rx_phys,
    uint16_t phy_options);

#endif
