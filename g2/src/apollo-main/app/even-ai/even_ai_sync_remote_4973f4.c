/* Stock ANCC clear/sync path, 0x4973f4. */
#include <stdint.h>

extern void *audio_settings_ancc_mutex;
extern uint8_t audio_settings_ancc_count;
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_even_ai_ancc_display_clear_4e1af8(uint32_t, uint32_t);

/* Stock ANCC records at 0x20104c54..0x20106a7b; placement remains gated. */
uint8_t g2_audio_ancc_records_20104c54[0x1e28];
uint32_t g2_audio_ancc_sequence_20074918;

static const char module[] = "svc.ancc";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\message_notify\\service_ancc.c";
static const char function[] = "SVC_ANCC_Clear";
static const char no_mutex[] = "ANCC message mutex not initialized";
static const char no_mutex_short[] =
    "[svc.ancc]ANCC message mutex not initialized";
static const char acquire_failed[] =
    "Failed to acquire ANCC message mutex during clear";
static const char acquire_failed_short[] =
    "[svc.ancc]Failed to acquire ANCC message mutex during clear";

void audio_even_ai_sync_remote_4973f4(uint32_t notify) {
    void *mutex = audio_settings_ancc_mutex;
    if (!mutex) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x94u, no_mutex);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, no_mutex_short,
                                        no_mutex_short);
        return;
    }
    if (audio_file_mutex_acquire(mutex, UINT32_MAX) != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 0x99u, acquire_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, acquire_failed_short,
                                        acquire_failed_short);
        return;
    }
    audio_uart_buffer_zero(g2_audio_ancc_records_20104c54, 0x1e28u, 0u);
    g2_audio_ancc_sequence_20074918 = 0u;
    audio_settings_ancc_count = 0u;
    uint8_t count = audio_settings_ancc_count;
    (void)audio_file_mutex_release(mutex);
    if ((uint8_t)notify)
        audio_even_ai_ancc_display_clear_4e1af8(0u, count);
}
