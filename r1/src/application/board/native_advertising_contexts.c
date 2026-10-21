/* Typed compatible Nordic advertising storage. Observer pointers authenticate
 * the bases; init/observer/start field accesses and cold initialization bound
 * the compatible spans. Product mode/callback initialization remains a gate. */
#include "ble_advertising.h"
ble_advertising_t r1_ble_advertising_context_a __attribute__((section(".r1.advertising.a")));
ble_advertising_t r1_ble_advertising_context_b __attribute__((section(".r1.advertising.b")));
