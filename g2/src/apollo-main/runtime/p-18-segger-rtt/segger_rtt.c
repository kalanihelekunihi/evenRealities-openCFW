/* SEGGER RTT (Real Time Transfer) up-channel writer, stock SEGGER_RTT.c
 * (V7-style: DMB around the control-block ID and before every WrOff update).
 * Native 0x5d9950..0x5d9b57; literal pool 0x5d9b58..0x5d9b6b.
 *
 * Its only caller is the IAR DLIB __write retarget at 0x5f9fe8, which passes
 * channel 0. The control block lives at RAM 0x20071520 with a 1 KiB up
 * buffer and a 16-byte down buffer, both named "Terminal". Initialisation is
 * keyed on id[0] != 'S' (stock INIT() variant), not on id[0] == '\0'.
 * Lock = BASEPRI raised to 0x20 (SEGGER_RTT_MAX_INTERRUPT_PRIORITY). */
#include <stdint.h>
#include <stddef.h>
#include "g2_segger_rtt.h"

#define RTT_UP_BUFFER_SIZE   0x400u
#define RTT_DOWN_BUFFER_SIZE 0x10u
#define RTT_MAX_INTERRUPT_PRIORITY 0x20u

extern char g2_segger_rtt_up_buffer[RTT_UP_BUFFER_SIZE];     /* RAM 0x2006c530 */
extern char g2_segger_rtt_down_buffer[RTT_DOWN_BUFFER_SIZE]; /* RAM 0x20073ec4 */

static const char rtt_terminal_name[] = "Terminal"; /* ROM 0x78bdd4 */
/* "SEGGER RTT" reversed so the ID never appears verbatim in flash. */
static const char rtt_init_str[] = "\0\0\0\0\0\0TTR REGGES"; /* ROM 0x782dbc */

extern void audio_uart_buffer_zero(void *destination, uint32_t length, uint32_t fill); /* 0x43c0e4 memset */
extern void audio_uart_checksum_copy(void *destination, const void *source, uint32_t length); /* 0x439be4 memcpy */

static inline void rtt_dmb(void)
{
    __asm__ volatile("dmb sy" ::: "memory");
}

/* _DoInit */
void segger_rtt_do_init_5d9950(void)
{
    g2_rtt_control_block_t *p = &g2_segger_rtt;
    uint32_t i;

    audio_uart_buffer_zero(p, sizeof(*p), 0u);
    p->max_up_buffers = (int32_t)G2_RTT_MAX_UP_BUFFERS;
    p->max_down_buffers = (int32_t)G2_RTT_MAX_DOWN_BUFFERS;

    p->up[0].name = rtt_terminal_name;
    p->up[0].buffer = g2_segger_rtt_up_buffer;
    p->up[0].size = RTT_UP_BUFFER_SIZE;
    p->up[0].rd_off = 0u;
    p->up[0].wr_off = 0u;
    p->up[0].flags = G2_RTT_MODE_NO_BLOCK_SKIP;

    p->down[0].name = rtt_terminal_name;
    p->down[0].buffer = g2_segger_rtt_down_buffer;
    p->down[0].size = RTT_DOWN_BUFFER_SIZE;
    p->down[0].rd_off = 0u;
    p->down[0].wr_off = 0u;
    p->down[0].flags = G2_RTT_MODE_NO_BLOCK_SKIP;

    rtt_dmb();
    for (i = 0u; i < sizeof(rtt_init_str) - 1u; i++) {
        p->id[i] = rtt_init_str[sizeof(rtt_init_str) - 2u - i];
    }
    rtt_dmb();
}

/* _WriteBlocking: copy in chunks, waiting for the host to drain the ring. */
uint32_t segger_rtt_write_blocking_5d99c0(g2_rtt_buffer_up_t *ring, const char *data,
                                          uint32_t length)
{
    uint32_t written = 0u;
    uint32_t wr_off = ring->wr_off;

    do {
        uint32_t rd_off = ring->rd_off;
        uint32_t chunk;

        if (wr_off < rd_off) {
            chunk = rd_off - wr_off - 1u;
        } else {
            chunk = rd_off + (ring->size - wr_off) - 1u;
        }
        if (chunk >= ring->size - wr_off) {
            chunk = ring->size - wr_off;
        }
        if (chunk >= length) {
            chunk = length;
        }
        audio_uart_checksum_copy(ring->buffer + wr_off, data, chunk);
        written += chunk;
        data += chunk;
        length -= chunk;
        wr_off += chunk;
        if (wr_off == ring->size) {
            wr_off = 0u;
        }
        rtt_dmb();
        ring->wr_off = wr_off;
    } while (length != 0u);
    return written;
}

/* _WriteNoCheck: caller guarantees the space; wraps at most once. */
void segger_rtt_write_no_check_5d9a44(g2_rtt_buffer_up_t *ring, const char *data,
                                      uint32_t length)
{
    uint32_t wr_off = ring->wr_off;
    uint32_t rem = ring->size - wr_off;

    if (length < rem) {
        audio_uart_checksum_copy(ring->buffer + wr_off, data, length);
        rtt_dmb();
        ring->wr_off = length + wr_off;
    } else {
        audio_uart_checksum_copy(ring->buffer + wr_off, data, rem);
        length -= rem;
        audio_uart_checksum_copy(ring->buffer, data + rem, length);
        rtt_dmb();
        ring->wr_off = length;
    }
}

/* _GetAvailWriteSpace */
uint32_t segger_rtt_get_avail_write_space_5d9aa2(const g2_rtt_buffer_up_t *ring)
{
    uint32_t rd_off = ring->rd_off;
    uint32_t wr_off = ring->wr_off;

    if (wr_off >= rd_off) {
        return rd_off + (ring->size - 1u - wr_off);
    }
    return rd_off - wr_off - 1u;
}

/* SEGGER_RTT_WriteNoLock */
uint32_t segger_rtt_write_no_lock_5d9abc(uint32_t channel, const void *data, uint32_t length)
{
    g2_rtt_buffer_up_t *ring = &g2_segger_rtt.up[channel];
    uint32_t status;

    switch (ring->flags) {
    case G2_RTT_MODE_NO_BLOCK_SKIP:
        if (segger_rtt_get_avail_write_space_5d9aa2(ring) < length) {
            status = 0u;
        } else {
            status = length;
            segger_rtt_write_no_check_5d9a44(ring, data, length);
        }
        break;
    case G2_RTT_MODE_NO_BLOCK_TRIM:
        status = segger_rtt_get_avail_write_space_5d9aa2(ring);
        if (status >= length) {
            status = length;
        }
        segger_rtt_write_no_check_5d9a44(ring, data, status);
        break;
    case G2_RTT_MODE_BLOCK_IF_FIFO_FULL:
        status = segger_rtt_write_blocking_5d99c0(ring, data, length);
        break;
    default:
        status = 0u;
        break;
    }
    return status;
}

/* SEGGER_RTT_Write */
uint32_t segger_rtt_write_5d9b28(uint32_t channel, const void *data, uint32_t length)
{
    uint32_t saved;
    uint32_t status;

    if (g2_segger_rtt.id[0] != 'S') {
        segger_rtt_do_init_5d9950();
    }
    __asm__ volatile("mrs %0, BASEPRI" : "=r"(saved) : : "memory");
    __asm__ volatile("msr BASEPRI, %0" : : "r"(RTT_MAX_INTERRUPT_PRIORITY) : "memory");
    status = segger_rtt_write_no_lock_5d9abc(channel, data, length);
    __asm__ volatile("msr BASEPRI, %0" : : "r"(saved) : "memory");
    return status;
}
