/* KV record "kvTerminalMode", stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb_terminal_mode.c.
 * Native 0x4b03e0..0x4b04c3 (SVC_KvdbWriteTerminalMode 0x4b04c4 is
 * audio_settings_persist_record in app/settings-persist); pool 0x4b0530..0x4b055f.
 * Record: g2_kvdb_terminal_mode_t, 4 bytes, version 1, CRC over the first 2 bytes.
 * Stock default (RAM 0x20003808, initialised data) is 01 00 00 00. */
#include "kvdb_private.h"

#define RECORD_VERSION 1u

extern uint8_t audio_settings_terminal_record[4];                 /* RAM 0x20003808 */
extern uint32_t audio_settings_persist_record(const void *source); /* 0x4b04c4 */

#define TERMINAL_RECORD ((g2_kvdb_terminal_mode_t *)(void *)audio_settings_terminal_record)

static const char key[] = "kvTerminalMode"; /* ROM 0x788b20 */
static const char module_tag[] = "kv.terminal_mode"; /* ROM 0x7833e8 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\flashDB\\kv\\service_kvdb_terminal_mode.c"; /* ROM 0x6de794 */
static const char update_fn[] = "_kvdbUpdataTerminalMode"; /* ROM 0x77ba1c */
static const char version_msg[] = "version %d(%d)"; /* ROM 0x788b30 */
static const char version_msg_short[] = "[kv.terminal_mode]version %d(%d)"; /* ROM 0x759bac */
static const char crc_msg[] = "crc 0x%x(0x%x)"; /* ROM 0x788b40 */
static const char crc_msg_short[] = "[kv.terminal_mode]crc 0x%x(0x%x)"; /* ROM 0x759bd0 */

/* Stock init table entry, level 75: seal the default record before mount. */
int32_t kvdbTerminalModeDefaultInitialize(void) {
    TERMINAL_RECORD->crc = audio_uart_hand_checksum_49acd4(TERMINAL_RECORD, 2u, NULL);
    return 0;
}

int32_t _kvdbUpdataTerminalMode(void) {
    g2_kvdb_terminal_mode_t stored;
    if (SVC_KvdbBlobRead(key, &stored, (uint16_t)sizeof(stored)) > 0) {
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 30u, version_msg, version_msg_short,
                  0x10800000u, stored.version, RECORD_VERSION);
        G2_KV_LOG(4u, module_tag, source_file, update_fn, 31u, crc_msg, crc_msg_short,
                  0x10800000u, stored.crc, TERMINAL_RECORD->crc);
        if (stored.crc != TERMINAL_RECORD->crc && stored.version < RECORD_VERSION)
            (void)audio_settings_persist_record(TERMINAL_RECORD);
        return 0;
    }
    (void)audio_settings_persist_record(TERMINAL_RECORD);
    return 0;
}
G2_KVDB_MIGRATION_EXPORT(_kvdbUpdataTerminalMode);
