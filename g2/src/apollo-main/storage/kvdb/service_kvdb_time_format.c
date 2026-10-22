/* KV record "kvTimeFormat", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_time_format.c.
 * Native 0x49ae90..0x49afe3; literal pool 0x49afe4..0x49b013.
 * Record: g2_kvdb_word_record_t, 12 bytes, current version 1, CRC over the first 8 bytes. */
#include "kvdb_private.h"

#define RECORD_VERSION 1u

g2_kvdb_word_record_t g2_kvdb_time_format_record = { 1u, { 0u, 0u, 0u }, 0u, 0u, 0u }; /* RAM 0x20003818, stock default */

static const char key[] = "kvTimeFormat"; /* ROM 0x788b80 */
static const char module_tag[] = "kv.tz"; /* ROM 0x78e5dc */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_time_format.c"; /* ROM 0x6e1880 */
static const char update_fn[] = "_kvdbUpdataTimeFormat"; /* ROM 0x77ba64 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788b90 */
static const char version_msg_short[] = "[kv.tz]version %d(%d)"; /* ROM 0x77ba7c */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788ba0 */
static const char crc_msg_short[] = "[kv.tz]crc 0x%x(0x%x)"; /* ROM 0x77ba94 */
static const char write_fn[] = "SVC_KvdbWriteTimeFormat"; /* ROM 0x77baac */
static const char write_msg[] = "write time format failed, ret = %d"; /* ROM 0x759c18 */
static const char write_msg_short[] = "[kv.tz]write time format failed, ret = %d"; /* ROM 0x743410 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbTimeFormatDefaultInitialize(void) {
    g2_kvdb_time_format_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_time_format_record, 8u, NULL);
    return 0;
}

int32_t _kvdbUpdataTimeFormat(void) {
    g2_kvdb_word_record_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 35u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 36u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_time_format_record.crc);
        if (stored.crc != g2_kvdb_time_format_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteTimeFormat(&g2_kvdb_time_format_record);
        return 0;
    }
    (void)SVC_KvdbWriteTimeFormat(&g2_kvdb_time_format_record);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataTimeFormat);

int32_t SVC_KvdbWriteTimeFormat(const g2_kvdb_word_record_t *record) {
    g2_kvdb_time_format_record = *record;
    g2_kvdb_time_format_record.version = RECORD_VERSION;
    g2_kvdb_time_format_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_time_format_record, 8u, NULL);
    int32_t status = audio_settings_kvdb_blob_write(key, &g2_kvdb_time_format_record, sizeof(g2_kvdb_time_format_record));
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 54u, write_msg, write_msg_short,
                  0x04400000u, status);
    return 0;
}
