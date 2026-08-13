#ifndef OPENR1_CONNECTION_PARAMS_PORT_H
#define OPENR1_CONNECTION_PARAMS_PORT_H

#include <stdbool.h>
#include <stdint.h>

#include "openr1/r1_connection_params.h"

uint32_t openr1_connection_parameter_mode_apply(
    uint16_t connection, uint16_t phone_connection,
    uint16_t glasses_connection, uint8_t requested_mode,
    uint8_t current_phone_mode, bool glasses_fast_active,
    bool alternate_fast_profile, r1_connection_parameter_mode_plan *applied);

#endif
