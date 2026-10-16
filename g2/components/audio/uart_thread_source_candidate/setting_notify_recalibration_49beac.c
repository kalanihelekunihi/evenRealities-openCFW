/* Native setting_notify_recalibration_status_to_app 0x49beac..0x49bf16. */
#include <stdint.h>

extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_settings_notify_common(uint8_t *);

static const char module[] = "pb_service_setting";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_setting\\pb_service_setting.c";
static const char function[] = "setting_notify_recalibration_status_to_app";
static const char message[] = "[Notify Recalibration Status] status = %d";
static const char compact[] =
    "[pb_service_setting][Notify Recalibration Status] status = %d";

void audio_settings_notify_recalibration_status_49beac(uint32_t status) {
    uint8_t packet[104];
    audio_uart_buffer_zero(packet, 104u, 0u);
    packet[0] = 3u;
    packet[8] = 5u;
    packet[9] = 0u;
    packet[12] = 1u;
    packet[13] = 0u;
    packet[16] = (uint8_t)status;
    packet[17] = (uint8_t)(status >> 8);
    packet[18] = (uint8_t)(status >> 16);
    packet[19] = (uint8_t)(status >> 24);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x1b0u, message, status);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c400000u, compact, compact, status);
    (void)audio_settings_notify_common(packet);
}
