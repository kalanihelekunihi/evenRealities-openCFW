/* Apollo main 0x4e2976: EvenAI common-data dispatch, stock-derived. */
#include <stdint.h>

extern void audio_even_ai_prepare_4e1f7c(void);
extern int32_t audio_even_ai_frame_process_4e31cc(uint32_t, uint32_t);
extern int32_t audio_even_ai_local_decode_498092(uint32_t, uint32_t);
extern void audio_even_ai_ready_4e20f2(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "even_ai.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai.c";
static const char function[] = "EvenAI_common_data_handler";
static const char frame_error[] = "APP_PbRxEvenAIFrameDataProcess failed";
static const char decode_error[] = "SVC_DecodeLocalEvenAIInfo failed";
static const char frame_short[] = "[even_ai.page]APP_PbRxEvenAIFrameDataProcess failed";
static const char decode_short[] = "[even_ai.page]SVC_DecodeLocalEvenAIInfo failed";

uint64_t audio_uart_registry_callback_4e2976(uint32_t kind, uint32_t data,
                                               uint32_t length) {
    audio_even_ai_prepare_4e1f7c();
    int32_t failed;
    if (kind == 0u) {
        failed = audio_even_ai_frame_process_4e31cc(data, length & 0xffffu);
    } else if (kind == 5u) {
        failed = audio_even_ai_local_decode_498092(data, length);
    } else {
        return ((uint64_t)length << 32) | 0xffffffffu;
    }
    if (failed != 0) {
        uint32_t high_word = length;
        if ((audio_log_flags() & 2u) != 0u) {
            high_word = kind == 0u ? 0x291u : 0x298u;
            audio_log_extended(1u, module, path, function,
                               kind == 0u ? 0x291u : 0x298u,
                               kind == 0u ? frame_error : decode_error);
        }
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u) {
            const char *compact = kind == 0u ? frame_short : decode_short;
            (void)compressed_log_output(0x04000000u, compact, compact);
        }
        return ((uint64_t)high_word << 32) | 0xffffffffu;
    }
    audio_even_ai_ready_4e20f2(0u);
    return (uint64_t)length << 32;
}
