/* Stock 0x92b98: pair request state and legacy seven-byte response. */
#include <stdint.h>

extern int32_t r1_native_delayed_cancel(void (*)(uint32_t), uint32_t);
extern void r1_legacy_pair_timeout_callback(uint32_t);
extern void r1_legacy_pair_hook_nop(uint32_t);
extern uint32_t r1_glasses_connection_handle_get(void);
extern void r1_glasses_connection_role_assign(uint32_t);
extern uint32_t r1_service_touch_open(uint32_t);
extern uint32_t r1_service_touch_close(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t, const char *,
                                         const char *, ...);
extern void nrf_log_frontend_std_2(uint32_t, const char *, uint32_t, uint32_t);
extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);

uint32_t r1_legacy_pair_command_plan(uint32_t handle, void *packet)
{
    static const char ring[] =
        "[RING]glasses is connected, can't connect 2 glasses,disconnect it. "
        "conn_handle: %d, glasses_conn_handle: %d";
    static const char plain[] =
        "glasses is connected, can't connect 2 glasses,disconnect it. "
        "conn_handle: %d, glasses_conn_handle: %d";
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] != 1u)
        return r1_legacy_bounded_reply_send(packet, 7u);

    uint32_t pair_value = bytes[4];
    (void)r1_native_delayed_cancel(r1_legacy_pair_timeout_callback, 0u);
    (void)r1_native_delayed_cancel(r1_legacy_pair_hook_nop, 0u);
    uint32_t current = r1_glasses_connection_handle_get();
    if (current != 0xffffu && current != handle) {
        if ((r1_structured_log_mode_get() & 1u) ||
            (r1_structured_log_mode_get() & 4u))
            (void)r1_structured_log_format(0x04800000u, ring, ring,
                                            handle, current);
        if (r1_structured_log_mode_get() & 2u)
            nrf_log_frontend_std_2(0x001c0001u, plain, handle, current);
        r1_legacy_pair_hook_nop(handle);
        return 0u;
    }

    if (pair_value != 0xffu)
        r1_glasses_connection_role_assign(handle);
    if (bytes[5] != 0xaau && bytes[6] != 0xaau && bytes[7] != 0xaau) {
        if (pair_value != 0xffu)
            (void)r1_service_touch_open(0u);
        else
            (void)r1_service_touch_close(0u);
    }
    bytes[4] = 1u;
    return r1_legacy_bounded_reply_send(packet, 7u);
}
