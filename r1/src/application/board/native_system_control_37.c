/* Stock 0x628f6: legacy system-control command 0x37. */
#include <stdint.h>
#include <stddef.h>

extern uint32_t r1_legacy_bounded_reply_send(const void *, uint32_t);
extern uint32_t r1_device_info_configuration_byte70_get(void);
extern uint32_t r1_kv_nv_r1_byte_set_c(uint32_t);
extern void r1_peers_delete_checked(void);
extern int32_t osDelay(uint32_t);
extern uint32_t r1_reset_trace_persist_tag_write(uint32_t);
extern _Noreturn void r1_manager_system_reset(void);
extern void r1_sysctl_op_sequence_thunk(void);
extern const char *r1_identity_data_ptr_get(void);
extern size_t strlen(const char *);
extern void *r1_native_memory_move(void *, const void *, size_t);

static uint32_t read32le(const uint8_t *bytes)
{
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8) |
           ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);
}

uint32_t r1_system_control_command_37_plan(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = packet;
    switch (bytes[3]) {
    case 0u:
        if (read32le(bytes + 4) < 60u) bytes[4] = 0u;
        return r1_legacy_bounded_reply_send(bytes, 5u);
    case 1u:
        return r1_legacy_bounded_reply_send(bytes, 8u);
    case 2u: {
        uint32_t previous = r1_device_info_configuration_byte70_get();
        (void)r1_kv_nv_r1_byte_set_c(0x5au);
        (void)r1_legacy_bounded_reply_send(bytes, 5u);
        r1_peers_delete_checked();
        (void)osDelay(200u);
        if (previous == 0x55u) {
            r1_sysctl_op_sequence_thunk();
            return 0u;
        }
        (void)r1_reset_trace_persist_tag_write(4u);
        r1_manager_system_reset();
    }
    case 3u:
        (void)r1_legacy_bounded_reply_send(bytes, 5u);
        if (bytes[4] == 1u) {
            (void)osDelay(200u);
            (void)r1_reset_trace_persist_tag_write(5u);
            r1_manager_system_reset();
        }
        return 0u;
    case 4u: {
        const char *identity = r1_identity_data_ptr_get();
        uint8_t length = (uint8_t)strlen(identity);
        (void)r1_native_memory_move(bytes + 4, identity, length);
        return r1_legacy_bounded_reply_send(bytes, (uint32_t)length + 4u);
    }
    case 5u:
        (void)r1_kv_nv_r1_byte_set_c(0x55u);
        (void)osDelay(200u);
        (void)r1_reset_trace_persist_tag_write(6u);
        r1_manager_system_reset();
    case 13u:
        return r1_legacy_bounded_reply_send(bytes, 10u);
    case 0xfdu:
    case 0xfeu:
        return r1_legacy_bounded_reply_send(bytes, 5u);
    case 0xffu:
        bytes[3] = 0xa0u;
        return 0u;
    default:
        return 0u;
    }
}
