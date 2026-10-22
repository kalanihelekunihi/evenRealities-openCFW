/* Apollo main logger product state: EasyLogger async transport glue
 * (system/a-03-elog-async), log output flags (a-01), compressed-log core and
 * port (p-03 / a-03) and the tracepoint defer timer (p-05). EasyLogger's own
 * statics (elog 0x20070be8, log_buf 0x2006bd30, elog_assert_hook 0x2007456c)
 * are owned by the upstream elog.c unit and are not defined here.
 *
 * .data values are from the decoded startup init image (RAM
 * 0x20000000..0x20004557): 0x20004543 = 0x01 and 0x20004546 = 0x01. Sizes
 * are the sizeof of the referencing declarations and match the gap to the
 * next stock RAM object. */
#include <stdint.h>

/* RAM 0x20004543 (.data): log output flags, initial 1 (UART text sink). */
volatile uint8_t g2_log_output_flags = 0x01u;

/* RAM 0x20004546 (.data): default async log level, initial 1. */
volatile uint8_t g2_elog_default_level = 0x01u;

/* EasyLogger async transport (elog_async_transport.c). */
volatile uint8_t g2_elog_async_enabled;                                  /* RAM 0x20074fc0 */
uint8_t g2_elog_dummy_node[0x110] __attribute__((aligned(4)));           /* RAM 0x202e4eb8 */
void *volatile g2_elog_pending_head;                                     /* RAM 0x20074138 */
void *volatile g2_elog_pending_tail;                                     /* RAM 0x2007413c */
uint8_t g2_elog_sink[8] __attribute__((aligned(4)));                     /* RAM 0x20073b90 */
uint8_t g2_elog_stats[0x30] __attribute__((aligned(4)));                 /* RAM 0x2007342c */

/* Compressed-log core (compress_log_core.c). */
volatile uint32_t g2_compress_log_last_sync_tick;                        /* RAM 0x2007438c */
uint8_t g2_compress_log_mutex_storage[0x50] __attribute__((aligned(4))); /* RAM 0x20072998, StaticSemaphore_t (80 B) */
uint8_t g2_compress_log_sync_block[0x1000] __attribute__((aligned(4)));  /* RAM 0x200d4bd8 */

/* Compressed-log port (compress_log_port.c). */
uint8_t g2_clog_manager[0xc] __attribute__((aligned(4)));                /* RAM 0x20073f9c */
volatile uint8_t g2_clog_manager_loaded;                                 /* RAM 0x20074fa0 */

/* Tracepoint defer timer control block (tracepoint_defer.c). */
uint8_t g2_tracepoint_defer_timer_buffer[44] __attribute__((aligned(4))); /* RAM 0x20073758, StaticTimer_t */
