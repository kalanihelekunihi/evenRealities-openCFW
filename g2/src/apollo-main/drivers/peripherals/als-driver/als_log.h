/* Private logging helper for the ALS driver units.
 *
 * Every stock log site in als.c expands the same pattern: an EasyLogger
 * elog_output call (0x43d574) when flag bit 1 is set, then a short-event log
 * (0x43ce9e) when bit 0 or bit 2 is set. The short-event token is
 * level << 26 | argument_count << 22 (e.g. 0x0cc00000 = level 3, 3 args). */
#ifndef G2_ALS_LOG_H
#define G2_ALS_LOG_H

#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

extern const char g2_als_log_module[]; /* ROM 0x789f8c "sensor_als" */
extern const char g2_als_log_path[];   /* ROM 0x711ce0 */

#define ALS_LOG(level, function, line, token, format, short_format, ...)          \
    do {                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                       \
            audio_log_extended((level), g2_als_log_module, g2_als_log_path,       \
                               (function), (line), (format), ##__VA_ARGS__);     \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)    \
            (void)compressed_log_output((token), (short_format), (short_format), \
                                        ##__VA_ARGS__);                          \
    } while (0)

#endif
