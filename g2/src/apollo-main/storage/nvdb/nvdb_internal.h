/* Private helpers shared by the NVDB record units.
 *
 * Every stock log site expands the EasyLogger pattern: elog_output (0x43d574)
 * when flag bit 1 is set, then the short-event log (0x43ce9e) when bit 0 or
 * bit 2 is set. The short-event token is level << 26 | argument_count << 22. */
#ifndef G2_NVDB_INTERNAL_H
#define G2_NVDB_INTERNAL_H

#include <stdint.h>
#include "g2_nvdb.h"

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* CRC16-CCITT table walk, seed 0xffff when seed == NULL. */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *data, uint32_t length,
                                                const uint16_t *seed);
extern void audio_uart_checksum_copy(void *, const void *, uint32_t); /* memcpy 0x439be4 */

#define NVDB_LOG(module, path, level, function, line, token, format, short_format, ...) \
    do {                                                                              \
        if ((audio_log_flags() & 2u) != 0u)                                           \
            audio_log_extended((level), (module), (path), (function), (line),         \
                               (format), ##__VA_ARGS__);                             \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)        \
            (void)compress_log_output((token), (short_format), (short_format),       \
                                      ##__VA_ARGS__);                                \
    } while (0)

#endif
