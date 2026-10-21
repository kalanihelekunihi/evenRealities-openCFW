/* Stock APP_MasterBeginRingConnectFailureNotifyAfterRetry, 0x4a1546..0x4a159e. */
#include <stdint.h>

extern volatile uint8_t audio_ble_master_failure_notify;
extern volatile uint8_t audio_ble_master_failure_count;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.master";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[] = "APP_MasterBeginRingConnectFailureNotifyAfterRetry";
static const char message[] = "Ring connect failure notify armed after second failure";
static const char compact[] = "[ble.master]Ring connect failure notify armed after second failure";

void audio_ble_master_begin_failure_notify_4a1546(void)
{
    audio_ble_master_failure_notify = 1u;
    audio_ble_master_failure_count = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x374u, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, compact, compact);
}
