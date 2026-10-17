/* Native SVC_Settings_SyncHandler 0x46bbb4. The two version children remain
 * explicit imports until their C implementations are integrated. */
#include <stdint.h>

extern uint8_t audio_settings_config_live[];
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern uint32_t audio_settings_terminal_mode(void);
extern void audio_settings_terminal_mode_set(uint32_t);
extern void SVC_Settings_DumpSettingConfig(void);
extern void audio_settings_apply_display_levels(void);
extern void audio_settings_send_config_to_peer(void);
extern void audio_settings_update_left_version(const uint8_t *);
extern void audio_settings_sync_version_only_send(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "service.settings";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[] = "SVC_Settings_SyncHandler";
static const char invalid[] = "invalid sync data, len=%u";
static const char invalid_short[] = "[service.settings]invalid sync data, len=%u";
static const char terminal[] = "terminal mode changed: %d -> %d, save to kv";
static const char terminal_short[] = "[service.settings]terminal mode changed: %d -> %d, save to kv";
static const char master[] = "recv master settings sync:";
static const char master_short[] = "[service.settings]recv master settings sync:";
static const char same_crc[] = "crc value match, not send";
static const char same_crc_short[] = "[service.settings]crc value match, not send";
static const char different_crc[] = "recv slave settings sync, crc value not match, send config to slave";
static const char different_crc_short[] = "[service.settings]recv slave settings sync, crc value not match, send config to slave";
static const char version_request[] = "recv master version request, reply local version";
static const char version_request_short[] = "[service.settings]recv master version request, reply local version";

static void sync_log(uint8_t severity, uint32_t line, const char *message,
                     uint32_t compact_code, const char *short_message)
{
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(severity, module, path, function, line, message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(compact_code, short_message, short_message);
}

uint32_t audio_setting_handle_command5_46bbb4(const uint8_t *payload, uint32_t length)
{
    if (payload == 0 || length < 48u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, function, 0x10du,
                               invalid, length);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08400000u, invalid_short,
                                        invalid_short, length);
        return 0u;
    }

    if (payload[0] == 0u && audio_uart_device_role_get() == 2u) {
        audio_uart_checksum_copy(audio_settings_config_live, payload + 4u, 28u);
        uint8_t new_mode = payload[0x21u];
        if (audio_settings_terminal_mode() != new_mode) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(3u, module, path, function, 0x114u,
                                   terminal, audio_settings_terminal_mode(), new_mode);
            if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x0c800000u, terminal_short,
                                            terminal_short,
                                            audio_settings_terminal_mode(), new_mode);
            audio_settings_terminal_mode_set(new_mode);
        }
        sync_log(3u, 0x118u, master, 0x0c000000u, master_short);
        SVC_Settings_DumpSettingConfig();
        audio_settings_apply_display_levels();
        audio_settings_sync_version_only_send();
    } else if (payload[0] == 1u && audio_uart_device_role_get() == 1u) {
        audio_settings_update_left_version(payload + 0x24u);
        uint16_t packet_crc = (uint16_t)payload[0x1cu] |
                              (uint16_t)((uint16_t)payload[0x1du] << 8);
        uint16_t local_crc = (uint16_t)audio_settings_config_live[0x18u] |
                             (uint16_t)((uint16_t)audio_settings_config_live[0x19u] << 8);
        if (packet_crc == local_crc)
            sync_log(3u, 0x125u, same_crc, 0x0c000000u, same_crc_short);
        else {
            sync_log(3u, 0x128u, different_crc, 0x0c000000u,
                     different_crc_short);
            audio_settings_send_config_to_peer();
        }
    } else if (payload[0] == 2u && audio_uart_device_role_get() == 1u) {
        audio_settings_update_left_version(payload + 0x24u);
    } else if (payload[0] == 3u && audio_uart_device_role_get() == 2u) {
        sync_log(3u, 0x12fu, version_request, 0x0c000000u,
                 version_request_short);
        audio_settings_sync_version_only_send();
    }
    return 0u;
}
