/* Native tracepoint_handle_ble_data 0x5ee8bc. The 0x206-byte decode
 * destination is live RAM at 0x2037b9c0; startup and final extent are open. */
#include <stdint.h>

struct tracepoint_pb_stream {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct tracepoint_pb_stream) == 16u, "nanopb stream ABI");

extern uint8_t audio_tracepoint_decode_buffer[]; /* 0x2037b9c0 */
extern const uint8_t audio_tracepoint_message_descriptor[]; /* ROM 0x77cd84 */
extern uint32_t audio_tracepoint_role_char_5edadc(void);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern void audio_uart_pb_stream_init(struct tracepoint_pb_stream *, const void *, uint32_t);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);
extern void audio_tracepoint_request_file_name_5ee1f8(uint8_t);
extern void audio_tracepoint_delete_file_5ee488(uint8_t, const void *);
extern void audio_tracepoint_delete_all_5ee7b4(uint8_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_handle_ble_data";
static const char length_message[] = "tracepoint ble data len=%u role=%c";
static const char length_short[] = "[tp.setting]tracepoint ble data len=%u role=%c";
static const char none[] = "(none)";
static const char decode_message[] = "tracepoint protobuf decode failed: %s";
static const char decode_short[] = "[tp.setting]tracepoint protobuf decode failed: %s";
static const char command_message[] = "tracepoint recv cmd=%d magic=%u which=%u";
static const char command_short[] = "[tp.setting]tracepoint recv cmd=%d magic=%u which=%u";
static const char heartbeat_message[] = "tracepoint heartbeat";
static const char heartbeat_short[] = "[tp.setting]tracepoint heartbeat";
static const char missing_message[] = "tracepoint delete file missing del_msg which=%u";
static const char missing_short[] = "[tp.setting]tracepoint delete file missing del_msg which=%u";
static const char unknown_message[] = "tracepoint unknown cmd=%d";
static const char unknown_short[] = "[tp.setting]tracepoint unknown cmd=%d";

uint32_t audio_tracepoint_handle_ble_data_5ee8bc(const void *data, uint32_t length)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x1a9u,
                           length_message, length, audio_tracepoint_role_char_5edadc());
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10800000u, length_short, length_short,
                                    length, audio_tracepoint_role_char_5edadc());
    if (data == 0 || length == 0u)
        return UINT32_MAX;
    audio_uart_buffer_zero(audio_tracepoint_decode_buffer, 0x206u, 0u);
    struct tracepoint_pb_stream initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    audio_uart_checksum_copy(&stream, &initial, 16u);
    if ((uint8_t)audio_uart_pb_decode(&stream, audio_tracepoint_message_descriptor,
                                      audio_tracepoint_decode_buffer) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x1b5u,
                               decode_message, error);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, decode_short,
                                        decode_short, error);
        return UINT32_MAX;
    }
    const uint8_t *decoded = audio_tracepoint_decode_buffer;
    uint32_t command = decoded[0], magic = decoded[1];
    uint32_t which = (uint32_t)decoded[2] | ((uint32_t)decoded[3] << 8);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x1bcu,
                           command_message, command, magic, which);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10c00000u, command_short,
                                    command_short, command, magic, which);
    if (command == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x1c0u,
                               heartbeat_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, heartbeat_short,
                                        heartbeat_short);
    } else if (command == 1u) {
        audio_tracepoint_request_file_name_5ee1f8((uint8_t)magic);
    } else if (command == 2u) {
        if (which == 4u) {
            audio_tracepoint_delete_file_5ee488((uint8_t)magic, decoded + 4u);
        } else {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(2u, module, path, function, 0x1cdu,
                                   missing_message, which);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x08400000u, missing_short,
                                            missing_short, which);
        }
    } else if (command == 3u) {
        audio_tracepoint_delete_all_5ee7b4((uint8_t)magic);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x1d6u,
                               unknown_message, command);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, unknown_short,
                                        unknown_short, command);
    }
    return 0u;
}
