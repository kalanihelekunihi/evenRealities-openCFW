/* Shared declarations for the stock platform\service\flashDB units. */
#ifndef G2_KVDB_PRIVATE_H
#define G2_KVDB_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "g2_kvdb.h"

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* The stock log macro: EasyLogger-style record when flag bit 1 is set, then the
 * compressed record (code = level << 26 | argument count << 22). */
#define G2_KV_LOG(level, tag, file, func, line, fmt, short_fmt, code, ...)                 \
    do {                                                                                   \
        if ((audio_log_flags() & 2u) != 0u)                                                \
            audio_log_extended((level), (tag), (file), (func), (line), (fmt), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)              \
            (void)compress_log_output((code), (short_fmt), (short_fmt), ##__VA_ARGS__);    \
    } while (0)

/* Migration callbacks are collected by the linker into one ROM section
 * (stock bounds 0x746d20..0x746d4c, eleven entries). */
#define G2_KVDB_MIGRATION_EXPORT(fn)                                        \
    static const g2_kvdb_migration_fn g2_kvdb_migration_##fn                \
        __attribute__((used, section("kvdb_migration"))) = (fn)

/* Existing g2/src names for the db_api and service_kvdb siblings. */
extern uint32_t g2_flashdb_candidate_blob_read(uint32_t index, uint32_t key, uint32_t buf,
                                               uint32_t length); /* SVC_FlashDBBlobRead 0x54116e */
extern int32_t audio_flashdb_blob_write(uint32_t index, const char *key, const void *data,
                                        uint16_t length); /* SVC_FlashDBBlobWrite 0x5411f2 */
extern int32_t audio_settings_kvdb_blob_write(const char *key, const void *data,
                                              uint32_t length); /* SVC_KvdbBlobWrite 0x4d957e */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *bytes, uint32_t length,
                                                const uint16_t *seed); /* CRC-16/CCITT */

#endif
