/* Production-test font image CRC check, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\product_common.c.
 * Native 0x58f1ec..0x58f499; literal pool 0x58f49c..0x58f4e3.
 *
 * Font images live in the external NOR flash, read through the MSPI XIP
 * window 0x80000000..0x81ffffff under the NOR flash lock. Each image starts
 * with a header whose little-endian payload length sits at +0x3c and whose
 * CRC16 (chained helper 0x49acd4) sits at +0x40; the CRC covers the payload
 * from base+0x45, read in 1 KiB chunks.
 * pt_production_mode_orchestrate (0x56f92c) ORs the two results into its
 * failure flag. */
#include <stdint.h>
#include <stddef.h>

#define FONT_XIP_BASE      0x80000000u
#define FONT_XIP_SPAN      0x02000000u
#define FONT_XIP_LIMIT     0x82000001u  /* ROM 0x58f4c0 */
#define FONT_HEADER_READ   0x46u
#define FONT_PAYLOAD_START 0x45u
#define FONT_CHUNK         0x400u
#define FONT_A_BASE        0x80100000u  /* ROM 0x58f4dc */
#define FONT_B_BASE        0x80700000u  /* ROM 0x58f4e0 */

extern void g2_norflash_lock_46f65e(void);
extern void g2_norflash_unlock_46f674(void);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t len, const uint16_t *seed);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "product_common"; /* ROM 0x787f80 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\product_common.c"; /* ROM 0x6f5360 */
static const char fn_name[] = "checkFontCrc16"; /* ROM 0x787f70 */
static const char bad_base[] = "font crc: invalid base addr 0x%08x"; /* ROM 0x7580f4 */
static const char bad_base_short[] = "[product_common]font crc: invalid base addr 0x%08x"; /* ROM 0x72be60 */
static const char bad_len[] = "font crc: invalid len=0"; /* ROM 0x77a6e4 */
static const char bad_len_short[] = "[product_common]font crc: invalid len=0"; /* ROM 0x74c8b4 */
static const char header_fmt[] = "font crc: len=%u, crc16=0x%04x"; /* ROM 0x7639b0 */
static const char header_fmt_short[] = "[product_common]font crc: len=%u, crc16=0x%04x"; /* ROM 0x736b54 */
static const char overflow_fmt[] = "font crc: len overflow, base=0x%08x len=%u"; /* ROM 0x741864 */
static const char overflow_fmt_short[] = "[product_common]font crc: len overflow, base=0x%08x len=%u"; /* ROM 0x7179ec */
static const char match_fmt[] = "font crc: match, calc=0x%04x expect=0x%04x"; /* ROM 0x741890 */
static const char match_fmt_short[] = "[product_common]font crc: match, calc=0x%04x expect=0x%04x"; /* ROM 0x717a28 */
static const char mismatch_fmt[] = "font crc: mismatch, calc=0x%04x expect=0x%04x"; /* ROM 0x736b84 */
static const char mismatch_fmt_short[] = "[product_common]font crc: mismatch, calc=0x%04x expect=0x%04x"; /* ROM 0x70dd24 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* XIP copy of external flash bytes under the NOR flash lock. */
void product_flash_read_58f1ec(uint32_t src, void *dst, uint32_t len)
{
    g2_norflash_lock_46f65e();
    (void)audio_queue_copy_bytes(dst, (const void *)(uintptr_t)src, len);
    g2_norflash_unlock_46f674();
}

/* checkFontCrc16: 0 when the stored CRC matches, 1 otherwise. */
uint32_t checkFontCrc16_58f208(uint32_t base)
{
    uint8_t header[FONT_HEADER_READ];
    uint8_t chunk[FONT_CHUNK];

    if (base - FONT_XIP_BASE >= FONT_XIP_SPAN) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_name, 0x1au, bad_base, base);
        if (log_compressed_on())
            (void)compress_log_output(0x04400000u, bad_base_short, bad_base_short, base);
        return 1u;
    }

    product_flash_read_58f1ec(base, header, sizeof(header));
    uint32_t len = (uint32_t)header[0x3c] | ((uint32_t)header[0x3d] << 8) |
                   ((uint32_t)header[0x3e] << 16) | ((uint32_t)header[0x3f] << 24);
    uint16_t expect = (uint16_t)(header[0x40] | (header[0x41] << 8));

    if (len == 0u) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_name, 0x29u, bad_len);
        if (log_compressed_on())
            (void)compress_log_output(0x04000000u, bad_len_short, bad_len_short);
        return 1u;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_name, 0x2du, header_fmt, len, expect);
    if (log_compressed_on())
        (void)compress_log_output(0x0c800000u, header_fmt_short, header_fmt_short, len, expect);

    if ((uint64_t)base + len + FONT_PAYLOAD_START >= FONT_XIP_LIMIT) {
        if (log_extended_on())
            audio_log_extended(1u, module_tag, source_file, fn_name, 0x31u, overflow_fmt, base, len);
        if (log_compressed_on())
            (void)compress_log_output(0x04800000u, overflow_fmt_short, overflow_fmt_short, base, len);
        return 1u;
    }

    uint32_t offset = FONT_PAYLOAD_START;
    uint16_t crc = 0u;
    uint8_t first = 1u;
    while (len != 0u) {
        uint32_t n = len > FONT_CHUNK ? FONT_CHUNK : len;
        product_flash_read_58f1ec(offset + base, chunk, n);
        crc = audio_uart_hand_checksum_49acd4(chunk, n, first ? NULL : &crc);
        first = 0u;
        len -= n;
        offset += n;
    }

    if (crc == expect) {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_name, 0x45u, match_fmt, crc, expect);
        if (log_compressed_on())
            (void)compress_log_output(0x0c800000u, match_fmt_short, match_fmt_short, crc, expect);
        return 0u;
    }
    if (log_extended_on())
        audio_log_extended(1u, module_tag, source_file, fn_name, 0x49u, mismatch_fmt, crc, expect);
    if (log_compressed_on())
        (void)compress_log_output(0x04800000u, mismatch_fmt_short, mismatch_fmt_short, crc, expect);
    return 1u;
}

uint32_t product_check_font_a_crc_58f486(void)
{
    return checkFontCrc16_58f208(FONT_A_BASE);
}

uint32_t product_check_font_b_crc_58f490(void)
{
    return checkFontCrc16_58f208(FONT_B_BASE);
}
