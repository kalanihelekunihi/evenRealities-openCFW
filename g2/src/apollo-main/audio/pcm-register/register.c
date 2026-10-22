#include <stdint.h>

/* SVC_PcmAppRegister, native 0x57ab78..0x57accf. The registration
 * rows are product RAM at 0x20073c20; their initializer is external. */
extern uint32_t g2_pcm_registration_rows[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "svc.audio";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio.c";
static const char function[] = "SVC_PcmAppRegister";
static const char invalid[] = "Invalid parameters for app registration";
static const char simple_invalid[] =
    "[svc.audio]Invalid parameters for app registration";
static const char replacing[] =
    "PCM stream is already occupied by app ID %d, unregistering previous app";
static const char simple_replacing[] =
    "[svc.audio]PCM stream is already occupied by app ID %d, unregistering previous app";
static const char registered[] = "PCM app registered: ID=%d, Source=%d";
static const char simple_registered[] =
    "[svc.audio]PCM app registered: ID=%d, Source=%d";

/* Stock 0x0057AB78 (SVC_PcmAppRegister) */
int32_t audio_register(uint32_t app_id, uint32_t mode, uint32_t callback) {
    const uint32_t index = (uint8_t)mode;
    if (index >= 2u || callback == 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 191u, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, simple_invalid, simple_invalid);
        return -1;
    }

    volatile uint32_t *const row = &g2_pcm_registration_rows[3u * index];
    if (row[2] != 0u) {
        const uint32_t previous = row[0];
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, file, function, 198u,
                               replacing, previous);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08400000u, simple_replacing,
                             simple_replacing, previous);
        /* Native zero fill stores words +4, +8, then +0. */
        row[1] = 0u;
        row[2] = 0u;
        row[0] = 0u;
    }
    row[0] = app_id;
    ((volatile uint8_t *)row)[4] = (uint8_t)mode;
    row[2] = callback;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, file, function, 208u,
                           registered, app_id, index);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, simple_registered,
                         simple_registered, app_id, index);
    return 0;
}
