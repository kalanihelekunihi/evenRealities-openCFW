#include <stdint.h>

/* gx8002_send_message, native 0x57c0d6..0x57c1fb. */
extern uint8_t g2_audio_tx_packet[];
extern int32_t audio_packet_pack(uint32_t code, uint32_t family,
                                 uint32_t payload, uint32_t length,
                                 uint32_t flags, uint8_t *packet,
                                 uint16_t *packed_length);
extern void audio_dump_hex(const char *label, uint32_t width,
                           const void *data, uint32_t length);
extern int32_t audio_uart_send_bytes(const void *data, uint32_t length);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_send_message";
static const char dump_label[] = "8002_tx";
static const char pack_failed[] = "Failed to pack message: %d";
static const char simple_pack_failed[] =
    "[codec.host]Failed to pack message: %d";
static const char send_failed[] = "Failed to send UART data: %d";
static const char simple_send_failed[] =
    "[codec.host]Failed to send UART data: %d";
static const char sent[] = "Message sent successfully";
static const char simple_sent[] =
    "[codec.host]Message sent successfully";

int32_t audio_transaction_construct(uint32_t code, uint32_t family,
                                     uint32_t payload, uint32_t length,
                                     uint32_t flags) {
    uint16_t packed_length = 0u;
    int32_t status = audio_packet_pack((uint16_t)code, (uint16_t)family,
                                       payload, (uint16_t)length,
                                       (uint8_t)flags, g2_audio_tx_packet,
                                       &packed_length);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 218u,
                               pack_failed, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_pack_failed,
                             simple_pack_failed, status);
        return status;
    }
    audio_dump_hex(dump_label, 16u, g2_audio_tx_packet, packed_length);
    status = audio_uart_send_bytes(g2_audio_tx_packet, packed_length);
    if (status != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 226u,
                               send_failed, status);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_send_failed,
                             simple_send_failed, status);
        return status;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, 229u, sent);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x10000000u, simple_sent, simple_sent);
    return 0;
}
