/* Native tracepoint_setting_common_data_handler 0x5eeec4 and role-char
 * helper 0x5edadc. Child handlers at 0x5ee8bc/0x5eeb98 remain explicit. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t audio_tracepoint_handle_ble_data_5ee8bc(const void *, uint32_t);
extern uint32_t audio_tracepoint_handle_slave_file_list_5eeb98(const void *, uint32_t);
extern uint32_t audio_ring_pb_tx_ble_475b14(uint32_t, uint32_t, const void *, uint32_t);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_setting_common_data_handler";
static const char event_message[] = "tracepoint handler event=%d len=%u role=%c";
static const char event_short[] = "[tp.setting]tracepoint handler event=%d len=%u role=%c";
static const char delete_message[] = "tracepoint forward slave delete result len=%u ret=%d";
static const char delete_short[] = "[tp.setting]tracepoint forward slave delete result len=%u ret=%d";

uint32_t audio_tracepoint_role_char_5edadc(void)
{
    return audio_uart_device_role_get() == 1u ? (uint32_t)'R' : (uint32_t)'L';
}

uint32_t audio_uart_registry_callback_5eeec4(uint32_t event,
                                               const void *payload,
                                               uint32_t length,
                                               uint32_t fourth)
{
    (void)fourth;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x21eu,
                           event_message, event, length,
                           audio_tracepoint_role_char_5edadc(), fourth);
    if ((audio_log_flags() & 1u) != 0u ||
        (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10c00000u, event_short, event_short,
                                    event, length,
                                    audio_tracepoint_role_char_5edadc());
    if (event == 0u)
        return audio_tracepoint_handle_ble_data_5ee8bc(payload, length);
    if (event == 0xbu)
        return audio_tracepoint_handle_slave_file_list_5eeb98(payload, length);
    if (event == 0xcu) {
        if (payload == 0 || length == 0u)
            return UINT32_MAX;
        uint32_t result = audio_ring_pb_tx_ble_475b14(1u, 0x11u,
                                                       payload, length & 0xffffu);
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x22au,
                               delete_message, length, result);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10800000u, delete_short,
                                        delete_short, length, result);
        return result;
    }
    return 0u;
}
