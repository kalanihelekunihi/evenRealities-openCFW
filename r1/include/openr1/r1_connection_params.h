#ifndef OPENR1_R1_CONNECTION_PARAMS_H
#define OPENR1_R1_CONNECTION_PARAMS_H

#include <stdbool.h>
#include <stdint.h>

#define R1_CONNECTION_HANDLE_INVALID UINT16_C(0xffff)
#define R1_CONNECTION_FAST_MAX_INTERVAL UINT16_C(50)
#define R1_CONNECTION_RETRY_AFTER_SLOW_MS UINT32_C(4)
#define R1_CONNECTION_RETRY_AFTER_FAST_MS UINT32_C(2000)

typedef enum {
    R1_CONNECTION_SPEED_SLOW = 0,
    R1_CONNECTION_SPEED_FAST = 1
} r1_connection_speed;

typedef struct {
    uint16_t minimum_interval;
    uint16_t maximum_interval;
    uint16_t peripheral_latency;
    uint16_t supervision_timeout;
} r1_connection_parameters;

typedef enum {
    R1_CONNECTION_PARAMETER_ACTION_NONE = 0,
    R1_CONNECTION_PARAMETER_ACTION_CANCEL_RETRY,
    R1_CONNECTION_PARAMETER_ACTION_SCHEDULE_RETRY
} r1_connection_parameter_action_type;

typedef struct {
    r1_connection_parameter_action_type type;
    r1_connection_speed requested_speed;
    uint32_t delay_ms;
} r1_connection_parameter_action;

typedef struct {
    r1_connection_speed requested_speed;
    r1_connection_speed phone_speed;
    r1_connection_speed glasses_speed;
    uint8_t initial_parameter_status;
} r1_connection_parameter_policy;

typedef enum {
    R1_CONNECTION_ROLE_PHONE = 1,
    R1_CONNECTION_ROLE_GLASSES = 2
} r1_connection_role;

typedef enum {
    R1_CONNECTION_ROLE_ASSIGN_INVALID = 0,
    R1_CONNECTION_ROLE_ASSIGN_ASSIGNED,
    R1_CONNECTION_ROLE_ASSIGN_ALREADY_SAME,
    R1_CONNECTION_ROLE_ASSIGN_OCCUPIED,
    R1_CONNECTION_ROLE_ASSIGN_CROSS_ROLE_CONFLICT
} r1_connection_role_assign_status;

typedef struct {
    uint16_t phone;
    uint16_t glasses;
} r1_connection_role_handles;

typedef struct {
    r1_connection_role_assign_status status;
    bool publish_role;
    r1_connection_role published_role;
} r1_connection_role_assign_result;

void r1_connection_parameter_policy_initialize(
    r1_connection_parameter_policy *policy);
r1_connection_speed r1_connection_parameters_speed(
    const r1_connection_parameters *parameters);
void r1_connection_parameters_connected(
    r1_connection_parameter_policy *policy, bool peripheral_role,
    const r1_connection_parameters *parameters);
r1_connection_parameter_action r1_connection_parameters_disconnected(void);
r1_connection_parameter_action r1_connection_parameters_updated(
    r1_connection_parameter_policy *policy, uint16_t connection,
    uint16_t phone_connection, uint16_t glasses_connection,
    const r1_connection_parameters *parameters);
r1_connection_role_assign_result r1_connection_role_assign(
    r1_connection_role_handles *handles, r1_connection_role role,
    uint16_t connection);

#endif
