/* Stock Apollo system_alert_common_data_handler 0x4d2bce. */
#include <stdint.h>

uint32_t audio_system_alert_message_notify
    __attribute__((section(".bss.g2.ram.system_alert_message_notify"),used,aligned(4))); /* native RAM 0x200749f4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_log_wake_allowed(void); /* 0x443484 */
extern uint32_t audio_system_alert_command_45a8ee(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);

static const char module[] = "system_alert";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c";
static const char function[] = "system_alert_common_data_handler";
static const char message[] = "MessageNotify recv data len = %d";
static const char compact[] = "[system_alert]MessageNotify recv data len = %d";

uint32_t audio_uart_registry_callback_4d2bce(uint32_t unused,
                                               uint32_t payload,
                                               uint32_t length) {
    (void)unused;
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 59u, message, length);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x10400000u, compact, compact, length);
    audio_system_alert_message_notify = *(const uint8_t *)(uintptr_t)payload;
    if(audio_uart_device_role_get() == 1u && audio_log_wake_allowed() == 1u)
        (void)audio_system_alert_command_45a8ee(33u, 0u, 0u, 200u);
    return 0u;
}
