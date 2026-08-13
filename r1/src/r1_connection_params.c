#include "openr1/r1_connection_params.h"

#include <stddef.h>

void r1_connection_parameter_policy_initialize(
    r1_connection_parameter_policy *policy) {
    if (policy == NULL) {
        return;
    }
    policy->requested_speed = R1_CONNECTION_SPEED_SLOW;
    policy->phone_speed = R1_CONNECTION_SPEED_SLOW;
    policy->glasses_speed = R1_CONNECTION_SPEED_SLOW;
    policy->initial_parameter_status = UINT8_MAX;
}

r1_connection_speed r1_connection_parameters_speed(
    const r1_connection_parameters *parameters) {
    return parameters != NULL &&
        parameters->maximum_interval < R1_CONNECTION_FAST_MAX_INTERVAL
        ? R1_CONNECTION_SPEED_FAST : R1_CONNECTION_SPEED_SLOW;
}

void r1_connection_parameters_connected(
    r1_connection_parameter_policy *policy, bool peripheral_role,
    const r1_connection_parameters *parameters) {
    if (policy == NULL || parameters == NULL || !peripheral_role) {
        return;
    }
    policy->requested_speed = r1_connection_parameters_speed(parameters);
    policy->phone_speed = R1_CONNECTION_SPEED_FAST;
    policy->glasses_speed = R1_CONNECTION_SPEED_FAST;

    const bool recognized_initial_pair =
        (parameters->minimum_interval == 39u &&
         parameters->maximum_interval == 39u) ||
        (parameters->minimum_interval == 36u &&
         parameters->maximum_interval == 36u);
    if (recognized_initial_pair && policy->initial_parameter_status == UINT8_MAX) {
        policy->initial_parameter_status = 1u;
    }
}

r1_connection_parameter_action r1_connection_parameters_disconnected(void) {
    return (r1_connection_parameter_action){
        .type = R1_CONNECTION_PARAMETER_ACTION_CANCEL_RETRY,
        .requested_speed = R1_CONNECTION_SPEED_SLOW,
        .delay_ms = 0u,
    };
}

r1_connection_parameter_action r1_connection_parameters_updated(
    r1_connection_parameter_policy *policy, uint16_t connection,
    uint16_t phone_connection, uint16_t glasses_connection,
    const r1_connection_parameters *parameters) {
    r1_connection_parameter_action action = {
        .type = R1_CONNECTION_PARAMETER_ACTION_NONE,
        .requested_speed = R1_CONNECTION_SPEED_SLOW,
        .delay_ms = 0u,
    };
    if (policy == NULL || parameters == NULL) {
        return action;
    }

    const r1_connection_speed actual =
        r1_connection_parameters_speed(parameters);
    if (actual == policy->requested_speed) {
        if (connection == glasses_connection) {
            policy->glasses_speed = actual;
        } else if (connection == phone_connection) {
            policy->phone_speed = actual;
        }
        return action;
    }

    action.type = R1_CONNECTION_PARAMETER_ACTION_SCHEDULE_RETRY;
    action.requested_speed = policy->requested_speed;
    action.delay_ms = actual == R1_CONNECTION_SPEED_SLOW
        ? R1_CONNECTION_RETRY_AFTER_SLOW_MS
        : R1_CONNECTION_RETRY_AFTER_FAST_MS;
    return action;
}

r1_connection_role_assign_result r1_connection_role_assign(
    r1_connection_role_handles *handles, r1_connection_role role,
    uint16_t connection) {
    r1_connection_role_assign_result result = {
        .status = R1_CONNECTION_ROLE_ASSIGN_INVALID,
        .publish_role = false,
        .published_role = role,
    };
    if (handles == NULL ||
        (role != R1_CONNECTION_ROLE_PHONE &&
         role != R1_CONNECTION_ROLE_GLASSES) ||
        connection == R1_CONNECTION_HANDLE_INVALID) {
        return result;
    }
    uint16_t *target = role == R1_CONNECTION_ROLE_PHONE
        ? &handles->phone : &handles->glasses;
    const uint16_t other = role == R1_CONNECTION_ROLE_PHONE
        ? handles->glasses : handles->phone;
    if (other != R1_CONNECTION_HANDLE_INVALID && other == connection) {
        result.status = R1_CONNECTION_ROLE_ASSIGN_CROSS_ROLE_CONFLICT;
    } else if (*target == R1_CONNECTION_HANDLE_INVALID) {
        *target = connection;
        result.status = R1_CONNECTION_ROLE_ASSIGN_ASSIGNED;
        result.publish_role = true;
    } else if (*target == connection) {
        result.status = R1_CONNECTION_ROLE_ASSIGN_ALREADY_SAME;
    } else {
        result.status = R1_CONNECTION_ROLE_ASSIGN_OCCUPIED;
    }
    return result;
}
