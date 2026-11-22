#ifndef R1_BOOTLOADER_CORDIO_BLE_EVENTS_H
#define R1_BOOTLOADER_CORDIO_BLE_EVENTS_H

#include <stdbool.h>
#include <stdint.h>

/* Called in WSF context by the future lower-flash DFU event adapter. */
bool r1_bootloader_ble_event_publish(const void *event, uint16_t length);

#endif
