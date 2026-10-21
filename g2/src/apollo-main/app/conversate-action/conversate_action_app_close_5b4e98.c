/* Native conversate_action_app_close 0x5b4e98..0x5b4f71. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t);
extern uint32_t audio_uart_device_role_get(void);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t, uint32_t, const void *);
extern void audio_conversate_report_5b02e4(uint32_t, uint32_t);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_action_app_close";
static const char null_message[] = "pData is NULL";
static const char null_short[] = "[conversate]pData is NULL";
static const char close_message[] = "conversate app close, errCode: %d";
static const char close_short[] = "[conversate]conversate app close, errCode: %d";
static const uint32_t wear_descriptor[2] = {1u, 2u};

uint32_t audio_conversate_action_5b4e98(void *context, const void *arg1,
                                           void *arg2) {
    (void)arg2;
    if (!arg1) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 237u, null_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, null_short, null_short);
        return UINT32_MAX;
    }
    const uint8_t error = ((const uint8_t *)arg1)[0x90];
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 241u, close_message, error);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c400000u, close_short, close_short, error);
    audio_uart_buffer_zero(context, 6u, 0u);
    if (audio_uart_device_role_get() == 1u)
        audio_uart_ring_wear_persist_48eb32(0x40102u, 2u, wear_descriptor);
    audio_conversate_report_5b02e4(20u, error);
    return 0u;
}
