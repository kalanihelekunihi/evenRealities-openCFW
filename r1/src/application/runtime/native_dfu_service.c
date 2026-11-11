/* The reconstructed priority-2 table owns the stock DFU BLE registration.
 * Compile the pinned service once without its additional observer record;
 * all SDK functions and its private initialized service state remain here. */
#include "nrf_sdh_ble.h"
#undef NRF_SDH_BLE_OBSERVER
#define NRF_SDH_BLE_OBSERVER(...)
#include "ble_dfu.c"
