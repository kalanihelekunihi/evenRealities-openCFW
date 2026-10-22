/* MD5 for the CLI "md5" command, reconstructed from the 2.2.6.10 disassembly.
 * The body is Alexander Peslyak's public-domain MD5 (openwall md5.c, the
 * portable variant that stages each word in ctx->block with SET/GET); the
 * stock layout and code match it, so this follows that implementation.
 *
 * Stock ranges:
 *   0x005948d0..0x0059544d  body            (static; literal pool 0x595468..0x595567
 *                                            holds the 64 T constants)
 *   0x0059544e..0x00595467  MD5_Init        (init words in pool 0x595568..0x595577)
 *   0x00595578..0x00595607  MD5_Update
 *   0x00595608..0x00595705  MD5_Final       (result, ctx); 0x595706 is padding
 * Context: lo +0, hi +4, a..d +8..+20, buffer[64] +24, block[16] +88; 152 bytes,
 * cleared by MD5_Final. Final stores the raw hi word (no << 3), as in the
 * older openwall revision.
 * memcpy 0x439be4 = audio_queue_copy_bytes, memset 0x43c0e4 =
 * audio_uart_buffer_zero(dst, len, fill). Profile g2-apollo-main-2. */
#include <stdint.h>
#include <stddef.h>

extern void *audio_queue_copy_bytes(void *destination, const void *source, uint32_t size); /* 0x439be4 memcpy */
extern void audio_uart_buffer_zero(void *destination, uint32_t length, uint32_t fill);   /* 0x43c0e4 memset */

typedef struct {
    uint32_t lo, hi;        /* +0, +4 */
    uint32_t a, b, c, d;    /* +8..+20 */
    uint8_t buffer[64];     /* +24 */
    uint32_t block[16];     /* +88 */
} g2_md5_ctx;
_Static_assert(sizeof(g2_md5_ctx) == 0x98u, "stock MD5 context is 152 bytes");

void md5_init_59544e(void *ctx);
void md5_update_595578(void *ctx, const void *data, uint32_t len);
void md5_final_595608(uint8_t digest[16], void *ctx);

#define F(x, y, z) ((z) ^ ((x) & ((y) ^ (z))))
#define G(x, y, z) ((y) ^ ((z) & ((x) ^ (y))))
#define H(x, y, z) (((x) ^ (y)) ^ (z))
#define H2(x, y, z) ((x) ^ ((y) ^ (z)))
#define I(x, y, z) ((y) ^ ((x) | ~(z)))

#define STEP(f, a, b, c, d, x, t, s)                       \
    (a) += f((b), (c), (d)) + (x) + (t);                   \
    (a) = (((a) << (s)) | ((a) >> (32 - (s))));            \
    (a) += (b);

#define SET(n)                                             \
    (ctx->block[(n)] = (uint32_t)ptr[(n) * 4] |            \
                       ((uint32_t)ptr[(n) * 4 + 1] << 8) | \
                       ((uint32_t)ptr[(n) * 4 + 2] << 16) | \
                       ((uint32_t)ptr[(n) * 4 + 3] << 24))
#define GET(n) (ctx->block[(n)])

#define OUT(dst, src)                      \
    (dst)[0] = (uint8_t)(src);             \
    (dst)[1] = (uint8_t)((src) >> 8);      \
    (dst)[2] = (uint8_t)((src) >> 16);     \
    (dst)[3] = (uint8_t)((src) >> 24);

/* Stock 0x005948d0 (MD5 body) */
static const void *md5_body_5948d0(g2_md5_ctx *ctx, const void *data, uint32_t size)
{
    const uint8_t *ptr = (const uint8_t *)data;
    uint32_t a = ctx->a, b = ctx->b, c = ctx->c, d = ctx->d;

    do {
        uint32_t saved_a = a, saved_b = b, saved_c = c, saved_d = d;

        /* Round 1 */
        STEP(F, a, b, c, d, SET(0), 0xd76aa478u, 7)
        STEP(F, d, a, b, c, SET(1), 0xe8c7b756u, 12)
        STEP(F, c, d, a, b, SET(2), 0x242070dbu, 17)
        STEP(F, b, c, d, a, SET(3), 0xc1bdceeeu, 22)
        STEP(F, a, b, c, d, SET(4), 0xf57c0fafu, 7)
        STEP(F, d, a, b, c, SET(5), 0x4787c62au, 12)
        STEP(F, c, d, a, b, SET(6), 0xa8304613u, 17)
        STEP(F, b, c, d, a, SET(7), 0xfd469501u, 22)
        STEP(F, a, b, c, d, SET(8), 0x698098d8u, 7)
        STEP(F, d, a, b, c, SET(9), 0x8b44f7afu, 12)
        STEP(F, c, d, a, b, SET(10), 0xffff5bb1u, 17)
        STEP(F, b, c, d, a, SET(11), 0x895cd7beu, 22)
        STEP(F, a, b, c, d, SET(12), 0x6b901122u, 7)
        STEP(F, d, a, b, c, SET(13), 0xfd987193u, 12)
        STEP(F, c, d, a, b, SET(14), 0xa679438eu, 17)
        STEP(F, b, c, d, a, SET(15), 0x49b40821u, 22)

        /* Round 2 */
        STEP(G, a, b, c, d, GET(1), 0xf61e2562u, 5)
        STEP(G, d, a, b, c, GET(6), 0xc040b340u, 9)
        STEP(G, c, d, a, b, GET(11), 0x265e5a51u, 14)
        STEP(G, b, c, d, a, GET(0), 0xe9b6c7aau, 20)
        STEP(G, a, b, c, d, GET(5), 0xd62f105du, 5)
        STEP(G, d, a, b, c, GET(10), 0x02441453u, 9)
        STEP(G, c, d, a, b, GET(15), 0xd8a1e681u, 14)
        STEP(G, b, c, d, a, GET(4), 0xe7d3fbc8u, 20)
        STEP(G, a, b, c, d, GET(9), 0x21e1cde6u, 5)
        STEP(G, d, a, b, c, GET(14), 0xc33707d6u, 9)
        STEP(G, c, d, a, b, GET(3), 0xf4d50d87u, 14)
        STEP(G, b, c, d, a, GET(8), 0x455a14edu, 20)
        STEP(G, a, b, c, d, GET(13), 0xa9e3e905u, 5)
        STEP(G, d, a, b, c, GET(2), 0xfcefa3f8u, 9)
        STEP(G, c, d, a, b, GET(7), 0x676f02d9u, 14)
        STEP(G, b, c, d, a, GET(12), 0x8d2a4c8au, 20)

        /* Round 3 */
        STEP(H, a, b, c, d, GET(5), 0xfffa3942u, 4)
        STEP(H2, d, a, b, c, GET(8), 0x8771f681u, 11)
        STEP(H, c, d, a, b, GET(11), 0x6d9d6122u, 16)
        STEP(H2, b, c, d, a, GET(14), 0xfde5380cu, 23)
        STEP(H, a, b, c, d, GET(1), 0xa4beea44u, 4)
        STEP(H2, d, a, b, c, GET(4), 0x4bdecfa9u, 11)
        STEP(H, c, d, a, b, GET(7), 0xf6bb4b60u, 16)
        STEP(H2, b, c, d, a, GET(10), 0xbebfbc70u, 23)
        STEP(H, a, b, c, d, GET(13), 0x289b7ec6u, 4)
        STEP(H2, d, a, b, c, GET(0), 0xeaa127fau, 11)
        STEP(H, c, d, a, b, GET(3), 0xd4ef3085u, 16)
        STEP(H2, b, c, d, a, GET(6), 0x04881d05u, 23)
        STEP(H, a, b, c, d, GET(9), 0xd9d4d039u, 4)
        STEP(H2, d, a, b, c, GET(12), 0xe6db99e5u, 11)
        STEP(H, c, d, a, b, GET(15), 0x1fa27cf8u, 16)
        STEP(H2, b, c, d, a, GET(2), 0xc4ac5665u, 23)

        /* Round 4 */
        STEP(I, a, b, c, d, GET(0), 0xf4292244u, 6)
        STEP(I, d, a, b, c, GET(7), 0x432aff97u, 10)
        STEP(I, c, d, a, b, GET(14), 0xab9423a7u, 15)
        STEP(I, b, c, d, a, GET(5), 0xfc93a039u, 21)
        STEP(I, a, b, c, d, GET(12), 0x655b59c3u, 6)
        STEP(I, d, a, b, c, GET(3), 0x8f0ccc92u, 10)
        STEP(I, c, d, a, b, GET(10), 0xffeff47du, 15)
        STEP(I, b, c, d, a, GET(1), 0x85845dd1u, 21)
        STEP(I, a, b, c, d, GET(8), 0x6fa87e4fu, 6)
        STEP(I, d, a, b, c, GET(15), 0xfe2ce6e0u, 10)
        STEP(I, c, d, a, b, GET(6), 0xa3014314u, 15)
        STEP(I, b, c, d, a, GET(13), 0x4e0811a1u, 21)
        STEP(I, a, b, c, d, GET(4), 0xf7537e82u, 6)
        STEP(I, d, a, b, c, GET(11), 0xbd3af235u, 10)
        STEP(I, c, d, a, b, GET(2), 0x2ad7d2bbu, 15)
        STEP(I, b, c, d, a, GET(9), 0xeb86d391u, 21)

        a += saved_a;
        b += saved_b;
        c += saved_c;
        d += saved_d;

        ptr += 64;
    } while (size -= 64u);

    ctx->a = a;
    ctx->b = b;
    ctx->c = c;
    ctx->d = d;
    return ptr;
}

/* Stock 0x0059544e (MD5_Init) */
void md5_init_59544e(void *context)
{
    g2_md5_ctx *ctx = (g2_md5_ctx *)context;

    ctx->a = 0x67452301u;
    ctx->b = 0xefcdab89u;
    ctx->c = 0x98badcfeu;
    ctx->d = 0x10325476u;
    ctx->lo = 0u;
    ctx->hi = 0u;
}

/* Stock 0x00595578 (MD5_Update) */
void md5_update_595578(void *context, const void *data, uint32_t size)
{
    g2_md5_ctx *ctx = (g2_md5_ctx *)context;
    const uint8_t *p = (const uint8_t *)data;
    uint32_t saved_lo = ctx->lo;
    uint32_t used, available;

    if ((ctx->lo = (saved_lo + size) & 0x1fffffffu) < saved_lo)
        ctx->hi++;
    ctx->hi += size >> 29;

    used = saved_lo & 0x3fu;
    if (used != 0u) {
        available = 64u - used;
        if (size < available) {
            (void)audio_queue_copy_bytes(&ctx->buffer[used], p, size);
            return;
        }
        (void)audio_queue_copy_bytes(&ctx->buffer[used], p, available);
        p += available;
        size -= available;
        (void)md5_body_5948d0(ctx, ctx->buffer, 64u);
    }
    if (size >= 64u) {
        p = (const uint8_t *)md5_body_5948d0(ctx, p, size & ~(uint32_t)0x3fu);
        size &= 0x3fu;
    }
    (void)audio_queue_copy_bytes(ctx->buffer, p, size);
}

/* Stock 0x00595608 (MD5_Final) */
void md5_final_595608(uint8_t result[16], void *context)
{
    g2_md5_ctx *ctx = (g2_md5_ctx *)context;
    uint32_t used, available;

    used = ctx->lo & 0x3fu;
    ctx->buffer[used++] = 0x80u;
    available = 64u - used;
    if (available < 8u) {
        audio_uart_buffer_zero(&ctx->buffer[used], available, 0u);
        (void)md5_body_5948d0(ctx, ctx->buffer, 64u);
        used = 0u;
        available = 64u;
    }
    audio_uart_buffer_zero(&ctx->buffer[used], available - 8u, 0u);

    ctx->lo <<= 3;
    OUT(&ctx->buffer[56], ctx->lo)
    OUT(&ctx->buffer[60], ctx->hi)
    (void)md5_body_5948d0(ctx, ctx->buffer, 64u);

    OUT(&result[0], ctx->a)
    OUT(&result[4], ctx->b)
    OUT(&result[8], ctx->c)
    OUT(&result[12], ctx->d)

    audio_uart_buffer_zero(ctx, sizeof(*ctx), 0u);
}
