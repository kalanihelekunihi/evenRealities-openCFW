/* Stock Apollo APP_PbRxRingFrameDataProcess 0x5ce1dc. */
#include <stdint.h>
#include "ring_buffers.h"

struct ring_pb_stream {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;
};
_Static_assert(sizeof(struct ring_pb_stream) == 16u, "nanopb stream ABI");

struct pb_msgdesc_candidate;
extern const struct pb_msgdesc_candidate audio_ring_pb_descriptor; /* native 0x77b104 */
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x43c0e4 */
extern void audio_uart_pb_stream_init(struct ring_pb_stream *, const void *, uint32_t); /* 0x48f49c */
extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* 0x439c04 */
extern uint32_t audio_uart_pb_decode(void *, const void *, void *); /* 0x490120 */
extern uint32_t audio_ring_command_validate_5ce3ce(uint32_t, const void *);
extern uint32_t audio_ring_command_dispatch_5ce4e6(uint32_t, const void *);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module[] = "pb.ring";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_ring\\pb_service_ring.c";
static const char function[] = "APP_PbRxRingFrameDataProcess";
static const char len_message[] = "len=%d";
static const char len_short[] = "[pb.ring]len=%d";
static const char null_message[] = "pData is NULL";
static const char null_short[] = "[pb.ring]pData is NULL";
static const char decode_message[] = "Decoding failed: %s";
static const char decode_short[] = "[pb.ring]Decoding failed: %s";
static const char command_message[] = "ring command_id: %d";
static const char command_short[] = "[pb.ring]ring command_id: %d";
static const char unknown_message[] = "Unknown command_id: %d";
static const char unknown_short[] = "[pb.ring]Unknown command_id: %d";
static const char none[] = "(none)";

uint32_t audio_ring_data_relay_5ce1dc(const void *data, uint16_t length) {
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x31u,
                           len_message, length);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, len_short, len_short, length);
    if(data == 0) {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x33u, null_message);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }
    audio_uart_buffer_zero(audio_ring_buffers.decode, 64u, 0u);
    struct ring_pb_stream initial, stream;
    audio_uart_pb_stream_init(&initial, data, length);
    audio_uart_checksum_copy(&stream, &initial, 16u);
    if((uint8_t)audio_uart_pb_decode(&stream, &audio_ring_pb_descriptor,
                                      audio_ring_buffers.decode) == 0u) {
        const char *error = stream.errmsg ? stream.errmsg : none;
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x3du,
                               decode_message, error);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, decode_short,
                                        decode_short, error);
        return 0x2bu;
    }
    uint8_t command = audio_ring_buffers.decode[0];
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x41u,
                           command_message, command);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, command_short,
                                    command_short, command);
    if(command == 1u) {
        const void *args = audio_ring_buffers.decode + 4u;
        uint32_t id = audio_ring_buffers.decode[1];
        if(audio_ring_command_validate_5ce3ce(id, args) == 0u)
            return audio_ring_command_dispatch_5ce4e6(id, args);
    } else {
        if((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x4eu,
                               unknown_message, command);
        if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, unknown_short,
                                        unknown_short, command);
    }
    return 1u;
}
