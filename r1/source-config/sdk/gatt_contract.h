#ifndef R1_GATT_CONTRACT_H
#define R1_GATT_CONTRACT_H
#include <stddef.h>
#include "sdk_common.h"
/* Native init 0x78186 writes 247/247/251 and loops three 8-byte records.
 * Only the link sum is authenticated here. The inherited 3/0 role split
 * remains a historical candidate, not a recovered SoftDevice configuration. */
#undef NRF_SDH_BLE_GATT_MAX_MTU_SIZE
#define NRF_SDH_BLE_GATT_MAX_MTU_SIZE 247
#undef NRF_SDH_BLE_GAP_DATA_LENGTH
#define NRF_SDH_BLE_GAP_DATA_LENGTH 251
/* Native connected path has no initial MTU request. Remaining product
 * connected/data-length behavior differs and this SDK observer is unselected. */
#undef NRF_BLE_GATT_MTU_EXCHANGE_INITIATION_ENABLED
#define NRF_BLE_GATT_MTU_EXCHANGE_INITIATION_ENABLED 0
#include "nrf_ble_gatt.h"
_Static_assert(NRF_BLE_GATT_LINK_COUNT==3,"native aggregate link count");
_Static_assert(sizeof(nrf_ble_gatt_link_t)==8,"native link stride");
_Static_assert(sizeof(nrf_ble_gatt_t)==36,"native context span");
_Static_assert(offsetof(nrf_ble_gatt_t,links)==6,"native links base");
_Static_assert(offsetof(nrf_ble_gatt_t,evt_handler)==32,"native callback");
#endif
