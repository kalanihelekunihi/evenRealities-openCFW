/* Three zero-initialized SDK instances: observer pointers and native init loop
 * authenticate 0x20007e40/4c/58 and a 12-byte stride. Initialization of the
 * error callback remains the caller's responsibility. */
#include "nrf_ble_qwr.h"
nrf_ble_qwr_t r1_ble_qwr_context_a __attribute__((section(".r1.qwr.a")));
nrf_ble_qwr_t r1_ble_qwr_context_b __attribute__((section(".r1.qwr.b")));
nrf_ble_qwr_t r1_ble_qwr_context_c __attribute__((section(".r1.qwr.c")));
