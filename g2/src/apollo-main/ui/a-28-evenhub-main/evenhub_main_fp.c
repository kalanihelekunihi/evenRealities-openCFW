/* evenhub_common_data_handler, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_main.c (log tag "evenhub.main").
 * Native 0x4e1192..0x4e1405; literal pool shared with evenhub_main.c (0x4e1958..0x4e1a47).
 * The IMU report logs its three floats promoted to double (vcvt.f64.f32) and forwards them
 * in s0..s2: build with profile g2-apollo-main-20.
 *
 * UI registry slot 7 data callback: type 0 is an EvenHub protobuf frame from the phone,
 * type 5 a peer (other arm) private message: 00 abnormal error exit, 01 IMU report
 * {01, f32 x, f32 y, f32 z}. */
#include <stdint.h>
#include <stddef.h>

#define EVENHUB_VFP __attribute__((pcs("aapcs-vfp")))
#define EVENHUB_APP_ID 0xe0u

enum {
    EVENHUB_DATA_FRAME = 0u,
    PEER_SEND_MSG_TO_COMMON_DATA_HANDLER = 5u,
};

enum {
    EVENHUB_PRIVATE_ABNORMAL_ERROR_EXIT = 0u,
    EVENHUB_PRIVATE_IMU_DATA_REPORT = 1u,
};

#define EVENHUB_IMU_REPORT_LEN 13u

extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_log_wake_allowed(void);                                  /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);          /* 0x4434d0 */
extern void audio_system_alert_close_464c36(uint32_t application_id, uint32_t payload,
                                            uint32_t length, uint32_t flags);
extern int32_t evenhub_data_parser_4da834(const uint8_t *data, uint32_t len);
extern EVENHUB_VFP int32_t evenhub_send_imu_event_4d9f6e(float x, float y, float z);
extern int32_t evenhub_send_container_event_4da16a(uint8_t type, uint32_t id, const char *name,
                                                   uint8_t sub, int32_t index, int16_t extra);

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char eh_tag[] = "evenhub.main"; /* ROM 0x785e70 */
static const char eh_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_main.c"; /* ROM 0x702988 */
static const char fn_data[] = "evenhub_common_data_handler"; /* ROM 0x76b848 */
static const char cd_type[] = "evenhub_common_data_handler eventType = %d"; /* ROM 0x73ed40 */
static const char cd_type_s[] = "[evenhub.main]evenhub_common_data_handler eventType = %d"; /* ROM 0x7150ac */
static const char cd_null[] = "evenhub_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER raw_data is NULL or len is 0"; /* ROM 0x6dd2f4 */
static const char cd_null_s[] = "[evenhub.main]evenhub_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER raw_data is NULL or len is 0"; /* ROM 0x6ca6a4 */
static const char cd_abnormal[] = "evenhub_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_ABNORMAL_ERROR_EXIT"; /* ROM 0x6d899c */
static const char cd_abnormal_s[] = "[evenhub.main]evenhub_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_ABNORMAL_ERROR_EXIT"; /* ROM 0x6a01cc */
static const char cd_imu[] = "evenhu_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_IMU_DATA_REPORT"; /* ROM 0x6dd354 */
static const char cd_imu_s[] = "[evenhub.main]evenhu_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_IMU_DATA_REPORT"; /* ROM 0x6d6fd0 */
static const char cd_short[] = "evenhu_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_IMU_DATA_REPORT len is less than 13"; /* ROM 0x6a05c4 */
static const char cd_short_s[] = "[evenhub.main]evenhu_common_data_handler PEER_SEND_MSG_TO_COMMON_DATA_HANDLER EVENHUB_PRIVATE_IMU_DATA_REPORT len is less than 13"; /* ROM 0x6d4fc4 */
static const char cd_xyz[] = "x = %f, y = %f, z = %f"; /* ROM 0x7775f4 */
static const char cd_xyz_s[] = "[evenhub.main]x = %f, y = %f, z = %f"; /* ROM 0x74a014 */

#define EH_LOG(level, func, line, cflags, text, short_text, ...)                                 \
    do {                                                                                         \
        if ((audio_log_flags() & 2u) != 0u)                                                      \
            audio_log_extended((level), eh_tag, eh_file, (func), (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                    \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);      \
    } while (0)

/* evenhub_common_data_handler. Stock leaves the return register as the last callee's
 * result on the abnormal-exit and unknown-type paths; 0 is returned here. */
int32_t audio_uart_registry_callback_4e1192(uint32_t event, const uint8_t *data, uint32_t len,
                                            void *context)
{
    (void)context;
    EH_LOG(4u, fn_data, 0xd9u, 0x10400000u, cd_type, cd_type_s, event);
    if (event == EVENHUB_DATA_FRAME)
        return evenhub_data_parser_4da834(data, len);
    if (event != PEER_SEND_MSG_TO_COMMON_DATA_HANDLER)
        return 0;
    if ((data == NULL || len == 0u) &&
        (audio_log_wake_allowed() == 0u ||
         audio_quicklist_refresh_enabled_4434d0(EVENHUB_APP_ID) == 0u)) {
        EH_LOG(1u, fn_data, 0xdfu, 0x04000000u, cd_null, cd_null_s);
        return -1;
    }
    if (data[0] == EVENHUB_PRIVATE_ABNORMAL_ERROR_EXIT) {
        EH_LOG(1u, fn_data, 0xe5u, 0x04000000u, cd_abnormal, cd_abnormal_s);
        (void)evenhub_send_container_event_4da16a(0u, 0u, NULL, 6u, 0, 0);
        audio_system_alert_close_464c36(EVENHUB_APP_ID, 0u, 0u, 0u);
        return 0;
    }
    if (data[0] != EVENHUB_PRIVATE_IMU_DATA_REPORT)
        return 0;
    EH_LOG(4u, fn_data, 0xeau, 0x10000000u, cd_imu, cd_imu_s);
    if (len < EVENHUB_IMU_REPORT_LEN) {
        EH_LOG(1u, fn_data, 0xecu, 0x04000000u, cd_short, cd_short_s);
        return -1;
    }
    float x;
    float y;
    float z;
    (void)audio_queue_copy_bytes(&x, data + 1, 4u);
    (void)audio_queue_copy_bytes(&y, data + 5, 4u);
    (void)audio_queue_copy_bytes(&z, data + 9, 4u);
    EH_LOG(4u, fn_data, 0xf3u, 0x10c00000u, cd_xyz, cd_xyz_s, (double)x, (double)y, (double)z);
    return evenhub_send_imu_event_4d9f6e(x, y, z);
}
