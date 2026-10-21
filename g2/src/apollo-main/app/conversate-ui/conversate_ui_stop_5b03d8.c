/* Native Conversate heartbeat stop/check 0x5b03d8..0x5b0475. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t audio_conversate_last_success_tick_20074394;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_conversate_success_5b03c2(void);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t, const void *);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "conversate_heartbeat_check";
static const char message[] = "Heartbeat timeout! Time diff: %u ms, timeout: %u ms";
static const char short_message[] =
    "[conversate]Heartbeat timeout! Time diff: %u ms, timeout: %u ms";

void audio_conversate_ui_stop_5b03d8(void) {
    if (audio_uart_device_role_get() != 1u)
        return;
    uint32_t elapsed = g2_flashdb_candidate_tick() -
                       audio_conversate_last_success_tick_20074394;
    if (elapsed < 60001u)
        return;
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 160u, message,
                           elapsed, 60000u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04800000u, short_message, short_message,
                         elapsed, 60000u);
    audio_conversate_success_5b03c2();
    uint32_t descriptor[2] = {1u, 3u};
    audio_uart_ring_wear_persist_48eb32(0x40102u, 2u, descriptor);
    audio_conversate_report_5b02e4(19u, 1u);
}
