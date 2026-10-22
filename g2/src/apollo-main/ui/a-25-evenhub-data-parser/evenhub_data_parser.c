/* EvenHub protobuf reply / event encoders, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_data_parser.c.
 * Native 0x4d9b34..0x4da5ee and 0x4da60c..0x4da6ca, 0x4da720..0x4da7be;
 * literal pools 0x4da5f0..0x4da608, 0x4da6cc..0x4da6d0, 0x4da7c0..0x4da830.
 * The float encoders 0x4d9f6e and 0x4da6d4 are in evenhub_data_parser_fp.c;
 * the 0x4da834 frame parser (main body) is a separate row.
 *
 * Every encoder fills the shared tx message (RAM 0x20340b48) under the data
 * mutex, encodes it with the EvenHub descriptor (ROM 0x77754c) into the
 * 0x38ec-byte packet at RAM 0x203362c4 and sends it on service 0xe0: replies
 * to phone requests via Thread_MsgPbTxByBle, unsolicited events via
 * Thread_MsgPbNotifyByBle, and events that the right-hand (slave) side must
 * mirror via the glasses sync channel when the service mode is 1. */
#include <stdint.h>
#include <stddef.h>
#include "evenhub_data_parser_private.h"

extern void *g2_evenhub_data_mutex_2007458c;                                   /* RAM 0x2007458c */
extern void *osMutexNew(const void *attr);                                     /* 0x44971c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                  /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                    /* 0x44981c */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload, uint16_t length); /* 0x475b14 */
extern void audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern uint32_t audio_uart_service_mode(void);                                 /* 0x45a570 */
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len, uint32_t flags); /* 0x464bb2 */
extern int32_t async_request_display_reflash_45aaca(uint32_t application, const void *payload,
                                                    uint32_t length, uint32_t delay);
extern int32_t HUB_Open(uint8_t func_type);                                    /* 0x4a6d58 */
extern int32_t HUB_Close(uint8_t func_type);                                   /* 0x4a6dca */
extern uint32_t audio_hub_parameter_config_4a6e3c(uint32_t type, const int32_t *param); /* HUB_ParameterConfig */

static const char fn_lock[] = "evenhub_lock_data";                         /* ROM 0x77f39c */
static const char fn_unlock[] = "evenhub_unlock_data";                     /* ROM 0x77f3c4 */
static const char fn_common_response[] = "evenhub_common_response_cmd";    /* ROM 0x76b730 */
static const char fn_system_event[] = "evenhub_SendSystemEvent_cmd";       /* ROM 0x76b74c */
static const char fn_menu_startup[] = "evenhub_SendMenuStartup_cmd";       /* ROM 0x76b768 */
static const char fn_system_exit[] = "evenhub_SendSystemExitEvent_cmd";    /* ROM 0x75feb0 */
static const char fn_device_event[] = "evenhub_SendDeviceEvent_cmd";       /* ROM 0x76b7a0 */
static const char fn_private_event[] = "evenhub_common_device_private_event_cmd"; /* ROM 0x749efc */
static const char fn_imu_ctr[] = "evenhub_response_imu_ctr_cmd";           /* ROM 0x75fed0 */
static const char fn_imu_setting[] = "common_imu_setting_cmd";             /* ROM 0x77757c */
static const char none_text[] = "(none)";                                  /* ROM 0x78d59c */

#define EVENHUB_HUB_IMU 5u           /* sensor-hub function: IMU report */
#define EVENHUB_LONG_PRESS_EVENT 0x4cu

/* Create the data mutex once (called on entry of the 0x4da834 parser). */
void evenhub_data_mutex_init_4d9b34(void)
{
    if (g2_evenhub_data_mutex_2007458c == NULL)
        g2_evenhub_data_mutex_2007458c = osMutexNew(NULL);
}

void evenhub_lock_data_4d9b4a(void)
{
    if (g2_evenhub_data_mutex_2007458c == NULL) {
        EH_DP_LOG(1u, fn_lock, 0x48u, 0x04000000u, "evenhub_lock_data: mutex is NULL");
        return;
    }
    (void)osMutexAcquire(g2_evenhub_data_mutex_2007458c, 0xffffffffu);
}

void evenhub_unlock_data_4d9ba6(void)
{
    if (g2_evenhub_data_mutex_2007458c == NULL) {
        EH_DP_LOG(1u, fn_unlock, 0x51u, 0x04000000u, "evenhub_unlock_data: mutex is NULL");
        return;
    }
    (void)osMutexRelease(g2_evenhub_data_mutex_2007458c);
}

/* Audio-control acknowledgement: cmd 0xc, which 0xf, word at +4 and byte at +8.
 * Returns 0 on encode failure, else the BLE tx result. */
int32_t evenhub_send_audio_ctrl_ack_4d9bfe(uint8_t seq, uint8_t cmd, uint32_t value)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x0cu;
    msg->seq = seq;
    msg->which = 0x0fu;
    evenhub_put_u8(0x08u, cmd);
    evenhub_put_u32(0x04u, value);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                        (uint16_t)stream.bytes_written);
}

/* evenhub_common_response_cmd: echo cmd/seq with a one-byte status in the
 * submessage selected by which (4, 8, 10, 12 at +4; 15 at +8). Returns -1 for
 * any other which, 0 on encode failure, else the BLE tx result. */
int32_t evenhub_send_reply_4d9c86(uint8_t cmd, uint8_t seq, uint16_t which, uint32_t value)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = cmd;
    msg->seq = seq;
    msg->which = which;
    switch (which) {
    case 4u:
    case 8u:
    case 10u:
    case 12u:
        evenhub_put_u8(0x04u, (uint8_t)value);
        break;
    case 15u:
        evenhub_put_u8(0x08u, (uint8_t)value);
        break;
    default:
        EH_DP_LOG(1u, fn_common_response, 0x94u, 0x04400000u,
                  "which_Msg_Ctx is not CreateMessage_tag. exit! received msgTag is %d", which);
        evenhub_unlock_data_4d9ba6();
        return -1;
    }
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                        (uint16_t)stream.bytes_written);
}

/* evenhub_SendSystemEvent_cmd: cmd 0xe, which 0x11. Only the service-mode-1
 * side forwards it through the display sync; returns -3 on encode failure,
 * the service mode when it is not 1, else the sync result. */
int32_t evenhub_send_system_event_4d9d9a(uint8_t event, uint32_t value)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x0eu;
    msg->seq = 0u;
    msg->which = 0x11u;
    evenhub_put_u8(0x04u, event);
    evenhub_put_u32(0x08u, value);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_system_event, 0xb9u, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    int32_t result = (int32_t)audio_uart_service_mode();
    if (result == 1)
        result = audio_uart_master_display_refresh(EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                                   (uint16_t)stream.bytes_written, 0u);
    return result;
}

/* evenhub_SendMenuStartup_cmd: notify the phone that an EvenHub app was
 * launched from the menu (cmd 0x11, which 0x14). -3 on encode failure. */
int32_t evenhub_send_app_startup_4d9e88(uint32_t ext_app_id)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x11u;
    msg->seq = 0u;
    msg->which = 0x14u;
    evenhub_put_u32(0x04u, ext_app_id);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_menu_startup, 0xd2u, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    return (int32_t)Thread_MsgPbNotifyByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                            (uint16_t)stream.bytes_written);
}

/* evenhub_SendSystemExitEvent_cmd: device event, system submessage, event
 * type 7 with the exit value at +0x18. -3 on encode failure. */
int32_t evenhub_send_system_exit_event_4da078(uint32_t value)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 2u;
    msg->seq = 0u;
    msg->which = 0x0du;
    evenhub_put_u16(EVENHUB_DEV_WHICH_OFF, 3u);
    evenhub_put_u8(EVENHUB_DEV_SYS_EVENT_OFF, 7u);
    evenhub_put_u32(EVENHUB_DEV_SYS_EXIT_OFF, value);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_system_exit, 0x116u, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    return (int32_t)Thread_MsgPbNotifyByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                            (uint16_t)stream.bytes_written);
}

/* evenhub_SendDeviceEvent_cmd: type 0 system event (sub = event type; for
 * events 0 and 3 the input device 0/1/4 maps to 3/1/2), 1 list container
 * event (index at +0x5c), 2 text container event. -1 for type > 2, -3 on
 * encode failure, else the notify result. */
int32_t evenhub_send_container_event_4da16a(uint8_t type, uint32_t id, const char *name,
                                            uint8_t sub, int32_t index, int16_t extra)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 2u;
    msg->seq = 0u;
    msg->which = 0x0du;
    if (type == 0u) {
        evenhub_put_u16(EVENHUB_DEV_WHICH_OFF, 3u);
        evenhub_put_u8(EVENHUB_DEV_SYS_EVENT_OFF, sub);
        if (sub == 0u || sub == 3u) {
            uint16_t device = (uint16_t)extra;
            EH_DP_LOG(4u, fn_device_event, 0x134u, 0x10400000u, "Input_Device_Type = %d", device);
            if (device == 0u)
                evenhub_put_u8(EVENHUB_DEV_SYS_DEVICE_OFF, 3u);
            else if (device == 1u)
                evenhub_put_u8(EVENHUB_DEV_SYS_DEVICE_OFF, 1u);
            else if (device == 4u)
                evenhub_put_u8(EVENHUB_DEV_SYS_DEVICE_OFF, 2u);
        }
        if (sub == 7u)
            evenhub_put_u32(EVENHUB_DEV_SYS_EXIT_OFF, 0u);
    } else if (type == 2u) {
        evenhub_put_u16(EVENHUB_DEV_WHICH_OFF, 2u);
        evenhub_put_u32(EVENHUB_DEV_CTR_ID_OFF, id);
        audio_settings_copy_text((uint8_t *)msg + EVENHUB_DEV_CTR_NAME_OFF, name, 16u);
        evenhub_put_u8(EVENHUB_DEV_TEXT_EVENT_OFF, sub);
    } else if (type < 2u) {
        evenhub_put_u16(EVENHUB_DEV_WHICH_OFF, 1u);
        evenhub_put_u32(EVENHUB_DEV_CTR_ID_OFF, id);
        audio_settings_copy_text((uint8_t *)msg + EVENHUB_DEV_CTR_NAME_OFF, name, 16u);
        evenhub_put_u8(EVENHUB_DEV_LIST_EVENT_OFF, sub);
        evenhub_put_u32(EVENHUB_DEV_LIST_INDEX_OFF, (uint32_t)index);
    } else {
        evenhub_unlock_data_4d9ba6();
        EH_DP_LOG(1u, fn_device_event, 0x153u, 0x04400000u, "%d is not a valid container type. exit!", type);
        return -1;
    }
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_device_event, 0x15au, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    return (int32_t)Thread_MsgPbNotifyByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                            (uint16_t)stream.bytes_written);
}

/* evenhub_common_device_private_event_cmd: cmd 0xb, which 0x10 (container id,
 * name, event code, data). Sent over the display sync only in service mode 1;
 * event 0x4c goes through the async reflash request with a 300 ms delay.
 * -3 on encode failure, else 0. */
int32_t evenhub_send_input_event_4da382(uint32_t id, const char *name, int32_t event_code, uint32_t data)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x0bu;
    msg->seq = 0u;
    msg->which = 0x10u;
    evenhub_put_u32(0x04u, id);
    audio_settings_copy_text((uint8_t *)msg + 0x08u, name, 16u);
    evenhub_put_u32(0x18u, (uint32_t)event_code);
    evenhub_put_u32(0x1cu, data);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_private_event, 0x17cu, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    if (audio_uart_service_mode() == 1u) {
        if (event_code == (int32_t)EVENHUB_LONG_PRESS_EVENT)
            (void)async_request_display_reflash_45aaca(EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                                       (uint16_t)stream.bytes_written, 300u);
        else
            (void)audio_uart_master_display_refresh(EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                                    (uint16_t)stream.bytes_written, 0u);
    }
    return 0;
}

/* Reply to an image raw-data fragment (cmd 4, which 6): container id and name
 * plus the five fragment header words of the request and a status byte at
 * +0x2c (4 / 5 from the 0x4da834 parser). Returns 0 on encode failure, else
 * the BLE tx result. */
int32_t evenhub_send_image_raw_data_response_4da4a4(uint8_t seq, uint8_t status, uint32_t id,
                                                    const char *name, uint32_t session_id,
                                                    uint32_t total_size, uint32_t compress_mode,
                                                    uint32_t fragment_index, uint32_t fragment_size)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 4u;
    msg->seq = seq;
    msg->which = 6u;
    evenhub_put_u32(0x04u, id);
    audio_settings_copy_text((uint8_t *)msg + 0x08u, name, 16u);
    evenhub_put_u32(0x18u, session_id);
    evenhub_put_u32(0x1cu, total_size);
    evenhub_put_u32(0x20u, compress_mode);
    evenhub_put_u32(0x24u, fragment_index);
    evenhub_put_u32(0x28u, fragment_size);
    evenhub_put_u8(0x2cu, status);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                        (uint16_t)stream.bytes_written);
}

/* Audio-control reply (cmd 0x10, which 0x13) carrying the resulting state.
 * Returns 0 on encode failure, else the BLE tx result. */
int32_t evenhub_send_audio_ctrl_reply_4da56e(uint8_t seq, uint8_t state)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x10u;
    msg->seq = seq;
    msg->which = 0x13u;
    evenhub_put_u32(0x04u, state);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                        (uint16_t)stream.bytes_written);
}

/* evenhub_response_imu_ctr_cmd: reply to an IMU control request (cmd 0x14,
 * which 0x17). Returns 0 on encode failure, else the BLE tx result. */
int32_t evenhub_response_imu_ctr_4da60c(uint8_t seq, uint32_t status)
{
    EH_DP_LOG(4u, fn_imu_ctr, 0x1cbu, 0x10400000u, "evenhub_response_imu_ctr_cmd status = %d", status);
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 0x14u;
    msg->seq = seq;
    msg->which = 0x17u;
    evenhub_put_u32(0x04u, status);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                        (uint16_t)stream.bytes_written);
}

/* common_imu_setting_cmd: enable == 1 opens the sensor-hub IMU report at
 * report_freq, anything else closes it. Always returns 0. */
int32_t common_imu_setting_4da720(uint32_t enable, int32_t report_freq)
{
    if (enable == 1u) {
        (void)HUB_Open(EVENHUB_HUB_IMU);
        int32_t param = report_freq;
        (void)audio_hub_parameter_config_4a6e3c(EVENHUB_HUB_IMU, &param);
        EH_DP_LOG(2u, fn_imu_setting, 0x202u, 0x08400000u,
                  "common_imu_setting_cmd imu_report_en = 1, report_frq = %d", report_freq);
    } else {
        (void)HUB_Close(EVENHUB_HUB_IMU);
        EH_DP_LOG(2u, fn_imu_setting, 0x205u, 0x08000000u, "common_imu_setting_cmd imu_report_en = 0");
    }
    return 0;
}
