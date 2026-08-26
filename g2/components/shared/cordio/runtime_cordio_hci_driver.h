#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_DRIVER_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

typedef void (*open_cfw_hci_driver_error_handler_t)(uint32_t status);

uint32_t HciDrvRadioBoot(bool cold_boot);
void HciDrvRadioShutdown(void);
void HciDrvShutdown(void);
uint16_t hciDrvWrite(uint8_t type, uint16_t length, uint8_t *data);
void HciDrvHandlerInit(uint8_t handler_id);
void HciDrvIntService(void);
void HciDrvHandler(uint8_t event_mask, void *message);
void HciDrvErrorHandlerSet(open_cfw_hci_driver_error_handler_t handler);
void HciVscUpdateNvdsParam(void);
bool HciVscSetRfPowerLevelEx(int8_t power_dbm);
void HciVscConstantTransmission(uint8_t channel);
bool HciVscSetCustom_BDAddr(uint8_t *address);
void HciVscUpdateBDAddress(void);
void HciVscCarrierWaveMode(uint8_t channel);
void HciDrvBleSleepSet(bool enable);
void HciDrvEmptyWriteQueue(void);

#if defined(OPEN_CFW_HCI_DRIVER_TEST)
void open_cfw_hci_driver_reset_for_test(void);
uint32_t open_cfw_hci_driver_error_for_test(void);
uint8_t *open_cfw_hci_driver_mac_for_test(void);
uint8_t *open_cfw_hci_driver_nvds_for_test(void);
uint32_t open_cfw_hci_driver_interrupts_for_test(void);
#endif

#endif
