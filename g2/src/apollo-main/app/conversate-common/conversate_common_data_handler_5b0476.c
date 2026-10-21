/* Native Conversate_common_data_handler 0x5b0476..0x5b05cf.
 * Deeper receive, packet handler and response functions remain explicit. */
#include <stdint.h>

extern uint8_t audio_conversate_reply_status_200d6b84[];
extern uint8_t audio_conversate_context_200d5bd8[];
extern uint32_t audio_conversate_enter_5b01ca(void);
extern uint32_t audio_conversate_receive_5b1b4c(const void *, uint16_t, void *);
extern uint32_t audio_conversate_data_handler_5b08a2(void *);
extern uint32_t audio_conversate_respond_5b200e(const uint8_t *, uint32_t);
extern void audio_conversate_success_5b03c2(void);
extern void audio_conversate_leave_5b0284(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate.c";
static const char function[] = "Conversate_common_data_handler";
static const char duplicate[] =
    "conversate duplicate packet, ignore and send success response";
static const char duplicate_short[] =
    "[conversate]conversate duplicate packet, ignore and send success response";
static const char error[] = "conversate error: %d, send error response";
static const char error_short[] =
    "[conversate]conversate error: %d, send error response";
static const char failed[] = "conversate data recv handler failed, ret: %d";
static const char failed_short[] =
    "[conversate]conversate data recv handler failed, ret: %d";

static void log_duplicate(uint32_t length, uint32_t extra) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, 174u,
                           duplicate, length, extra);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08000000u, duplicate_short, duplicate_short);
}
static void log_error(uint32_t status, uint32_t extra) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, 180u,
                           error, status, extra);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08400000u, error_short, error_short, status);
}
static void log_handler_failure(uint32_t result, uint32_t extra) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, path, function, 187u,
                           failed, result, extra);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x08400000u, failed_short, failed_short, result);
}

uint32_t audio_uart_registry_callback_5b0476(uint32_t event,
                                                const void *bytes,
                                                uint32_t length,
                                                uint32_t extra) {
    audio_conversate_enter_5b01ca();
    if (event == 0u) {
        uint8_t *const reply = audio_conversate_reply_status_200d6b84;
        uint8_t *const context = audio_conversate_context_200d5bd8;
        *reply = (uint8_t)audio_conversate_receive_5b1b4c(
            bytes, (uint16_t)length, context);
        if (*reply == 13u) {
            log_duplicate(length, extra);
            *reply = 0u;
            audio_conversate_respond_5b200e(reply, context[1]);
        } else if (*reply != 0u) {
            const uint32_t status = *reply;
            log_error(status, extra);
            *reply = 1u;
            audio_conversate_respond_5b200e(reply, context[1]);
        } else {
            const uint32_t result = audio_conversate_data_handler_5b08a2(context);
            if (result != 0u) {
                log_handler_failure(result, extra);
                *reply = 1u;
                audio_conversate_respond_5b200e(reply, context[1]);
            } else {
                *reply = 0u;
                audio_conversate_respond_5b200e(reply, context[1]);
                audio_conversate_success_5b03c2();
            }
        }
    }
    audio_conversate_leave_5b0284();
    return 0u;
}
