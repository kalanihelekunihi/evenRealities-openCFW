/* Allocation-failure branch of Apollo registration 0x45f402..0x45f486. */
#include <stdint.h>

extern const uint8_t g2_audio_page_registration_template_45f678[];
extern void (*g2_extended_log_fatal_callback)(const void *, const char *, uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_ble_radio_ready_44b0ae(void);

static const char module[] = "page.mgr";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\page_manager\\page_manager.c";
static const char function[] = "page_manager_register";
static const char message[] = "page manager register failed, malloc failed";
static const char compact[] =
    "[page.mgr]page manager register failed, malloc failed";
static const char assertion[] = "(%s) has assert failed at %s:%ld.";
static const char emergency_module[] = "elog";

void audio_uart_display_audio_allocation_fatal_45f402(void) {
    if ((audio_log_level() & 2u) != 0u)
        audio_log_extended(1u, module, path, function, 0x1ecu, message);
    if ((audio_log_level() & 1u) != 0u || (audio_log_level() & 4u) != 0u)
        (void)compressed_log_output(0x04000000u, compact, compact);
    if (g2_extended_log_fatal_callback == 0) {
        audio_log_extended(0u, emergency_module, path, function, 0x1edu,
                           assertion, g2_audio_page_registration_template_45f678,
                           function, 0x1edu);
        for (;;) audio_ble_radio_ready_44b0ae();
    }
    g2_extended_log_fatal_callback(
        g2_audio_page_registration_template_45f678, function, 0x1edu);
}
