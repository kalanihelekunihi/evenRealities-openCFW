/* Apollo main PB_RxEvenAIAnalyseInfo at 0x4e403c, stock-derived C candidate. */
#include <stdint.h>

struct even_ai_fault_record {
    uint32_t type;
    uint32_t detail;
    const char *path;
    const char *function;
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
static const char function[] = "PB_RxEvenAIAnalyseInfo";
static const char null_message[] = "PORINT NULL";
static const char null_short[] = "[pb.evenai]PORINT NULL";
static const char info_message[] = "pAnalyseInfo";
static const char info_short[] = "[pb.evenai]pAnalyseInfo";

uint32_t audio_even_ai_rx_analyse(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0) {
        struct even_ai_fault_record fault = {0u, 1u, path, function, 0x1a3u};
        audio_ring_pb_assert_509b48(&fault);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x1a5u,
                               null_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x1a9u,
                           info_message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10000000u, info_short, info_short);
    return audio_even_ai_service_dispatch_497ea2(4u, payload, 1u) == 0 ? 0u : 1u;
}
