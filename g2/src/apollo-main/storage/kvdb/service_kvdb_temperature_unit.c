/* KV record "kvTemperatureUnit", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_temperature_unit.c.
 * Native 0x49b014..0x49b167; literal pool 0x49b168..0x49b197.
 * Record: g2_kvdb_word_record_t, 12 bytes, current version 1, CRC over the first 8 bytes. */
#include "kvdb_private.h"

#define RECORD_VERSION 1u

g2_kvdb_word_record_t g2_kvdb_temperature_unit_record = { 1u, { 0u, 0u, 0u }, 0u, 0u, 0u }; /* RAM 0x200037fc, stock default */

static const char key[] = "kvTemperatureUnit"; /* ROM 0x7833d4 */
static const char module_tag[] = "kv.tu"; /* ROM 0x78e5c4 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_temperature_unit.c"; /* ROM 0x6de734 */
static const char update_fn[] = "_kvdbUpdataTemperatureUnit"; /* ROM 0x771380 */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788b00 */
static const char version_msg_short[] = "[kv.tu]version %d(%d)"; /* ROM 0x77b9ec */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788b10 */
static const char crc_msg_short[] = "[kv.tu]crc 0x%x(0x%x)"; /* ROM 0x77ba04 */
static const char write_fn[] = "SVC_KvdbWriteTemperatureUnit"; /* ROM 0x765050 */
static const char write_msg[] = "write temperature unit failed, ret = %d"; /* ROM 0x74df84 */
static const char write_msg_short[] = "[kv.tu]write temperature unit failed, ret = %d"; /* ROM 0x738564 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbTemperatureUnitDefaultInitialize(void) {
    g2_kvdb_temperature_unit_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_temperature_unit_record, 8u, NULL);
    return 0;
}

int32_t _kvdbUpdataTemperatureUnit(void) {
    g2_kvdb_word_record_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 34u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 35u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, g2_kvdb_temperature_unit_record.crc);
        if (stored.crc != g2_kvdb_temperature_unit_record.crc && stored.version < RECORD_VERSION)
            (void)SVC_KvdbWriteTemperatureUnit(&g2_kvdb_temperature_unit_record);
        return 0;
    }
    (void)SVC_KvdbWriteTemperatureUnit(&g2_kvdb_temperature_unit_record);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataTemperatureUnit);

int32_t SVC_KvdbWriteTemperatureUnit(const g2_kvdb_word_record_t *record) {
    g2_kvdb_temperature_unit_record = *record;
    g2_kvdb_temperature_unit_record.version = RECORD_VERSION;
    g2_kvdb_temperature_unit_record.crc = audio_uart_hand_checksum_49acd4(&g2_kvdb_temperature_unit_record, 8u, NULL);
    int32_t status = audio_settings_kvdb_blob_write(key, &g2_kvdb_temperature_unit_record, sizeof(g2_kvdb_temperature_unit_record));
    if (status != 0)
        G2_KV_LOG(1u, module_tag, source_file, write_fn, 53u, write_msg, write_msg_short,
                  0x04400000u, status);
    return 0;
}
