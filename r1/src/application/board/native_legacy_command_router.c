/* Stock 0x4e258: BLE legacy command frame router. */
#include <stdint.h>

typedef uint32_t (*legacy_command_fn)(uint32_t, void *);

extern uint32_t r1_legacy_cmd_version_reply(uint32_t, void *);
extern uint32_t r1_legacy_cmd_battery_type_reply(uint32_t, void *);
extern uint32_t r1_legacy_bsn_verify_command(uint32_t, void *);
extern uint32_t r1_legacy_sn_verify_command(uint32_t, void *);
extern uint32_t r1_goodix_profile_2_command_adapter(uint32_t, void *);
extern uint32_t r1_goodix_profile_40_command_adapter(uint32_t, void *);
extern uint32_t r1_legacy_cmd_mac_compare_reply(uint32_t, void *);
extern uint32_t r1_system_control_command_37_plan(uint32_t, void *);
extern uint32_t r1_factory_aging_stream_command(uint32_t, void *);
extern uint32_t r1_legacy_pair_command_plan(uint32_t, void *);
extern uint32_t r1_glasses_status_plan_command(uint32_t, void *);
extern uint32_t r1_touch_long_press_time_command(uint32_t, void *);
extern uint32_t r1_legacy_cmd_ring_size_reply(uint32_t, void *);
extern uint32_t r1_legacy_cmd_cancel_event_reply(uint32_t, void *);
extern uint32_t r1_legacy_reply_status_ff(uint32_t, void *);
extern uint32_t r1_ati_calibration_command_plan(uint32_t, void *);
extern uint32_t r1_legacy_subcommand_plan(uint32_t, void *);
extern uint32_t r1_legacy_reply_nfc_field_seen(uint32_t, void *);
extern uint32_t r1_legacy_device_info_build(uint32_t, void *);
extern uint32_t r1_legacy_power_config_command(uint32_t, void *);
extern uint32_t r1_legacy_sn_derived_command(uint32_t, void *);
extern uint32_t r1_legacy_command_subdispatch(uint32_t, void *);
extern uint32_t r1_ble_thread_message_encode(uint32_t, uint32_t, uint32_t,
                                              const void *);
extern uint32_t r1_charge_state_byte_get(void);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *,
                                         const char *, ...);
extern void nrf_log_frontend_std_0(uint32_t, const char *);

static legacy_command_fn command_handler(uint8_t command)
{
    switch (command) {
    case 0x11: return r1_legacy_cmd_version_reply;
    case 0x12: return r1_legacy_cmd_battery_type_reply;
    case 0x21: return r1_legacy_bsn_verify_command;
    case 0x22: return r1_legacy_sn_verify_command;
    case 0x23: return r1_goodix_profile_2_command_adapter;
    case 0x24: return r1_goodix_profile_40_command_adapter;
    case 0x34: return r1_legacy_cmd_mac_compare_reply;
    case 0x37: return r1_system_control_command_37_plan;
    case 0x40: return r1_factory_aging_stream_command;
    case 0x52: return r1_legacy_reply_status_ff;
    case 0x53: return r1_legacy_subcommand_plan;
    case 0x54: return r1_legacy_reply_nfc_field_seen;
    case 0x55: return r1_legacy_device_info_build;
    case 0x56: return r1_legacy_power_config_command;
    case 0x57: return r1_legacy_cmd_ring_size_reply;
    case 0x85: return r1_legacy_pair_command_plan;
    case 0x89: return r1_glasses_status_plan_command;
    case 0x8a: return r1_touch_long_press_time_command;
    case 0x91: return r1_ati_calibration_command_plan;
    case 0x94: return r1_legacy_cmd_cancel_event_reply;
    case 0x95: return r1_legacy_sn_derived_command;
    case 0xf2: return r1_legacy_command_subdispatch;
    default: return 0;
    }
}

/* This helper keeps the stock copy and dispatch together for a host probe.
 * Stock clears 36 bytes, then copies the caller's unbounded length into the
 * fixed RAM scratch. The caller must provide the same writable span. */
static void copy_frame(uint8_t *scratch, const uint8_t *frame, uint32_t length)
{
    for (uint32_t i = 0; i < 36u; ++i)
        scratch[i] = 0u;
    for (uint32_t i = 0; i < length; ++i)
        scratch[i] = frame[i];
}

static uint32_t pair_authentication_command(uint32_t handle)
{
        static const char structured[] =
            "[RING]glasses BLE pair authentication command";
        static const char plain[] =
            "glasses BLE pair authentication command";
        if ((r1_structured_log_mode_get() & 1u) ||
            (r1_structured_log_mode_get() & 4u))
            (void)r1_structured_log_format(0x0c000000u, structured,
                                            structured);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_0(0x001c0003u, plain);
        uint8_t response = 2u;
        return r1_ble_thread_message_encode(handle, 2u, 1u, &response);
}

static uint32_t route_frame(uint8_t *scratch, uint32_t handle,
                            const uint8_t *frame, uint32_t length)
{
    copy_frame(scratch, frame, length);
    if (scratch[2] == 0x88u) {
        (void)pair_authentication_command(handle);
        return 0u;
    }

    legacy_command_fn handler = command_handler(scratch[2]);
    if (handler == 0)
        return UINT32_MAX;
    (void)handler(handle, scratch);
    return 0u;
}

/* Stock 0x625c0 uses the same scratch and child map. Its child branches are
 * tail calls, so this entry preserves their result instead of forcing zero. */
static uint32_t route_factory_frame(uint8_t *scratch, uint32_t handle,
                                    const uint8_t *frame, uint32_t length)
{
    copy_frame(scratch, frame, length);
    if (scratch[2] == 0x88u)
        return pair_authentication_command(handle);
    if (scratch[2] == 0x8bu) {
        scratch[4] = (uint8_t)r1_charge_state_byte_get();
        scratch[5] = 0u;
        return r1_legacy_bounded_reply_send(scratch, 6u);
    }
    legacy_command_fn handler = command_handler(scratch[2]);
    if (handler == 0)
        return scratch[2];
    return handler(handle, scratch);
}

uint32_t r1_legacy_command_route_frame(uint32_t handle, const void *frame,
                                        uint32_t length)
{
    return route_frame((uint8_t *)(uintptr_t)0x2001a174u, handle,
                       (const uint8_t *)frame, length);
}

uint32_t r1_factory_legacy_command_route_frame(uint32_t handle,
                                                const void *frame,
                                                uint32_t length)
{
    return route_factory_frame((uint8_t *)(uintptr_t)0x2001a174u, handle,
                               (const uint8_t *)frame, length);
}
