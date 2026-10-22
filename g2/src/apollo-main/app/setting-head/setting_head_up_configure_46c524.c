/* Stock SVC_Settings_HeadUpConfig, 0x46c524..0x46c5f2. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void);
extern uint8_t audio_settings_config_live[]; /* stock RAM 0x20072da8 */
extern uint8_t *audio_settings_config_previous; /* manager +4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern int32_t HUB_Open(uint8_t func_type); /* 0x4a6d58 */
extern int32_t HUB_Close(uint8_t func_type); /* 0x4a6dca */
extern uint32_t audio_hub_parameter_config_4a6e3c(uint32_t, const int32_t *);

static const char module[] = "service.settings";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\settings\\service_settings.c";
static const char function[] = "SVC_Settings_HeadUpConfig";
static const char open_format[] = "head up switch open, open head up display";
static const char close_format[] = "head up switch close, close head up display";
static const char open_short[] = "[service.settings]head up switch open, open head up display";
static const char close_short[] = "[service.settings]head up switch close, close head up display";

static uint32_t word(const uint8_t *data)
{
    return (uint32_t)data[0] | ((uint32_t)data[1] << 8) |
           ((uint32_t)data[2] << 16) | ((uint32_t)data[3] << 24);
}

void audio_setting_head_up_configure_46c524(void)
{
    if (audio_uart_device_role_get() != 1u)
        return;
    const uint8_t *config = audio_settings_config_live[0] != 0u ?
                            audio_settings_config_live : audio_settings_config_previous;
    if (config[0xau] == 1u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x241u, open_format);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, open_short, open_short);
        (void)HUB_Open(1u);
        int32_t angle = (int32_t)(word(config + 0x10u) + word(config + 0xcu));
        if (angle > 90)
            angle = 90;
        if (angle < -90)
            angle = -90;
        int32_t params[2] = {angle, 0};
        (void)audio_hub_parameter_config_4a6e3c(1u, params);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, function, 0x24cu, close_format);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x0c000000u, close_short, close_short);
        (void)HUB_Close(1u);
    }
}
