/* Native tracepoint_reply_result 0x5ee134, role-selected reply routing. */
#include <stdint.h>

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern uint32_t audio_tracepoint_send_to_master_5ee066(uint32_t, const uint8_t *);
extern uint32_t audio_tracepoint_send_to_phone_5edfd8(const uint8_t *);

static const char module[] = "tp.setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function[] = "tracepoint_reply_result";
static const char master_message[] = "tracepoint reply slave result to master cmd=%d result=%u";
static const char master_short[] = "[tp.setting]tracepoint reply slave result to master cmd=%d result=%u";
static const char phone_message[] = "tracepoint reply result to phone cmd=%d result=%u";
static const char phone_short[] = "[tp.setting]tracepoint reply result to phone cmd=%d result=%u";

void audio_tracepoint_reply_result_5ee134(const uint8_t *reply)
{
    uint32_t command = reply[0], result = reply[4];
    if (audio_uart_device_role_get() == 2u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x11au,
                               master_message, command, result);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10800000u, master_short,
                                        master_short, command, result);
        (void)audio_tracepoint_send_to_master_5ee066(0xcu, reply);
    } else {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x11fu,
                               phone_message, command, result);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10800000u, phone_short,
                                        phone_short, command, result);
        (void)audio_tracepoint_send_to_phone_5edfd8(reply);
    }
}
