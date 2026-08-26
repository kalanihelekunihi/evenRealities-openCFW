#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_CORE_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_CORE_H

#include <stdbool.h>
#include <stdint.h>

void *hciCoreConnByHandle(uint16_t handle);
void hciCoreConnAlloc(uint16_t handle);
void hciCoreConnFree(uint16_t handle);
void *hciCoreNextConnFragment(void);
void hciCoreConnOpen(uint16_t handle);
void hciCoreConnClose(uint16_t handle);
bool hciCoreTxAclDataFragmented(void *connection);
bool hciCoreSendAclData(void *connection, uint8_t *data);
bool hciCoreTxReady(uint8_t buffers);
bool hciCoreTxAclStart(void *connection, uint16_t length, uint8_t *data);
bool hciCoreTxAclContinue(void *connection);
void hciCoreTxAclComplete(void *connection, uint8_t *data);
uint8_t *hciCoreAclReassembly(uint8_t *data);
void HciCoreInit(void);
void HciResetSequence(void);
void HciSetMaxRxAclLen(uint16_t length);
void HciSetAclQueueWatermarks(uint8_t high, uint8_t low);
void HciSetLeSupFeat(uint64_t features, bool enable);
void HciSendAclData(uint8_t *data);
void *hciCoreCisByHandle(uint16_t handle);
void hciCoreCisAlloc(uint16_t handle);
void hciCoreCisFree(uint16_t handle);
void hciCoreCisOpen(uint16_t handle);
void hciCoreCisClose(uint16_t handle);

#if defined(OPEN_CFW_HCI_CORE_TEST)
void open_cfw_hci_core_reset_for_test(void);
void open_cfw_hci_core_set_controller_for_test(uint16_t buffer_size, uint8_t buffers);
void open_cfw_hci_core_set_flow_callback_for_test(void (*callback)(uint16_t, bool));
void open_cfw_hci_core_set_queue_empty_for_test(bool empty);
#endif

#endif
