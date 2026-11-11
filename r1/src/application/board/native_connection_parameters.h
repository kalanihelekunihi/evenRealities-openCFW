#ifndef R1_NATIVE_CONNECTION_PARAMETERS_H
#define R1_NATIVE_CONNECTION_PARAMETERS_H
#include <stdint.h>
#include "ble_gap.h"
#include "native_ble_identity.h"
/* Native0x200064be..bf; profile byte0x200064c0 belongs to the GAP owner. */
extern volatile uint8_t r1_connection_parameter_flags[2];
extern volatile uint8_t r1_connection_parameter_fast;
extern const ble_gap_conn_params_t r1_gap_preferred_parameter_profiles[2];
extern const ble_gap_conn_params_t r1_connection_slow_parameters;
extern const ble_gap_conn_params_t r1_connection_glasses_parameters;
void r1_connection_parameter_mode_adapter(uint32_t,uint32_t);
void r1_app_ble_set_fast_mode_delayed(uint32_t);
void r1_app_ble_set_fast_mode(uint32_t);
void r1_app_ble_set_slow_mode(uint32_t,uint32_t);
void r1_app_ble_set_slow_mode_again(uint32_t);
uint32_t r1_ble_control_flag_get(void);
uint32_t r1_ble_control_flag_set(uint32_t);
#endif
