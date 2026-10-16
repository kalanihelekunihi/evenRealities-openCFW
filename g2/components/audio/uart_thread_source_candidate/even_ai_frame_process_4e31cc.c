/* Apollo main 0x4e31cc: EvenAI protobuf frame dispatch candidate.
 * Derived from authenticated stock pseudocode and bound into the experimental
 * relocatable Apollo candidate after bounded decoder/encoder comparisons.
 */
#include <stdint.h>
#include <stddef.h>
#include "even_ai_decoder_context_48f49c.h"
#include "pb_decode.h"

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

extern const pb_msgdesc_t audio_even_ai_decode_fields;
extern uint8_t audio_even_ai_last_frame[2];
extern const uint8_t audio_even_ai_duplicate_status;
extern const uint8_t audio_even_ai_generic_status;

extern uint32_t audio_even_ai_encode_common(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_ctrl(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_ctrl(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_vad(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_vad(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_ask(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_ask(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_analyse(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_analyse(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_reply(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_reply(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_skill(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_skill(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_prompt(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_prompt(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_event(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_event(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_heartbeat(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_heartbeat(uint8_t, const void *);
extern uint32_t audio_even_ai_rx_config(uint8_t, const void *);
extern uint32_t audio_even_ai_tx_config(uint8_t, const void *);

struct even_ai_frame {
    uint8_t command;
    uint8_t sequence;
    uint8_t reserved[2];
    uint8_t message[520];
};

_Static_assert(sizeof(struct even_ai_frame) == 0x20cu, "stock frame size");
_Static_assert(offsetof(struct even_ai_frame, message) == 4u,
               "stock oneof payload offset");
_Static_assert(sizeof(struct even_ai_decode_context) == sizeof(pb_istream_t),
               "pinned nanopb stream ABI");

static const char module[] = "pb.evenai";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c";
static const char function[] = "APP_PbRxEvenAIFrameDataProcess";
static const char none[] = "(none)";
static const char decode_error[] = "Decoding failed: %s";
static const char decode_short[] = "[pb.evenai]Decoding failed: %s";
static const char duplicate[] = "magic_random is equal to last_magic_random = %d, ignore";
static const char duplicate_short[] = "[pb.evenai]magic_random is equal to last_magic_random = %d, ignore";
static const char command[] = "even ai command_id: %d";
static const char command_short[] = "[pb.evenai]even ai command_id: %d";

static void log_frame_length(uint32_t length) {
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x33u, "len=%d:", length);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, "[pb.evenai]len=%d:", "[pb.evenai]len=%d:", length);
}

typedef uint32_t (*frame_handler)(uint8_t, const void *);

static const frame_handler receive[11] = {
    0, audio_even_ai_rx_ctrl, audio_even_ai_rx_vad, audio_even_ai_rx_ask,
    audio_even_ai_rx_analyse, audio_even_ai_rx_reply, audio_even_ai_rx_skill,
    audio_even_ai_rx_prompt, audio_even_ai_rx_event,
    audio_even_ai_rx_heartbeat, audio_even_ai_rx_config
};
static const frame_handler transmit[11] = {
    0, audio_even_ai_tx_ctrl, audio_even_ai_tx_vad, audio_even_ai_tx_ask,
    audio_even_ai_tx_analyse, audio_even_ai_tx_reply, audio_even_ai_tx_skill,
    audio_even_ai_tx_prompt, audio_even_ai_tx_event,
    audio_even_ai_tx_heartbeat, audio_even_ai_tx_config
};

uint32_t audio_even_ai_frame_process_4e31cc(uint32_t data, uint32_t length) {
    struct even_ai_frame frame;
    struct even_ai_decode_context envelope;
    uint8_t response[4] = {0};
    log_frame_length(length & 0xffffu);
    if (data == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x35u, "pData is NULL");
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, "[pb.evenai]pData is NULL",
                                        "[pb.evenai]pData is NULL");
        return 2u;
    }
    for (uint32_t i = 0; i < sizeof frame; ++i)
        ((uint8_t *)&frame)[i] = 0u;
    audio_even_ai_decoder_context_init_48f49c(
        &envelope, (const void *)(uintptr_t)data, length & 0xffffu);
    if (!pb_decode((pb_istream_t *)&envelope, &audio_even_ai_decode_fields, &frame)) {
        const char *error = envelope.reserved != 0u
                                ? (const char *)(uintptr_t)envelope.reserved : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x3eu,
                               decode_error, error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, decode_short,
                                        decode_short, error);
        return 0x2bu;
    }
    if (audio_even_ai_last_frame[0] == 1u &&
        audio_even_ai_last_frame[1] == frame.sequence) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x45u,
                               duplicate, frame.sequence);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, duplicate_short,
                                        duplicate_short, frame.sequence);
        response[1] = audio_even_ai_duplicate_status;
        (void)audio_even_ai_encode_common(frame.sequence, &response[1]);
        return 1u;
    }
    audio_even_ai_last_frame[0] = 1u;
    audio_even_ai_last_frame[1] = frame.sequence;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x50u,
                           command, frame.command);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, command_short,
                                    command_short, frame.command);
    if (frame.command == 0u || frame.command > 10u) {
        response[0] = audio_even_ai_generic_status;
        return audio_even_ai_encode_common(frame.sequence, response);
    }
    if (receive[frame.command](frame.sequence, frame.message) == 0u)
        return transmit[frame.command](frame.sequence, frame.message);
    return 1u;
}
