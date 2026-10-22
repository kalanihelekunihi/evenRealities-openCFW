#include <stdint.h>

/* Stock SVC_PcmAppUnregister 0x0057acd0..0x0057adf7. The 12-byte rows
 * live at stock 0x20073c20. Their count and producer are product data. */
struct g2_pcm_registration_slot {
    uint32_t app_id;
    uint32_t context;
    uint32_t active;
};
extern struct g2_pcm_registration_slot g2_pcm_registration_rows[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "svc.audio";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio.c";
static const char function[] = "SVC_PcmAppUnregister";
static const char none[] = "No PCM app registered";
static const char simple_none[] = "[svc.audio]No PCM app registered";
static const char mismatch[] = "App ID %d not found, current app ID is %d";
static const char simple_mismatch[] =
    "[svc.audio]App ID %d not found, current app ID is %d";
static const char removed[] = "PCM app unregistered: ID=%d";
static const char simple_removed[] = "[svc.audio]PCM app unregistered: ID=%d";

/* Stock 0x0057ACD0 (SVC_PcmAppUnregister) */
int32_t audio_unregister(uint32_t app_id, uint32_t index) {
    struct g2_pcm_registration_slot *slot = &g2_pcm_registration_rows[(uint8_t)index];
    if (slot->active == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, file, function, 216u, none);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, simple_none, simple_none);
        return 0;
    }
    if (slot->app_id == app_id) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, file, function, 225u, removed, app_id);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x0c400000u, simple_removed, simple_removed, app_id);
        slot->app_id = 0u;
        slot->context = 0u;
        slot->active = 0u;
        return 0;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, file, function, 221u, mismatch,
                           app_id, slot->app_id);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08800000u, simple_mismatch, simple_mismatch,
                         app_id, slot->app_id);
    return -1;
}
