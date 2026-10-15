#ifndef R1_QWR_CONTRACT_H
#define R1_QWR_CONTRACT_H
#include <stddef.h>
#include "nrf_ble_qwr.h"
_Static_assert(NRF_BLE_QWR_MAX_ATTR == 0, "native queued-write attribute policy");
_Static_assert(sizeof(nrf_ble_qwr_t) == 12, "native queued-write instance stride");
_Static_assert(sizeof(nrf_ble_qwr_init_t) == 4, "native initializer width");
_Static_assert(offsetof(nrf_ble_qwr_t,conn_handle)==2, "native handle");
_Static_assert(offsetof(nrf_ble_qwr_t,error_handler)==4, "native callback");
_Static_assert(offsetof(nrf_ble_qwr_t,is_user_mem_reply_pending)==8, "native pending flag");
#endif
