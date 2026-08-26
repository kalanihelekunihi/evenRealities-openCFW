#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_TR_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_TR_H

#include <stdbool.h>
#include <stdint.h>

/*
 * The first argument is the HCI ACL transmit context.  The Ambiq transport
 * does not inspect it, but it is part of the caller ABI and must be retained.
 */
uint16_t hciTrSendAclData(void *context, const uint8_t *data);
bool hciTrSendCmd(const uint8_t *data);
uint16_t hciTrSerialRxIncoming(const uint8_t *data, uint16_t length);
bool hciTrReceivingPacket(void);

#if defined(OPEN_CFW_HCI_TR_TEST)
void open_cfw_hci_tr_reset_for_test(void);
#endif

#endif
