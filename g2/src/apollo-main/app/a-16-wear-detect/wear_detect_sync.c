/* Wear-detect peer sync, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_wear_detect\ux_wear_detect.c.
 * Native 0x49eae2..0x49eb1e and 0x49ed04..0x49efac; literal pool 0x49efac..0x49f020.
 *
 * Both arms exchange 8-byte records on sync application 0x107 (UI registry row
 * 42 points its handler at 0x49ed04): +0 type, +4 value.
 *   2  wear state (1 removed, 2 worn) -> stored in RAM 0x20074edc
 *   3  sensor state sync, value = role << 16 | state
 *   4  request the sensor state (handled by role 2)
 *   5  request the wear state (handled by role 1)
 * Role 1 also measures how long the glasses were worn and reports it as
 * tracking event 0x60101 when they are removed. */
#include <stdint.h>

#define WEAR_SYNC_APP 0x107u
#define WEAR_MSG_STATE 2u
#define WEAR_MSG_SENSOR_SYNC 3u
#define WEAR_MSG_SENSOR_REQUEST 4u
#define WEAR_MSG_STATE_REQUEST 5u
#define WEAR_STATE_REMOVED 1u
#define WEAR_STATE_WORN 2u
#define ROLE_1 1u
#define ROLE_2 2u
#define TP_WEAR_GLASSES_REMOVE 0x60101u

typedef struct {
    uint8_t type;   /* +0 */
    uint8_t pad[3]; /* +1 */
    uint32_t value; /* +4 */
} g2_wear_sync_msg_t;
_Static_assert(sizeof(g2_wear_sync_msg_t) == 8u, "wear sync record");

extern volatile uint32_t audio_uart_lcd_status_cell;      /* RAM 0x20074edc wear state */
extern volatile uint32_t g2_wear_detect_role2_state_20074ee0; /* RAM 0x20074ee0 */
extern volatile uint32_t g2_wear_detect_role1_state_20074ee4; /* RAM 0x20074ee4 */
extern volatile uint32_t g2_wear_detect_worn_tick_20074ee8;   /* RAM 0x20074ee8 0 = not timing */
extern const g2_wear_sync_msg_t g2_wear_sync_msg_template;    /* ROM 0x78ee04, all zero */

extern uint8_t audio_uart_device_role_get(void); /* 0x45a568 */
extern uint32_t osKernelGetTickCount(void);      /* 0x4490cc */
extern uint8_t wear_detect_sensor_state_get_502dae(void); /* reads RAM 0x20075018 */
extern int32_t audio_uart_input_event_send_464d1c(uint16_t app, const void *payload, uint32_t length,
                                                  uint32_t context);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t event, uint32_t count, const void *values);
extern uint32_t audio_wear_detect_handle_status_change_49ebb6(uint32_t state);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);     /* 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "wear.detect"; /* ROM 0x78c914 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_wear_detect\\ux_wear_detect.c"; /* ROM 0x6f7cf0 */
static const char handler_fn[] = "WearDetect_DataHandler"; /* ROM 0x77d864 */
static const char invalid_data[] = "Invalid wear detect data"; /* ROM 0x774790 */
static const char invalid_data_short[] = "[wear.detect]Invalid wear detect data"; /* ROM 0x7514a4 */
static const char invalid_state[] = "wear detect state is invalid"; /* ROM 0x768210 */
static const char invalid_state_short[] = "[wear.detect]wear detect state is invalid"; /* ROM 0x746c44 */
static const char unchanged[] = "wear detect state not changed"; /* ROM 0x768230 */
static const char unchanged_short[] = "[wear.detect]wear detect state not changed"; /* ROM 0x746c70 */
static const char removed[] = "[TP] wear_glasses_remove wear_duration=%ums"; /* ROM 0x746c9c */
static const char removed_short[] = "[wear.detect][TP] wear_glasses_remove wear_duration=%ums"; /* ROM 0x71b5b0 */
static const char sensor_sync[] = "recv sensor data sync, role=%d, state=%d"; /* ROM 0x746cc8 */
static const char sensor_sync_short[] = "[wear.detect]recv sensor data sync, role=%d, state=%d"; /* ROM 0x7262c0 */

#define LOG_EXT_ON() ((audio_log_flags() & 2u) != 0u)
#define LOG_CMP_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* Sensor sync records carry the sender role in the upper half-word. */
int32_t wear_detect_sync_send_49eae2(uint8_t type, uint32_t value)
{
    g2_wear_sync_msg_t msg = g2_wear_sync_msg_template;
    msg.type = type;
    if (type == WEAR_MSG_SENSOR_SYNC)
        msg.value = (value & 0xffffu) | ((uint32_t)(uint16_t)audio_uart_device_role_get() << 16);
    else
        msg.value = value;
    (void)audio_uart_input_event_send_464d1c(WEAR_SYNC_APP, &msg, sizeof msg, 0u);
    return 0;
}

int32_t WearDetect_DataHandler_49ed04(uint32_t app, const void *data, uint32_t length)
{
    g2_wear_sync_msg_t msg;
    (void)app;
    if (data == 0) {
        if (LOG_EXT_ON())
            audio_log_extended(2u, module_tag, source_file, handler_fn, 0x89u, invalid_data);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x08000000u, invalid_data_short, invalid_data_short);
        return -1;
    }
    audio_uart_buffer_zero(&msg, sizeof msg, 0u);
    audio_uart_checksum_copy(&msg, data, length);
    if (msg.type == WEAR_MSG_STATE) {
        if (msg.value == 0u) {
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0x92u, invalid_state);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10000000u, invalid_state_short, invalid_state_short);
            return 0;
        }
        if (audio_uart_lcd_status_cell == msg.value) {
            if (LOG_EXT_ON())
                audio_log_extended(4u, module_tag, source_file, handler_fn, 0x96u, unchanged);
            if (LOG_CMP_ON())
                (void)compress_log_output(0x10000000u, unchanged_short, unchanged_short);
            return 0;
        }
        audio_uart_lcd_status_cell = msg.value;
        if (audio_uart_device_role_get() == ROLE_1) {
            if (audio_uart_lcd_status_cell == WEAR_STATE_WORN) {
                g2_wear_detect_worn_tick_20074ee8 = osKernelGetTickCount();
            } else if (audio_uart_lcd_status_cell == WEAR_STATE_REMOVED &&
                       g2_wear_detect_worn_tick_20074ee8 != 0u) {
                uint32_t duration = osKernelGetTickCount() - g2_wear_detect_worn_tick_20074ee8;
                audio_uart_ring_wear_persist_48eb32(TP_WEAR_GLASSES_REMOVE, 1u, &duration);
                if (LOG_EXT_ON())
                    audio_log_extended(3u, module_tag, source_file, handler_fn, 0xa3u, removed, duration);
                if (LOG_CMP_ON())
                    (void)compress_log_output(0x0c400000u, removed_short, removed_short, duration);
                g2_wear_detect_worn_tick_20074ee8 = 0u;
            }
        }
        (void)audio_wear_detect_handle_status_change_49ebb6((uint8_t)audio_uart_lcd_status_cell);
        return 0;
    }
    if (msg.type == WEAR_MSG_SENSOR_SYNC) {
        uint32_t role = msg.value >> 16;
        uint32_t state = msg.value;
        if (LOG_EXT_ON())
            audio_log_extended(3u, module_tag, source_file, handler_fn, 0xadu, sensor_sync,
                               (uint16_t)role, (uint16_t)state);
        if (LOG_CMP_ON())
            (void)compress_log_output(0x0c800000u, sensor_sync_short, sensor_sync_short,
                                      (uint16_t)role, (uint16_t)state);
        if ((uint16_t)role == ROLE_2)
            g2_wear_detect_role2_state_20074ee0 = (uint16_t)state;
        else if ((uint16_t)role == ROLE_1)
            g2_wear_detect_role1_state_20074ee4 = (uint16_t)state;
        if (audio_uart_device_role_get() == ROLE_2) {
            if (audio_uart_lcd_status_cell == 0u)
                (void)wear_detect_sync_send_49eae2(WEAR_MSG_STATE_REQUEST, 0u);
            return 0;
        }
        if (g2_wear_detect_role2_state_20074ee0 == 0u)
            (void)wear_detect_sync_send_49eae2(WEAR_MSG_SENSOR_REQUEST, 0u);
        else if (g2_wear_detect_role1_state_20074ee4 == WEAR_STATE_WORN &&
                 g2_wear_detect_role2_state_20074ee0 == WEAR_STATE_WORN)
            (void)wear_detect_sync_send_49eae2(WEAR_MSG_STATE, WEAR_STATE_WORN);
        else if (g2_wear_detect_role1_state_20074ee4 == WEAR_STATE_REMOVED &&
                 g2_wear_detect_role2_state_20074ee0 == WEAR_STATE_REMOVED)
            (void)wear_detect_sync_send_49eae2(WEAR_MSG_STATE, WEAR_STATE_REMOVED);
        return 0;
    }
    if (msg.type == WEAR_MSG_SENSOR_REQUEST) {
        if (audio_uart_device_role_get() != ROLE_2)
            return 0;
        uint8_t sensor = wear_detect_sensor_state_get_502dae();
        if (sensor != 0u)
            (void)wear_detect_sync_send_49eae2(WEAR_MSG_SENSOR_SYNC, sensor);
        return 0;
    }
    if (msg.type == WEAR_MSG_STATE_REQUEST) {
        if (audio_uart_device_role_get() != ROLE_1)
            return 0;
        if (audio_uart_lcd_status_cell != 0u)
            (void)wear_detect_sync_send_49eae2(WEAR_MSG_STATE, audio_uart_lcd_status_cell);
    }
    return 0;
}
