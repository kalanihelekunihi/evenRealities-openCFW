#include <stdint.h>

/* Local transaction protocol inferred from stock 0x57ce78. Driver transport,
 * transaction release, flags and log emission remain explicit providers.
 */
extern int32_t audio_send_transaction(uint32_t code, uint32_t family,
                                      uint32_t a2, uint32_t a3, uint32_t a4,
                                      void *transaction, uint32_t timeout);
extern void audio_release_transaction(void *transaction);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "GX8002_DMICCtrl";

int32_t audio_dmic_request(uint32_t enabled, uint16_t *response,
                           uint32_t timeout) {
    if (!response) return -1;
    uint32_t code = (uint8_t)enabled ? 12u : 13u;
    int32_t status = -1;
    uint8_t transaction[26];
    for (uint32_t attempt = 0; attempt < 3; ++attempt) {
        for (uint32_t i = 0; i < sizeof(transaction); ++i) transaction[i] = 0;
        status = audio_send_transaction(code, 0x100u, 0, 0, 0,
                                        transaction, timeout);
        if (!status) break;
        if (audio_log_flags() & 2u)
            audio_log_extended(2, module, file, function, 617,
                               "DMICCtrl attempt %d failed: %d",
                               attempt + 1, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08800000,
                             "[codec.host]DMICCtrl attempt %d failed: %d",
                             "[codec.host]DMICCtrl attempt %d failed: %d",
                             attempt + 1, status);
        audio_release_transaction(transaction);
    }
    if (status) return status;
    uint32_t length = (uint32_t)transaction[18] |
                      ((uint32_t)transaction[19] << 8);
    if (length < 2) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1, module, file, function, 627,
                               "Invalid DMIC ctrl response length: %d", length);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000,
                             "[codec.host]Invalid DMIC ctrl response length: %d",
                             "[codec.host]Invalid DMIC ctrl response length: %d",
                             length);
        audio_release_transaction(transaction);
        return -1;
    }
    uint32_t data = (uint32_t)transaction[14] |
                    ((uint32_t)transaction[15] << 8) |
                    ((uint32_t)transaction[16] << 16) |
                    ((uint32_t)transaction[17] << 24);
    const uint8_t *packet = (const uint8_t *)(uintptr_t)data;
    *response = (uint16_t)((uint16_t)packet[0] |
                           ((uint16_t)packet[1] << 8));
    if (audio_log_flags() & 2u)
        audio_log_extended(4, module, file, function, 632,
                           "DMIC ctrl status: 0x%04X", (uint32_t)*response);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10400000,
                         "[codec.host]DMIC ctrl status: 0x%04X",
                         "[codec.host]DMIC ctrl status: 0x%04X",
                         (uint32_t)*response);
    audio_release_transaction(transaction);
    return 0;
}
