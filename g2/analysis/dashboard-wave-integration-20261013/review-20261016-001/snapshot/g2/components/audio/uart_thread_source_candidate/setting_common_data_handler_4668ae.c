/* Native Setting_common_data_handler 0x4668ae..0x466976. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_setting_parse_data_package_49b1f8(const uint8_t *, uint32_t,
                                                          uint8_t *);
extern uint32_t audio_setting_process_data_466976(uint8_t *);
extern uint32_t audio_setting_handle_command5_46bbb4(const uint8_t *, uint32_t);
extern uint8_t audio_settings_last_message_state[];

static const char module[] = "setting";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "Setting_common_data_handler";
static const char start_message[] = "BLE data parsing started";
static const char start_short[] = "[setting]BLE data parsing started";
static const char failure_message[] = "setting_parse_data_package failed!";
static const char failure_short[] = "[setting]setting_parse_data_package failed!";

int32_t audio_uart_registry_callback_4668ae(uint32_t command,
                                              const uint8_t *payload,
                                              uint32_t length) {
    if (command == 0u && payload != 0 && length != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x63u, start_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u, start_short, start_short);
        if ((uint8_t)audio_setting_parse_data_package_49b1f8(
                payload, length, audio_settings_last_message_state) == 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(2u, module, path, function, 0x67u,
                                   failure_message);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x08000000u, failure_short,
                                            failure_short);
            return -1;
        }
        (void)audio_setting_process_data_466976(audio_settings_last_message_state);
    } else if (command == 5u) {
        (void)audio_setting_handle_command5_46bbb4(payload, length);
    }
    return 0;
}
