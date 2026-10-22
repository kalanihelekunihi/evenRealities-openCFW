/* Apollo main PB_RxEvenAIVADInfo at 0x4e391a, stock-derived C candidate. */
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
static const char function[] = "PB_RxEvenAIVADInfo";
static const char null_message[] = "PORINT NULL";
static const char null_short[] = "[pb.evenai]PORINT NULL";
static const char status_message[] = "pVADInfo->status = %d";
static const char status_short[] = "[pb.evenai]pVADInfo->status = %d";

/* Stock 0x4E391A (PB_RxEvenAIVADInfo) */
uint32_t audio_even_ai_rx_vad(uint8_t sequence, const void *payload) {
    (void)sequence;
    if (payload == 0) {
        struct even_ai_fault_record fault = {0u, 1u, path, function, 0x10fu};
        audio_ring_pb_assert_509b48(&fault);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x111u,
                               null_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, null_short, null_short);
        return 2u;
    }
    uint32_t status = *(const uint8_t *)payload;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x115u,
                           status_message, status);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, status_short,
                                    status_short, status);
    return audio_even_ai_service_dispatch_497ea2(2u, payload, 2u) == 0 ? 0u : 1u;
}
