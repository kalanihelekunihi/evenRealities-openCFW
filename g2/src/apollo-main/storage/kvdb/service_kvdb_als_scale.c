/* KV record "kvAlsScale", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_als_scale.c.
 * Native 0x4aeca4..0x4aedf7; literal pool 0x4aedf8..0x4aee27.
 * Record: g2_kvdb_word_record_t, 12 bytes, current version 1, CRC over the first 8 bytes. */
#include "kvdb_private.h"

#define RECORD_VERSION 1u

g2_kvdb_word_record_t g2_kvdb_als_scale_record = { 1u, { 0u, 0u, 0u }, 0x400u, 0u, 0u }; /* RAM 0x200037bc, stock default */

static const char key[] = "kvAlsScale"; /* ROM 0x78bf90 */
static const char module_tag[] = "kv.als_scale"; /* ROM 0x788a70 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_als_scale.c"; /* ROM 0x6e1824 */
static const char update_fn[] = "_kvdbUpdataAlsScale"; /* ROM 0x783320 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788a80 */
static const char version_msg_short[] = "[kv.als_scale]version %d(%d)"; /* ROM 0x764f90 */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788a90 */
static const char crc_msg_short[] = "[kv.als_scale]crc 0x%x(0x%x)"; /* ROM 0x764fb0 */
static const char write_fn[] = "SVC_KvdbWriteAlsScale"; /* ROM 0x77b92c */
static const char write_msg[] = "write als scale failed, ret = %d"; /* ROM 0x759af8 */
static const char write_msg_short[] = "[kv.als_scale]write als scale failed, ret = %d"; /* ROM 0x7384d4 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbAlsScaleDefaultInitialize(void) {
    g2_kvdb_als_scale_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_als_scale_record, 8u, NULL);
    return 0;
}

int32_t _kvdbUpdataAlsScale(void) {
    g2_kvdb_word_record_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 32u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 33u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_als_scale_record.crc);
        if (stored.crc != g2_kvdb_als_scale_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteAlsScale(&g2_kvdb_als_scale_record);
        return 0;
    }
    (void)SVC_KvdbWriteAlsScale(&g2_kvdb_als_scale_record);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataAlsScale);

int32_t SVC_KvdbWriteAlsScale(const g2_kvdb_word_record_t *record) {
    g2_kvdb_als_scale_record = *record;
    g2_kvdb_als_scale_record.version = RECORD_VERSION;
    g2_kvdb_als_scale_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_als_scale_record, 8u, NULL);
    int32_t status = audio_settings_kvdb_blob_write(key, &g2_kvdb_als_scale_record, sizeof(g2_kvdb_als_scale_record));
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 50u, write_msg, write_msg_short,
                  0x04400000u, status);
    return 0;
}
