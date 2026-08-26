#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_VS_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_VS_H

#include <stdint.h>

void hciCoreReadResolvingListSize(void);
void hciCoreReadMaxDataLen(void);
void hciCoreResetStart(void);
void hciCoreResetSequence(uint8_t *message);
uint8_t hciCoreVsCmdCmplRcvd(uint16_t opcode, uint8_t *message, uint8_t length);
uint8_t hciCoreVsEvtRcvd(uint8_t *message, uint8_t length);
uint8_t hciCoreHwErrorRcvd(uint8_t *message);
void HciVsInit(uint8_t parameter);

#if defined(OPEN_CFW_HCI_VS_TEST)
void open_cfw_hci_vs_reset_for_test(void);
uint8_t *open_cfw_hci_vs_core_for_test(void);
uint8_t *open_cfw_hci_vs_hci_cb_for_test(void);
void open_cfw_hci_vs_set_features_for_test(uint64_t configured, uint64_t controller);
void open_cfw_hci_vs_set_callbacks_for_test(
    void (*reset)(void *), void (*extended)(const uint8_t *, uint16_t));
#endif

#endif
