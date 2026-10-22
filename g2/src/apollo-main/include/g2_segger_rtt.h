/* SEGGER RTT (Real Time Transfer) as linked into the G2 Apollo main image
 * (2.2.6.10, native 0x5d9950..0x5d9b57). Three up and three down buffers;
 * only channel 0 ("Terminal") is configured by the init routine. */
#ifndef G2_SEGGER_RTT_H
#define G2_SEGGER_RTT_H

#include <stdint.h>

#define G2_RTT_MAX_UP_BUFFERS   3u
#define G2_RTT_MAX_DOWN_BUFFERS 3u

/* Flags (operating mode) of an up buffer. */
enum {
    G2_RTT_MODE_NO_BLOCK_SKIP = 0u,
    G2_RTT_MODE_NO_BLOCK_TRIM = 1u,
    G2_RTT_MODE_BLOCK_IF_FIFO_FULL = 2u,
};

typedef struct {
    const char *name;           /* +0x00 sName */
    char *buffer;               /* +0x04 pBuffer */
    uint32_t size;              /* +0x08 SizeOfBuffer */
    uint32_t wr_off;            /* +0x0c WrOff, written by the target */
    volatile uint32_t rd_off;   /* +0x10 RdOff, written by the host */
    uint32_t flags;             /* +0x14 */
} g2_rtt_buffer_up_t;
_Static_assert(sizeof(g2_rtt_buffer_up_t) == 0x18, "RTT up buffer is 24 bytes");

typedef struct {
    const char *name;           /* +0x00 */
    char *buffer;               /* +0x04 */
    uint32_t size;              /* +0x08 */
    volatile uint32_t wr_off;   /* +0x0c written by the host */
    uint32_t rd_off;            /* +0x10 */
    uint32_t flags;             /* +0x14 */
} g2_rtt_buffer_down_t;
_Static_assert(sizeof(g2_rtt_buffer_down_t) == 0x18, "RTT down buffer is 24 bytes");

typedef struct {
    char id[16];                                        /* +0x00 "SEGGER RTT" */
    int32_t max_up_buffers;                             /* +0x10 */
    int32_t max_down_buffers;                           /* +0x14 */
    g2_rtt_buffer_up_t up[G2_RTT_MAX_UP_BUFFERS];       /* +0x18 */
    g2_rtt_buffer_down_t down[G2_RTT_MAX_DOWN_BUFFERS]; /* +0x60 */
} g2_rtt_control_block_t;
_Static_assert(sizeof(g2_rtt_control_block_t) == 0xa8, "RTT control block is 168 bytes");

extern g2_rtt_control_block_t g2_segger_rtt; /* RAM 0x20071520 (_SEGGER_RTT) */

void segger_rtt_do_init_5d9950(void);
uint32_t segger_rtt_write_no_lock_5d9abc(uint32_t channel, const void *data, uint32_t length);
uint32_t segger_rtt_write_5d9b28(uint32_t channel, const void *data, uint32_t length);

#endif
