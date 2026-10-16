/* Stock audio manager app acquisition, 0x54f380 and count helper 0x54f364. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_app_first_hardware_prepare_57a926(const void *);
extern void audio_app_codec_enable_53ca32(uint32_t);
extern void audio_app_stream_enable_53ca10(uint32_t);
extern uint8_t g2_audio_first_hardware_context_20108948;

/* Eight stock byte slots begin at 0x20074180; final placement remains gated. */
uint8_t g2_audio_app_acquired[8];
static const char module[] = "service.audio.manager";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio_manager.c";
static const char function[] = "AUDM_appAcquire";
static const char invalid[] = "invalid parameters";
static const char invalid_short[] = "[service.audio.manager]invalid parameters";
static const char already[] = "app %d already acquired";
static const char already_short[] = "[service.audio.manager]app %d already acquired";
static const char acquired[] = "app %d acquired, remaining apps: %d";
static const char acquired_short[] = "[service.audio.manager]app %d acquired, remaining apps: %d";
static const char first[] = "first app acquired, initializing hardware";
static const char first_short[] =
    "[service.audio.manager]first app acquired, initializing hardware";

uint8_t audio_even_ai_app_count_54f364(void) {
    uint8_t count = 0u;
    for (uint32_t index = 0; index < 8u; ++index)
        if (g2_audio_app_acquired[index] == 1u)
            ++count;
    return count;
}

uint32_t audio_even_ai_app_acquire_54f380(uint32_t app, uint32_t unused2,
                                            uint32_t unused3, uint32_t logged4) {
    (void)unused2;
    if (audio_uart_device_role_get() != 2u)
        return 0u;
    app = (uint8_t)app;
    if (app == 0u || app >= 8u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x2bu, invalid,
                               unused3, logged4);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, invalid_short, invalid_short);
        return UINT32_MAX;
    }
    if (g2_audio_app_acquired[app] == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 0x30u, already,
                               app, logged4);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x08400000u, already_short,
                                        already_short, app);
        return 0u;
    }
    g2_audio_app_acquired[app] = 1u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 0x35u, acquired,
                           app, audio_even_ai_app_count_54f364());
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x0c800000u, acquired_short,
                                    acquired_short, app,
                                    audio_even_ai_app_count_54f364());
    if (audio_even_ai_app_count_54f364() == 1u) {
        audio_app_first_hardware_prepare_57a926(&g2_audio_first_hardware_context_20108948);
        audio_app_codec_enable_53ca32(1u);
        audio_app_stream_enable_53ca10(1u);
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0x3cu, first);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c000000u, first_short, first_short);
    }
    return 0u;
}
