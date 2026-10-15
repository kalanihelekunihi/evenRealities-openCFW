#ifndef R1_ADVERTISING_CONTRACT_H
#define R1_ADVERTISING_CONTRACT_H
#include <stddef.h>
#include "ble_advertising.h"
_Static_assert(sizeof(ble_adv_mode_t)==1,"native byte mode");
_Static_assert(sizeof(ble_adv_modes_config_t)==44,"native mode config copy");
_Static_assert(sizeof(ble_advertising_t)==1076,"native compatible advertising storage");
_Static_assert(offsetof(ble_advertising_t,adv_modes_config)==4,"native config");
_Static_assert(offsetof(ble_advertising_t,conn_cfg_tag)==48,"native config tag");
_Static_assert(offsetof(ble_advertising_t,evt_handler)==52,"native event callback");
_Static_assert(offsetof(ble_advertising_t,error_handler)==56,"native error callback");
_Static_assert(offsetof(ble_advertising_t,adv_params)==60,"native params");
_Static_assert(offsetof(ble_advertising_t,adv_handle)==84,"native adv handle");
_Static_assert(offsetof(ble_advertising_t,adv_data)==1040,"native data buffers");
_Static_assert(offsetof(ble_advertising_t,p_adv_data)==1056,"native data pointer");
_Static_assert(offsetof(ble_advertising_t,current_slave_link_conn_handle)==1060,"native connection");
_Static_assert(offsetof(ble_advertising_t,peer_address)==1062,"native peer address");
_Static_assert(offsetof(ble_advertising_t,whitelist_temporarily_disabled)==1070,"native whitelist flag");
#endif
