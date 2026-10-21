/* Apollo main EvenAI command encoders, stock-derived.
 * Uses pinned nanopb 0.4.9 and authenticated EvenAI descriptor.
 */
#include <stdint.h>
#include "pb_encode.h"

struct even_ai_fault_record {
    uint32_t type, detail;
    const char *path, *function;
    uint32_t line;
};
_Static_assert(sizeof(struct even_ai_fault_record) == 20u, "fault record ABI");

extern uint8_t audio_even_ai_tx_buffer_2037c4a0[256];
extern uint8_t audio_even_ai_proto_message_200f5884[0x20c];
extern const pb_msgdesc_t audio_even_ai_decode_fields;
extern void audio_ring_pb_assert_509b48(const struct even_ai_fault_record *);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.evenai";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c";
static const char null_message[] = "PORINT NULL";
static const char null_short[] = "[pb.evenai]PORINT NULL";
static const char tx_length[] = "txLen = %d";
static const char tx_length_short[] = "[pb.evenai]txLen = %d";
static const char encode_error[] = "Encoding failed: %s\n";
static const char encode_error_short[] = "[pb.evenai]Encoding failed: %s\n";
static const char none[] = "(none)";

struct even_ai_tx_simple_config {
    const char *function;
    uint32_t fault_line, null_line, length_line, error_line;
    uint8_t command, oneof, second_byte;
};
static const struct even_ai_tx_simple_config control_config = {
    "APP_PbTxEncodeEvenAICtrl", 0xc9u, 0xcbu, 0xdfu, 0xe2u, 1u, 3u, 0u
};
static const struct even_ai_tx_simple_config vad_config = {
    "APP_PbTxEncodeEvenAIVADInfo", 0x123u, 0x125u, 0x139u, 0x13cu, 2u, 4u, 0u
};
static const struct even_ai_tx_simple_config prompt_config = {
    "APP_PbTxEncodeEvenAIPromptInfo", 0x25eu, 0x260u, 0x274u, 0x277u, 7u, 9u, 0u
};
static const struct even_ai_tx_simple_config event_config = {
    "APP_PbTxEncodeEvenAIEvent", 0x2b8u, 0x2bau, 0x2ceu, 0x2d1u, 8u, 10u, 0u
};
static const struct even_ai_tx_simple_config heartbeat_config = {
    "APP_PbTxEncodeEvenAIHeartbeat", 0x312u, 0x314u, 0x32cu, 0x32fu,
    9u, 11u, 8u
};
static const struct even_ai_tx_simple_config ask_config = {
    "APP_PbTxEncodeEvenAIAskInfo", 0x17fu, 0x181u, 0x195u, 0x198u,
    3u, 5u, 0u
};
static const struct even_ai_tx_simple_config analyse_config = {
    "APP_PbTxEncodeEvenAIAnalyseInfo", 0x1b7u, 0x1b9u, 0x1ccu, 0x1cfu,
    4u, 6u, 0u
};
static const struct even_ai_tx_simple_config reply_config = {
    "APP_PbTxEncodeEvenAIReplyInfo", 0x1eeu, 0x1f0u, 0x204u, 0x207u,
    5u, 7u, 0u
};
static const struct even_ai_tx_simple_config skill_config = {
    "APP_PbTxEncodeEvenAISkillInfo", 0x226u, 0x228u, 0x23cu, 0x23fu,
    6u, 8u, 0u
};
static const struct even_ai_tx_simple_config config_config = {
    "APP_PbTxEncodeEvenAIConfig", 0x34fu, 0x351u, 0x367u, 0x36au,
    10u, 13u, 0u
};

static uint32_t encode_simple(const struct even_ai_tx_simple_config *config,
                              uint8_t sequence, const void *payload) {
    if (payload == 0) {
        struct even_ai_fault_record fault = {
            0u, 1u, path, config->function, config->fault_line
        };
        audio_ring_pb_assert_509b48(&fault);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, config->function,
                               config->null_line, null_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }

    pb_ostream_t stream = pb_ostream_from_buffer(audio_even_ai_tx_buffer_2037c4a0,
                                                 256u);
    for (uint32_t i = 0; i < 0x20cu; ++i)
        audio_even_ai_proto_message_200f5884[i] = 0u;
    audio_even_ai_proto_message_200f5884[0] = config->command;
    audio_even_ai_proto_message_200f5884[1] = sequence;
    audio_even_ai_proto_message_200f5884[2] = config->oneof;
    const uint8_t *p = payload;
    if (config->command == 4u) {
        audio_even_ai_proto_message_200f5884[4] = 0u;
    } else if (config->command == 6u) {
        audio_even_ai_proto_message_200f5884[5] = p[1];
    } else if (config->command == 10u) {
        audio_even_ai_proto_message_200f5884[4] = p[0];
        audio_even_ai_proto_message_200f5884[5] = p[1];
        audio_even_ai_proto_message_200f5884[7] = p[3];
    } else {
        audio_even_ai_proto_message_200f5884[4] = p[0];
        audio_even_ai_proto_message_200f5884[5] = config->second_byte;
    }
    uint32_t encoded = pb_encode(&stream, &audio_even_ai_decode_fields,
                                 audio_even_ai_proto_message_200f5884) ? 1u : 0u;
    uint32_t length = (uint32_t)stream.bytes_written & 0xffffu;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, config->function,
                           config->length_line,
                           tx_length, length);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, tx_length_short,
                                    tx_length_short, length);
    if (encoded == 0u) {
        const char *error = stream.errmsg != 0 ? stream.errmsg : none;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, config->function,
                               config->error_line,
                               encode_error, error);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, encode_error_short,
                                        encode_error_short, error);
        return 0x2bu;
    }
    (void)audio_ring_pb_tx_ble_475b14(1u, 7u,
                                       audio_even_ai_tx_buffer_2037c4a0, length);
    return 0u;
}

uint32_t audio_even_ai_tx_ctrl(uint8_t sequence, const void *payload) {
    return encode_simple(&control_config, sequence, payload);
}

uint32_t audio_even_ai_tx_vad(uint8_t sequence, const void *payload) {
    return encode_simple(&vad_config, sequence, payload);
}

uint32_t audio_even_ai_tx_prompt(uint8_t sequence, const void *payload) {
    return encode_simple(&prompt_config, sequence, payload);
}

uint32_t audio_even_ai_tx_event(uint8_t sequence, const void *payload) {
    return encode_simple(&event_config, sequence, payload);
}

uint32_t audio_even_ai_tx_heartbeat(uint8_t sequence, const void *payload) {
    return encode_simple(&heartbeat_config, sequence, payload);
}

uint32_t audio_even_ai_tx_ask(uint8_t sequence, const void *payload) {
    return encode_simple(&ask_config, sequence, payload);
}
uint32_t audio_even_ai_tx_analyse(uint8_t sequence, const void *payload) {
    return encode_simple(&analyse_config, sequence, payload);
}
uint32_t audio_even_ai_tx_reply(uint8_t sequence, const void *payload) {
    return encode_simple(&reply_config, sequence, payload);
}
uint32_t audio_even_ai_tx_skill(uint8_t sequence, const void *payload) {
    return encode_simple(&skill_config, sequence, payload);
}
uint32_t audio_even_ai_tx_config(uint8_t sequence, const void *payload) {
    return encode_simple(&config_config, sequence, payload);
}
