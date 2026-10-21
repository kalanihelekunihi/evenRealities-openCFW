/* Native SyncInfoService_common_data_handler 0x472102..0x4721f3.
 * Protobuf schema/descriptor and command setup remain explicit lowers. */
#include <stdint.h>

struct sync_info_stream {
    uint32_t callback;
    uint32_t state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct sync_info_stream) == 16u, "nanopb stream ABI");

extern uint8_t audio_sync_info_state_200740bc[12];
extern const uint8_t audio_sync_info_pb_descriptor_77c1cc[];
extern void audio_uart_pb_stream_init(struct sync_info_stream *, const void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(void *, const void *, void *);
extern uint32_t audio_sync_info_command_471ee8(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "sync_info.main";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\sync_info\\sync_info.c";
static const char function[] = "SyncInfoService_common_data_handler";
static const char none[] = "(none)";
static const char decode_failed[] = "sync_info_data_handler protobuf decode failed: %s\n";
static const char simple_failed[] =
    "[sync_info.main]sync_info_data_handler protobuf decode failed: %s\n";
static const char unknown[] = "sync_info_data_handler: unknown cmd = %d";
static const char simple_unknown[] =
    "[sync_info.main]sync_info_data_handler: unknown cmd = %d";

uint32_t audio_uart_registry_callback_472102(uint32_t event,
                                                const void *bytes,
                                                uint32_t length) {
    if (event != 0u) return 0u;
    for (unsigned i = 0; i < 12; ++i) audio_sync_info_state_200740bc[i] = 0u;
    struct sync_info_stream stream, decoding;
    audio_uart_pb_stream_init(&stream, bytes, length);
    (void)audio_uart_display_area_copy_439c04(&decoding, &stream, 16u);
    if (audio_uart_pb_decode(&decoding, audio_sync_info_pb_descriptor_77c1cc,
                             audio_sync_info_state_200740bc) == 0u) {
        const char *error = decoding.errmsg ? decoding.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 140u,
                               decode_failed, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_failed, simple_failed, error);
    } else {
        const uint8_t command = audio_sync_info_state_200740bc[0];
        if (command == 0u) {
            (void)audio_sync_info_command_471ee8(audio_sync_info_state_200740bc[1]);
        } else {
            if (audio_log_flags() & 2u)
                audio_log_extended(2u, module, file, function, 154u,
                                   unknown, command);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                audio_log_simple(0x08400000u, simple_unknown, simple_unknown,
                                 command);
        }
    }
    return 0u;
}
