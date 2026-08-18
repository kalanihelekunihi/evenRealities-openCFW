#include "openr1/r1_runtime.h"

static bool runtime_lock(r1_runtime *runtime);
static void runtime_unlock(r1_runtime *runtime);

static r1_runtime_link *find_link(r1_runtime *runtime, uint16_t connection) {
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        if (runtime->links[index].active &&
            runtime->links[index].connection == connection) {
            return &runtime->links[index];
        }
    }
    return NULL;
}

r1_bae8_event_plan r1_runtime_plan_bae8_event(uint8_t event_type) {
    r1_bae8_event_plan plan = {R1_BAE8_EVENT_IGNORE, false, false};
    switch (event_type) {
        case 2u:
            plan.route = R1_BAE8_EVENT_BC_RX;
            break;
        case 3u:
            plan.route = R1_BAE8_EVENT_EUS_RX;
            break;
        case 6u:
        case 7u:
            plan.route = R1_BAE8_EVENT_LINK_GROUP_A;
            plan.assign_glasses_role = true;
            plan.requires_link_context = true;
            break;
        case 8u:
        case 9u:
            plan.route = R1_BAE8_EVENT_LINK_GROUP_B;
            plan.requires_link_context = true;
            break;
        default:
            break;
    }
    return plan;
}

r1_error r1_bae8_connection_event_plan_build(
    bool link_context_lookup_succeeded, bool callback_installed,
    bool channel1_cccd_read_succeeded, uint16_t channel1_cccd,
    bool channel2_cccd_read_succeeded, uint16_t channel2_cccd,
    r1_bae8_connection_event_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_bae8_connection_event_plan){
        .log_link_context_lookup_failure =
            !link_context_lookup_succeeded,
        .request_channel1_cccd_read = true,
        .request_channel2_cccd_read = true,
        .mark_channel1_notifications_enabled =
            link_context_lookup_succeeded && callback_installed &&
            channel1_cccd_read_succeeded &&
            (channel1_cccd & R1_BAE8_CCCD_NOTIFICATION_BIT) != 0u,
        .mark_channel2_notifications_enabled =
            link_context_lookup_succeeded && callback_installed &&
            channel2_cccd_read_succeeded &&
            (channel2_cccd & R1_BAE8_CCCD_NOTIFICATION_BIT) != 0u,
        .dispatch_connection_event = callback_installed,
        .callback_event_type = R1_BAE8_CONNECTION_EVENT_TYPE,
        .callback_event_record_bytes =
            R1_BAE8_CONNECTION_EVENT_RECORD_BYTES,
    };
    return R1_OK;
}

r1_error r1_gap_event_plan_build(
    const r1_gap_event_observation *observation, r1_gap_event_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_gap_event_plan){0};
    switch (observation->event_id) {
        case R1_GAP_EVT_CONNECTED:
            plan->route = R1_GAP_EVENT_CONNECTED;
            plan->cancel_connection_timeout = true;
            plan->schedule_connection_timeout = true;
            plan->connection_timeout_ticks =
                R1_GAP_CONNECTION_TIMEOUT_TICKS;
            plan->cache_peer_record = observation->connection < 3u;
            plan->cancel_role_timers = true;
            plan->factory_role_delay_ticks =
                R1_GAP_FACTORY_ROLE_DELAY_TICKS;
            if (observation->factory_marker == UINT8_C(0x5a)) {
                plan->schedule_factory_role_timer_a = true;
                if (observation->phone_connection == R1_INVALID_CONNECTION) {
                    plan->request_no_phone_advertising_policy = true;
                } else {
                    plan->schedule_factory_role_timer_b = true;
                }
            }
            plan->store_latest_connection = true;
            plan->register_link_context =
                observation->free_link_slot_available;
            plan->enter_fail_stop_on_link_context_error =
                observation->free_link_slot_available &&
                !observation->link_context_initialization_succeeded;
            break;

        case R1_GAP_EVT_DISCONNECTED:
            plan->route = R1_GAP_EVENT_DISCONNECTED;
            plan->cancel_connection_timeout = true;
            plan->cancel_role_timers = true;
            plan->clear_connection_latch = true;
            plan->release_link_context = true;
            plan->clear_peer_record = observation->connection < 3u;
            plan->query_peripheral_link_count = true;
            plan->disconnect_reason = observation->event_byte8;
            plan->publish_disconnect_status = true;
            if (observation->connection == observation->glasses_connection) {
                plan->disconnected_role = R1_GAP_DISCONNECTED_GLASSES;
                plan->reset_glasses_transport = true;
                plan->clear_glasses_connection = true;
            } else if (observation->connection ==
                       observation->phone_connection) {
                plan->disconnected_role = R1_GAP_DISCONNECTED_PHONE;
                plan->apply_phone_disconnect_policy = true;
                plan->clear_phone_connection = true;
            } else {
                plan->disconnected_role = R1_GAP_DISCONNECTED_UNASSIGNED;
            }
            plan->inspect_advertising_tx_power =
                observation->advertising_tx_power_configured;
            plan->enter_fail_stop_on_tx_power_error =
                observation->advertising_tx_power_configured &&
                observation->advertising_tx_power_status != 0u &&
                observation->advertising_tx_power_status != 8u;
            plan->start_advertising = true;
            plan->advertising_mode = R1_ADVERTISING_MODE_DIRECTED_OR_FAST;
            plan->schedule_advertising_retry =
                observation->advertising_start_status != 0u;
            plan->advertising_retry_ticks = plan->schedule_advertising_retry
                ? R1_GAP_ADVERTISING_RETRY_TICKS : 0u;
            plan->clear_latest_connection = true;
            break;

        case R1_GAP_EVT_PHY_UPDATE_REQUEST:
            plan->route = R1_GAP_EVENT_PHY_UPDATE_REQUEST;
            plan->request_phy_update = true;
            plan->use_glasses_local_phy_preference =
                observation->connection == observation->glasses_connection;
            if (plan->use_glasses_local_phy_preference) {
                plan->transmit_phy = observation->event_byte9;
                plan->receive_phy = observation->event_byte8;
            } else {
                plan->transmit_phy = 1u;
                plan->receive_phy = 1u;
            }
            break;

        case R1_GAP_EVT_PHY_UPDATE:
            plan->route = R1_GAP_EVENT_PHY_UPDATE_COMPLETE;
            if (observation->event_byte8 != 0u) {
                plan->phy_result = R1_GAP_PHY_RESULT_FAILED;
            } else if (observation->event_byte9 == 4u ||
                       observation->event_byte10 == 4u) {
                plan->phy_result = R1_GAP_PHY_RESULT_CODED;
            } else {
                plan->phy_result = R1_GAP_PHY_RESULT_NON_CODED;
            }
            break;

        case R1_GATTC_EVT_TIMEOUT:
            plan->route = R1_GAP_EVENT_GATTC_TIMEOUT;
            plan->log_gatt_timeout = true;
            break;

        case R1_GATTS_EVT_TIMEOUT:
            plan->route = R1_GAP_EVENT_GATTS_TIMEOUT;
            plan->log_gatt_timeout = true;
            break;

        default:
            plan->route = R1_GAP_EVENT_IGNORE;
            break;
    }
    return R1_OK;
}

r1_error r1_nfc_charge_task_plan_build(
    const r1_nfc_charge_task_observation *observation,
    r1_nfc_charge_task_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_nfc_charge_task_plan){0};
    const uint32_t flags = observation->event_flags;

    plan->wait_for_message =
        (flags & R1_NFC_CHARGE_EVENT_MESSAGE_PENDING) != 0u;
    plan->message_bytes = plan->wait_for_message
        ? R1_NFC_CHARGE_MESSAGE_BYTES : 0u;

    plan->set_charged_notification =
        (flags & R1_NFC_CHARGE_EVENT_CHARGED_NOTIFICATION) != 0u;
    plan->run_standard_command_irq_sequence =
        (flags & R1_NFC_CHARGE_EVENT_STANDARD_COMMAND_IRQ) != 0u;
    plan->open_touch = plan->set_charged_notification ||
        plan->run_standard_command_irq_sequence;
    if (plan->run_standard_command_irq_sequence) {
        plan->clear_nfc_field_seen = true;
        plan->st25_dynamic_register =
            R1_NFC_CHARGE_ST25_DYNAMIC_REGISTER;
        plan->standard_command_register_value = 1u;
        plan->standard_command_delay_ticks =
            R1_NFC_CHARGE_STANDARD_DELAY_TICKS;
    }

    plan->run_not_charging_sequence =
        (flags & R1_NFC_CHARGE_EVENT_NOT_CHARGING) != 0u;
    if (plan->run_not_charging_sequence) {
        plan->close_touch = true;
        plan->reset_battery_charge_latches = true;
        plan->st25_dynamic_register =
            R1_NFC_CHARGE_ST25_DYNAMIC_REGISTER;
        plan->not_charging_register_value = 0u;
        plan->not_charging_delay_ticks =
            R1_NFC_CHARGE_NOT_CHARGING_DELAY_TICKS;
        plan->temperature_retry_delay_ticks =
            R1_NFC_CHARGE_TEMPERATURE_RETRY_TICKS;
        for (uint8_t index = 0u;
             index < R1_NFC_CHARGE_TEMPERATURE_ATTEMPTS; ++index) {
            ++plan->temperature_id_read_count;
            if (observation->temperature_ids[index][0] == UINT8_C(0x50) &&
                observation->temperature_ids[index][1] == UINT8_C(0x50)) {
                plan->temperature_ids_valid = true;
                plan->temperature_successful_attempt = index;
                break;
            }
            ++plan->temperature_retry_delay_count;
        }
        plan->enable_watchdog_reset = !plan->temperature_ids_valid;
    }

    plan->clear_charged_notification =
        (flags & R1_NFC_CHARGE_EVENT_CHARGED_NOTIFICATION_CLEAR) != 0u;
    plan->dispatch_pmic_charge_event =
        (flags & R1_NFC_CHARGE_EVENT_PMIC_CHARGE) != 0u;
    plan->pmic_charge_event = plan->dispatch_pmic_charge_event
        ? UINT8_C(0x5a) : 0u;
    plan->report_charging_battery_percent =
        (flags & R1_NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATE) != 0u;
    if (plan->report_charging_battery_percent &&
        observation->battery_percent == 0u) {
        plan->charging_zero_battery_update_calls =
            R1_NFC_CHARGE_ZERO_BATTERY_UPDATE_COUNT;
        plan->charging_zero_battery_update_delay_ticks =
            R1_NFC_CHARGE_ZERO_BATTERY_UPDATE_TICKS;
    }
    plan->periodic_battery_update_calls =
        (flags & R1_NFC_CHARGE_EVENT_BATTERY_UPDATE) != 0u ? 1u : 0u;

    plan->terminate_task =
        (flags & R1_NFC_CHARGE_EVENT_TERMINATE) != 0u;
    plan->release_task_synchronization = plan->terminate_task;
    plan->deregister_watchdog = plan->terminate_task;
    plan->terminal_delay_ticks = plan->terminate_task
        ? R1_RUNTIME_WAIT_FOREVER : 0u;
    return R1_OK;
}

r1_buttonless_dfu_event_plan r1_runtime_plan_buttonless_dfu_event(
    uint32_t event_type) {
    r1_buttonless_dfu_event_plan plan = {
        R1_BUTTONLESS_DFU_UNKNOWN, false, false, false
    };
    switch (event_type) {
        case 0u:
            plan.diagnostic = R1_BUTTONLESS_DFU_PREPARE;
            plan.disable_advertising_on_disconnect = true;
            plan.disconnect_all_connected_links = true;
            plan.report_disconnected_link_count = true;
            break;
        case 1u:
            plan.diagnostic = R1_BUTTONLESS_DFU_ENTER;
            break;
        case 2u:
            plan.diagnostic = R1_BUTTONLESS_DFU_ENTER_FAILED;
            break;
        case 3u:
            plan.diagnostic = R1_BUTTONLESS_DFU_RESPONSE_SEND_ERROR;
            break;
        default:
            break;
    }
    return plan;
}

r1_error r1_bae8_plan_hvx_result(
    bool serialized_path, bool credit_acquired, r1_tx_status status,
    uint8_t completed_retries, r1_bae8_hvx_retry_plan *plan) {
    if (plan == NULL || status > R1_TX_DROP) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_bae8_hvx_retry_plan){0};
    plan->release_credit = credit_acquired && status != R1_TX_SENT;
    plan->retry_once = serialized_path && credit_acquired &&
        status == R1_TX_RESOURCES && completed_retries == 0u;
    plan->retry_delay_ticks = plan->retry_once
        ? R1_EUS_RESOURCE_RETRY_TICKS : 0u;
    return R1_OK;
}

static void runtime_write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static r1_error runtime_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    if (output == NULL || allocation_bytes == NULL ||
        (payload_length != 0u && payload == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length > SIZE_MAX - 15u || payload_length > UINT32_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t required = (payload_length + 15u) & ~(size_t)3u;
    if (output_capacity < required) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t index = 0u; index < required; ++index) {
        output[index] = 0u;
    }
    runtime_write_u32(output, message_type);
    runtime_write_u32(output + 4u, context);
    runtime_write_u32(output + 8u, (uint32_t)payload_length);
    for (size_t index = 0u; index < payload_length; ++index) {
        output[R1_BLE_THREAD_MESSAGE_HEADER_BYTES + index] = payload[index];
    }
    *allocation_bytes = required;
    return R1_OK;
}

r1_error r1_ble_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    return runtime_thread_message_encode(
        message_type, context, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

static r1_error runtime_ble_tx_queue_dispatch_encode(
    uint32_t dispatch_type, uint32_t message_identifier,
    const uint8_t *payload, size_t payload_length, uint8_t *output,
    size_t output_capacity, size_t *allocation_bytes) {
    return r1_ble_thread_message_encode(
        message_identifier, dispatch_type, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_ble_tx_queue_dispatch_type0(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes) {
    return runtime_ble_tx_queue_dispatch_encode(
        0u, message_identifier, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_ble_tx_queue_dispatch_type1(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes) {
    return runtime_ble_tx_queue_dispatch_encode(
        1u, message_identifier, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_ble_tx_queue_dispatch_type2(
    uint32_t message_identifier, const uint8_t *payload, size_t payload_length,
    uint8_t *output, size_t output_capacity, size_t *allocation_bytes) {
    return runtime_ble_tx_queue_dispatch_encode(
        2u, message_identifier, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_factory_thread_message_encode(
    uint32_t message_type, uint32_t context, const uint8_t *payload,
    size_t payload_length, uint8_t *output, size_t output_capacity,
    size_t *allocation_bytes) {
    return runtime_thread_message_encode(
        message_type, context, payload, payload_length, output,
        output_capacity, allocation_bytes);
}

r1_error r1_peripheral_watchdog_plan_step(
    uint8_t previous_counter, uint32_t peripheral_connection_count,
    bool right_handle_valid, bool left_handle_valid,
    int advertising_stop_result, int advertising_start_result,
    r1_peripheral_watchdog_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_peripheral_watchdog_plan){
        .next_counter = previous_counter == UINT8_C(0xfe)
                            ? 0u
                            : (uint8_t)(previous_counter + 1u),
        .report_link_count =
            (previous_counter % R1_PERIPHERAL_WATCHDOG_LOG_PERIOD) == 0u,
        .schedule_next_check = true,
        .advertising_mode = R1_ADVERTISING_MODE_DIRECTED_OR_FAST,
        .next_delay_ticks = R1_PERIPHERAL_WATCHDOG_DELAY_TICKS,
    };
    if (peripheral_connection_count > 1u) {
        return R1_OK;
    }
    if (right_handle_valid && left_handle_valid) {
        plan->connection_invariant_violation = true;
        plan->schedule_next_check = false;
        return R1_OK;
    }
    if (advertising_stop_result == 0) {
        plan->cancel_pending_restart = true;
        plan->start_advertising = true;
        plan->report_advertising_start_failure =
            advertising_start_result != 0;
    }
    return R1_OK;
}

r1_error r1_glasses_status_plan_command(
    bool command_valid, uint8_t status_bits, bool previous_worn,
    bool previous_secondary_mode, bool dcdc_policy_enabled,
    r1_glasses_status_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_glasses_status_plan){.response_length = 7u};
    if (!command_valid) {
        return R1_OK;
    }
    const bool worn = (status_bits & UINT8_C(0x80)) != 0u;
    const bool secondary = (status_bits & UINT8_C(0x40)) != 0u;
    plan->wear_changed = worn != previous_worn;
    plan->secondary_mode_changed = secondary != previous_secondary_mode;
    if (plan->wear_changed) {
        plan->cancel_slow_event = true;
        if (worn) {
            plan->open_touch = true;
            if (!dcdc_policy_enabled) {
                plan->cancel_dcdc_event = true;
                plan->disable_dcdc_now = true;
            }
        } else {
            plan->schedule_slow_event = true;
            plan->slow_delay_ticks = R1_GLASSES_SLOW_DELAY_TICKS;
            if (!dcdc_policy_enabled) {
                plan->cancel_dcdc_event = true;
                plan->schedule_dcdc_enable = true;
                plan->dcdc_delay_ticks = R1_GLASSES_DCDC_DELAY_TICKS;
            }
        }
    }
    if (plan->secondary_mode_changed) {
        plan->set_touch_fast_mode = secondary;
        plan->set_ble_slow_mode = !secondary;
    }
    return R1_OK;
}

void r1_runtime_initialize(r1_runtime *runtime,
                           r1_runtime_transmit_fn transmit,
                           void *transmit_context) {
    if (runtime == NULL) {
        return;
    }
    r1_state_initialize(&runtime->device);
    r1_battery_controller_initialize(
        &runtime->battery, 0u, runtime->device.battery_percent,
        runtime->device.charge);
    r1_event_plane_initialize(&runtime->events);
    runtime->transmit = transmit;
    runtime->transmit_context = transmit_context;
    runtime->enqueue = NULL;
    runtime->enqueue_context = NULL;
    runtime->queue_idle = NULL;
    runtime->queue_idle_context = NULL;
    runtime->lock = NULL;
    runtime->unlock = NULL;
    runtime->lock_context = NULL;
    runtime->role_handler = NULL;
    runtime->role_context = NULL;
    runtime->touch_handler = NULL;
    runtime->touch_context = NULL;
    runtime->settings_handler = NULL;
    runtime->settings_context = NULL;
    runtime->health_settings_handler = NULL;
    runtime->health_settings_context = NULL;
    runtime->request_observer = NULL;
    runtime->request_observer_context = NULL;
    runtime->automatic_health_pending_mask = 0u;
    runtime->automatic_health_next_leg = 0u;
    runtime->automatic_health_batch_timestamp = 0u;
    runtime->automatic_health_legs_scheduled = 0u;
    runtime->automatic_health_legs_enqueued = 0u;
    runtime->automatic_health_leg_failures = 0u;
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        runtime->links[index].active = false;
        runtime->links[index].connection = R1_INVALID_CONNECTION;
        runtime->links[index].session.encrypted = false;
        runtime->links[index].session.bonded = false;
        runtime->links[index].session.authorized = false;
        runtime->links[index].session.role = R1_ROLE_UNASSIGNED;
        r1_reassembler_reset(&runtime->links[index].reassembler);
    }
}

void r1_runtime_configure_battery(r1_runtime *runtime, uint8_t battery_type) {
    if (runtime != NULL) {
        r1_battery_controller_set_type(&runtime->battery, battery_type);
    }
}

bool r1_runtime_update_battery(
    r1_runtime *runtime, r1_charge_state charge,
    uint16_t millivolts, uint32_t elapsed_seconds) {
    if (runtime == NULL || !r1_battery_controller_update(
            &runtime->battery, charge, millivolts, elapsed_seconds)) {
        return false;
    }
    runtime->device.battery_percent = runtime->battery.percent;
    runtime->device.charge = runtime->battery.charge;
    return true;
}

static r1_runtime_link *authenticated_phone_link(r1_runtime *runtime) {
    if (runtime == NULL) {
        return NULL;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        r1_runtime_link *link = &runtime->links[index];
        if (link->active && link->session.role == R1_ROLE_PHONE &&
            link->session.encrypted && link->session.bonded &&
            link->session.authorized) {
            return link;
        }
    }
    return NULL;
}

r1_health_auto_sync_result r1_runtime_run_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context) {
    if (runtime != NULL) {
        return r1_health_run_automatic_sync(
            &runtime->device.health,
            authenticated_phone_link(runtime) != NULL, now_seconds,
            emit, emit_context);
    }
    return r1_health_run_automatic_sync(
        NULL, false, now_seconds, emit, emit_context);
}

static void schedule_automatic_health_leg(
    void *context, r1_health_auto_sync_leg leg, uint8_t serial) {
    r1_runtime *runtime = context;
    if (runtime == NULL || serial != R1_HEALTH_AUTO_SYNC_SERIAL ||
        leg > R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP) {
        return;
    }
    const uint8_t bit = (uint8_t)(1u << (uint8_t)leg);
    if ((runtime->automatic_health_pending_mask & bit) == 0u) {
        runtime->automatic_health_pending_mask |= bit;
        ++runtime->automatic_health_legs_scheduled;
    }
}

r1_health_auto_sync_result r1_runtime_schedule_automatic_health_sync(
    r1_runtime *runtime, uint32_t now_seconds) {
    if (!runtime_lock(runtime)) {
        return (r1_health_auto_sync_result){
            R1_HEALTH_AUTO_SYNC_INVALID, false, false, 0u,
        };
    }
    const r1_health_auto_sync_result result =
        r1_runtime_run_automatic_health_sync(
        runtime, now_seconds, schedule_automatic_health_leg, runtime);
    if (runtime != NULL && result.batch_started) {
        runtime->automatic_health_batch_timestamp = now_seconds;
    }
    runtime_unlock(runtime);
    return result;
}

void r1_runtime_set_role_handler(r1_runtime *runtime,
                                 r1_runtime_role_fn role_handler,
                                 void *role_context) {
    if (runtime != NULL) {
        runtime->role_handler = role_handler;
        runtime->role_context = role_context;
    }
}

void r1_runtime_set_touch_handler(r1_runtime *runtime,
                                  r1_runtime_touch_fn touch_handler,
                                  void *touch_context) {
    if (runtime != NULL) {
        runtime->touch_handler = touch_handler;
        runtime->touch_context = touch_context;
    }
}

void r1_runtime_set_settings_handler(r1_runtime *runtime,
                                     r1_runtime_settings_fn settings_handler,
                                     void *settings_context) {
    if (runtime != NULL) {
        runtime->settings_handler = settings_handler;
        runtime->settings_context = settings_context;
    }
}

void r1_runtime_set_health_settings_handler(
    r1_runtime *runtime,
    r1_runtime_health_settings_fn health_settings_handler,
    void *health_settings_context) {
    if (runtime != NULL) {
        runtime->health_settings_handler = health_settings_handler;
        runtime->health_settings_context = health_settings_context;
    }
}

void r1_runtime_set_request_observer(
    r1_runtime *runtime, r1_runtime_request_observer_fn observer,
    void *observer_context) {
    if (runtime != NULL) {
        runtime->request_observer = observer;
        runtime->request_observer_context = observer_context;
    }
}

void r1_runtime_set_transmit(r1_runtime *runtime,
                             r1_runtime_transmit_fn transmit,
                             void *transmit_context) {
    if (runtime != NULL) {
        runtime->transmit = transmit;
        runtime->transmit_context = transmit_context;
    }
}

void r1_runtime_set_enqueue(r1_runtime *runtime,
                            r1_runtime_enqueue_fn enqueue,
                            void *enqueue_context) {
    if (runtime != NULL) {
        runtime->enqueue = enqueue;
        runtime->enqueue_context = enqueue_context;
    }
}

void r1_runtime_set_queue_idle(r1_runtime *runtime,
                               r1_runtime_queue_idle_fn queue_idle,
                               void *queue_idle_context) {
    if (runtime != NULL) {
        runtime->queue_idle = queue_idle;
        runtime->queue_idle_context = queue_idle_context;
    }
}

void r1_runtime_set_lock(r1_runtime *runtime, r1_runtime_lock_fn lock,
                         r1_runtime_unlock_fn unlock, void *lock_context) {
    if (runtime != NULL && ((lock == NULL) == (unlock == NULL))) {
        runtime->lock = lock;
        runtime->unlock = unlock;
        runtime->lock_context = lock_context;
    }
}

static bool runtime_lock(r1_runtime *runtime) {
    return runtime != NULL && (runtime->lock == NULL ||
        runtime->lock(runtime->lock_context));
}

static void runtime_unlock(r1_runtime *runtime) {
    if (runtime != NULL && runtime->unlock != NULL) {
        runtime->unlock(runtime->lock_context);
    }
}

static r1_error connect_unlocked(r1_runtime *runtime, uint16_t connection) {
    if (runtime == NULL || connection == R1_INVALID_CONNECTION) {
        return R1_ERROR_ARGUMENT;
    }
    if (find_link(runtime, connection) != NULL) {
        return R1_OK;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        r1_runtime_link *link = &runtime->links[index];
        if (!link->active) {
            link->active = true;
            link->connection = connection;
            link->session.encrypted = false;
            link->session.bonded = false;
            link->session.authorized = false;
            link->session.role = R1_ROLE_UNASSIGNED;
            r1_reassembler_reset(&link->reassembler);
            return R1_OK;
        }
    }
    return R1_ERROR_CAPACITY;
}

static void disconnect_unlocked(r1_runtime *runtime, uint16_t connection) {
    if (runtime == NULL) {
        return;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link != NULL) {
        const bool was_phone = link->session.role == R1_ROLE_PHONE;
        link->active = false;
        link->connection = R1_INVALID_CONNECTION;
        link->session.encrypted = false;
        link->session.bonded = false;
        link->session.authorized = false;
        link->session.role = R1_ROLE_UNASSIGNED;
        r1_reassembler_reset(&link->reassembler);
        if (was_phone) {
            runtime->automatic_health_pending_mask = 0u;
            runtime->automatic_health_next_leg = 0u;
            runtime->automatic_health_batch_timestamp = 0u;
        }
    }
    r1_event_remove_connection(&runtime->events, connection);
}

static r1_error set_security_unlocked(
    r1_runtime *runtime, uint16_t connection,
    bool encrypted, bool bonded, bool authorized) {
    if (runtime == NULL || (authorized && (!encrypted || !bonded))) {
        return R1_ERROR_ARGUMENT;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link == NULL) {
        return R1_ERROR_STATE;
    }
    link->session.encrypted = encrypted;
    link->session.bonded = bonded;
    link->session.authorized = authorized;
    return R1_OK;
}

r1_error r1_runtime_connect(r1_runtime *runtime, uint16_t connection) {
    if (runtime == NULL || connection == R1_INVALID_CONNECTION) {
        return R1_ERROR_ARGUMENT;
    }
    if (!runtime_lock(runtime)) {
        return R1_ERROR_STATE;
    }
    const r1_error error = connect_unlocked(runtime, connection);
    runtime_unlock(runtime);
    return error;
}

void r1_runtime_disconnect(r1_runtime *runtime, uint16_t connection) {
    if (!runtime_lock(runtime)) {
        return;
    }
    disconnect_unlocked(runtime, connection);
    runtime_unlock(runtime);
}

r1_error r1_runtime_set_security(r1_runtime *runtime, uint16_t connection,
                                 bool encrypted, bool bonded, bool authorized) {
    if (runtime == NULL || (authorized && (!encrypted || !bonded))) {
        return R1_ERROR_ARGUMENT;
    }
    if (!runtime_lock(runtime)) {
        return R1_ERROR_STATE;
    }
    const r1_error error = set_security_unlocked(
        runtime, connection, encrypted, bonded, authorized);
    runtime_unlock(runtime);
    return error;
}

r1_peer_role r1_runtime_connection_role(const r1_runtime *runtime,
                                        uint16_t connection) {
    if (runtime == NULL) {
        return R1_ROLE_UNASSIGNED;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        if (runtime->links[index].active &&
            runtime->links[index].connection == connection) {
            return runtime->links[index].session.role;
        }
    }
    return R1_ROLE_UNASSIGNED;
}

void r1_runtime_role_occupancy(const r1_runtime *runtime,
                               bool *phone_occupied, bool *glasses_occupied) {
    if (phone_occupied != NULL) {
        *phone_occupied = false;
    }
    if (glasses_occupied != NULL) {
        *glasses_occupied = false;
    }
    if (runtime == NULL) {
        return;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        const r1_runtime_link *link = &runtime->links[index];
        if (!link->active) {
            continue;
        }
        if (link->session.role == R1_ROLE_PHONE && phone_occupied != NULL) {
            *phone_occupied = true;
        }
        if (link->session.role == R1_ROLE_GLASSES && glasses_occupied != NULL) {
            *glasses_occupied = true;
        }
    }
}

static size_t fragment_count(size_t logical_length) {
    return logical_length / R1_FRAGMENT_PAYLOAD_MAX + 1u;
}

static r1_error commit_role_change(r1_runtime *runtime, r1_runtime_link *link,
                                   r1_peer_role previous_role) {
    if (link->session.role == previous_role) {
        return R1_OK;
    }
    if (previous_role != R1_ROLE_UNASSIGNED ||
        link->session.role == R1_ROLE_UNASSIGNED) {
        link->session.role = previous_role;
        return R1_ERROR_STATE;
    }
    for (size_t index = 0u; index < R1_RUNTIME_LINK_MAX; ++index) {
        const r1_runtime_link *other = &runtime->links[index];
        if (other != link && other->active &&
            other->session.role == link->session.role) {
            link->session.role = previous_role;
            return R1_ERROR_STATE;
        }
    }
    if (runtime->role_handler != NULL) {
        const r1_error error = runtime->role_handler(
            runtime->role_context, link->connection, link->session.role);
        if (error != R1_OK) {
            link->session.role = previous_role;
            return error;
        }
    }
    return R1_OK;
}

static r1_error enqueue_dispatch(r1_runtime *runtime, uint16_t connection) {
    size_t required = 0u;
    for (size_t index = 0u; index < runtime->dispatch_scratch.count; ++index) {
        required += fragment_count(runtime->dispatch_scratch.lengths[index]);
    }
    if (required > runtime->events.eus.capacity - runtime->events.eus.count) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t response = 0u; response < runtime->dispatch_scratch.count; ++response) {
        r1_error error = r1_fragment_message(
            runtime->dispatch_scratch.models[response],
            runtime->dispatch_scratch.lengths[response],
            &runtime->fragment_scratch);
        if (error != R1_OK) {
            return error;
        }
        for (size_t index = 0u; index < runtime->fragment_scratch.count; ++index) {
            const r1_fragment *fragment = &runtime->fragment_scratch.fragments[index];
            r1_tx_event event = {0};
            event.connection = connection;
            event.channel = 2u;
            event.length = fragment->length;
            for (size_t byte = 0u; byte < fragment->length; ++byte) {
                event.bytes[byte] = fragment->bytes[byte];
            }
            error = runtime->enqueue == NULL
                ? r1_event_enqueue(&runtime->events, true, &event)
                : runtime->enqueue(runtime->enqueue_context, true, &event,
                                   R1_TX_ENQUEUE_WAIT_TICKS);
            if (error != R1_OK) {
                return error;
            }
        }
    }
    return R1_OK;
}

static r1_error service_automatic_health_sync_unlocked(r1_runtime *runtime) {
    if (runtime == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (runtime->automatic_health_pending_mask == 0u) {
        return R1_OK;
    }
    /* A complete daily leg can consume almost the entire recovered 50-record
     * shared queue (sixteen 632-byte sleep sessions need 49 fragments with
     * their response).  Starting only from an empty queue preserves that
     * bound and makes each leg atomic at queue admission. */
    const bool shared_queue_idle = runtime->enqueue == NULL
        ? runtime->events.eus.count == 0u
        : runtime->queue_idle != NULL && runtime->queue_idle(
            runtime->queue_idle_context, true);
    if (!shared_queue_idle) {
        return R1_ERROR_STATE;
    }
    r1_runtime_link *link = authenticated_phone_link(runtime);
    if (link == NULL) {
        return R1_ERROR_UNAUTHORIZED;
    }

    uint8_t selected = runtime->automatic_health_next_leg;
    for (uint8_t checked = 0u; checked <= R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP;
         ++checked) {
        if (selected > R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP) {
            selected = 0u;
        }
        if ((runtime->automatic_health_pending_mask &
             (uint8_t)(1u << selected)) != 0u) {
            break;
        }
        ++selected;
    }
    if (selected > R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP ||
        (runtime->automatic_health_pending_mask &
         (uint8_t)(1u << selected)) == 0u) {
        ++runtime->automatic_health_leg_failures;
        runtime->automatic_health_pending_mask = 0u;
        runtime->automatic_health_next_leg = 0u;
        return R1_ERROR_STATE;
    }

    static const uint8_t commands[] = {1u, 2u, 4u, 5u, 6u};
    const r1_model request = {
        R1_PROTOCOL_VERSION, 2u, R1_MODULE_VERSION,
        R1_HEALTH_AUTO_SYNC_SERIAL, 0u, commands[selected], 1u,
        NULL, 0u,
    };
    const r1_error dispatch_error = r1_dispatch(
        &runtime->device, &link->session, &request,
        &runtime->dispatch_scratch);
    /* dispatch_health shares the public query path and therefore applies the
     * explicit-query cooldown reset.  Automatic legs are not queries: retain
     * the batch timestamp written by the recovered common gate. */
    runtime->device.health.last_auto_sync_or_query_seconds =
        runtime->automatic_health_batch_timestamp;
    const r1_error enqueue_error = enqueue_dispatch(runtime, link->connection);
    if (enqueue_error != R1_OK) {
        ++runtime->automatic_health_leg_failures;
        return enqueue_error;
    }

    runtime->automatic_health_pending_mask &=
        (uint8_t)~(uint8_t)(1u << selected);
    runtime->automatic_health_next_leg = (uint8_t)(selected + 1u);
    if (runtime->automatic_health_pending_mask == 0u) {
        runtime->automatic_health_next_leg = 0u;
    }
    ++runtime->automatic_health_legs_enqueued;
    if (dispatch_error != R1_OK) {
        ++runtime->automatic_health_leg_failures;
    }
    return dispatch_error;
}

r1_error r1_runtime_service_automatic_health_sync(r1_runtime *runtime) {
    if (runtime == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!runtime_lock(runtime)) {
        return R1_ERROR_STATE;
    }
    const r1_error error = service_automatic_health_sync_unlocked(runtime);
    runtime_unlock(runtime);
    return error;
}

static r1_error receive_eus_unlocked(r1_runtime *runtime, uint16_t connection,
                                     const uint8_t *value, size_t length) {
    if (runtime == NULL || value == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    r1_runtime_link *link = find_link(runtime, connection);
    if (link == NULL) {
        return R1_ERROR_STATE;
    }
    r1_error error = R1_OK;
    const r1_reassembly_status status = r1_reassembler_feed(
        &link->reassembler, value, length, &error);
    if (status == R1_REASSEMBLY_WAITING) {
        return R1_OK;
    }
    if (status == R1_REASSEMBLY_REJECTED) {
        return error;
    }

    r1_model request;
    error = r1_model_decode(link->reassembler.bytes, link->reassembler.length,
                            R1_CHECKSUM_PHONE_COMPACT_CCITT, &request);
    if (error != R1_OK) {
        return error;
    }
    if (runtime->request_observer != NULL) {
        runtime->request_observer(
            runtime->request_observer_context, &request);
    }
    const r1_peer_role previous_role = link->session.role;
    const bool previous_touch_enabled = runtime->device.touch_enabled;
    uint8_t previous_settings[R1_SYSTEM_SETTINGS_BYTES];
    for (size_t index = 0u; index < R1_SYSTEM_SETTINGS_BYTES; ++index) {
        previous_settings[index] = runtime->device.system_settings[index];
    }
    r1_health_settings_record previous_health_settings = {
        .timestamp_seconds = (uint32_t)runtime->device.health_settings[0]
            | ((uint32_t)runtime->device.health_settings[1] << 8u)
            | ((uint32_t)runtime->device.health_settings[2] << 16u)
            | ((uint32_t)runtime->device.health_settings[3] << 24u),
        .enabled = (uint8_t)(runtime->device.health_settings[4] != 0u),
        .reserved = {0u},
    };
    const r1_error dispatch_error = r1_dispatch(
        &runtime->device, &link->session, &request, &runtime->dispatch_scratch);
    const r1_error role_error = commit_role_change(runtime, link, previous_role);
    if (runtime->touch_handler != NULL &&
        runtime->device.touch_enabled != previous_touch_enabled) {
        runtime->touch_handler(
            runtime->touch_context, runtime->device.touch_enabled);
    }
    if (runtime->settings_handler != NULL) {
        bool settings_changed = false;
        for (size_t index = 0u; index < R1_SYSTEM_SETTINGS_BYTES; ++index) {
            settings_changed = settings_changed ||
                runtime->device.system_settings[index] !=
                    previous_settings[index];
        }
        if (settings_changed) {
            runtime->settings_handler(
                runtime->settings_context, runtime->device.system_settings);
        }
    }
    error = enqueue_dispatch(runtime, connection);
    if (error != R1_OK) {
        return error;
    }
    if (dispatch_error == R1_OK && runtime->health_settings_handler != NULL &&
        request.module == R1_MODULE_SYSTEM &&
        request.command == R1_COMMAND_SYSTEM &&
        request.subcommand == 0x0eu && (request.status & 0x02u) != 0u) {
        r1_health_settings_command_plan health_settings_plan;
        if (r1_health_settings_plan_command(
                true, &previous_health_settings, request.payload,
                request.payload_length, &health_settings_plan) == R1_OK) {
            runtime->health_settings_handler(
                runtime->health_settings_context, &health_settings_plan);
        }
    }
    return role_error != R1_OK ? role_error : dispatch_error;
}

r1_error r1_runtime_receive_eus(r1_runtime *runtime, uint16_t connection,
                                const uint8_t *value, size_t length) {
    if (runtime == NULL || value == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!runtime_lock(runtime)) {
        return R1_ERROR_STATE;
    }
    const r1_error error = receive_eus_unlocked(
        runtime, connection, value, length);
    runtime_unlock(runtime);
    return error;
}

void r1_runtime_hvn_complete(r1_runtime *runtime, uint8_t completed) {
    if (runtime_lock(runtime)) {
        r1_event_complete(&runtime->events, completed);
        runtime_unlock(runtime);
    }
}

static bool tick_reached(uint32_t now_tick, uint32_t deadline_tick) {
    return now_tick - deadline_tick < UINT32_C(0x80000000);
}

static uint32_t ticks_until(uint32_t now_tick, uint32_t deadline_tick) {
    return tick_reached(now_tick, deadline_tick) ? 0u : deadline_tick - now_tick;
}

static uint32_t runtime_poll_unlocked(
    r1_runtime *runtime, uint32_t now_tick) {
    if (runtime == NULL || runtime->transmit == NULL) {
        return R1_RUNTIME_WAIT_FOREVER;
    }
    r1_tx_event *event;
    while ((event = r1_event_front(&runtime->events, true)) != NULL) {
        if (event->resource_retry_pending) {
            const uint32_t remaining = ticks_until(now_tick, event->deadline_tick);
            if (remaining != 0u) {
                return remaining;
            }
            event->resource_retry_pending = false;
        }
        if (runtime->events.hvn_credits == 0u) {
            if (!event->credit_wait_started) {
                event->credit_wait_started = true;
                event->deadline_tick = now_tick + R1_EUS_CREDIT_WAIT_TICKS;
            }
            const uint32_t remaining = ticks_until(now_tick, event->deadline_tick);
            if (remaining != 0u) {
                return remaining;
            }
            (void)r1_event_drop(&runtime->events, true);
            continue;
        }
        event->credit_wait_started = false;
        const r1_tx_status status = runtime->transmit(runtime->transmit_context, event);
        if (status == R1_TX_RESOURCES) {
            if (event->resource_retries == 0u) {
                event->resource_retries = 1u;
                event->resource_retry_pending = true;
                event->deadline_tick = now_tick + R1_EUS_RESOURCE_RETRY_TICKS;
                return R1_EUS_RESOURCE_RETRY_TICKS;
            }
            (void)r1_event_drop(&runtime->events, true);
            continue;
        }
        (void)r1_event_drop(&runtime->events, true);
        if (status == R1_TX_SENT) {
            (void)r1_event_consume_credit(&runtime->events);
        }
    }
    return R1_RUNTIME_WAIT_FOREVER;
}

uint32_t r1_runtime_poll(r1_runtime *runtime, uint32_t now_tick) {
    if (runtime == NULL || runtime->transmit == NULL ||
        !runtime_lock(runtime)) {
        return R1_RUNTIME_WAIT_FOREVER;
    }
    const uint32_t wait = runtime_poll_unlocked(runtime, now_tick);
    runtime_unlock(runtime);
    return wait;
}
