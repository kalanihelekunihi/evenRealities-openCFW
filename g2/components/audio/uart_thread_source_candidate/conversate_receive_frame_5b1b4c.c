/* Native APP_PbConversateRxFrameDataProcess 0x5b1b4c..0x5b1d29. */
#include <stdint.h>

struct conversate_istream {
    uint32_t callback;
    uint32_t state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct conversate_istream) == 16u, "nanopb istream ABI");

extern uint8_t audio_conversate_last_magic_20074ff8;
extern uint32_t audio_conversate_last_frame_tick_2007485c;
extern const uint8_t audio_conversate_response_descriptor_775b24[];
extern void audio_dump_hex(const char *, uint32_t, const uint8_t *, uint32_t);
extern void audio_uart_pb_stream_init(struct conversate_istream *, const void *, uint32_t);
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);
extern uint32_t audio_uart_pb_decode(struct conversate_istream *, const void *, void *);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_conversate\\pb_service_conversate.c";
static const char function[] = "APP_PbConversateRxFrameDataProcess";
static const char none[] = "(none)";
static const char null_message[] = "pData or message is NULL";
static const char null_short[] = "[pb.conversate]pData or message is NULL";
static const char decode_failed[] = "Decoding failed: %s";
static const char decode_short[] = "[pb.conversate]Decoding failed: %s";
static const char receive_message[] =
    "command_id: %d, magic number = %d, last magic number = %d";
static const char receive_short[] =
    "[pb.conversate]command_id: %d, magic number = %d, last magic number = %d";
static const char duplicate_message[] =
    "Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore";
static const char duplicate_short[] =
    "[pb.conversate]Duplicate message detected: magic_random = %d, time_elapsed = %d ms, ignore";
static const char dump_label[] = "Conversate_pb_rx";

uint32_t audio_conversate_receive_5b1b4c(const void *bytes,
                                             uint16_t length, void *message) {
    if (!bytes || !message) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 62u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return 6u;
    }
    uint8_t *const decoded = (uint8_t *)message;
    const uint32_t dump_length = length > 32u ? 32u : length;
    audio_dump_hex(dump_label, 16u, bytes, dump_length);
    struct conversate_istream stream, decoding;
    audio_uart_pb_stream_init(&stream, bytes, length);
    (void)audio_uart_display_area_copy_439c04(&decoding, &stream, 16u);
    if (!(uint8_t)audio_uart_pb_decode(&decoding,
                                       audio_conversate_response_descriptor_775b24,
                                       decoded)) {
        const char *error = decoding.errmsg ? decoding.errmsg : none;
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 69u,
                               decode_failed, error);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, decode_short, decode_short, error);
        return 5u;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 72u,
                           receive_message, decoded[0], decoded[1],
                           audio_conversate_last_magic_20074ff8);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0cc00000u, receive_short, receive_short,
                         decoded[0], decoded[1],
                         audio_conversate_last_magic_20074ff8);
    const uint32_t now = g2_flashdb_candidate_tick();
    const uint32_t elapsed = now - audio_conversate_last_frame_tick_2007485c;
    if (decoded[1] == audio_conversate_last_magic_20074ff8 && elapsed < 3000u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 79u,
                               duplicate_message,
                               audio_conversate_last_magic_20074ff8, elapsed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08800000u, duplicate_short, duplicate_short,
                             audio_conversate_last_magic_20074ff8, elapsed);
        return 13u;
    }
    audio_conversate_last_magic_20074ff8 = decoded[1];
    audio_conversate_last_frame_tick_2007485c = now;
    return 0u;
}
