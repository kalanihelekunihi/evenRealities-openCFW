#include <stdint.h>

/* Native packet constructor 0x57bb0a. Selected codec_pack supplies
 * the full payload/CRC algorithm; this wrapper supplies stock's
 * overflow and successful-packet diagnostic branches. */
extern int32_t codec_pack(uint16_t low, uint16_t high,
                          const uint8_t *payload, uint16_t length,
                          uint8_t crcflag, uint8_t *wire,
                          uint16_t *total);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_pack_message";
static const char too_large[] = "Message body too large: %d";
static const char simple_too_large[] =
    "[codec.host]Message body too large: %d";
static const char packed[] =
    "Pack message(total len=%d): cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X";
static const char simple_packed[] =
    "[codec.host]Pack message(total len=%d): cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X";

static uint32_t packed_crc(const uint8_t *wire) {
    return (uint32_t)wire[10] | ((uint32_t)wire[11] << 8) |
           ((uint32_t)wire[12] << 16) | ((uint32_t)wire[13] << 24);
}

/* Stock 0x57BB0A (gx8002_pack_message) */
int32_t audio_packet_pack(uint32_t code, uint32_t family,
                          uint32_t payload, uint32_t length,
                          uint32_t flags, uint8_t *wire,
                          uint16_t *total) {
    const uint16_t declared = (uint16_t)((uint16_t)length +
                                          ((uint8_t)flags != 0u ? 4u : 0u));
    const int32_t status = codec_pack((uint16_t)code, (uint16_t)family,
                                      (const uint8_t *)(uintptr_t)payload,
                                      (uint16_t)length, (uint8_t)flags,
                                      wire, total);
    if (status == -2 && wire != 0 && total != 0) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 87u,
                               too_large, declared);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04400000u, simple_too_large,
                             simple_too_large, declared);
        return status;
    }
    if (status != 0)
        return status;
    const uint16_t command = (uint16_t)((uint16_t)wire[4] |
                                         ((uint16_t)wire[5] << 8));
    const uint32_t crc = packed_crc(wire);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, file, function, 122u,
                           packed, *total, command, wire[5], wire[4],
                           wire[6], wire[7],
                           (uint16_t)((uint16_t)wire[8] |
                                      ((uint16_t)wire[9] << 8)), crc);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x12000000u, simple_packed, simple_packed,
                         *total, command, wire[5], wire[4], wire[6],
                         wire[7],
                         (uint16_t)((uint16_t)wire[8] |
                                    ((uint16_t)wire[9] << 8)), crc);
    return 0;
}
