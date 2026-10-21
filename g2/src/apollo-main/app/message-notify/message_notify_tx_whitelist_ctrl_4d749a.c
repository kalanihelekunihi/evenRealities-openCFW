/* Stock Apollo APP_PbTxEncodeNotifWhitelistCtrl 0x4d749a. */
#include <stdint.h>

struct audio_message_notify_ostream_4d749a {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written;
    const char *errmsg;
};
_Static_assert(sizeof(struct audio_message_notify_ostream_4d749a) == 20u,
               "nanopb ostream ABI");
struct audio_message_notify_fault_4d749a {
    uint32_t type;
    uint32_t detail;
    const char *path;
    const char *function;
    uint32_t line;
};
_Static_assert(sizeof(struct audio_message_notify_fault_4d749a) == 20u,
               "fault record ABI");

extern uint8_t audio_message_notify_tx_packet_2037c7a0[0x100];
extern uint8_t audio_message_notify_tx_state_200f60e0[0x4c];
extern const uint8_t audio_ble_ancc_not_whitelisted_pb_descriptor[];
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_pb_ostream_from_buffer(struct audio_message_notify_ostream_4d749a *,
                                         void *, uint32_t);
extern uint32_t audio_pb_encode(void *, const void *, const void *);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t,
                                             const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.notif";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_notification\\pb_service_notification.c";
static const char function[] = "APP_PbTxEncodeNotifWhitelistCtrl";
static const char none[] = "(none)";
static const char null_message[] = "POINT NULL";
static const char null_compact[] = "[pb.notif]POINT NULL";
static const char fail_message[] = "Encoding failed: %s\n";
static const char fail_compact[] = "[pb.notif]Encoding failed: %s\n";
static const char length_message[] = "txLen = %d";
static const char length_compact[] = "[pb.notif]txLen = %d";
static const struct audio_message_notify_fault_4d749a fault_template = {
    0u, 0u, path, function, 0x103u
};

uint32_t audio_message_notify_tx_whitelist_ctrl_4d749a(uint32_t id,
                                               const uint8_t *body) {
    if (body == 0) {
        struct audio_message_notify_fault_4d749a fault;
        audio_uart_checksum_copy(&fault, &fault_template, sizeof fault);
        fault.detail = (fault.detail & 0xffff0000u) | 1u;
        audio_ring_pb_assert_509b48(&fault);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x105u,
                               null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, null_compact,
                                        null_compact);
        return 2u;
    }
    struct audio_message_notify_ostream_4d749a initial, stream;
    audio_pb_ostream_from_buffer(&initial, audio_message_notify_tx_packet_2037c7a0,
                                  0x100u);
    audio_uart_checksum_copy(&stream, &initial, sizeof stream);
    uint8_t *state = audio_message_notify_tx_state_200f60e0;
    audio_uart_buffer_zero(state, 0x4cu, 0u);
    state[0] = 3u;
    state[1] = (uint8_t)id;
    state[2] = 6u;
    state[3] = 0u;
    state[4] = body[0];
    state[5] = 0u;
    uint32_t encoded = (uint8_t)audio_pb_encode(
        &stream, audio_ble_ancc_not_whitelisted_pb_descriptor, state);
    uint32_t written = (uint16_t)stream.bytes_written;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x119u,
                           length_message, written);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, length_compact,
                                    length_compact, written);
    if (encoded == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x11cu,
                               fail_message, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, fail_compact,
                                        fail_compact, error);
        return 0x2bu;
    }
    (void)audio_ring_pb_tx_ble_475b14(1u, 4u,
                                       audio_message_notify_tx_packet_2037c7a0,
                                       written);
    return 0u;
}
