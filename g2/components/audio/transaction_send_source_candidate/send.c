#include <stdint.h>

/* gx8002_send_and_wait_response, native 0x57c512..0x57c60f.
 * Protocol packet construction and transport are real explicit lowers. */
extern uint8_t g2_audio_transaction_transport[];
extern int32_t audio_transaction_init(void);
extern int32_t audio_transaction_construct(uint32_t code, uint32_t family,
                                           uint32_t payload, uint32_t length,
                                           uint32_t flags);
extern void audio_transaction_cleanup(void);
extern int32_t audio_transaction_exchange(void *transport, uint32_t expected,
                                          uint16_t *response, uint32_t timeout);
extern int32_t audio_transaction_extract(void *transport, uint32_t response,
                                         void *transaction);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_send_and_wait_response";
static const char response_format[] =
    "Response received: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X";
static const char simple_response[] =
    "[codec.host]Response received: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X";

int32_t audio_send_transaction(uint32_t code, uint32_t family,
                               uint32_t payload, uint32_t length,
                               uint32_t flags, void *transaction,
                               uint32_t timeout) {
    if (transaction == 0)
        return -1;
    (void)audio_transaction_init();
    int32_t status = audio_transaction_construct((uint16_t)code,
                                                  (uint16_t)family,
                                                  payload, (uint16_t)length,
                                                  (uint8_t)flags);
    if (status != 0) {
        audio_transaction_cleanup();
        return status;
    }
    uint16_t response = 0;
    status = audio_transaction_exchange(g2_audio_transaction_transport,
                                        30u, &response, timeout);
    if (status != 0) {
        audio_transaction_cleanup();
        return status;
    }
    audio_transaction_cleanup();
    status = audio_transaction_extract(g2_audio_transaction_transport,
                                       response, transaction);
    if (status != 0)
        return status;
    const uint8_t *const bytes = transaction;
    const uint16_t cmd = (uint16_t)((uint16_t)bytes[4] |
                                     ((uint16_t)bytes[5] << 8));
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, 344u,
                           response_format, cmd, bytes[5], bytes[4],
                           bytes[6], bytes[7]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x11400000u, simple_response,
                         simple_response, cmd, bytes[5], bytes[4],
                         bytes[6], bytes[7]);
    return 0;
}
