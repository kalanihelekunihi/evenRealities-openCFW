/* EvenHub image payload decompressors, firmware 2.2.6.10.
 * Stock ranges (no literal pool):
 *   0x4e0c0c..0x4e0c33  evenhub_lz4_decompress_4e0c0c
 *   0x4e0c34..0x4e0c3b  evenhub_rle_decompress_4e0c34 (forwards to 0x4e0c3c)
 *   0x4e0c3c..0x4e0c9f  RLE decoder body (single caller 0x4e0c36)
 *
 * Used by the EvenHub image container (ui/a-14-evenhub-ui/evenhub_ui_page.c)
 * and the navigation mini/max map (ui/a-49-navigation-ui/navigation_ui_pages.c).
 * Both return the number of bytes written to dst, 0 on failure. The LZ4 path
 * calls upstream LZ4_decompress_safe (third-party/upstream/lz4, stock 0x54f338).
 * The RLE stream is a sequence of {count, byte} pairs; output is truncated at
 * dst_cap and a trailing odd byte is ignored. */
#include <stdint.h>

extern int LZ4_decompress_safe(const char *src, char *dst, int compressedSize,
                               int dstCapacity); /* 0x54f338 */

/* Stock 0x004E0C0C (evenhub_lz4_decompress_4e0c0c) */
uint32_t evenhub_lz4_decompress_4e0c0c(const void *src, uint32_t src_len, void *dst,
                                       uint32_t dst_cap)
{
    int written;

    if (src == 0 || dst == 0 || src_len == 0u || dst_cap == 0u)
        return 0u;
    written = LZ4_decompress_safe((const char *)src, (char *)dst, (int)src_len, (int)dst_cap);
    if (written < 1)
        written = 0;
    return (uint32_t)written;
}

/* Stock 0x004E0C3C (EvenHub RLE decoder body) */
uint32_t evenhub_rle_decode_4e0c3c(const void *src, uint32_t src_len, void *dst,
                                   uint32_t dst_cap)
{
    const uint8_t *in = (const uint8_t *)src;
    uint8_t *out = (uint8_t *)dst;
    uint32_t pos = 0u;
    uint32_t written = 0u;
    uint32_t i;

    if (src == 0 || dst == 0 || src_len == 0u || dst_cap == 0u)
        return 0u;
    while (pos < src_len && pos + 1u < src_len) {
        uint8_t count = in[pos++];
        uint8_t value = in[pos++];
        if (dst_cap < written + count) {
            uint32_t room = dst_cap - written;
            for (i = 0u; i < room; i++)
                out[written++] = value;
            break;
        }
        for (i = 0u; i < count; i++)
            out[written++] = value;
    }
    return written;
}

/* Stock 0x004E0C34 (evenhub_rle_decompress_4e0c34) */
uint32_t evenhub_rle_decompress_4e0c34(const void *src, uint32_t src_len, void *dst,
                                       uint32_t dst_cap)
{
    return evenhub_rle_decode_4e0c3c(src, src_len, dst, dst_cap);
}
