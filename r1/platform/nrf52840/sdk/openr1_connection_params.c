#include "openr1_connection_params.h"

#include <stddef.h>

#include "ble.h"
#include "nrf_error.h"

/* The four public Nordic parameter records recovered at application address
 * 0x0009917a. FAST_A and FAST_B are distinct stock selections even though this
 * image stores identical values for them. */
static const ble_gap_conn_params_t connection_parameter_sets[] = {
    [R1_CONNECTION_PARAMETER_SET_DEFAULT] = {
        .min_conn_interval = 72u,
        .max_conn_interval = 84u,
        .slave_latency = 4u,
        .conn_sup_timeout = 600u,
    },
    [R1_CONNECTION_PARAMETER_SET_FAST_A] = {
        .min_conn_interval = 12u,
        .max_conn_interval = 24u,
        .slave_latency = 4u,
        .conn_sup_timeout = 600u,
    },
    [R1_CONNECTION_PARAMETER_SET_FAST_B] = {
        .min_conn_interval = 12u,
        .max_conn_interval = 24u,
        .slave_latency = 4u,
        .conn_sup_timeout = 600u,
    },
    [R1_CONNECTION_PARAMETER_SET_GLASSES] = {
        .min_conn_interval = 16u,
        .max_conn_interval = 16u,
        .slave_latency = 2u,
        .conn_sup_timeout = 600u,
    },
};

uint32_t openr1_connection_parameter_mode_apply(
    uint16_t connection, uint16_t phone_connection,
    uint16_t glasses_connection, uint8_t requested_mode,
    uint8_t current_phone_mode, bool glasses_fast_active,
    bool alternate_fast_profile, r1_connection_parameter_mode_plan *applied) {
    r1_connection_parameter_mode_plan local;
    r1_connection_parameter_mode_plan *const plan =
        applied == NULL ? &local : applied;
    const r1_error plan_error = r1_connection_parameter_mode_adapter(
        connection, phone_connection, glasses_connection, requested_mode,
        current_phone_mode, glasses_fast_active, alternate_fast_profile, plan);
    if (plan_error != R1_OK) {
        return NRF_ERROR_INVALID_PARAM;
    }
    if (!plan->set_preferred || !plan->request_update) {
        return NRF_SUCCESS;
    }

    const ble_gap_conn_params_t *const parameters =
        &connection_parameter_sets[plan->parameter_set];
    uint32_t error = sd_ble_gap_ppcp_set(parameters);
    if (error == NRF_SUCCESS) {
        error = sd_ble_gap_conn_param_update(connection, parameters);
    }
    return error;
}
