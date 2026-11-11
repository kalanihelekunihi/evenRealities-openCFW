#ifndef R1_NATIVE_BLE_CONNECTION_CONTROL_H
#define R1_NATIVE_BLE_CONNECTION_CONTROL_H
#include <stdint.h>
void r1_ble_connection_control_event_consumer(void);
/* Native0x4e1e2 is empty, but its address remains a shared scheduler key. */
void r1_legacy_pair_timeout_callback(uint32_t);
#endif
