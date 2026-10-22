/* Apollo main Prompt/Event/Heartbeat receive wrappers, stock-derived.
 * Native entries: 0x4e47a0, 0x4e4a34, 0x4e4e5c.
 */
#include <stdint.h>

struct even_ai_fault_record {
    uint32_t type, detail;
    const char *path, *function;
    uint32_t line;
};
_Static_assert(sizeof(struct even_ai_fault_record) == 20u, "fault record ABI");

extern void audio_ring_pb_assert_509b48(const struct even_ai_fault_record *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern int32_t audio_even_ai_service_dispatch_497ea2(uint8_t, const void *, uint32_t);

static const char module[] = "pb.evenai";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_even_ai\\pb_service_even_ai.c";
static const char null_message[] = "PORINT NULL";
static const char null_short[] = "[pb.evenai]PORINT NULL";

struct even_ai_rx_config {
    const char *function;
    const char *value_message;
    const char *value_short;
    uint32_t fault_line, null_line, value_line;
    uint8_t opcode;
};

static uint32_t receive_simple(const struct even_ai_rx_config *config,
                               const void *payload) {
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
    uint32_t value = *(const uint8_t *)payload;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, config->function,
                           config->value_line, config->value_message, value);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, config->value_short,
                                    config->value_short, value);
    return audio_even_ai_service_dispatch_497ea2(config->opcode, payload, 2u) == 0
               ? 0u : 1u;
}

static const struct even_ai_rx_config prompt = {
    "PB_RxEvenAIPromptInfo", "pPromptInfo->prompt_type = %d",
    "[pb.evenai]pPromptInfo->prompt_type = %d",
    0x24au, 0x24cu, 0x250u, 7u
};
static const struct even_ai_rx_config event = {
    "PB_RxEvenAIEvent", "pEventInfo->event = %d",
    "[pb.evenai]pEventInfo->event = %d",
    0x2a4u, 0x2a6u, 0x2aau, 8u
};
static const struct even_ai_rx_config heartbeat = {
    "PB_RxEvenAIHeartbeat", "pHeartbeatInfo->hb_cnt = %d",
    "[pb.evenai]pHeartbeatInfo->hb_cnt = %d",
    0x2feu, 0x300u, 0x304u, 9u
};

/* Stock 0x4E47A0 (PB_RxEvenAIPromptInfo) */
uint32_t audio_even_ai_rx_prompt(uint8_t sequence, const void *payload) {
    (void)sequence;
    return receive_simple(&prompt, payload);
}
/* Stock 0x4E4A34 (PB_RxEvenAIEvent) */
uint32_t audio_even_ai_rx_event(uint8_t sequence, const void *payload) {
    (void)sequence;
    return receive_simple(&event, payload);
}
/* Stock 0x4E4E5C (PB_RxEvenAIHeartbeat) */
uint32_t audio_even_ai_rx_heartbeat(uint8_t sequence, const void *payload) {
    (void)sequence;
    return receive_simple(&heartbeat, payload);
}
