/* KV record "kvSetting", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_setting.c.
 * Native 0x4aeb20..0x4aec73; literal pool 0x4aec74..0x4aeca3.
 * Record: g2_kvdb_setting_t, 28 bytes, current version 4, CRC over the first 24 bytes. */
#include "kvdb_private.h"

#define RECORD_VERSION 4u
extern void *audio_uart_display_area_copy_439c04(void *, const void *, uint32_t);

g2_kvdb_setting_t g2_kvdb_setting_record = { 1u, { 0x64u, 0x01u, 0u, 0u, 0u, 0u, 0u, 0x06u, 0x01u, 0x01u, 0u, 0x1eu }, 0u, { 0u, 0u } }; /* RAM 0x200037e0, stock default */

static const char key[] = "kvSetting"; /* ROM 0x78bf9c */
static const char module_tag[] = "kv.tz"; /* ROM 0x78e5bc */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_setting.c"; /* ROM 0x6e4f30 */
static const char update_fn[] = "_kvdbUpdataSetting"; /* ROM 0x7833c0 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788ae0 */
static const char version_msg_short[] = "[kv.tz]version %d(%d)"; /* ROM 0x77b9a4 */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788af0 */
static const char crc_msg_short[] = "[kv.tz]crc 0x%x(0x%x)"; /* ROM 0x77b9bc */
static const char write_fn[] = "SVC_KvdbWriteSetting"; /* ROM 0x77b9d4 */
static const char write_msg[] = "write setting failed, ret = %d"; /* ROM 0x765030 */
static const char write_msg_short[] = "[kv.tz]write setting failed, ret = %d"; /* ROM 0x74df5c */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbSettingDefaultInitialize(void) {
    g2_kvdb_setting_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_setting_record, 24u, NULL);
    return 0;
}

int32_t _kvdbUpdataSetting(void) {
    g2_kvdb_setting_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 49u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 50u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_setting_record.crc);
        if (stored.crc != g2_kvdb_setting_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteSetting(&g2_kvdb_setting_record);
        return 0;
    }
    (void)SVC_KvdbWriteSetting(&g2_kvdb_setting_record);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataSetting);

int32_t SVC_KvdbWriteSetting(const g2_kvdb_setting_t *setting) {
    audio_uart_display_area_copy_439c04(&g2_kvdb_setting_record, setting, sizeof(g2_kvdb_setting_record));
    g2_kvdb_setting_record.version = RECORD_VERSION;
    g2_kvdb_setting_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_setting_record, 24u, NULL);
    int32_t status = audio_settings_kvdb_blob_write(key, &g2_kvdb_setting_record, sizeof(g2_kvdb_setting_record));
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 67u, write_msg, write_msg_short,
                  0x04400000u, status);
    return 0;
}
