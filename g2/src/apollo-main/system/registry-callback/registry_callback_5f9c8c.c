/* Stock Apollo UX_SettingsCommonDataHandler 0x5f9c8c. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern int32_t audio_uart_thread_msg_rx_from_ble_48f12c(uint32_t, const void *, uint32_t);

static const char module[] = "ux.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_settings\\ux_settings.c";
static const char function[] = "UX_SettingsCommonDataHandler";
static const char message[] = "SID_UX_DEVICE_SETTINGS_APP_ID = %d";
static const char compact[] = "[ux.setting]SID_UX_DEVICE_SETTINGS_APP_ID = %d";

uint32_t audio_uart_registry_callback_5f9c8c(uint32_t unused,
                                                uint32_t payload,
                                                uint32_t length) {
    (void)unused;
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 19u, message, 0x80u);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, 0x80u);
    (void)audio_uart_thread_msg_rx_from_ble_48f12c(0x80u,
                                                      (const void *)(uintptr_t)payload,
                                                      (uint16_t)length);
    return 0u;
}
