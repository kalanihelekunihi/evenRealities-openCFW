/* gx8002_uart_read_blocking, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_host.c.
 * Native 0x57c1fc..0x57c441, literal pool 0x57c618.., 0x57cb54..0x57cb5f,
 * 0x57ccd8..0x57cceb, 0x57ce54.
 *
 * Full version including the four log sites. It supersedes the
 * logger-disabled codec_response_read in codec-response/response.c; only one
 * of the two may be linked for this address.
 *
 * Reads the 14-byte header, then the rest of the frame (header +8 body
 * length + 14) from the UART3 RX ring. Header and body share one deadline:
 * the u64 tick difference from the start is compared with the zero-extended
 * timeout before every read; an empty read sleeps one tick. The header is
 * written to the buffer before the capacity is checked. Returns the frame
 * length, or -1. */
#include <stdint.h>
#include <stddef.h>
#include "gx8002_host.h"

extern uint64_t codec_tick_snapshot(void);                /* 0x58fac8, zero-extended tick */
extern uint32_t codec_uart_read(uint8_t *dst, uint32_t capacity); /* 0x58fb2a, drains RX ring */
extern int32_t osDelay(uint32_t ticks);                   /* 0x449376 */

static const char module[] = "codec.host"; /* ROM 0x78bed0 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c"; /* ROM 0x6fccd4 */
static const char function[] = "gx8002_uart_read_blocking"; /* ROM 0x771054 */
static const char header_short[] = "Failed to read message header: %d/%d bytes"; /* ROM 0x742f40 */
static const char header_short_s[] = "[codec.host]Failed to read message header: %d/%d bytes"; /* ROM 0x7229e0 */
static const char too_large[] = "Message too large: %d > %d"; /* ROM 0x771070 */
static const char too_large_s[] = "[codec.host]Message too large: %d > %d"; /* ROM 0x74db24 */
static const char body_short[] = "Failed to read complete message: %d/%d bytes"; /* ROM 0x738084 */
static const char body_short_s[] = "[codec.host]Failed to read complete message: %d/%d bytes"; /* ROM 0x71852c */
static const char read_ok[] = "Successfully read message: %d bytes"; /* ROM 0x7596c0 */
static const char read_ok_s[] = "[codec.host]Successfully read message: %d bytes"; /* ROM 0x7380b4 */

#define GX8002_HEADER_BYTES 14u

int32_t gx8002_uart_read_blocking(uint8_t *buffer, uint16_t capacity, uint32_t timeout)
{
    uint64_t start;
    uint32_t got;
    uint16_t count;
    uint16_t total;

    if (buffer == NULL || capacity == 0u)
        return -1;
    start = codec_tick_snapshot();
    count = 0u;
    while (count < GX8002_HEADER_BYTES) {
        if (codec_tick_snapshot() - start >= (uint64_t)timeout)
            break;
        got = codec_uart_read(buffer + count, GX8002_HEADER_BYTES - count);
        if ((int32_t)got < 1)
            (void)osDelay(1u);
        else
            count = (uint16_t)(count + got);
    }
    if (count < GX8002_HEADER_BYTES) {
        GX8002_LOG(4u, 0x10800000u, function, 257u, header_short, header_short_s, count,
                   GX8002_HEADER_BYTES);
        return -1;
    }
    total = (uint16_t)(*(const uint16_t *)(const void *)(buffer + 8) + GX8002_HEADER_BYTES);
    if (capacity < total) {
        GX8002_LOG(1u, 0x04800000u, function, 267u, too_large, too_large_s, total, capacity);
        return -1;
    }
    while (count < total) {
        if (codec_tick_snapshot() - start >= (uint64_t)timeout)
            break;
        got = codec_uart_read(buffer + count, (uint32_t)total - count);
        if ((int32_t)got < 1)
            (void)osDelay(1u);
        else
            count = (uint16_t)(count + got);
    }
    if (count < total) {
        GX8002_LOG(1u, 0x04800000u, function, 282u, body_short, body_short_s, count, total);
        return -1;
    }
    GX8002_LOG(4u, 0x10400000u, function, 286u, read_ok, read_ok_s, count);
    return count;
}
