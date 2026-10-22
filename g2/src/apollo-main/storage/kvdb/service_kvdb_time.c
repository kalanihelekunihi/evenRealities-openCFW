/* KV record "kvTime", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_time.c.
 * Native 0x585618..0x585805; literal pool 0x585808..0x58583f.
 * Record: g2_kvdb_time_t, 12 bytes, current version 3, CRC over the first 10
 * bytes. The factory default is version 1, timestamp 0x68372d2b
 * (2025-05-28 15:35:07 UTC) and timezone 32. */
#include "kvdb_private.h"

#define RECORD_VERSION 3u

g2_kvdb_time_t g2_kvdb_time_record = { 1u, { 0u, 0u, 0u }, 0x68372d2bu, 32, 0u, 0u }; /* RAM 0x2000380c, stock default */

static const char key[] = "kvTime"; /* ROM 0x78e5cc */
static const char module_tag[] = "kv.tz"; /* ROM 0x78e5d4 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_time.c"; /* ROM 0x6e9de4 */
static const char update_fn[] = "_kvdbUpdataTime"; /* ROM 0x788b50 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788b60 */
static const char version_msg_short[] = "[kv.tz]version %d(%d)"; /* ROM 0x77ba34 */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788b70 */
static const char crc_msg_short[] = "[kv.tz]crc 0x%x(0x%x)"; /* ROM 0x77ba4c */
static const char record_msg[] = "record_timezone = %d timestamp = %d"; /* ROM 0x759bf4 */
static const char record_msg_short[] = "[kv.tz]record_timezone = %d timestamp = %d"; /* ROM 0x7433e4 */
static const char write_fn[] = "SVC_KvdbWriteTime"; /* ROM 0x7833fc */
static const char check_msg[] = "record_check 0x%x"; /* ROM 0x783410 */
static const char check_msg_short[] = "[kv.tz]record_check 0x%x"; /* ROM 0x7713b8 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbTimeDefaultInitialize(void) {
    g2_kvdb_time_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_time_record, 10u, NULL);
    return 0;
}

int32_t _kvdbUpdataTime(void) {
    g2_kvdb_time_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 45u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 46u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_time_record.crc);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 47u, record_msg, record_msg_short,
                  0x10800000u, (int32_t)g2_kvdb_time_record.timezone, g2_kvdb_time_record.timestamp);
        if (stored.crc != g2_kvdb_time_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteTime(g2_kvdb_time_record.timestamp, g2_kvdb_time_record.timezone);
        return 0;
    }
    (void)SVC_KvdbWriteTime(g2_kvdb_time_record.timestamp, g2_kvdb_time_record.timezone);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataTime);

int32_t SVC_KvdbWriteTime(uint32_t timestamp, int8_t timezone) {
    g2_kvdb_time_record.timezone = timezone;
    g2_kvdb_time_record.timestamp = timestamp;
    g2_kvdb_time_record.version = RECORD_VERSION;
    g2_kvdb_time_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_time_record, 10u, NULL);
    G2_KV_LOG(4u, module_tag, source_file, write_fn, 65u, check_msg, check_msg_short, 0x10400000u,
              g2_kvdb_time_record.crc);
    G2_KV_LOG(4u, module_tag, source_file, write_fn, 66u, record_msg, record_msg_short, 0x10800000u,
              (int32_t)g2_kvdb_time_record.timezone, g2_kvdb_time_record.timestamp);
    return audio_settings_kvdb_blob_write(key, &g2_kvdb_time_record, sizeof(g2_kvdb_time_record));
}
