/* EvenHub IMU encoders with float arguments, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_data_parser.c.
 * Native 0x4d9f6e..0x4da078 (evenhub_SendIMUEvent_cmd) and 0x4da6d4..0x4da720
 * (IMU sample forward to the peer side). Hard-float arguments in s0..s2:
 * build with profile g2-apollo-main-3. */
#include <stdint.h>
#include <stddef.h>
#include "evenhub_data_parser_private.h"

#define EVENHUB_VFP __attribute__((pcs("aapcs-vfp")))

extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);

static const char fn_imu_event[] = "evenhub_SendIMUEvent_cmd"; /* ROM 0x76b784 */
static const char none_text[] = "(none)";                      /* ROM 0x78d59c */

static inline __attribute__((always_inline)) void evenhub_put_f32(uint32_t offset, float value)
{
    *(float *)(void *)((uint8_t *)&g2_evenhub_tx_msg_20340b48 + offset) = value;
}

/* Device event, system submessage, event type 8 (IMU data) with the has-IMU
 * flag set and the three axis values. -3 on encode failure, else the notify
 * result. */
EVENHUB_VFP int32_t evenhub_send_imu_event_4d9f6e(float x, float y, float z)
{
    g2_evenhub_tx_msg_t *msg = evenhub_tx_begin();
    msg->cmd = 2u;
    msg->seq = 0u;
    msg->which = 0x0du;
    evenhub_put_u16(EVENHUB_DEV_WHICH_OFF, 3u);
    evenhub_put_u8(EVENHUB_DEV_SYS_IMU_OFF, 1u);
    evenhub_put_u8(EVENHUB_DEV_SYS_EVENT_OFF, 8u);
    evenhub_put_f32(EVENHUB_DEV_SYS_X_OFF, x);
    evenhub_put_f32(EVENHUB_DEV_SYS_Y_OFF, y);
    evenhub_put_f32(EVENHUB_DEV_SYS_Z_OFF, z);
    g2_pb_ostream_t stream;
    if (evenhub_tx_encode(&stream) == 0u) {
        EH_DP_LOG(1u, fn_imu_event, 0xf5u, 0x04400000u, "evenhub protobuf encode failed: %s\n",
                  stream.errmsg != NULL ? stream.errmsg : none_text);
        return -3;
    }
    return (int32_t)Thread_MsgPbNotifyByBle(1u, EVENHUB_APP_ID, g2_evenhub_tx_buffer_203362c4,
                                            (uint16_t)stream.bytes_written);
}

/* Forward one accelerometer sample to the other glasses side over the sync
 * channel: 13-byte packet {1, x, y, z} (raw little-endian floats), app 0xe0,
 * id 0, event 5. */
EVENHUB_VFP void imu_accel_report_send_4da6d4(float x, float y, float z)
{
    uint8_t packet[13];
    packet[0] = 1u;
    (void)audio_queue_copy_bytes(&packet[1], &x, 4u);
    (void)audio_queue_copy_bytes(&packet[5], &y, 4u);
    (void)audio_queue_copy_bytes(&packet[9], &z, 4u);
    (void)audio_sync_send_to_both_ext_464f76(EVENHUB_APP_ID, packet, sizeof packet, 0u, 5u);
}
