/* The reconstructed observer table owns the stock registration. Export the
 * pinned SDK callback itself; do not emit its second registration record.
 * See r1/docs/reference/peer-observer-review.md for bounded validation. */
#include "nrf_sdh_ble.h"
#undef NRF_SDH_BLE_OBSERVER
#define NRF_SDH_BLE_OBSERVER(...)
#include "peer_manager.c"
extern __typeof__(ble_evt_handler) r1_sdk_peer_manager_event
 __attribute__((alias("ble_evt_handler")));
_Static_assert(sizeof(pm_evt_t)==20 && PM_MAX_REGISTRANTS==3,
 "stock peer-manager event and subscriber count");
