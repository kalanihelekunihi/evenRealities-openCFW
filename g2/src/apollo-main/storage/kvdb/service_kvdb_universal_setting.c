/* KV record "kvUniversalSetting", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_universal_setting.c.
 * Native 0x49ad0c..0x49ae5f; literal pool 0x49ae60..0x49ae8f.
 * Record: g2_kvdb_universal_setting_t, 20 bytes, current version 3, CRC over the first 18 bytes. */
#include "kvdb_private.h"

#define RECORD_VERSION 3u
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* 0x439be4 */

g2_kvdb_universal_setting_t g2_kvdb_universal_setting_record = { 3u, { 0u, 0u, 0u }, 1u, 0u, 0xffffffffu, 0xffffu, 0u }; /* RAM 0x20003824, stock default */

static const char key[] = "kvUniversalSetting"; /* ROM 0x783424 */
static const char module_tag[] = "kvdb_universal_setting"; /* ROM 0x77bac4 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_universal_setting.c"; /* ROM 0x6db998 */
static const char update_fn[] = "_kvdbUpdataUniversalSetting"; /* ROM 0x7713d4 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788bb0 */
static const char version_msg_short[] = "[kvdb_universal_setting]version %d(%d)"; /* ROM 0x74dfd4 */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788bc0 */
static const char crc_msg_short[] = "[kvdb_universal_setting]crc 0x%x(0x%x)"; /* ROM 0x74dffc */
static const char write_fn[] = "SVC_KvdbWriteUniversalSetting"; /* ROM 0x765070 */
static const char write_msg[] = "write universal setting failed, ret = %d"; /* ROM 0x74343c */
static const char write_msg_short[] = "[kvdb_universal_setting]write universal setting failed, ret = %d"; /* ROM 0x705a68 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbUniversalSettingDefaultInitialize(void) {
    g2_kvdb_universal_setting_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_universal_setting_record, 18u, NULL);
    return 0;
}

int32_t _kvdbUpdataUniversalSetting(void) {
    g2_kvdb_universal_setting_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 38u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 39u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_universal_setting_record.crc);
        if (stored.crc != g2_kvdb_universal_setting_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteUniversalSetting(&g2_kvdb_universal_setting_record);
        return 0;
    }
    (void)SVC_KvdbWriteUniversalSetting(&g2_kvdb_universal_setting_record);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataUniversalSetting);

int32_t SVC_KvdbWriteUniversalSetting(const g2_kvdb_universal_setting_t *setting) {
    audio_queue_copy_bytes(&g2_kvdb_universal_setting_record, setting, sizeof(g2_kvdb_universal_setting_record));
    g2_kvdb_universal_setting_record.version = RECORD_VERSION;
    g2_kvdb_universal_setting_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_universal_setting_record, 18u, NULL);
    int32_t status = audio_settings_kvdb_blob_write(key, &g2_kvdb_universal_setting_record, sizeof(g2_kvdb_universal_setting_record));
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 57u, write_msg, write_msg_short,
                  0x04400000u, status);
    return 0;
}
