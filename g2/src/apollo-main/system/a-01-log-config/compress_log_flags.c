/* Compact-log output switches, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\compress_log\core\compress_log.c.
 * Native 0x43d0c8..0x43d0cd and 0x43d0d4..0x43d0d9 (shared literal pool
 * 0x43d13c..0x43d143 with compress_log_core.c).
 *
 * Byte RAM 0x20004543 is the log output mask read by audio_log_flags 0x43d0ce:
 * bit 1 = extended elog line, bit 0 / bit 2 = compact record. Factory mode
 * (0x4c953e) sets it to 3. Byte RAM 0x20004544 is the compact-log level
 * threshold read by audio_log_level 0x43d0da; the UART log-level command
 * (0x4592dc) writes it together with elog_set_filter_lvl. */
#include <stdint.h>

extern volatile uint8_t g2_log_output_flags; /* RAM 0x20004543 */
extern volatile uint8_t audio_log_policy_byte; /* RAM 0x20004544 */

void compress_log_set_output_flags_43d0c8(uint8_t flags)
{
    g2_log_output_flags = flags;
}

void compress_log_set_level_43d0d4(uint8_t level)
{
    audio_log_policy_byte = level;
}
