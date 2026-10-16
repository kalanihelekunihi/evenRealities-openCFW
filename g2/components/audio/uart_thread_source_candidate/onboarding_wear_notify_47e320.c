/* Stock onboarding_notify_wear_status_to_app, 0x47e320..0x47e3e6. */
#include <stdint.h>

extern uint32_t audio_ota_transfer_active(void); /* 0x4487ac */
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t); /* 0x4434d0 */
extern uint32_t audio_onboarding_event_encode_4a8368(uint32_t, const void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "onboarding.data_mgr";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding_data_manager.c";
static const char function[] = "onboarding_notify_wear_status_to_app";
static const char success_message[] = "Onboarding: wear status notified to app, status=%d";
static const char failure_message[] = "Onboarding: failed to notify wear status to app, ret=%d";
static const char success_short[] = "[onboarding.data_mgr]Onboarding: wear status notified to app, status=%d";
static const char failure_short[] = "[onboarding.data_mgr]Onboarding: failed to notify wear status to app, ret=%d";

void audio_wear_child_47e320(uint8_t status)
{
    if (audio_ota_transfer_active() == 1u || audio_log_wake_allowed() == 0u ||
        audio_quicklist_refresh_enabled_4434d0(0x10u) != 1u)
        return;
    /* Stock template at 0x78b648 is {1, 0, 0}; the middle word carries status. */
    uint32_t event[3] = {1u, (uint32_t)status, 0u};
    uint32_t result = audio_onboarding_event_encode_4a8368(0u, event);
    if (result == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x51u,
                               success_message, (uint32_t)status);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10400000u, success_short,
                                        success_short, (uint32_t)status);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x53u,
                               failure_message, result);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, failure_short,
                                        failure_short, result);
    }
}
