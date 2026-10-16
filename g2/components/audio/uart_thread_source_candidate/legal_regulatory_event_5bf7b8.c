/* LegalRegulatory UI callback at stock 0x5bf7b8. The event copy, two
 * logging branches, page-build call and scroll response follow the native
 * body; referenced page providers and final RAM placement remain separate. */
#include <stdint.h>

extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_legal_regulatory_build_5bf332(uint32_t);
extern void audio_uart_page_58c238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_lv_scroll_to_y_44ea04(void *, int32_t, uint32_t);
extern uint32_t audio_legal_regulatory_root_200746a4;
extern uint32_t audio_uart_registry_context_200014cc[];

static const char module[] = "legal_regulatory";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\LegalRegulatory\\legal_regulatory.c";
static const char function[] = "legal_regulatory_ui_event_handler";
static const char start_plain[] = "LegalRegulatory display startup";
static const char exit_plain[] = "LegalRegulatory display exit";
static const char start_compact[] = "[legal_regulatory]LegalRegulatory display startup";
static const char exit_compact[] = "[legal_regulatory]LegalRegulatory display exit";

static void event_log(uint32_t line, const char *plain, const char *compact) {
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, line, plain);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, compact, compact);
}

uint32_t audio_uart_registry_callback_5bf7b8(uint32_t event,
                                               const uint8_t *message,
                                               uint32_t length,
                                               uint32_t parent) {
    (void)length;
    uint8_t copy[8] = {0};
    for (uint32_t i = 0; i < 8u; ++i) copy[i] = message[i];
    if (event == 2u) {
        event_log(0x140u, start_plain, start_compact);
        audio_legal_regulatory_build_5bf332(parent);
        audio_uart_registry_context_200014cc[1] = audio_legal_regulatory_root_200746a4;
        audio_uart_page_58c238(audio_legal_regulatory_root_200746a4, 0xfau, 0u);
    } else if (event == 3u) {
        uint32_t kind = (uint32_t)copy[0] | ((uint32_t)copy[1] << 8) |
                        ((uint32_t)copy[2] << 16) | ((uint32_t)copy[3] << 24);
        if (kind == 1u) {
            uint32_t target = (uint32_t)copy[4] | ((uint32_t)copy[5] << 8) |
                              ((uint32_t)copy[6] << 16) | ((uint32_t)copy[7] << 24);
            audio_uart_lv_scroll_to_y_44ea04(
                (void *)(uintptr_t)audio_legal_regulatory_root_200746a4,
                (int32_t)target, 1u);
        }
    } else if (event == 5u) {
        event_log(0x155u, exit_plain, exit_compact);
    }
    return 0u;
}
