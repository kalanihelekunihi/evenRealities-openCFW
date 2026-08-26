#ifndef OPEN_CFW_RUNTIME_CORDIO_HCI_EVT_H
#define OPEN_CFW_RUNTIME_CORDIO_HCI_EVT_H

#include <stdint.h>
#include "hci_api.h"

typedef struct {
    uint32_t received;
    uint32_t delivered;
    uint32_t malformed;
    uint32_t unknown;
} open_cfw_hci_evt_stats_t;

void hciEvtProcessCmdStatus(uint8_t *data);
void hciEvtProcessCmdCmpl(uint8_t *data, uint8_t length);
void hciEvtProcessMsg(uint8_t *event);
void hciEvtCmdStatusFailure(uint8_t status, uint16_t opcode);
open_cfw_hci_evt_stats_t *hciEvtGetStats(void);

#if defined(OPEN_CFW_HCI_EVT_TEST)
void open_cfw_hci_evt_reset_for_test(void);
void open_cfw_hci_evt_set_callback_for_test(hciEvtCback_t callback);
#endif

#endif
