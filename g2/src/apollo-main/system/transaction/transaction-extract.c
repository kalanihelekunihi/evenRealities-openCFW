#include <stdint.h>

/* gx8002_unpack_message, native 0x57bd06..0x57c0d5.
 * Based on selected codec_unpack's pinned packet/CRC algorithm;
 * diagnostics and body-CRC failure cleanup stay in native order. */
extern void *codec_allocate(uint32_t bytes);
extern void codec_release(void *buffer);
extern uint32_t codec_crc32(const uint8_t *data, uint32_t length,
                            const uint32_t *previous);
extern void audio_dump_hex(const char *label, uint32_t width,
                           const void *data, uint32_t length);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "codec.host";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c";
static const char function[] = "gx8002_unpack_message";
static const char magic[] = "Invalid magic word";
static const char simple_magic[] = "[codec.host]Invalid magic word";
static const char length_failed[] =
    "Message length mismatch: expected=%d, actual=%d";
static const char simple_length_failed[] =
    "[codec.host]Message length mismatch: expected=%d, actual=%d";
static const char header_crc_failed[] =
    "Header CRC32 mismatch: expected=0x%08X, calculated=0x%08X";
static const char simple_header_crc_failed[] =
    "[codec.host]Header CRC32 mismatch: expected=0x%08X, calculated=0x%08X";
static const char content_large[] = "Message content too large: %d";
static const char simple_content_large[] =
    "[codec.host]Message content too large: %d";
static const char alloc_failed[] =
    "Failed to allocate memory for message content";
static const char simple_alloc_failed[] =
    "[codec.host]Failed to allocate memory for message content";
static const char body_crc_failed[] =
    "Body CRC32 mismatch: expected=0x%08X, calculated=0x%08X";
static const char simple_body_crc_failed[] =
    "[codec.host]Body CRC32 mismatch: expected=0x%08X, calculated=0x%08X";
static const char unpacked[] =
    "Unpack message: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X";
static const char simple_unpacked[] =
    "[codec.host]Unpack message: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X";
static const char body_length[] = "body content length: %d";
static const char simple_body_length[] =
    "[codec.host]body content length: %d";
static const char body_dump[] = "8002_rx body";

static uint16_t read16(const uint8_t *data) {
    return (uint16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}
static uint32_t read32(const uint8_t *data) {
    return (uint32_t)read16(data) | ((uint32_t)read16(data + 2) << 16);
}
static void write16(uint8_t *data, uint16_t value) {
    data[0] = (uint8_t)value;
    data[1] = (uint8_t)(value >> 8);
}
static void write32(uint8_t *data, uint32_t value) {
    write16(data, (uint16_t)value);
    write16(data + 2, (uint16_t)(value >> 16));
}
static void copy_bytes(uint8_t *destination, const uint8_t *source,
                       uint32_t count) {
    for (uint32_t i = 0; i < count; ++i)
        destination[i] = source[i];
}
static int32_t unpack_core(const uint8_t *input, uint16_t available,
                           uint8_t *output) {
    if (input == 0 || output == 0 || available < 14u)
        return -1;
    copy_bytes(output, input, 14u);
    if (output[0] != 'B' || output[1] != 'U' ||
        output[2] != 'X' || output[3] != 'X')
        return -2;
    const uint16_t total = (uint16_t)(read16(output + 8) + 14u);
    if (available < total)
        return -3;
    if (codec_crc32(input, 10u, 0) != read32(output + 10))
        return -4;
    uint16_t body = read16(output + 8);
    if (output[7] & 1u)
        body = (uint16_t)(body - 4u);
    if (body == 0u) {
        write32(output + 14, 0u);
        write16(output + 18, 0u);
    } else {
        if (body > 16u)
            return -5;
        uint8_t *const owned = codec_allocate(body);
        write32(output + 14, (uint32_t)(uintptr_t)owned);
        if (owned == 0)
            return -6;
        copy_bytes(owned, input + 14, body);
        write16(output + 18, body);
        if (output[7] & 1u) {
            copy_bytes(output + 20, input + 14 + body, 4u);
            if (codec_crc32(owned, body, 0) != read32(output + 20))
                return -7;
        }
    }
    write16(output + 24, total);
    return 0;
}
static int simple_enabled(void) {
    return (audio_log_flags() & 1u) || (audio_log_flags() & 4u);
}

/* Stock 0x57BD06 (gx8002_unpack_message) */
int32_t audio_transaction_extract(const void *wire, uint32_t available,
                                   void *message) {
    const uint16_t size = (uint16_t)available;
    const int32_t status = unpack_core(wire, size, message);
    if (status == -1)
        return status;
    const uint8_t *const input = wire;
    uint8_t *const output = message;
    if (status == -2) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 141u, magic);
        if (simple_enabled())
            audio_log_simple(0x04000000u, simple_magic, simple_magic);
    } else if (status == -3) {
        const uint16_t expected = (uint16_t)(read16(output + 8) + 14u);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 148u,
                               length_failed, expected, size);
        if (simple_enabled())
            audio_log_simple(0x04800000u, simple_length_failed,
                             simple_length_failed, expected, size);
    } else if (status == -4) {
        const uint32_t expected = read32(output + 10);
        const uint32_t calculated = codec_crc32(input, 10u, 0);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 157u,
                               header_crc_failed, expected, calculated);
        if (simple_enabled())
            audio_log_simple(0x04800000u, simple_header_crc_failed,
                             simple_header_crc_failed, expected, calculated);
    } else if (status == -5) {
        const uint16_t body = (uint16_t)(read16(output + 8) -
                                               ((output[7] & 1u) ? 4u : 0u));
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 170u,
                               content_large, body);
        if (simple_enabled())
            audio_log_simple(0x04400000u, simple_content_large,
                             simple_content_large, body);
    } else if (status == -6) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 177u,
                               alloc_failed);
        if (simple_enabled())
            audio_log_simple(0x04000000u, simple_alloc_failed,
                             simple_alloc_failed);
    } else if (status == -7) {
        const uint16_t body = read16(output + 18);
        const uint32_t expected = read32(output + 20);
        const uint32_t calculated = codec_crc32(input + 14, body, 0);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, file, function, 188u,
                               body_crc_failed, expected, calculated);
        if (simple_enabled())
            audio_log_simple(0x04800000u, simple_body_crc_failed,
                             simple_body_crc_failed, expected, calculated);
        codec_release((void *)(uintptr_t)read32(output + 14));
        write32(output + 14, 0u);
    } else if (status == 0) {
        const uint16_t command = read16(output + 4);
        const uint16_t length = read16(output + 8);
        const uint32_t crc = read32(output + 10);
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, file, function, 202u,
                               unpacked, command, output[5], output[4],
                               output[6], output[7], length, crc);
        if (simple_enabled())
            audio_log_simple(0x11c00000u, simple_unpacked,
                             simple_unpacked, command, output[5], output[4],
                             output[6], output[7], length, crc);
        const uint16_t content = read16(output + 18);
        if (content != 0u) {
            if (audio_log_flags() & 2u)
                audio_log_extended(4u, module, file, function, 204u,
                                   body_length, content);
            if (simple_enabled())
                audio_log_simple(0x10400000u, simple_body_length,
                                 simple_body_length, content);
            audio_dump_hex(body_dump, 16u,
                           (const void *)(uintptr_t)read32(output + 14),
                           content);
        }
    }
    return status;
}
