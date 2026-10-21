/* Apollo main Ask/Reply/Skill/Config receive wrappers, stock-derived.
 * Native entries: 0x4e3d34, 0x4e42b4, 0x4e4538, 0x4e50d8.
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

static uint32_t receive_null(const char *function, uint32_t fault_line,
                             uint32_t log_line) {
    struct even_ai_fault_record fault = {0u, 1u, path, function, fault_line};
    audio_ring_pb_assert_509b48(&fault);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, log_line, null_message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x04000000u, null_short, null_short);
    return 2u;
}

static void log_byte(const char *function, uint32_t line, const char *message,
                     const char *compact, uint32_t value) {
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, line, message, value);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, value);
}

static const char ask_function[] = "PB_RxEvenAIAskInfo";
uint32_t audio_even_ai_rx_ask(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0)
        return receive_null(ask_function, 0x169u, 0x16bu);
    const uint8_t *p = payload;
    log_byte(ask_function, 0x16fu, "pAskInfo->status = %d",
             "[pb.evenai]pAskInfo->status = %d", p[0]);
    log_byte(ask_function, 0x170u, "pAskInfo->stream_enable = %d",
             "[pb.evenai]pAskInfo->stream_enable = %d", p[1]);
    log_byte(ask_function, 0x171u, "pAskInfo->text_mode = %d",
             "[pb.evenai]pAskInfo->text_mode = %d", p[2]);
    return audio_even_ai_service_dispatch_497ea2(3u, payload, 0x208u) == 0 ? 0u : 1u;
}

static const char reply_function[] = "PB_RxEvenAIReplyInfo";
uint32_t audio_even_ai_rx_reply(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0)
        return receive_null(reply_function, 0x1dau, 0x1dcu);
    log_byte(reply_function, 0x1e0u, "pReplyInfo->cmd_cnt = %d",
             "[pb.evenai]pReplyInfo->cmd_cnt = %d", *(const uint8_t *)payload);
    return audio_even_ai_service_dispatch_497ea2(5u, payload, 0x208u) == 0 ? 0u : 1u;
}

static const char skill_function[] = "PB_RxEvenAISkillInfo";
uint32_t audio_even_ai_rx_skill(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0)
        return receive_null(skill_function, 0x212u, 0x214u);
    log_byte(skill_function, 0x218u, "pSkillInfo->skill_id = %d",
             "[pb.evenai]pSkillInfo->skill_id = %d",
             ((const uint8_t *)payload)[1]);
    return audio_even_ai_service_dispatch_497ea2(6u, payload, 0x10cu) == 0 ? 0u : 1u;
}

static const char config_function[] = "PB_RxEvenAIConfig";
static const char config_message[] =
    "EvenAI config voice_switch=%d, stream_speed=%d, duplex_mode=%d";
static const char config_short[] =
    "[pb.evenai]EvenAI config voice_switch=%d, stream_speed=%d, duplex_mode=%d";
uint32_t audio_even_ai_rx_config(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0)
        return receive_null(config_function, 0x33au, 0x33cu);
    const uint8_t *p = payload;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, config_function, 0x341u,
                           config_message, p[0], p[1], p[3]);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10c00000u, config_short, config_short,
                                    p[0], p[1], p[3]);
    return audio_even_ai_service_dispatch_497ea2(10u, payload, 4u) == 0 ? 0u : 1u;
}
