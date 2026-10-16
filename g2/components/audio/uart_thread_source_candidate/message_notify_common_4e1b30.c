/* Stock Apollo MessageNotify_common_data_handler 0x4e1b30 and state write 0x4e1b28.
 * The frame decoder at 0x4d6ba8 remains an explicit child provider. */
#include <stdint.h>

uint8_t audio_message_notify_startup_state_20074fe5
    __attribute__((section(".bss.g2.ram.message_notify_startup_state"), used));

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern uint32_t audio_message_notify_frame_process_4d6ba8(const void *,
                                                             uint32_t);

static const char module[] = "message_notify.page";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\MessageNotify\\message_notify.c";
static const char function[] = "MessageNotify_common_data_handler";
static const char length_message[] = "MessageNotify recv data len = %d";
static const char length_compact[] =
    "[message_notify.page]MessageNotify recv data len = %d";
static const char startup_message[] = "recv msg_notif startup:%d";
static const char startup_compact[] =
    "[message_notify.page]recv msg_notif startup:%d";

void audio_message_notify_set_startup_4e1b28(uint8_t value) {
    audio_message_notify_startup_state_20074fe5 = value;
}

uint32_t audio_uart_registry_callback_4e1b30(uint32_t command,
                                               const uint8_t *payload,
                                               uint32_t length,
                                               uint32_t value) {
    (void)value;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, function, 0x4cu,
                           length_message, length);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, length_compact,
                                    length_compact, length);
    if (command == 0u) {
        (void)audio_message_notify_frame_process_4d6ba8(payload,
                                                          (uint16_t)length);
    } else if (command == 5u && payload[0] == 1u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(3u, module, path, function, 0x5cu,
                               startup_message, payload[1]);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x0c400000u, startup_compact,
                                        startup_compact, payload[1]);
        if (payload[1] == 2u || payload[1] == 4u) {
            audio_message_notify_set_startup_4e1b28(2u);
            uint32_t startup_value = (uint32_t)payload[2] |
                                     ((uint32_t)payload[3] << 8u) |
                                     ((uint32_t)payload[4] << 16u) |
                                     ((uint32_t)payload[5] << 24u);
            uint8_t request[6];
            audio_uart_buffer_zero(request, 6u, 0u);
            request[0] = 1u;
            request[1] = 3u;
            (void)audio_system_alert_command_45a8ee(
                4u, (uint32_t)(uintptr_t)request, 6u, startup_value);
        }
    }
    return 0u;
}
