/* Stock APP_MasterResetSceneConnectPending, 0x4a2658..0x4a26b2. */
#include <stdint.h>

extern volatile uint8_t audio_ble_master_connect_state;
extern void audio_ble_master_connect_event(void);
extern void audio_event_loop_remove_delayed(void (*)(void));
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.master";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[] = "APP_MasterResetSceneConnectPending";
static const char message[] = "[Ring] Reset stale scene connect pending";
static const char compact[] = "[ble.master][Ring] Reset stale scene connect pending";

void audio_ble_master_reset_scene_pending_4a2658(void)
{
    if (audio_ble_master_connect_state != 1u) return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(2u, module, path, function, 0x503u, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x08000000u, compact, compact);
    audio_ble_master_connect_state = 0u;
    audio_event_loop_remove_delayed(audio_ble_master_connect_event);
}
