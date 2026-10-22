/* Native SVC_Settings_UpdateLeftVersion 0x46baec and
 * SVC_Settings_SyncVersionOnlySend 0x46b988. */
#include <stdint.h>

extern uint8_t audio_settings_config_live[];
extern const uint8_t audio_settings_version_text[9];
extern void *audio_settings_copy_text(void *, const void *, uint32_t);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern int32_t audio_settings_send_peer_packet(uint16_t, const void *, uint32_t,
                                               uint32_t, uint32_t);
extern uint32_t audio_settings_notify_device_status(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "service.settings";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char update_function[] = "SVC_Settings_UpdateLeftVersion";
static const char update_message[] = "recv left version: %s";
static const char update_short[] = "[service.settings]recv left version: %s";
static const char send_function[] = "SVC_Settings_SyncVersionOnlySend";
static const char send_message[] = "sync version reply send, local version: %s";
static const char send_short[] =
    "[service.settings]sync version reply send, local version: %s";

/* Stock 0x46BAEC (SVC_Settings_UpdateLeftVersion) */
void audio_settings_update_left_version(const uint8_t *version)
{
    if (version == 0 || version[0] == 0u)
        return;
    uint8_t *left_version = audio_settings_config_live + 0x44u;
    uint8_t had_version = left_version[0];
    (void)audio_settings_copy_text(left_version, version, 9u);
    audio_settings_config_live[0x4du] = 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, update_function, 0x103u,
                           update_message, left_version);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, update_short, update_short,
                                    left_version);
    if (had_version == 0u)
        (void)audio_settings_notify_device_status();
}

/* Stock 0x46B988 (SVC_Settings_SyncVersionOnlySend) */
void audio_settings_sync_version_only_send(void)
{
    uint8_t packet[48];
    audio_uart_buffer_zero(packet, 48u, 0u);
    packet[0] = 2u;
    (void)audio_settings_copy_text(packet + 36u, audio_settings_version_text, 9u);
    (void)audio_settings_send_peer_packet(9u, packet, 48u, 0u, 5u);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, send_function, 0xd9u,
                           send_message, audio_settings_version_text);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, send_short, send_short,
                                    audio_settings_version_text);
}
