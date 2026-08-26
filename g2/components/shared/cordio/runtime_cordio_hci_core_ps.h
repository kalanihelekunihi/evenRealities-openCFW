#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_CORE_PS_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_CORE_PS_H

#include <stdbool.h>
#include <stdint.h>

typedef void (*open_cfw_hci_acl_callback_t)(uint8_t *data);
typedef void (*open_cfw_hci_iso_callback_t)(uint8_t *data);
typedef void (*open_cfw_hci_flow_callback_t)(uint16_t handle, bool disabled);

void hciCoreInit(void);
void hciCoreNumCmplPkts(uint8_t *message);
void hciCoreRecv(uint8_t message_type, uint8_t *message);
void HciCoreHandler(uint8_t event, void *message);
uint8_t *HciGetBdAddr(void);
uint8_t HciGetWhiteListSize(void);
int8_t HciGetAdvTxPwr(void);
uint16_t HciGetBufSize(void);
uint8_t HciGetNumBufs(void);
uint8_t *HciGetSupStates(void);
uint64_t HciGetLeSupFeat(void);
uint32_t HciGetLeSupFeat32(void);
uint16_t HciGetMaxRxAclLen(void);
uint8_t HciGetResolvingListSize(void);
bool HciLlPrivacySupported(void);
uint16_t HciGetMaxAdvDataLen(void);
uint8_t HciGetNumSupAdvSets(void);
bool HciLeAdvExtSupported(void);
uint8_t HciGetPerAdvListSize(void);
void *HciGetLocalVerInfo(void);

#if defined(OPEN_CFW_HCI_CORE_PS_TEST)
void open_cfw_hci_core_ps_reset_for_test(void);
void open_cfw_hci_core_ps_set_core_u8_for_test(uint16_t offset, uint8_t value);
void open_cfw_hci_core_ps_set_core_u16_for_test(uint16_t offset, uint16_t value);
void open_cfw_hci_core_ps_set_core_u64_for_test(uint16_t offset, uint64_t value);
void open_cfw_hci_core_ps_set_callbacks_for_test(
    open_cfw_hci_acl_callback_t acl,
    open_cfw_hci_flow_callback_t flow,
    open_cfw_hci_iso_callback_t iso);
void open_cfw_hci_core_ps_set_handler_for_test(uint8_t handler_id, bool resetting);
#endif

#endif
