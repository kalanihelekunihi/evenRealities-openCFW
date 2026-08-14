#ifndef OPENR1_BAE8_H
#define OPENR1_BAE8_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_peer_target.h"
#include "openr1/r1_runtime.h"

uint32_t openr1_bae8_initialize(void);
uint32_t openr1_bae8_last_error(void);
r1_tx_status openr1_bae8_transmit(const r1_tx_event *event);
uint32_t openr1_bae8_request_phy_update(
    uint16_t connection, uint8_t transmit_phy, uint8_t receive_phy);
/* The peer address captured from the GAP connected event for a live link;
 * false when the link is unknown. */
bool openr1_bae8_peer_address(
    uint16_t connection, uint8_t address[R1_PEER_ADDRESS_SIZE]);

#endif
