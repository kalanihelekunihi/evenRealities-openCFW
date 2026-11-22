#ifndef R1_ADV_BRIDGE_H
#define R1_ADV_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>
#include "ble_gap.h"

void r1_cordio_adv_connected(ble_gap_evt_connected_t *event);
void r1_cordio_adv_started(uint8_t status);
void r1_cordio_adv_stopped(uint8_t status);
bool r1_cordio_adv_is_idle(void);
void r1_cordio_adv_set_stop_wait(bool (*wait_for_stop)(void));
void r1_cordio_adv_set_hooks(
    bool (*terminated)(uint8_t reason, const ble_gap_adv_data_t *data),
    uint16_t (*hci_handle)(uint16_t nordic_handle));
bool r1_cordio_event_adv_terminated(uint8_t reason,
                                    const ble_gap_adv_data_t *data);

#endif
