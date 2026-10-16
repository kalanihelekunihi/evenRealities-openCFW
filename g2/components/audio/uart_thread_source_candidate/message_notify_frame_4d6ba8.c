/* Stock Apollo APP_PbRxNotificationFrameDataProcess 0x4d6ba8. */
#include <stdint.h>

struct pb_stream_4d6ba8 {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct pb_stream_4d6ba8) == 16u, "nanopb stream ABI");

extern const uint8_t audio_ble_ancc_not_whitelisted_pb_descriptor[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_pb_stream_init(struct pb_stream_4d6ba8 *, const void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);
extern uint32_t audio_message_notify_rx_ctrl_4d6db0(uint32_t, const void *);
extern uint32_t audio_message_notify_tx_ctrl_4d6ea2(uint32_t, const void *);
extern uint32_t audio_message_notify_rx_whitelist_ctrl_4d73d6(uint32_t, const void *);
extern uint32_t audio_message_notify_tx_whitelist_ctrl_4d749a(uint32_t, const void *);
extern uint32_t audio_message_notify_rx_whitelist_check_4d7624(uint32_t, const void *);
extern uint32_t audio_message_notify_tx_whitelist_check_4d76cc(uint32_t, const void *);
extern uint32_t audio_message_notify_tx_common_response_4d7038(uint32_t, const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.notif";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_notification\\pb_service_notification.c";
static const char function[] = "APP_PbRxNotificationFrameDataProcess";
static const char none[] = "(none)";

uint32_t audio_message_notify_frame_process_4d6ba8(const void *data,
                                                     uint32_t raw_length) {
    uint32_t length = (uint16_t)raw_length;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x2cu,
                           "len=%d:", length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, "[pb.notif]len=%d:",
                                    "[pb.notif]len=%d:", length);
    if (data == 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x2eu,
                               "pData is NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u,
                                        "[pb.notif]pData is NULL",
                                        "[pb.notif]pData is NULL");
        return 2u;
    }
    uint8_t decoded[0x4c];
    audio_uart_buffer_zero(decoded, sizeof decoded, 0u);
    struct pb_stream_4d6ba8 initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    audio_uart_checksum_copy(&stream, &initial, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream,
                audio_ble_ancc_not_whitelisted_pb_descriptor, decoded) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x37u,
                               "Decoding failed: %s", error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u,
                                        "[pb.notif]Decoding failed: %s",
                                        "[pb.notif]Decoding failed: %s", error);
        return 0x2bu;
    }
    uint32_t command = decoded[0];
    uint32_t id = decoded[1];
    const void *body = decoded + 4u;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x3bu,
                           "command_id: %d", command);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u,
                                    "[pb.notif]command_id: %d",
                                    "[pb.notif]command_id: %d", command);
    if (command == 1u) {
        if (audio_message_notify_rx_ctrl_4d6db0(id, body) == 0u)
            return audio_message_notify_tx_ctrl_4d6ea2(id, body);
    } else if (command == 3u) {
        if (audio_message_notify_rx_whitelist_ctrl_4d73d6(id, body) == 0u)
            return audio_message_notify_tx_whitelist_ctrl_4d749a(id, body);
    } else if (command == 4u) {
        if (audio_message_notify_rx_whitelist_check_4d7624(id, body) == 0u)
            return audio_message_notify_tx_whitelist_check_4d76cc(id, body);
    } else {
        const uint8_t response[2] = {(uint8_t)command, 8u};
        (void)audio_message_notify_tx_common_response_4d7038(id, response);
    }
    return 0u;
}
