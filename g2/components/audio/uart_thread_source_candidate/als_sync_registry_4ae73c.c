/* Native ALSSyncHandler 0x4ae73c and settings_set_auto_brightness 0x46bff4.
 * The settings byte is offset +1 in the live 0x20072da8 record. */
#include <stdint.h>

extern uint8_t audio_settings_config_live[];
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern const uint32_t g2_display_state_table[]; /* ROM 0x776a3c */

void *audio_als_callback_context_47394c(void)
{
    return (void *)(uintptr_t)g2_display_state_table;
}
extern uint32_t audio_settings_notify_device_status(void);

static const char module[] = "sensor_als";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\sensor\\als\\als.c";
static const char function[] = "ALSSyncHandler";
static const char received[] = "ALSSyncHandler, recv brightness_level:%d, notify_app:%d";
static const char received_short[] = "[sensor_als]ALSSyncHandler, recv brightness_level:%d, notify_app:%d";
static const char bad_length[] = "ALSSyncHandler, data length error, len:%d";
static const char bad_length_short[] = "[sensor_als]ALSSyncHandler, data length error, len:%d";

uint32_t audio_als_settings_set_auto_brightness_46bff4(uint8_t value)
{
    audio_settings_config_live[1] = value;
    return 0;
}

uint32_t audio_uart_registry_callback_4ae73c(uint32_t event,
                                               const uint8_t *data,
                                               uint32_t length)
{
    (void)event;
    if (length != 2u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 0x26cu,
                               bad_length, length);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04400000u, bad_length_short,
                                        bad_length_short, length);
        return UINT32_MAX;
    }
    uint32_t level = data[0];
    uint32_t notify = data[1] != 0u;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, 0x271u,
                           received, level, notify);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c800000u, received_short,
                                    received_short, level, notify);
    (void)audio_als_settings_set_auto_brightness_46bff4((uint8_t)level);
    void *context = audio_als_callback_context_47394c();
    uintptr_t callback = *(const uintptr_t *)((const uint8_t *)context + 0x14u);
    ((void (*)(uint32_t))callback)(level);
    if (notify != 0u)
        (void)audio_settings_notify_device_status();
    return 0u;
}
