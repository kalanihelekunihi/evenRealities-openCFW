/* Retained crash record (p-05-crash-record) and the CmBacktrace product
 * port buffers (p-10-cmbacktrace/cmb_fault_port.c). CmBacktrace's own
 * statics are owned by the upstream cm_backtrace.c unit.
 *
 * The record at RAM 0x20075048 lies just past the stock startup zero-init
 * range [0x20004558, 0x20075048) and survives a warm reset, so it is placed
 * in a NOLOAD section (crash_record_noinit.ld beside this file). */
#include <stdint.h>

/* RAM 0x20075048, 0x11ac bytes, not initialised at startup. */
__attribute__((section(".noinit.crash_record"), aligned(4)))
uint8_t g2_crash_record[0x11ac];

uint32_t g2_crash_staging_length;                                /* RAM 0x200743a4 */
char g2_crash_staging_text[0x1194] __attribute__((aligned(4)));  /* RAM 0x2005ce68 */
char g2_crash_path_buffer[0x80] __attribute__((aligned(4)));     /* RAM 0x200e3b00 */
char g2_crash_header_buffer[0x200] __attribute__((aligned(4)));  /* RAM 0x200e3b80 */
char g2_crash_footer_buffer[0x100] __attribute__((aligned(4)));  /* RAM 0x200e3d80 */

/* CmBacktrace product port: 40 TaskStatus_t rows (0x24 B) and line buffer. */
uint8_t g2_cmb_task_status[40u * 0x24u] __attribute__((aligned(4))); /* RAM 0x20069028 */
char g2_cmb_line[0x80];                                              /* RAM 0x20071a48 */
