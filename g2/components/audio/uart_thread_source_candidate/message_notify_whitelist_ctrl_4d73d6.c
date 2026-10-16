/* Stock Apollo PB_RxNotifWhitelistCtrl 0x4d73d6 and state setter 0x4972b2. */
#include <stdint.h>

struct audio_message_notify_fault_4d73d6 {
    uint32_t type;
    uint32_t detail;
    const char *path;
    const char *function;
    uint32_t line;
};
_Static_assert(sizeof(struct audio_message_notify_fault_4d73d6) == 20u,
               "fault record ABI");

extern uint8_t audio_ble_ancc_service_state[]; /* native base 0x200036c8 */
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.notif";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_notification\\pb_service_notification.c";
static const char function[] = "PB_RxNotifWhitelistCtrl";
static const char null_message[] = "POINT NULL";
static const char null_compact[] = "[pb.notif]POINT NULL";
static const char disable_message[] = "whitelist_disable = %d";
static const char disable_compact[] = "[pb.notif]whitelist_disable = %d";
static const struct audio_message_notify_fault_4d73d6 fault_template = {
    0u, 0u, path, function, 0xf3u
};

void audio_message_notify_ancc_state_byte4_set_4972b2(uint8_t value) {
    audio_ble_ancc_service_state[4u] = value;
}

uint32_t audio_message_notify_rx_whitelist_ctrl_4d73d6(uint32_t id,
                                                          const uint8_t *body) {
    (void)id;
    if (body == 0) {
        struct audio_message_notify_fault_4d73d6 fault;
        audio_uart_checksum_copy(&fault, &fault_template, sizeof fault);
        fault.detail = (fault.detail & 0xffff0000u) | 1u;
        audio_ring_pb_assert_509b48(&fault);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0xf5u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_compact,
                                        null_compact);
        return 2u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0xf9u,
                           disable_message, body[0]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, disable_compact,
                                    disable_compact, body[0]);
    audio_message_notify_ancc_state_byte4_set_4972b2(body[0] != 0u);
    return 0u;
}
