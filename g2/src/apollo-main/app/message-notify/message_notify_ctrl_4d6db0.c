/* Stock Apollo PB_RxNotifCtrl 0x4d6db0 and ANCC state getter 0x49729c. */
#include <stdint.h>

struct audio_message_notify_fault_4d6db0 {
    uint32_t type;
    uint32_t detail;
    const char *path;
    const char *function;
    uint32_t line;
};
_Static_assert(sizeof(struct audio_message_notify_fault_4d6db0) == 20u,
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
static const char function[] = "PB_RxNotifCtrl";
static const char null_message[] = "PORINT NULL";
static const char null_compact[] = "[pb.notif]PORINT NULL";
static const char state_message[] =
    "notif_enable = %d, auto_disp_enable = %d, disp_time = %d, avoid_disturb_enable = %d";
static const char state_compact[] =
    "[pb.notif]notif_enable = %d, auto_disp_enable = %d, disp_time = %d, avoid_disturb_enable = %d";
static const struct audio_message_notify_fault_4d6db0 fault_template = {
    0u, 0u, path, function, 0x67u
};

uint8_t *audio_message_notify_ancc_state_get_49729c(void) {
    return audio_ble_ancc_service_state;
}

uint32_t audio_message_notify_rx_ctrl_4d6db0(uint32_t id,
                                               const uint8_t *body) {
    (void)id;
    if (body == 0) {
        struct audio_message_notify_fault_4d6db0 fault;
        audio_uart_checksum_copy(&fault, &fault_template, sizeof fault);
        fault.detail = (fault.detail & 0xffff0000u) | 1u;
        audio_ring_pb_assert_509b48(&fault);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x69u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_compact,
                                        null_compact);
        return 2u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x6eu, state_message,
                           body[0], body[1], body[2], body[4]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0d000000u, state_compact, state_compact,
                                    body[0], body[1], body[2], body[4]);
    audio_message_notify_ancc_state_get_49729c()[0] = body[0];
    audio_message_notify_ancc_state_get_49729c()[1] = body[1];
    audio_message_notify_ancc_state_get_49729c()[2] = body[2];
    audio_message_notify_ancc_state_get_49729c()[3] = body[4];
    return 0u;
}
