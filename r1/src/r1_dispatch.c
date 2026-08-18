#include "openr1/r1_dispatch.h"

typedef enum {
    RESULT_SUCCESS = 0,
    RESULT_ERROR = 1,
    RESULT_REFUSE = 2,
    RESULT_NOT_SUPPORTED = 3
} result_code;

static uint16_t read_u16(const uint8_t *input) {
    return (uint16_t)((uint16_t)input[0] | (uint16_t)((uint16_t)input[1] << 8u));
}

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0]
        | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u)
        | ((uint32_t)input[3] << 24u);
}

static void copy_bytes(uint8_t *output, const uint8_t *input, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = input[index];
    }
}

static r1_health_settings_record health_settings_record(
    const uint8_t bytes[12]) {
    const r1_health_settings_record record = {
        .timestamp_seconds = read_u32(bytes),
        .enabled = (uint8_t)(bytes[4] != 0u),
        .reserved = {0u},
    };
    return record;
}

static void health_settings_bytes(
    const r1_health_settings_record *record, uint8_t bytes[12]) {
    bytes[0] = (uint8_t)record->timestamp_seconds;
    bytes[1] = (uint8_t)(record->timestamp_seconds >> 8u);
    bytes[2] = (uint8_t)(record->timestamp_seconds >> 16u);
    bytes[3] = (uint8_t)(record->timestamp_seconds >> 24u);
    bytes[4] = (uint8_t)(record->enabled != 0u);
    for (size_t index = 5u; index < 12u; ++index) {
        bytes[index] = 0u;
    }
}

static r1_legacy_command_route legacy_route(uint8_t opcode) {
    switch (opcode) {
        case 0x11u: return R1_LEGACY_COMMAND_ROUTE_0X11;
        case 0x12u: return R1_LEGACY_COMMAND_ROUTE_0X12;
        case 0x21u: return R1_LEGACY_COMMAND_ROUTE_0X21;
        case 0x22u: return R1_LEGACY_COMMAND_ROUTE_0X22;
        case 0x23u: return R1_LEGACY_COMMAND_ROUTE_0X23;
        case 0x24u: return R1_LEGACY_COMMAND_ROUTE_0X24;
        case 0x34u: return R1_LEGACY_COMMAND_ROUTE_0X34;
        case 0x37u: return R1_LEGACY_COMMAND_ROUTE_0X37;
        case 0x40u: return R1_LEGACY_COMMAND_ROUTE_0X40;
        case 0x52u: return R1_LEGACY_COMMAND_ROUTE_0X52;
        case 0x53u: return R1_LEGACY_COMMAND_ROUTE_0X53;
        case 0x54u: return R1_LEGACY_COMMAND_ROUTE_0X54;
        case 0x55u: return R1_LEGACY_COMMAND_ROUTE_0X55;
        case 0x56u: return R1_LEGACY_COMMAND_ROUTE_0X56;
        case 0x57u: return R1_LEGACY_COMMAND_ROUTE_0X57;
        case 0x85u: return R1_LEGACY_COMMAND_ROUTE_0X85;
        case 0x88u: return R1_LEGACY_COMMAND_ROUTE_PAIR_AUTH_0X88;
        case 0x89u: return R1_LEGACY_COMMAND_ROUTE_0X89;
        case 0x8au: return R1_LEGACY_COMMAND_ROUTE_0X8A;
        case 0x91u: return R1_LEGACY_COMMAND_ROUTE_0X91;
        case 0x94u: return R1_LEGACY_COMMAND_ROUTE_0X94;
        case 0x95u: return R1_LEGACY_COMMAND_ROUTE_0X95;
        case 0xf2u: return R1_LEGACY_COMMAND_ROUTE_0XF2;
        default: return R1_LEGACY_COMMAND_ROUTE_NONE;
    }
}

static r1_legacy_command_route factory_legacy_route(uint8_t opcode) {
    if (opcode == 0x10u) {
        return R1_LEGACY_COMMAND_ROUTE_FACTORY_NOOP_0X10;
    }
    if (opcode == 0x8bu) {
        return R1_LEGACY_COMMAND_ROUTE_FACTORY_STATUS_0X8B;
    }
    return legacy_route(opcode);
}

static r1_error legacy_command_route_frame_with(
    const uint8_t *frame, size_t frame_length, uint8_t *workspace,
    size_t workspace_length, r1_legacy_command_route *route,
    bool factory) {
    if (frame == NULL || workspace == NULL || route == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *route = R1_LEGACY_COMMAND_ROUTE_NONE;
    if (frame_length <= R1_LEGACY_COMMAND_OPCODE_OFFSET ||
        frame_length > R1_LEGACY_COMMAND_WORKSPACE_SIZE ||
        workspace_length < R1_LEGACY_COMMAND_WORKSPACE_SIZE) {
        return R1_ERROR_LENGTH;
    }
    for (size_t index = 0u; index < R1_LEGACY_COMMAND_WORKSPACE_SIZE;
         ++index) {
        workspace[index] = 0u;
    }
    copy_bytes(workspace, frame, frame_length);
    *route = factory
        ? factory_legacy_route(workspace[R1_LEGACY_COMMAND_OPCODE_OFFSET])
        : legacy_route(workspace[R1_LEGACY_COMMAND_OPCODE_OFFSET]);
    return *route == R1_LEGACY_COMMAND_ROUTE_NONE
        ? R1_ERROR_UNSUPPORTED : R1_OK;
}

r1_error r1_legacy_command_route_frame(
    const uint8_t *frame, size_t frame_length, uint8_t *workspace,
    size_t workspace_length, r1_legacy_command_route *route) {
    return legacy_command_route_frame_with(
        frame, frame_length, workspace, workspace_length, route, false);
}

r1_error r1_factory_legacy_command_route_frame(
    const uint8_t *frame, size_t frame_length, uint8_t *workspace,
    size_t workspace_length, r1_legacy_command_route *route) {
    return legacy_command_route_frame_with(
        frame, frame_length, workspace, workspace_length, route, true);
}

static void fill_bytes(uint8_t *output, uint8_t value, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = value;
    }
}

/* Recovered selector 0...4 legacy device-info formatter. Persistent getters,
 * FICR/UICR reads, active-link selection, and transport sending remain external. */
r1_error r1_legacy_device_info_build(
    const uint8_t request_prefix[R1_LEGACY_DEVICE_INFO_PREFIX_BYTES],
    const r1_legacy_device_info_sources *sources,
    r1_legacy_device_info_response *response) {
    if (request_prefix == NULL || sources == NULL || response == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *response = (r1_legacy_device_info_response){0};
    copy_bytes(response->bytes, request_prefix,
               R1_LEGACY_DEVICE_INFO_PREFIX_BYTES);

    switch (request_prefix[3]) {
        case 0u:
            if (sources->product_bsn_length == UINT8_MAX) {
                fill_bytes(response->bytes + 4u, UINT8_MAX, 21u);
            } else {
                copy_bytes(response->bytes + 4u, sources->product_bsn, 21u);
            }
            response->length = 25u;
            break;
        case 1u:
            if (sources->product_sn_length == UINT8_MAX) {
                fill_bytes(response->bytes + 4u, UINT8_MAX, 15u);
            } else {
                copy_bytes(response->bytes + 4u, sources->product_sn, 15u);
            }
            response->length = 25u;
            break;
        case 2u:
            copy_bytes(response->bytes + 4u,
                       sources->temperature_calibration, 6u);
            copy_bytes(response->bytes + 10u,
                       sources->accelerometer_calibration, 6u);
            /* Stock passes length 13, exposing only the first three bytes of
             * the second six-byte copy. Preserve that wire quirk exactly. */
            response->length = 13u;
            break;
        case 3u:
            fill_bytes(response->bytes + 4u, UINT8_MAX, 36u);
            response->bytes[40] = sources->configuration_byte_0x70;
            response->bytes[41] = (uint8_t)sources->configuration_word_0x74;
            response->bytes[42] = sources->configuration_byte_0x78;
            response->length = 43u;
            break;
        case 4u:
            copy_bytes(response->bytes + 4u, sources->device_identity, 20u);
            response->length = 24u;
            break;
        default:
            return R1_ERROR_UNSUPPORTED;
    }
    return R1_OK;
}

r1_error r1_ati_calibration_plan_command(
    uint8_t subcommand, uint8_t argument_0, uint8_t argument_1,
    const r1_ati_calibration_observation *observation,
    r1_ati_calibration_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_ati_calibration_plan){
        .response_status = R1_ATI_CALIBRATION_RESPONSE_STATUS_DEFAULT
    };

    switch (subcommand) {
        case 0u:
            plan->action = R1_ATI_CALIBRATION_ACTION_SET_RAW_PRINT_LEVEL;
            plan->action_argument_0 = argument_0;
            break;
        case 1u:
            plan->event_flags = UINT32_C(0x40);
            break;
        case 2u:
            plan->event_flags = UINT32_C(0x80);
            break;
        case 3u:
            plan->action = R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION;
            plan->configuration_word_1 = 1u;
            plan->configuration_word_2 = 1u;
            plan->action_argument_0 = argument_0;
            plan->event_flags = UINT32_C(0x100);
            break;
        case 4u:
            plan->action = R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION;
            plan->configuration_word_1 = 2u;
            plan->configuration_word_2 = 2u;
            plan->action_argument_0 = argument_0;
            plan->action_argument_1 = argument_1;
            plan->event_flags = UINT32_C(0x200);
            break;
        case 5u:
            plan->action = R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION;
            plan->configuration_word_1 = 3u;
            plan->configuration_word_2 = 1u;
            plan->action_argument_0 = argument_0;
            plan->event_flags = UINT32_C(0x400);
            break;
        case 6u:
            plan->action = R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION;
            plan->configuration_word_1 = 4u;
            plan->configuration_word_2 = 1u;
            plan->action_argument_0 = argument_0 == 0u ? 0u : 1u;
            plan->event_flags = UINT32_C(0x800);
            break;
        case 7u:
            plan->action = R1_ATI_CALIBRATION_ACTION_QUERY_CALIBRATION;
            plan->response_update_length = observation->calibration_available ? 2u : 1u;
            plan->response_update[0] = observation->calibration_available
                ? observation->calibration_first : UINT8_MAX;
            plan->response_update[1] = observation->calibration_second;
            if (observation->calibration_available) {
                plan->response_status = R1_ATI_CALIBRATION_RESPONSE_STATUS_QUERY;
            }
            break;
        case 8u:
            plan->action = R1_ATI_CALIBRATION_ACTION_OPEN_TOUCH_SOURCE;
            plan->action_argument_0 = 2u;
            break;
        case 9u:
            plan->action = R1_ATI_CALIBRATION_ACTION_CLOSE_TOUCH_SOURCE;
            plan->action_argument_0 = 2u;
            break;
        case 10u:
            plan->action = R1_ATI_CALIBRATION_ACTION_READ_RING_SIZE;
            plan->response_update_length = 1u;
            plan->response_update[0] = observation->ring_size;
            break;
        default:
            break;
    }
    return R1_OK;
}

static void clear_result(r1_dispatch_result *result) {
    result->count = 0u;
    for (size_t index = 0u; index < R1_DISPATCH_RESPONSE_MAX; ++index) {
        result->lengths[index] = 0u;
    }
}

static size_t dispatch_fragment_count(size_t model_length) {
    /* r1_fragment_message always emits a terminal fragment, including for an
     * exact multiple of the 239-byte payload width. */
    return model_length / R1_FRAGMENT_PAYLOAD_MAX + 1u;
}

static bool dispatch_fragment_capacity_available(
    const r1_dispatch_result *result, size_t next_model_length) {
    size_t fragments = dispatch_fragment_count(next_model_length);
    for (size_t index = 0u; index < result->count; ++index) {
        fragments += dispatch_fragment_count(result->lengths[index]);
    }
    return fragments <= R1_DISPATCH_FRAGMENT_MAX;
}

static r1_error add_response(const r1_model *request, result_code code,
                             const uint8_t *payload, size_t payload_length,
                             r1_dispatch_result *result) {
    if (result->count >= R1_DISPATCH_RESPONSE_MAX) {
        return R1_ERROR_CAPACITY;
    }
    const r1_model response = {
        R1_PROTOCOL_VERSION, request->module, R1_MODULE_VERSION, request->serial,
        (uint8_t)(UINT8_C(0x03) | (uint8_t)((uint8_t)code << 2u)),
        request->command, request->subcommand, payload, payload_length
    };
    size_t written = 0u;
    const r1_error error = r1_model_encode(
        &response, R1_CHECKSUM_FIRMWARE_FULL_MODBUS,
        result->models[result->count], R1_DISPATCH_MODEL_MAX, &written);
    if (error == R1_OK &&
        !dispatch_fragment_capacity_available(result, written)) {
        return R1_ERROR_CAPACITY;
    }
    if (error == R1_OK) {
        result->lengths[result->count] = written;
        result->count += 1u;
    }
    return error;
}

static r1_error add_notification(const r1_model *request, uint16_t serial,
                                 const uint8_t *payload, size_t payload_length,
                                 r1_dispatch_result *result) {
    if (result->count >= R1_DISPATCH_RESPONSE_MAX) {
        return R1_ERROR_CAPACITY;
    }
    const r1_model notification = {
        R1_PROTOCOL_VERSION, request->module, R1_MODULE_VERSION, serial,
        0x02u, request->command, request->subcommand, payload, payload_length
    };
    size_t written = 0u;
    const r1_error error = r1_model_encode(
        &notification, R1_CHECKSUM_FIRMWARE_FULL_MODBUS,
        result->models[result->count], R1_DISPATCH_MODEL_MAX, &written);
    if (error == R1_OK &&
        !dispatch_fragment_capacity_available(result, written)) {
        return R1_ERROR_CAPACITY;
    }
    if (error == R1_OK) {
        result->lengths[result->count] = written;
        result->count += 1u;
    }
    return error;
}

static r1_error add_tracked_notification(r1_device_state *state,
                                         const r1_model *request,
                                         const uint8_t *payload, size_t payload_length,
                                         r1_pending_kind kind, uint8_t record_index,
                                         r1_dispatch_result *result) {
    const uint16_t serial = r1_health_next_serial(&state->health);
    r1_error error = add_notification(request, serial, payload, payload_length, result);
    if (error != R1_OK) {
        return error;
    }
    error = r1_health_register_pending(&state->health, request->module,
                                       request->command, request->subcommand,
                                       serial, kind, record_index);
    if (error != R1_OK) {
        result->count -= 1u;
        result->lengths[result->count] = 0u;
    }
    return error;
}

typedef struct {
    r1_device_state *state;
    const r1_model *request;
    r1_dispatch_result *result;
    uint8_t metric;
    uint32_t latest_timestamp;
    uint8_t latest_value;
} scalar_history_emit_context;

static r1_error add_scalar_history_notification(
    void *opaque, const r1_health_u8_history *history,
    uint32_t maximum_recorded_timestamp, uint8_t acknowledgement_mode) {
    scalar_history_emit_context *context = opaque;
    if (context == NULL || history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    r1_health_u8_history encoded_history = *history;
    /* The recovered HR/SpO2 sync flush always reserves the five-byte latest
     * prefix; an unavailable accessor contributes five zero bytes. */
    encoded_history.has_latest = true;
    encoded_history.latest_timestamp = context->latest_timestamp;
    encoded_history.latest_value = context->latest_value;
    uint8_t payload[R1_HEALTH_DAILY_U8_MAX_BYTES];
    size_t payload_length = 0u;
    r1_error error = r1_health_encode_daily_u8(
        &encoded_history, payload, sizeof payload, &payload_length);
    if (error != R1_OK) {
        return error;
    }
    const uint16_t serial = r1_health_next_serial(&context->state->health);
    error = add_notification(
        context->request, serial, payload, payload_length, context->result);
    if (error != R1_OK) {
        return error;
    }
    error = r1_health_register_scalar_history_pending(
        &context->state->health, context->request->module,
        context->request->command, context->request->subcommand, serial,
        context->metric, acknowledgement_mode, maximum_recorded_timestamp);
    if (error != R1_OK) {
        context->result->count -= 1u;
        context->result->lengths[context->result->count] = 0u;
    }
    return error;
}

typedef struct {
    r1_device_state *state;
    const r1_model *request;
    r1_dispatch_result *result;
} hrv_history_emit_context;

static r1_error add_hrv_history_notification(
    void *opaque, const r1_health_u16_history *history,
    uint32_t maximum_recorded_timestamp, uint8_t acknowledgement_mode) {
    hrv_history_emit_context *context = opaque;
    if (context == NULL || history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t payload[R1_HEALTH_DAILY_U16_MAX_BYTES];
    size_t payload_length = 0u;
    r1_error error = r1_health_encode_daily_u16(
        history, payload, sizeof payload, &payload_length);
    if (error != R1_OK) {
        return error;
    }
    const uint16_t serial = r1_health_next_serial(&context->state->health);
    error = add_notification(
        context->request, serial, payload, payload_length, context->result);
    if (error != R1_OK) {
        return error;
    }
    error = r1_health_register_scalar_history_pending(
        &context->state->health, context->request->module,
        context->request->command, context->request->subcommand, serial,
        2u, acknowledgement_mode, maximum_recorded_timestamp);
    if (error != R1_OK) {
        context->result->count -= 1u;
        context->result->lengths[context->result->count] = 0u;
    }
    return error;
}

typedef struct {
    r1_device_state *state;
    const r1_model *request;
    r1_dispatch_result *result;
} activity_history_emit_context;

static r1_error add_activity_history_notification(
    void *opaque, const r1_activity_history *history,
    uint32_t maximum_recorded_timestamp, uint8_t acknowledgement_mode) {
    activity_history_emit_context *context = opaque;
    if (context == NULL || history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint8_t payload[R1_ACTIVITY_DAILY_MAX_BYTES];
    size_t payload_length = 0u;
    r1_error error = r1_activity_encode_daily(
        history, payload, sizeof payload, &payload_length);
    if (error != R1_OK) {
        return error;
    }
    const uint16_t serial = r1_health_next_serial(&context->state->health);
    error = add_notification(
        context->request, serial, payload, payload_length, context->result);
    if (error != R1_OK) {
        return error;
    }
    error = r1_health_register_scalar_history_pending(
        &context->state->health, context->request->module,
        context->request->command, context->request->subcommand, serial,
        3u, acknowledgement_mode, maximum_recorded_timestamp);
    if (error != R1_OK) {
        context->result->count -= 1u;
        context->result->lengths[context->result->count] = 0u;
    }
    return error;
}

static bool is_set(const r1_model *request) {
    return (request->status & 0x02u) != 0u;
}

static bool authorized_mutation(const r1_session *session) {
    return session->encrypted && session->bonded && session->authorized;
}

static r1_error get_device_status(const r1_device_state *state, const r1_model *request,
                                  r1_dispatch_result *result) {
    uint8_t payload[7u] = {state->battery_percent, (uint8_t)state->charge, 1u, 0u, 0u, 0u, 0u};
    return add_response(request, RESULT_SUCCESS, payload, sizeof payload, result);
}

static r1_error get_device_info(const r1_device_state *state, const r1_model *request,
                                r1_dispatch_result *result) {
    uint8_t payload[32u] = {0u};
    for (size_t index = 0u; index < 16u; ++index) {
        payload[index] = (uint8_t)state->application_version[index];
        payload[16u + index] = (uint8_t)state->hardware_version[index];
    }
    return add_response(request, RESULT_SUCCESS, payload, sizeof payload, result);
}

static r1_error dispatch_health(r1_device_state *state, const r1_session *session,
                                const r1_model *request, r1_dispatch_result *result) {
    if (!session->authorized) {
        (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
        return R1_ERROR_UNAUTHORIZED;
    }
    if ((request->status & 0x03u) != 0u) {
        return R1_ERROR_STATE;
    }
    r1_health_history_route route;
    r1_error error = r1_health_history_route_command(
        request->command, request->subcommand, request->serial, &route);
    if (error != R1_OK) {
        (void)add_response(request, RESULT_NOT_SUPPORTED, NULL, 0u, result);
        return R1_ERROR_UNSUPPORTED;
    }
    r1_health_note_explicit_history_query(&state->health, state->unix_seconds);
    uint8_t payload[R1_ACTIVITY_DAILY_MAX_BYTES];
    size_t payload_length = 0u;

    if (route.action == R1_HEALTH_HISTORY_HEART_RATE_DAILY ||
        route.action == R1_HEALTH_HISTORY_HEART_RATE_POINT ||
        route.action == R1_HEALTH_HISTORY_SPO2_DAILY ||
        route.action == R1_HEALTH_HISTORY_SPO2_POINT) {
        r1_health_u8_history *history = route.metric == 0u
            ? &state->health.heart_rate : &state->health.blood_oxygen;
        if (route.query_kind == 1u) {
            error = add_response(request, RESULT_SUCCESS, NULL, 0u, result);
            if (error != R1_OK) {
                return error;
            }
            if (state->health.scalar_history_query != NULL) {
                scalar_history_emit_context emit_context = {
                    .state = state,
                    .request = request,
                    .result = result,
                    .metric = route.metric,
                    .latest_timestamp = history->has_latest
                        ? history->latest_timestamp : 0u,
                    .latest_value = history->has_latest
                        ? history->latest_value : 0u,
                };
                return state->health.scalar_history_query(
                    state->health.scalar_history_query_context,
                    route.metric, state->unix_seconds, history,
                    add_scalar_history_notification, &emit_context);
            }
            error = r1_health_encode_daily_u8(
                history, payload, sizeof payload, &payload_length);
            return error == R1_OK
                ? add_tracked_notification(
                    state, request, payload, payload_length,
                    R1_PENDING_GENERIC, 0u, result)
                : error;
        }
        uint8_t latest_value = 0u;
        uint32_t latest_timestamp = 0u;
        const bool latest_available = r1_health_u8_latest_sample(
            history, &latest_value, &latest_timestamp);
        (void)latest_value;
        (void)latest_timestamp;
        error = r1_health_encode_point_u8(
            history, latest_available ? 1u : 0u,
            payload, sizeof payload, &payload_length);
        return error == R1_OK
            ? add_response(request, RESULT_SUCCESS, payload, payload_length, result)
            : error;
    } else if (route.action == R1_HEALTH_HISTORY_HRV_DAILY ||
               route.action == R1_HEALTH_HISTORY_HRV_POINT) {
        r1_health_u16_history *history = &state->health.heart_rate_variability;
        if (route.query_kind == 1u) {
            error = add_response(request, RESULT_SUCCESS, NULL, 0u, result);
            if (error != R1_OK) {
                return error;
            }
            if (state->health.hrv_history_query != NULL) {
                hrv_history_emit_context emit_context = {
                    .state = state,
                    .request = request,
                    .result = result,
                };
                return state->health.hrv_history_query(
                    state->health.hrv_history_query_context,
                    state->unix_seconds, history,
                    add_hrv_history_notification, &emit_context);
            }
            error = r1_health_encode_daily_u16(
                history, payload, sizeof payload, &payload_length);
            if (error != R1_OK) {
                return error;
            }
            return add_tracked_notification(
                state, request, payload, payload_length,
                R1_PENDING_GENERIC, 0u, result);
        }
        uint16_t latest_value = 0u;
        uint32_t latest_timestamp = 0u;
        const bool latest_available = r1_health_u16_latest_sample(
            history, &latest_value, &latest_timestamp);
        (void)latest_value;
        (void)latest_timestamp;
        error = r1_health_encode_point_u16(
            history, latest_available ? 1u : 0u,
            payload, sizeof payload, &payload_length);
        return error == R1_OK
            ? add_response(request, RESULT_SUCCESS, payload, payload_length, result)
            : error;
    } else if (route.action == R1_HEALTH_HISTORY_ACTIVITY_DAILY ||
               route.action == R1_HEALTH_HISTORY_ACTIVITY_REFRESH) {
        if (route.action == R1_HEALTH_HISTORY_ACTIVITY_DAILY) {
            error = add_response(request, RESULT_SUCCESS, NULL, 0u, result);
            if (error != R1_OK) {
                return error;
            }
            if (state->health.activity_history_query != NULL) {
                activity_history_emit_context emit_context = {
                    .state = state,
                    .request = request,
                    .result = result,
                };
                return state->health.activity_history_query(
                    state->health.activity_history_query_context,
                    state->unix_seconds, &state->health.activity,
                    add_activity_history_notification, &emit_context);
            }
            error = r1_activity_encode_daily(
                &state->health.activity, payload, sizeof payload,
                &payload_length);
            return error == R1_OK
                ? add_tracked_notification(
                    state, request, payload, payload_length,
                    R1_PENDING_GENERIC, 0u, result)
                : error;
        }
        /* Exact 2.2.6.0009 behavior: refresh the accumulator without a direct response. */
        return R1_OK;
    } else if (route.action == R1_HEALTH_HISTORY_SLEEP_DAILY) {
        error = add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        if (error != R1_OK) {
            return error;
        }
        for (size_t position = 0u; position < state->health.sleep.count; ++position) {
            const size_t index = ((size_t)state->health.sleep.read_index + position)
                % R1_SLEEP_SESSION_MAX;
            const r1_sleep_session *session_record = &state->health.sleep.sessions[index];
            if (session_record->synchronized) {
                continue;
            }
            error = r1_sleep_encode(
                session_record, payload, sizeof payload, &payload_length);
            if (error != R1_OK) {
                return error;
            }
            error = add_tracked_notification(state, request, payload, payload_length,
                                             R1_PENDING_SLEEP_SESSION, (uint8_t)index,
                                             result);
            if (error != R1_OK) {
                return error;
            }
        }
        return R1_OK;
    }

    return R1_ERROR_STATE;
}

static bool valid_profile(const uint8_t *payload) {
    const uint16_t height = read_u16(payload + 2u);
    const uint16_t weight = read_u16(payload + 4u);
    return payload[0] <= 2u && payload[1] >= 11u && payload[1] <= 99u &&
        height >= 101u && height <= 219u && weight >= 31u && weight <= 149u;
}

r1_error r1_touch_switch_handler_plan_decode(
    const uint8_t *payload, size_t payload_length,
    r1_touch_switch_handler_plan *plan) {
    if (payload == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length != R1_TOUCH_SWITCH_PAYLOAD_SIZE) {
        return R1_ERROR_LENGTH;
    }

    *plan = (r1_touch_switch_handler_plan){
        .send_empty_success_response = true,
        .action = R1_TOUCH_SWITCH_ACTION_NONE,
        .selector = payload[0],
        .switch_value = payload[1],
        .touch_source = R1_TOUCH_SWITCH_SOURCE_GLASSES,
    };
    if (plan->selector == R1_TOUCH_SWITCH_SELECTOR_PHONE) {
        plan->action = R1_TOUCH_SWITCH_ACTION_PHONE_DIAGNOSTIC;
    } else if (plan->selector == R1_TOUCH_SWITCH_SELECTOR_GLASSES) {
        plan->action = plan->switch_value == 0u
            ? R1_TOUCH_SWITCH_ACTION_CLOSE_GLASSES_SOURCE
            : R1_TOUCH_SWITCH_ACTION_OPEN_GLASSES_SOURCE;
    }
    return R1_OK;
}

r1_error r1_dispatch(r1_device_state *state, r1_session *session,
                     const r1_model *request, r1_dispatch_result *result) {
    if (state == NULL || session == NULL || request == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_result(result);
    if (request->module == 0x02u) {
        return dispatch_health(state, session, request, result);
    }
    if (request->module != R1_MODULE_SYSTEM || request->command != R1_COMMAND_SYSTEM) {
        (void)add_response(request, RESULT_NOT_SUPPORTED, NULL, 0u, result);
        return R1_ERROR_UNSUPPORTED;
    }

    switch (request->subcommand) {
        case R1_SYSTEM_SUBCOMMAND_DEVICE_STATUS:
            return is_set(request) ? add_response(request, RESULT_REFUSE, NULL, 0u, result)
                                   : get_device_status(state, request, result);
        case 0x02u:
            return is_set(request) ? add_response(request, RESULT_REFUSE, NULL, 0u, result)
                                   : get_device_info(state, request, result);
        case 0x03u: {
            const uint8_t wear = (uint8_t)state->wear;
            return is_set(request) ? add_response(request, RESULT_REFUSE, NULL, 0u, result)
                                   : add_response(request, RESULT_SUCCESS, &wear, 1u, result);
        }
        case 0x04u:
            if (!is_set(request) || request->payload_length < 12u) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (!authorized_mutation(session)) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            if (!valid_profile(request->payload)) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            state->profile.gender = request->payload[0];
            state->profile.age_years = request->payload[1];
            state->profile.height_cm = read_u16(request->payload + 2u);
            state->profile.weight_kg = read_u16(request->payload + 4u);
            state->profile.valid = true;
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        case 0x05u:
            if (!is_set(request) || request->payload_length < 6u) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (!authorized_mutation(session)) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            state->timezone_minutes_raw = read_u16(request->payload);
            state->unix_seconds = read_u32(request->payload + 2u);
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        case 0x07u: {
            if (!is_set(request) ||
                request->payload_length != R1_TOUCH_SWITCH_PAYLOAD_SIZE) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (!authorized_mutation(session)) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            r1_touch_switch_handler_plan touch_plan;
            const r1_error touch_error = r1_touch_switch_handler_plan_decode(
                request->payload, request->payload_length, &touch_plan);
            if (touch_error != R1_OK) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (touch_plan.action == R1_TOUCH_SWITCH_ACTION_OPEN_GLASSES_SOURCE) {
                state->touch_enabled = true;
            } else if (touch_plan.action ==
                       R1_TOUCH_SWITCH_ACTION_CLOSE_GLASSES_SOURCE) {
                state->touch_enabled = false;
            }
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        }
        case 0x08u:
            /* Pair-role selection is not an authorization primitive in openR1. */
            if (request->payload_length < 1u) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (request->payload[0] == 1u) {
                session->role = R1_ROLE_PHONE;
            }
            {
                static const uint8_t pair_result = 0u;
                return add_response(request, RESULT_SUCCESS, &pair_result, 1u, result);
            }
        case 0x0eu: {
            const r1_health_settings_record stored =
                health_settings_record(state->health_settings);
            r1_health_settings_command_plan health_settings_plan;
            const r1_error plan_error = r1_health_settings_plan_command(
                is_set(request), &stored, request->payload,
                request->payload_length, &health_settings_plan);
            if (plan_error != R1_OK) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (!is_set(request)) {
                uint8_t response[12];
                health_settings_bytes(&health_settings_plan.response, response);
                return add_response(request, RESULT_SUCCESS, response,
                                    sizeof response, result);
            }
            if (!authorized_mutation(session)) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            health_settings_bytes(
                &health_settings_plan.persistent_record,
                state->health_settings);
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        }
        case 0x0fu:
            if (!is_set(request)) {
                return add_response(request, RESULT_SUCCESS, state->system_settings,
                                    sizeof state->system_settings, result);
            }
            if (request->payload_length != sizeof state->system_settings) {
                return add_response(request, RESULT_ERROR, NULL, 0u, result);
            }
            if (!authorized_mutation(session)) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            copy_bytes(state->system_settings, request->payload, sizeof state->system_settings);
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        case 0x10u:
            if (!session->authorized) {
                (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
                return R1_ERROR_UNAUTHORIZED;
            }
            return add_response(request, RESULT_SUCCESS, state->serial_number,
                                sizeof state->serial_number, result);
        case 0x7eu:
            if (!session->authorized) {
                return R1_ERROR_UNAUTHORIZED;
            }
            if (request->payload_length < 6u) {
                return R1_ERROR_LENGTH;
            }
            (void)r1_health_acknowledge(
                &state->health, request->payload[0], request->payload[1],
                request->payload[2], read_u16(request->payload + 4u));
            return R1_OK;
        case 0x7fu:
        case 0x80u:
        case 0x81u:
            return add_response(request, RESULT_SUCCESS, NULL, 0u, result);
        case 0x09u: /* otaStart */
        case 0x0au: /* advStart */
        case 0x0cu: /* setAlgoKey */
        case 0x11u: /* nvRecover */
        case 0x12u: /* powerControl */
        case 0x82u: /* removeRingNotify */
            (void)add_response(request, RESULT_REFUSE, NULL, 0u, result);
            return R1_ERROR_UNAUTHORIZED;
        default:
            (void)add_response(request, RESULT_NOT_SUPPORTED, NULL, 0u, result);
            return R1_ERROR_UNSUPPORTED;
    }
}
