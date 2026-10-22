/* Sensor hub thread, stock D:\01_workspace\s200_ap510b_iar_git\platform\sensor_hub\sensor_hub.c
 * (log tag "sensor_hub"), native 0x4a6644..0x4a7344; literal pools 0x4a6ecc..0x4a6ee7
 * and 0x4a713c..0x4a743f.
 *
 * Thread "sensor_hub": 8 KiB static stack, priority 0x29 (osPriorityHigh1),
 * thread-manager slot 5 (stop-ack event bit 0x20). Its queue holds 50 eight-byte
 * messages. The 16-bit id selects a row of the routing table at RAM 0x20003688.
 *
 * Function types (HUB_Open/HUB_Close argument, message ids 5/6):
 *   1 head-up detection, 2 compass, 3 "dis" (display), 4 ALS, 5 fifth IMU user
 *   (opened with work mode 0, like head-up). 0 is accepted and does nothing on
 *   open. 6 or more is rejected.
 * IMU work-mode priority: dis (mode 1) > compass (mode 2) > head-up / type 5
 *   (mode 0). When no IMU user is left, the IMU is powered off.
 *
 * Kept local to this directory; promote to include/g2_sensor_hub.h when other
 * units adopt these names. */
#ifndef G2_SENSOR_HUB_H
#define G2_SENSOR_HUB_H

#include <stdint.h>

/* Message ids, routing table RAM 0x20003688 (initialised data). */
enum {
    G2_HUB_MSG_IMU_SET_MODE = 1u,   /* HUB_IMUSetModeHandler, value = work mode 0..4 */
    G2_HUB_MSG_IMU_READ = 2u,       /* hub_imu_register_write -> DRV_IMUReadData(tick) */
    G2_HUB_MSG_IMU_CALIB = 3u,      /* hub_calib_init_wrapper -> HUB_IMUCalibParaInit */
    G2_HUB_MSG_IMU_COLLECT = 4u,    /* HUB_IMUCollectionHandler, value 1 start / 0 stop */
    G2_HUB_MSG_FUNC_OPEN = 5u,      /* HUB_IMUFuncOpenHandler, value = function type */
    G2_HUB_MSG_FUNC_CLOSE = 6u,     /* HUB_IMUFuncCloseHandler, value = function type */
    G2_HUB_MSG_NOP = 7u,            /* hub_empty_hook */
    G2_HUB_MSG_ALS_TIMER = 8u,      /* als_function_34 (DRV_ALSTimerHandler) */
};

enum {
    G2_HUB_FUNC_NONE = 0u,
    G2_HUB_FUNC_HEADUP = 1u,
    G2_HUB_FUNC_COMPASS = 2u,
    G2_HUB_FUNC_DIS = 3u,
    G2_HUB_FUNC_ALS = 4u,
    G2_HUB_FUNC_TYPE5 = 5u,
    G2_HUB_FUNC_COUNT = 6u,
};

/* hub_role_get values (RAM 0x20004526, reset value 3). Role 2 refuses
 * HUB_Open/HUB_Close/HUB_ParameterConfig ("role type is left"). */
enum { G2_HUB_ROLE_LEFT = 2u, G2_HUB_ROLE_RIGHT = 3u };

typedef struct {
    uint16_t id;    /* +0 */
    uint16_t pad;   /* +2 always 0 */
    uint32_t value; /* +4 */
} g2_hub_msg_t;
_Static_assert(sizeof(g2_hub_msg_t) == 8, "stock queue item size");

void HUB_ThreadInit(void);
void HUB_ResourceInit(void);
void hub_thread_terminate(void);
void hub_state_enter(void);
void hub_state_exit(void);
void hub_thread_entry(void *argument);
void HUB_MessageProcesser(const g2_hub_msg_t *msg);
void hub_msg_send_id8(void *argument);
void hub_timer_start(uint32_t ticks);
void hub_timer_stop(void);
void hub_imu_register_write(const g2_hub_msg_t *msg);
void hub_calib_init_wrapper(const g2_hub_msg_t *msg);
void HUB_IMUCollectionHandler(const g2_hub_msg_t *msg);
void HUB_SendMessage(const g2_hub_msg_t *msg);
int32_t hub_msg_send_id1(uint8_t mode);
int32_t hub_msg_send_id4(uint8_t start);
int32_t hub_msg_send_id3(void);
void hub_als_timer_callback(void);
void HUB_IMUSetModeHandler(const g2_hub_msg_t *msg);
void HUB_IMUCalibParaInit(void); /* sensor_hub_calib.c (FPU profile) */
void hub_empty_hook(const g2_hub_msg_t *msg);
void hub_role_init(void);
uint16_t hub_role_get(void);
int32_t HUB_Open(uint8_t func_type);
int32_t HUB_Close(uint8_t func_type);
void HUB_IMUFuncOpenHandler(const g2_hub_msg_t *msg);
void HUB_IMUFuncCloseHandler(const g2_hub_msg_t *msg);

/* Shared log plumbing (stock macro expands inline at every site). */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *path,
                               const char *function, uint32_t line, const char *fmt, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t code, const char *fmt, const char *fmt2, ...); /* 0x43ce9e */

#endif
