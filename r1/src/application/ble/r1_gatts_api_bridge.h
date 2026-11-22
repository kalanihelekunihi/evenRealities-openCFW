#ifndef R1_GATTS_API_BRIDGE_H
#define R1_GATTS_API_BRIDGE_H

#include <stdbool.h>
#include <stdint.h>
#include "ble.h"

void r1_cordio_gatts_api_bind(
    uint8_t (*conn_id)(uint16_t),
    uint32_t (*uuid_encode)(const ble_uuid_t *, uint8_t *, uint8_t *),
    bool (*tx_event)(uint8_t, uint16_t, bool, bool));

#endif
