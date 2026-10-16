/* Stock Apollo tracepoint_handle_slave_file_list 0x5eeb98. */
#include <stdint.h>

struct tracepoint_slave_stream_5eeb98 {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct tracepoint_slave_stream_5eeb98) == 16u,
               "nanopb stream ABI");

extern uint8_t audio_tracepoint_reply_buffer[0x206];
extern uint8_t audio_tracepoint_local_file_list_ready;
extern uint8_t audio_tracepoint_file_list_ready_extent_tail_20074ae5[3];
extern const uint8_t audio_tracepoint_message_descriptor[];
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_pb_stream_init(struct tracepoint_slave_stream_5eeb98 *,
                                      const void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);
extern void *audio_settings_copy_text(void *, const void *, uint32_t);
extern uint32_t audio_tracepoint_send_to_phone_5edfd8(const uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tp.setting";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_handle_slave_file_list";
static const char none[] = "(none)";
static const char recv_message[] = "tracepoint recv slave file list len=%u";
static const char recv_short[] = "[tp.setting]tracepoint recv slave file list len=%u";
static const char decode_message[] = "tracepoint slave list decode failed: %s";
static const char decode_short[] = "[tp.setting]tracepoint slave list decode failed: %s";
static const char ignored_message[] = "tracepoint ignore slave msg cmd=%d which=%u";
static const char ignored_short[] = "[tp.setting]tracepoint ignore slave msg cmd=%d which=%u";
static const char unready_message[] = "tracepoint master local file list not ready";
static const char unready_short[] = "[tp.setting]tracepoint master local file list not ready";
static const char merge_message[] = "tracepoint merge file list local=%u slave=%u";
static const char merge_short[] = "[tp.setting]tracepoint merge file list local=%u slave=%u";
static const char file_message[] = "tracepoint merge file[%u]=%s";
static const char file_short[] = "[tp.setting]tracepoint merge file[%u]=%s";
static const char send_fail_message[] = "tracepoint send merged file list failed";
static const char send_fail_short[] = "[tp.setting]tracepoint send merged file list failed";
static const char send_ok_message[] = "tracepoint send merged file list success count=%u";
static const char send_ok_short[] = "[tp.setting]tracepoint send merged file list success count=%u";

static uint16_t half_at(const uint8_t *p, uint32_t at) {
    return (uint16_t)((uint16_t)p[at] | ((uint16_t)p[at+1u] << 8u));
}
static void set_half(uint8_t *p, uint32_t at, uint16_t value) {
    p[at] = (uint8_t)value;
    p[at+1u] = (uint8_t)(value >> 8u);
}
static uint32_t ready_word_is_one(void) {
    return audio_tracepoint_local_file_list_ready == 1u &&
           audio_tracepoint_file_list_ready_extent_tail_20074ae5[0] == 0u &&
           audio_tracepoint_file_list_ready_extent_tail_20074ae5[1] == 0u &&
           audio_tracepoint_file_list_ready_extent_tail_20074ae5[2] == 0u;
}
static void ready_word_clear(void) {
    audio_tracepoint_local_file_list_ready = 0u;
    audio_tracepoint_file_list_ready_extent_tail_20074ae5[0] = 0u;
    audio_tracepoint_file_list_ready_extent_tail_20074ae5[1] = 0u;
    audio_tracepoint_file_list_ready_extent_tail_20074ae5[2] = 0u;
}

uint32_t audio_tracepoint_handle_slave_file_list_5eeb98(const void *data,
                                                          uint32_t length) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x1dfu,
                           recv_message, length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, recv_short, recv_short, length);
    if (data == 0 || length == 0u)
        return UINT32_MAX;
    uint8_t decoded[0x206];
    audio_uart_buffer_zero(decoded, sizeof decoded, 0u);
    struct tracepoint_slave_stream_5eeb98 initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    audio_uart_checksum_copy(&stream, &initial, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream,
                audio_tracepoint_message_descriptor, decoded) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x1edu,
                               decode_message, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04400000u, decode_short,
                                        decode_short, error);
        return UINT32_MAX;
    }
    uint32_t command = decoded[0];
    uint32_t which = half_at(decoded, 2u);
    if (command != 1u || which != 3u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 500u,
                               ignored_message, command, which);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08800000u, ignored_short,
                                        ignored_short, command, which);
        return 0u;
    }
    if (!ready_word_is_one()) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x1f9u,
                               unready_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08000000u, unready_short,
                                        unready_short);
        return 0u;
    }
    uint8_t *reply = audio_tracepoint_reply_buffer;
    uint32_t local_count = half_at(reply, 4u);
    uint32_t slave_count = half_at(decoded, 4u);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x200u,
                           merge_message, local_count, slave_count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10800000u, merge_short,
                                    merge_short, local_count, slave_count);
    uint32_t index = local_count;
    for (uint32_t i = 0; i < slave_count && index < 16u; ++i, ++index) {
        uint8_t *destination = reply + 6u + index * 0x20u;
        const uint8_t *source = decoded + 6u + i * 0x20u;
        (void)audio_settings_copy_text(destination, source, 0x1fu);
        destination[0x1fu] = 0u;
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0x209u,
                               file_message, index, destination);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10800000u, file_short,
                                        file_short, index, destination);
    }
    set_half(reply, 4u, (uint16_t)index);
    uint32_t result = audio_tracepoint_send_to_phone_5edfd8(reply);
    if (result != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x211u,
                               send_fail_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, send_fail_short,
                                        send_fail_short);
        return result;
    }
    ready_word_clear();
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x217u,
                           send_ok_message, index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, send_ok_short,
                                    send_ok_short, index);
    return 0u;
}
