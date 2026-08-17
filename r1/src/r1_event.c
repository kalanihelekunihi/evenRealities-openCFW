#include "openr1/r1_event.h"

static void initialize_task_suspend_targets(
    const uint8_t groups[R1_TASK_SUSPEND_TARGET_COUNT],
    r1_task_suspend_target targets[R1_TASK_SUSPEND_TARGET_COUNT]) {
    for (size_t index = 0u; index < R1_TASK_SUSPEND_TARGET_COUNT; ++index) {
        targets[index] = (r1_task_suspend_target){
            .sync_group = groups[index],
            .acknowledgment_flag = UINT32_C(1) << groups[index],
        };
    }
}

static void initialize_queue(r1_event_queue *queue, size_t capacity) {
    queue->head = 0u;
    queue->count = 0u;
    queue->capacity = capacity;
}

void r1_event_plane_initialize(r1_event_plane *plane) {
    if (plane == NULL) {
        return;
    }
    initialize_queue(&plane->normal, R1_NORMAL_QUEUE_CAPACITY);
    initialize_queue(&plane->eus, R1_EUS_QUEUE_CAPACITY);
    plane->hvn_credits = R1_HVN_CREDIT_MAX;
}

r1_error r1_event_enqueue(r1_event_plane *plane, bool eus, const r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (event->length > R1_BLE_VALUE_MAX) {
        return R1_ERROR_LENGTH;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count >= queue->capacity) {
        return R1_ERROR_CAPACITY;
    }
    const size_t index = (queue->head + queue->count) % queue->capacity;
    queue->entries[index] = *event;
    queue->count += 1u;
    return R1_OK;
}

bool r1_event_take(r1_event_plane *plane, bool eus, r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return false;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    *event = queue->entries[queue->head];
    queue->head = (queue->head + 1u) % queue->capacity;
    queue->count -= 1u;
    return true;
}

bool r1_event_peek(const r1_event_plane *plane, bool eus, r1_tx_event *event) {
    if (plane == NULL || event == NULL) {
        return false;
    }
    const r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    *event = queue->entries[queue->head];
    return true;
}

r1_tx_event *r1_event_front(r1_event_plane *plane, bool eus) {
    if (plane == NULL) {
        return NULL;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return NULL;
    }
    return &queue->entries[queue->head];
}

bool r1_event_drop(r1_event_plane *plane, bool eus) {
    if (plane == NULL) {
        return false;
    }
    r1_event_queue *queue = eus ? &plane->eus : &plane->normal;
    if (queue->count == 0u) {
        return false;
    }
    queue->head = (queue->head + 1u) % queue->capacity;
    queue->count -= 1u;
    return true;
}

static void remove_from_queue(r1_event_queue *queue, uint16_t connection) {
    size_t kept = 0u;
    const size_t original = queue->count;
    for (size_t offset = 0u; offset < original; ++offset) {
        const size_t source = (queue->head + offset) % queue->capacity;
        if (queue->entries[source].connection == connection) {
            continue;
        }
        const size_t destination = (queue->head + kept) % queue->capacity;
        if (destination != source) {
            queue->entries[destination] = queue->entries[source];
        }
        kept += 1u;
    }
    queue->count = kept;
}

void r1_event_remove_connection(r1_event_plane *plane, uint16_t connection) {
    if (plane == NULL) {
        return;
    }
    remove_from_queue(&plane->normal, connection);
    remove_from_queue(&plane->eus, connection);
}

bool r1_event_consume_credit(r1_event_plane *plane) {
    if (plane == NULL || plane->hvn_credits == 0u) {
        return false;
    }
    plane->hvn_credits -= 1u;
    return true;
}

void r1_event_complete(r1_event_plane *plane, uint8_t completed) {
    if (plane == NULL) {
        return;
    }
    const uint16_t sum = (uint16_t)plane->hvn_credits + completed;
    plane->hvn_credits = sum > R1_HVN_CREDIT_MAX
        ? R1_HVN_CREDIT_MAX : (uint8_t)sum;
}

void r1_event_disconnect(r1_event_plane *plane) {
    r1_event_plane_initialize(plane);
}

r1_error r1_channel1_task_plan_startup(
    bool queue_created, r1_channel1_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_channel1_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_NORMAL_QUEUE_CAPACITY,
        .queue_record_bytes = R1_CHANNEL1_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_CHANNEL1_TASK_SYNC_GROUP,
        .registry_name = "ble_gtx",
        .watchdog_ticks = R1_CHANNEL1_TASK_WATCHDOG_TICKS,
    };
    return R1_OK;
}

r1_error r1_channel1_task_plan_flags(
    uint32_t flags, r1_channel1_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    *plan = (r1_channel1_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .drain_queue = !provider_wait_error &&
            (flags & R1_CHANNEL1_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = !provider_wait_error &&
            (flags & R1_CHANNEL1_TASK_SUSPEND_FLAG) != 0u,
        .enter_suspend_wait = !provider_wait_error &&
            (flags & R1_CHANNEL1_TASK_SUSPEND_FLAG) != 0u,
        .wait_again = provider_wait_error ||
            (flags & R1_CHANNEL1_TASK_SUSPEND_FLAG) == 0u,
    };
    return R1_OK;
}

r1_error r1_bae8_input_task_plan_startup(
    bool queue_created, r1_bae8_input_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_bae8_input_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_BAE8_INPUT_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_BAE8_INPUT_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_BAE8_INPUT_TASK_SYNC_GROUP,
        .registry_name = "ble_msgrx",
        .watchdog_ticks = R1_BAE8_INPUT_TASK_WATCHDOG_TICKS,
    };
    return R1_OK;
}

r1_error r1_bae8_input_task_plan_flags(
    uint32_t flags, r1_bae8_input_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    *plan = (r1_bae8_input_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .drain_queue = !provider_wait_error &&
            (flags & R1_BAE8_INPUT_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = !provider_wait_error &&
            (flags & R1_BAE8_INPUT_TASK_SUSPEND_FLAG) != 0u,
        .enter_suspend_wait = !provider_wait_error &&
            (flags & R1_BAE8_INPUT_TASK_SUSPEND_FLAG) != 0u,
        .wait_again = provider_wait_error ||
            (flags & R1_BAE8_INPUT_TASK_SUSPEND_FLAG) == 0u,
    };
    return R1_OK;
}

r1_error r1_shared_tx_task_plan_startup(
    bool queue_created, r1_shared_tx_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_shared_tx_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_EUS_QUEUE_CAPACITY,
        .queue_record_bytes = R1_SHARED_TX_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_SHARED_TX_TASK_SYNC_GROUP,
        .registry_name = "ble_msgtx",
        .watchdog_ticks = R1_SHARED_TX_TASK_WATCHDOG_TICKS,
    };
    return R1_OK;
}

r1_error r1_shared_tx_task_plan_flags(
    uint32_t flags, r1_shared_tx_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    *plan = (r1_shared_tx_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .drain_queue = !provider_wait_error &&
            (flags & R1_SHARED_TX_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = !provider_wait_error &&
            (flags & R1_SHARED_TX_TASK_SUSPEND_FLAG) != 0u,
        .enter_suspend_wait = !provider_wait_error &&
            (flags & R1_SHARED_TX_TASK_SUSPEND_FLAG) != 0u,
        .wait_again = provider_wait_error ||
            (flags & R1_SHARED_TX_TASK_SUSPEND_FLAG) == 0u,
    };
    return R1_OK;
}

r1_error r1_factory_input_task_plan_startup(
    bool queue_created, r1_factory_input_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_input_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_FACTORY_INPUT_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_FACTORY_INPUT_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_FACTORY_INPUT_TASK_SYNC_GROUP,
    };
    if (!queue_created) {
        return R1_OK;
    }
    static const r1_factory_input_task_startup_action actions[] = {
        R1_FACTORY_INPUT_WEAR_BUFFER_FILL,
        R1_FACTORY_INPUT_SENSOR_STREAM_INITIALIZE,
        R1_FACTORY_INPUT_ACCELEROMETER_STREAM_CREATE,
        R1_FACTORY_INPUT_STREAM_NAMESPACE_REGISTER,
        R1_FACTORY_INPUT_TEMPERATURE_STREAM_CREATE,
    };
    for (size_t index = 0u;
         index < R1_FACTORY_INPUT_TASK_STARTUP_ACTION_COUNT; ++index) {
        plan->actions[index] = actions[index];
    }
    plan->action_count = R1_FACTORY_INPUT_TASK_STARTUP_ACTION_COUNT;
    return R1_OK;
}

r1_error r1_factory_input_task_plan_flags(
    uint32_t flags, r1_factory_input_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    const bool suspend = !provider_wait_error &&
        (flags & R1_FACTORY_INPUT_TASK_SUSPEND_FLAG) != 0u;
    *plan = (r1_factory_input_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .drain_queue = !provider_wait_error &&
            (flags & R1_FACTORY_INPUT_TASK_DISPATCH_FLAG) != 0u,
        .signal_suspend = suspend,
        .enter_suspend_wait = suspend,
        .run_periodic_operation = !suspend,
        .wait_again = !suspend,
    };
    return R1_OK;
}

r1_error r1_factory_input_thread_creation_plan_build(
    r1_factory_input_thread_creation_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_input_thread_creation_plan){
        .name = "factory_test",
        .stack_bytes = R1_FACTORY_INPUT_THREAD_STACK_BYTES,
        .priority_raw = R1_FACTORY_INPUT_THREAD_PRIORITY_RAW,
        .trustzone_module = R1_FACTORY_INPUT_THREAD_TRUSTZONE_MODULE,
        .request_thread_create = true,
        .store_returned_handle = true,
        .null_handle_enters_fail_stop = true,
    };
    return R1_OK;
}

r1_error r1_factory_input_record_plan_dispatch(
    uint16_t message_type, const uint8_t *payload, size_t payload_length,
    size_t payload_capacity, r1_factory_input_record_plan *plan) {
    if (plan == NULL || (payload == NULL && payload_length != 0u)) {
        return R1_ERROR_ARGUMENT;
    }
    const bool at_command = payload_length > 3u &&
        payload[0] == (uint8_t)'A' && payload[1] == (uint8_t)'T' &&
        payload[2] == (uint8_t)'^';
    if (at_command && payload_capacity <= payload_length) {
        return R1_ERROR_LENGTH;
    }
    *plan = (r1_factory_input_record_plan){
        .route = at_command ? R1_FACTORY_INPUT_RECORD_AT_COMMAND
                            : R1_FACTORY_INPUT_RECORD_STANDARD,
        .message_type = message_type,
        .dispatch_length = (uint16_t)payload_length,
        .observed_length = payload_length,
        .append_terminator = at_command,
        .terminator_index = at_command ? payload_length : 0u,
        .release_record = true,
    };
    return R1_OK;
}

static r1_error factory_f2_plan_initialize(
    r1_factory_f2_action action, r1_factory_f2_action_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_f2_action_plan){
        .action = action,
        .response_requested = true,
        .response_length = 4u,
    };
    return R1_OK;
}

r1_error r1_factory_f2_delayed_reset_plan(
    r1_factory_f2_action_plan *plan) {
    const r1_error error = factory_f2_plan_initialize(
        R1_FACTORY_F2_DELAYED_RESET, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->delay_before_action_ms = UINT16_C(2000);
    plan->reset_reason_write_requested = true;
    plan->reset_reason = 3u;
    plan->system_reset_requested = true;
    return R1_OK;
}

r1_error r1_factory_f2_ppg_mode_plan(
    const uint8_t *payload, size_t payload_length,
    r1_factory_f2_action_plan *plan) {
    if (payload == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length < 6u) {
        return R1_ERROR_LENGTH;
    }
    r1_factory_f2_action action = R1_FACTORY_F2_PPG_STOP;
    if (payload[4] == 1u) {
        action = R1_FACTORY_F2_PPG_PROFILE_4000;
    } else if (payload[5] == 1u) {
        action = R1_FACTORY_F2_PPG_PROFILE_2000;
    }
    return factory_f2_plan_initialize(action, plan);
}

r1_error r1_factory_f2_marked_ship_mode_plan(
    r1_factory_f2_action_plan *plan) {
    const r1_error error = factory_f2_plan_initialize(
        R1_FACTORY_F2_SHIP_MODE_MARKED, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->delay_before_action_ms = 100u;
    plan->delay_after_action_ms = 100u;
    plan->device_marker_write_requested = true;
    plan->device_marker = UINT8_C(0x5a);
    plan->ship_mode_sequence_requested = true;
    return R1_OK;
}

r1_error r1_factory_f2_ship_mode_plan(
    r1_factory_f2_action_plan *plan) {
    const r1_error error = factory_f2_plan_initialize(
        R1_FACTORY_F2_SHIP_MODE, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->delay_before_action_ms = 100u;
    plan->delay_after_action_ms = 100u;
    plan->ship_mode_sequence_requested = true;
    return R1_OK;
}

r1_error r1_sensor_task_plan_startup(
    bool queue_created, r1_sensor_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sensor_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_SENSOR_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_SENSOR_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_SENSOR_TASK_SYNC_GROUP,
        .registry_name = "sensor",
        .watchdog_ticks = R1_SENSOR_TASK_WATCHDOG_TICKS,
        .startup_event_id = R1_SENSOR_TASK_STARTUP_EVENT_ID,
        .use_sensor_stream_timeout = true,
    };
    if (!queue_created) {
        return R1_OK;
    }
    static const r1_sensor_task_startup_action actions[] = {
        R1_SENSOR_TASK_STREAM_INITIALIZE,
        R1_SENSOR_TASK_ACCELEROMETER_STREAM_CREATE,
        R1_SENSOR_TASK_STREAM_NAMESPACE_REGISTER,
        R1_SENSOR_TASK_TEMPERATURE_STREAM_CREATE,
        R1_SENSOR_TASK_HEALTH_SERVICES_INITIALIZE,
    };
    for (size_t index = 0u;
         index < R1_SENSOR_TASK_STARTUP_ACTION_COUNT; ++index) {
        plan->actions[index] = actions[index];
    }
    plan->action_count = R1_SENSOR_TASK_STARTUP_ACTION_COUNT;
    plan->publish_startup_event = true;
    return R1_OK;
}

r1_error r1_sensor_task_plan_flags(
    uint32_t flags, r1_sensor_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    const bool suspend = !provider_wait_error &&
        (flags & R1_SENSOR_TASK_SUSPEND_FLAG) != 0u;
    *plan = (r1_sensor_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .drain_event_records = !provider_wait_error &&
            (flags & R1_SENSOR_TASK_DISPATCH_FLAG) != 0u,
        .dispatch_motion_interrupt = !provider_wait_error &&
            (flags & R1_SENSOR_TASK_MOTION_INTERRUPT_FLAG) != 0u,
        .signal_suspend = suspend,
        .enter_suspend_wait = suspend,
        .wait_again = !suspend,
    };
    return R1_OK;
}

r1_error r1_system_task_plan_startup(
    bool queue_created, r1_system_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_system_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_SYSTEM_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_SYSTEM_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_SYSTEM_TASK_SYNC_GROUP,
        .workspace_clear_bytes = R1_SYSTEM_TASK_WORKSPACE_CLEAR_BYTES,
        .registry_name = "system",
        .watchdog_ticks = R1_SYSTEM_TASK_WATCHDOG_TICKS,
    };
    if (!queue_created) {
        return R1_OK;
    }
    static const r1_system_task_startup_action actions[] = {
        R1_SYSTEM_TASK_PRODUCT_SERVICES_INITIALIZE,
        R1_SYSTEM_TASK_WORKSPACE_CLEAR,
        R1_SYSTEM_TASK_NFC_LATE_INITIALIZE,
    };
    for (size_t index = 0u;
         index < R1_SYSTEM_TASK_STARTUP_ACTION_COUNT; ++index) {
        plan->actions[index] = actions[index];
    }
    plan->action_count = R1_SYSTEM_TASK_STARTUP_ACTION_COUNT;
    return R1_OK;
}

r1_error r1_system_task_plan_flags(
    uint32_t flags, r1_system_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    *plan = (r1_system_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .dispatch_system_flags = !provider_wait_error,
        .feed_watchdog = true,
        .wait_again = true,
    };
    return R1_OK;
}

r1_error r1_ble_task_plan_startup(
    bool queue_created, r1_ble_task_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_ble_task_startup_plan){
        .queue_create_failed = !queue_created,
        .enter_fail_stop = !queue_created,
        .queue_capacity = R1_BLE_TASK_QUEUE_CAPACITY,
        .queue_record_bytes = R1_BLE_TASK_QUEUE_RECORD_BYTES,
        .sync_group = R1_BLE_TASK_SYNC_GROUP,
        .role_sync_delay_ticks = R1_BLE_TASK_ROLE_SYNC_DELAY_TICKS,
        .slow_policy_delay_ticks = R1_BLE_TASK_SLOW_POLICY_DELAY_TICKS,
        .registry_name = "ble",
        .watchdog_ticks = R1_BLE_TASK_WATCHDOG_TICKS,
    };
    if (!queue_created) {
        return R1_OK;
    }
    plan->actions[0] = R1_BLE_TASK_PEER_RECORD_COMMIT;
    plan->actions[1] = R1_BLE_TASK_NORDIC_BOOTSTRAP_CONFIGURE;
    plan->action_count = R1_BLE_TASK_STARTUP_ACTION_COUNT;
    return R1_OK;
}

r1_error r1_ble_task_plan_flags(
    uint32_t flags, r1_ble_task_flag_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const bool provider_wait_error =
        flags == 0u || (flags & UINT32_C(0x80000000)) != 0u;
    const bool advertising_stop = !provider_wait_error &&
        (flags & R1_BLE_TASK_ADVERTISING_STOP_FLAG) != 0u;
    r1_ble_task_advertising_action advertising_action =
        R1_BLE_TASK_ADVERTISING_NONE;
    if (advertising_stop) {
        advertising_action = R1_BLE_TASK_ADVERTISING_STOP;
    } else if (!provider_wait_error &&
               (flags & R1_BLE_TASK_ADVERTISING_RESTART_3_FLAG) != 0u) {
        advertising_action = R1_BLE_TASK_ADVERTISING_RESTART_MODE_3;
    } else if (!provider_wait_error &&
               (flags & R1_BLE_TASK_ADVERTISING_RESTART_4_FLAG) != 0u) {
        advertising_action = R1_BLE_TASK_ADVERTISING_RESTART_MODE_4;
    }
    const bool suspend = !provider_wait_error &&
        (flags & R1_BLE_TASK_SUSPEND_FLAG) != 0u;
    *plan = (r1_ble_task_flag_plan){
        .observed_flags = flags,
        .provider_wait_error = provider_wait_error,
        .poll_softdevice_before = !provider_wait_error,
        .dispatch_connection_control = !provider_wait_error &&
            (flags & R1_BLE_TASK_CONNECTION_CONTROL_FLAG) != 0u,
        .advertising_action = advertising_action,
        .run_peripheral_watchdog = !provider_wait_error &&
            (flags & R1_BLE_TASK_PERIPHERAL_WATCHDOG_FLAG) != 0u,
        .prepare_buttonless_dfu = !provider_wait_error &&
            (flags & R1_BLE_TASK_DFU_PREPARE_FLAG) != 0u,
        .request_low_tx_power = !provider_wait_error &&
            (flags & R1_BLE_TASK_TX_POWER_LOW_FLAG) != 0u,
        .request_high_tx_power = !provider_wait_error &&
            (flags & R1_BLE_TASK_TX_POWER_HIGH_FLAG) != 0u,
        .poll_softdevice_after = !provider_wait_error,
        .feed_before_suspend = suspend,
        .signal_suspend = suspend,
        .enter_suspend_wait = suspend,
        .feed_watchdog = !suspend,
        .wait_again = !suspend,
    };
    return R1_OK;
}

r1_error r1_advertising_event_plan_build(
    uint32_t provider_event, r1_advertising_event_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_advertising_event_plan){0};
    switch (provider_event) {
        case 0u:
            plan->publish_status = true;
            break;
        case 3u:
            plan->publish_status = true;
            plan->advertising_active = true;
            plan->advertising_mode = 1u;
            plan->log = R1_ADVERTISING_EVENT_LOG_FAST;
            break;
        case 4u:
            plan->publish_status = true;
            plan->advertising_active = true;
            plan->advertising_mode = 2u;
            plan->log = R1_ADVERTISING_EVENT_LOG_SLOW;
            break;
        default:
            break;
    }
    return R1_OK;
}

r1_error r1_task_suspend_broadcast_plan_build(
    uint8_t configuration_byte, r1_task_suspend_broadcast_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    static const uint8_t normal_groups[R1_TASK_SUSPEND_TARGET_COUNT] = {
        5u, 0u, 7u, 1u, 9u, 2u, 3u, 10u, 4u,
    };
    static const uint8_t factory_groups[R1_TASK_SUSPEND_TARGET_COUNT] = {
        6u, 0u, 7u, 1u, 9u, 2u, 3u, 10u, 4u,
    };
    const bool factory = configuration_byte == UINT8_C(0x55);
    *plan = (r1_task_suspend_broadcast_plan){
        .target_count = R1_TASK_SUSPEND_TARGET_COUNT,
        .thread_flag = R1_TASK_SUSPEND_THREAD_FLAG,
        .acknowledgment_mask = factory ? UINT32_C(0x06df) : UINT32_C(0x06bf),
    };
    initialize_task_suspend_targets(
        factory ? factory_groups : normal_groups, plan->targets);
    return R1_OK;
}

r1_error r1_task_topology_startup_plan_build(
    uint8_t configuration_byte, r1_task_topology_startup_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    static const uint8_t common_groups[R1_TASK_TOPOLOGY_TARGET_COUNT] = {
        0u, 1u, 2u, 3u, 10u, 4u, 7u, 5u, 9u,
    };
    *plan = (r1_task_topology_startup_plan){
        .initialize_firmware_event_loop = true,
        .initialize_watchdog_registry = true,
        .target_count = R1_TASK_TOPOLOGY_TARGET_COUNT,
        .initial_thread_priority = R1_TASK_TOPOLOGY_INITIAL_PRIORITY,
        .final_thread_priority = R1_TASK_TOPOLOGY_FINAL_PRIORITY,
        .factory_group_selected =
            configuration_byte == R1_TASK_TOPOLOGY_FACTORY_MARKER,
    };
    for (size_t index = 0u; index < R1_TASK_TOPOLOGY_TARGET_COUNT; ++index) {
        plan->sync_groups[index] = common_groups[index];
    }
    if (plan->factory_group_selected) {
        plan->sync_groups[7] = 6u;
    }
    return R1_OK;
}

r1_error r1_task_suspend_barrier_plan_build(
    uint8_t configuration_byte, r1_task_suspend_barrier_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    static const uint8_t normal_groups[R1_TASK_SUSPEND_TARGET_COUNT] = {
        0u, 1u, 2u, 3u, 10u, 7u, 5u, 9u, 4u,
    };
    static const uint8_t factory_groups[R1_TASK_SUSPEND_TARGET_COUNT] = {
        0u, 1u, 2u, 3u, 10u, 7u, 6u, 9u, 4u,
    };
    const bool factory = configuration_byte == UINT8_C(0x55);
    *plan = (r1_task_suspend_barrier_plan){
        .target_count = R1_TASK_SUSPEND_TARGET_COUNT,
        .thread_flag = R1_TASK_SUSPEND_THREAD_FLAG,
        .per_target_wait_ticks = R1_TASK_SUSPEND_BARRIER_WAIT_TICKS,
    };
    initialize_task_suspend_targets(
        factory ? factory_groups : normal_groups, plan->targets);
    return R1_OK;
}

r1_error r1_delayed_event_timer_step(
    r1_delayed_event_state *state, uint32_t callback_argument,
    uint32_t kernel_tick, r1_delayed_event_step_result *result) {
    if (state == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_step_result){0};
    result->elapsed_override_used =
        (callback_argument >> 24u) == UINT32_C(0xff);
    result->elapsed_milliseconds = result->elapsed_override_used
        ? callback_argument & R1_DELAYED_EVENT_ELAPSED_MASK
        : state->last_timer_delay_milliseconds;

    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event == 0u) {
            continue;
        }
        slot->remaining_milliseconds =
            slot->remaining_milliseconds > result->elapsed_milliseconds
            ? slot->remaining_milliseconds - result->elapsed_milliseconds
            : 0u;
        if (slot->remaining_milliseconds == 0u) {
            result->due[result->due_count++] =
                (r1_delayed_event_due){slot->event, slot->context};
            slot->event = 0u;
        }
    }

    uint32_t next_delay = UINT32_MAX;
    bool has_active = false;
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        const r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event != 0u) {
            has_active = true;
            if (slot->remaining_milliseconds < next_delay) {
                next_delay = slot->remaining_milliseconds;
            }
        }
    }
    result->next_delay_milliseconds = next_delay;

    /* Preserve and label both recovered comparisons. An empty table leaves
     * UINT32_MAX, which passes the stock INT32_MAX sentinel test and requests
     * a maximum-delay timer. Conversely an exact INT32_MAX delay is skipped. */
    result->stock_empty_reload_quirk = !has_active;
    result->stock_int32_max_suppression_quirk =
        has_active && next_delay == (uint32_t)INT32_MAX;
    if (next_delay != (uint32_t)INT32_MAX && next_delay != 0u) {
        state->last_timer_delay_milliseconds = next_delay;
        state->last_timer_start_milliseconds =
            (kernel_tick * UINT32_C(1000)) >> 10u;
        result->timer_start_requested = true;
    }
    return R1_OK;
}

r1_error r1_delayed_event_schedule(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t delay_milliseconds, uint32_t kernel_tick,
    r1_delayed_event_schedule_result *result) {
    if (state == NULL || result == NULL || event == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_schedule_result){0};
    if (delay_milliseconds < 2u) {
        result->action = R1_DELAYED_EVENT_IMMEDIATE;
        result->immediate_push_requested = true;
        return R1_OK;
    }

    size_t slot_index = R1_DELAYED_EVENT_CAPACITY;
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        if (state->slots[index].event == 0u) {
            slot_index = index;
            break;
        }
    }
    if (slot_index == R1_DELAYED_EVENT_CAPACITY) {
        result->action = R1_DELAYED_EVENT_TABLE_FULL;
        result->slot_index = R1_DELAYED_EVENT_CAPACITY;
        return R1_ERROR_CAPACITY;
    }

    const uint32_t now_milliseconds =
        (kernel_tick * UINT32_C(1000)) >> 10u;
    const uint32_t elapsed = now_milliseconds
        - state->last_timer_start_milliseconds;
    state->slots[slot_index] = (r1_delayed_event_slot){
        event, context, delay_milliseconds + elapsed,
    };
    result->action = R1_DELAYED_EVENT_SCHEDULED;
    result->slot_index = slot_index;
    result->elapsed_milliseconds = elapsed;
    result->worker_wakeup_requested = true;
    return r1_delayed_event_timer_step(
        state, R1_DELAYED_EVENT_ELAPSED_TAG
            | (elapsed & R1_DELAYED_EVENT_ELAPSED_MASK),
        kernel_tick, &result->timer_step);
}

r1_error r1_delayed_event_cancel(
    r1_delayed_event_state *state, uint32_t event, uint32_t context,
    uint32_t kernel_tick, r1_delayed_event_cancel_result *result) {
    if (state == NULL || result == NULL || event == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_delayed_event_cancel_result){0};
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        r1_delayed_event_slot *slot = &state->slots[index];
        if (slot->event == event &&
            (context == 0u || slot->context == context)) {
            slot->event = 0u;
            result->removed_count += 1u;
        }
    }
    if (result->removed_count == 0u) {
        return R1_OK;
    }
    const uint32_t now_milliseconds =
        (kernel_tick * UINT32_C(1000)) >> 10u;
    result->elapsed_milliseconds =
        now_milliseconds - state->last_timer_start_milliseconds;
    result->worker_wakeup_requested = true;
    return r1_delayed_event_timer_step(
        state, R1_DELAYED_EVENT_ELAPSED_TAG |
            (result->elapsed_milliseconds & R1_DELAYED_EVENT_ELAPSED_MASK),
        kernel_tick, &result->timer_step);
}
