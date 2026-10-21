#ifndef R1_ADVERTISING_INIT_CONTRACT_H
#define R1_ADVERTISING_INIT_CONTRACT_H
#include "advertising_contract.h"
_Static_assert(sizeof(ble_advdata_t)==60,"native advertising input");
_Static_assert(sizeof(ble_advertising_init_t)==172,"native init input");
_Static_assert(offsetof(ble_advertising_init_t,config)==120,"native config input");
_Static_assert(offsetof(ble_advertising_init_t,evt_handler)==164,"native event input");
_Static_assert(offsetof(ble_advertising_init_t,error_handler)==168,"native error input");
_Static_assert(offsetof(ble_advdata_t,include_ble_device_addr)==45,"native device address field");
_Static_assert(offsetof(ble_advdata_t,p_manuf_specific_data)==36,"native manufacturer pointer");
_Static_assert(sizeof(ble_advdata_manuf_data_t)==12 && sizeof(ble_advdata_service_data_t)==12,"native data entries");
#endif
