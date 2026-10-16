/* Stock audio manager app release at 0x54f50e. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint8_t g2_audio_app_acquired[8]; /* stock 0x20074180 */
extern uint8_t audio_even_ai_app_count_54f364(void);
extern void audio_app_codec_enable_53ca32(uint32_t enabled);
extern void audio_app_stream_enable_53ca10(uint32_t enabled);

static const char module[] = "service.audio.manager";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio_manager.c";
static const char function[] = "AUDM_appRelease";
static const char invalid[] = "invalid app_id";
static const char invalid_short[] = "[service.audio.manager]invalid app_id";
static const char already[] = "app %d already released";
static const char already_short[] = "[service.audio.manager]app %d already released";
static const char released[] = "app %d released, remaining apps: %d";
static const char released_short[] = "[service.audio.manager]app %d released, remaining apps: %d";
static const char last[] = "no apps using audio, shutting down hardware";
static const char last_short[] = "[service.audio.manager]no apps using audio, shutting down hardware";

uint32_t audio_terminal_reset_mode_notice_54f50e(uint32_t raw_app) {
    if (audio_uart_device_role_get() != 2u)
        return 0u;
    uint8_t app = (uint8_t)raw_app;
    if (app == 0u || app >= 8u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x48u, invalid);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, invalid_short, invalid_short);
        return UINT32_MAX;
    }
    if (g2_audio_app_acquired[app] == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x4du, already, app);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, already_short, already_short, app);
        return 0u;
    }
    g2_audio_app_acquired[app] = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x54u, released,
                           app, audio_even_ai_app_count_54f364());
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, released_short,
                                    released_short, app,
                                    audio_even_ai_app_count_54f364());
    if (audio_even_ai_app_count_54f364() == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x58u, last);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, last_short, last_short);
        audio_app_codec_enable_53ca32(0u);
        audio_app_stream_enable_53ca10(0u);
    }
    return 0u;
}
