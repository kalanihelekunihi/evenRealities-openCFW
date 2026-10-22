/* Stock D:\01_workspace\s200_ap510b_iar_git\platform\service\service_universal_setting\service_universal_setting.c
 * Native rows 0x46607c..0x4661a5 (svc_universal_setting_save_to_kv), the byte
 * getters 0x4664fa/0x466500/0x466506/0x466512 and
 * svc_universal_setting_get_gesture_apptype 0x46651e..0x46658d; literal pool
 * 0x4667ec..0x466877. Other functions of this file are already sourced:
 * 0x466016 ring-hand/display_ring_hand_commit.c, 0x4661a6 ring-hand/display_ring_hand_publish.c,
 * 0x46636c/0x466412 system/registry-*, 0x46650c time-epoch, 0x466518 ring-getters,
 * 0x46658e setting-gesture, 0x466660 ring-hand/display_ring_hand_initialize.c.
 *
 * RAM 0x200736d4 holds the working copy of three KV records (0x2c bytes):
 *   +0x00 kvUniversalSetting (20 bytes, CRC at +0x12):
 *         +0x01 metric_unit, +0x02 date_format, +0x03 distance_unit,
 *         +0x04 temperature_unit, +0x05..+0x07 screen-off gesture apptypes,
 *         +0x08..+0x0a screen-on gesture apptypes, +0x0b dominant_hand,
 *         +0x0c..+0x11 ring MAC (logged reversed)
 *   +0x14 kvTimeFormat (12 bytes, word +0x18 time_format, CRC at +0x1c)
 *   +0x20 kvTemperatureUnit (12 bytes, word +0x24, CRC at +0x28)
 * The settings-manager block at RAM 0x200036fc points (+0x0c, +0x10, +0x14)
 * at the KV store's RAM copy of each record. */
#include <stdint.h>
#include "g2_kvdb.h"

#define US_METRIC_UNIT      0x01u
#define US_DATE_FORMAT      0x02u
#define US_DISTANCE_UNIT    0x03u
#define US_TEMPERATURE_UNIT 0x04u
#define US_SCREEN_OFF_APPS  0x05u
#define US_SCREEN_ON_APPS   0x08u
#define US_CRC              0x12u
#define US_TIME_FORMAT_REC  0x14u
#define US_TIME_FORMAT_CRC  0x1cu
#define US_TEMP_UNIT_REC    0x20u
#define US_TEMP_UNIT_CRC    0x28u

#define MANAGER_TIME_FORMAT 0x0cu
#define MANAGER_TEMP_UNIT   0x10u
#define MANAGER_UNIVERSAL   0x14u

extern uint8_t audio_uart_hand_record[0x30u];            /* RAM 0x200736d4 (pool 0x4667ec) */
extern uint8_t audio_uart_hand_snapshot_context[];       /* RAM 0x200036fc (pool 0x4667f0) */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "srv_universal_setting"; /* ROM 0x77bd04 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\service_universal_setting\\service_universal_setting.c"; /* ROM 0x6d7e10 */
static const char save_fn[] = "svc_universal_setting_save_to_kv"; /* ROM 0x759fc0 */
static const char save_setting[] = "save universal setting to kv"; /* ROM 0x765450 */
static const char save_setting_short[] = "[srv_universal_setting]save universal setting to kv"; /* ROM 0x72db04 */
static const char save_time[] = "save time format to kv"; /* ROM 0x77bd1c */
static const char save_time_short[] = "[srv_universal_setting]save time format to kv"; /* ROM 0x738804 */
static const char save_temp[] = "save temperature unit to kv"; /* ROM 0x7719a0 */
static const char save_temp_short[] = "[srv_universal_setting]save temperature unit to kv"; /* ROM 0x72db38 */
static const char get_gesture_fn[] = "svc_universal_setting_get_gesture_apptype"; /* ROM 0x743af0 */
static const char invalid_op[] = "Invalid operation_type: %d"; /* ROM 0x7719bc */
static const char invalid_op_short[] = "[srv_universal_setting]Invalid operation_type: %d"; /* ROM 0x72db6c */

static void log_saved(uint32_t line, const char *message, const char *short_message)
{
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, save_fn, line, message);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c000000u, short_message, short_message);
}

static const uint8_t *manager_record(uint32_t offset)
{
    return *(const uint8_t *const *)(const void *)(audio_uart_hand_snapshot_context + offset);
}

static uint16_t crc_at(const uint8_t *record, uint32_t offset)
{
    return *(const uint16_t *)(const void *)(record + offset);
}

/* Each record is written only when its CRC differs from the store's RAM copy;
 * after the write the working record is reloaded from that RAM copy
 * (memcpy(working, store_copy, n), as in stock). */
uint32_t svc_universal_setting_save_to_kv_46607c(void)
{
    uint8_t *working = audio_uart_hand_record;
    uint8_t *persisted = (uint8_t *)(uintptr_t)manager_record(MANAGER_UNIVERSAL);
    if (crc_at(persisted, US_CRC) != crc_at(working, US_CRC)) {
        (void)SVC_KvdbWriteUniversalSetting((const g2_kvdb_universal_setting_t *)(const void *)working);
        (void)audio_queue_copy_bytes(working, persisted, 0x14u);
        log_saved(0x4eu, save_setting, save_setting_short);
    }
    persisted = (uint8_t *)(uintptr_t)manager_record(MANAGER_TIME_FORMAT);
    if (crc_at(persisted, 8u) != crc_at(working, US_TIME_FORMAT_CRC)) {
        (void)SVC_KvdbWriteTimeFormat((const g2_kvdb_word_record_t *)(const void *)(working + US_TIME_FORMAT_REC));
        (void)audio_queue_copy_bytes(working + US_TIME_FORMAT_REC, persisted, 0x0cu);
        log_saved(0x56u, save_time, save_time_short);
    }
    persisted = (uint8_t *)(uintptr_t)manager_record(MANAGER_TEMP_UNIT);
    if (crc_at(persisted, 8u) != crc_at(working, US_TEMP_UNIT_CRC)) {
        (void)SVC_KvdbWriteTemperatureUnit((const g2_kvdb_word_record_t *)(const void *)(working + US_TEMP_UNIT_REC));
        (void)audio_queue_copy_bytes(working + US_TEMP_UNIT_REC, persisted, 0x0cu);
        log_saved(0x5eu, save_temp, save_temp_short);
    }
    return 0u;
}

uint8_t svc_universal_setting_get_metric_unit_4664fa(void)
{
    return audio_uart_hand_record[US_METRIC_UNIT];
}

uint8_t svc_universal_setting_get_date_format_466500(void)
{
    return audio_uart_hand_record[US_DATE_FORMAT];
}

uint8_t svc_universal_setting_get_distance_unit_466506(void)
{
    return audio_uart_hand_record[US_DISTANCE_UNIT];
}

uint8_t svc_universal_setting_get_temperature_unit_466512(void)
{
    return audio_uart_hand_record[US_TEMPERATURE_UNIT];
}

/* svc_universal_setting_get_gesture_apptype(screen_on, operation_type):
 * operation_type 0..2 indexes the screen-off (screen_on == 0) or screen-on
 * table; anything else logs a warning and returns 0. */
uint8_t universal_setting_startup_apptype_46651e(uint8_t screen_on, uint8_t operation_type)
{
    if (operation_type >= 3u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module_tag, source_file, get_gesture_fn, 0x11du, invalid_op,
                               (uint32_t)operation_type);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x08400000u, invalid_op_short, invalid_op_short,
                                      (uint32_t)operation_type);
        return 0u;
    }
    if (screen_on != 0u)
        return audio_uart_hand_record[US_SCREEN_ON_APPS + operation_type];
    return audio_uart_hand_record[US_SCREEN_OFF_APPS + operation_type];
}
