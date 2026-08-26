#ifndef OPEN_CFW_IMU_ICM45608_HOST_H
#define OPEN_CFW_IMU_ICM45608_HOST_H

#include <stdint.h>

extern uint64_t host_imu_device_words[12];
extern uint64_t host_imu_ring_words[282];
extern uint64_t host_imu_mode_words[10];
extern int32_t host_imu_accel_offset[3];
extern int32_t host_imu_gyro_offset[3];
extern int32_t host_imu_mag_offset[3];
extern float host_imu_orientation[9];
extern int16_t host_imu_orientation_q14[9];
extern int32_t host_imu_orientation_q30[9];
extern uint32_t host_imu_accel_interval;
extern int32_t host_imu_motion_threshold;
extern uint32_t host_imu_motion_period;
extern int32_t host_imu_heading_period;
extern float host_imu_heading;
extern float host_imu_magnetic[3];
extern float host_imu_orientation_vector[3];
extern uint32_t host_imu_raw_handle;
extern uint32_t host_imu_raw_count;
extern uint32_t host_imu_raw_started;
extern uint8_t host_imu_raw_active;
extern uint32_t host_imu_forward_divisor;
extern float host_imu_latest_result[9];
extern uint8_t host_imu_mode;
extern uint8_t host_imu_aid_enabled;
extern uint8_t host_imu_compass_ready;
extern uint8_t host_imu_compass_reported;
extern uint8_t host_imu_head_up_armed;
extern uint32_t host_imu_state_zero;
extern uint32_t host_imu_state_one;
extern uint32_t host_imu_state_two;
extern uint32_t host_imu_state_three;
extern uint8_t host_imu_odr_accel;
extern uint8_t host_imu_odr_gyro;
extern uint8_t host_imu_odr_index;
extern uint8_t host_imu_feature_enable;
extern uint32_t host_imu_fifo_watermark;
extern uint16_t host_imu_interrupt_period;
extern uint8_t host_imu_i2c_read_data[32];
extern uint8_t host_imu_registers[256];
extern uint8_t host_imu_i2c_last_register;
extern uint8_t host_imu_i2c_last_write[16];
extern uint32_t host_imu_i2c_last_write_size;
extern uint8_t host_imu_fifo_mirror[2048];

#define OPEN_CFW_IMU_DEVICE \
    (*(volatile struct open_cfw_imu_device *)(void *)host_imu_device_words)
#define OPEN_CFW_IMU_RING \
    (*(volatile struct open_cfw_imu_ring *)(void *)host_imu_ring_words)
#define OPEN_CFW_IMU_FIFO_MIRROR host_imu_fifo_mirror
#define OPEN_CFW_IMU_MODES \
    ((const struct open_cfw_imu_mode *)(const void *)host_imu_mode_words)
#define OPEN_CFW_IMU_ACCEL_OFFSET ((volatile int32_t *)host_imu_accel_offset)
#define OPEN_CFW_IMU_GYRO_OFFSET ((volatile int32_t *)host_imu_gyro_offset)
#define OPEN_CFW_IMU_MAG_OFFSET ((volatile int32_t *)host_imu_mag_offset)
#define OPEN_CFW_IMU_ORIENTATION ((volatile float *)host_imu_orientation)
#define OPEN_CFW_IMU_ORIENTATION_Q14 ((volatile int16_t *)host_imu_orientation_q14)
#define OPEN_CFW_IMU_ORIENTATION_Q30 ((volatile int32_t *)host_imu_orientation_q30)
#define OPEN_CFW_IMU_ACCEL_INTERVAL host_imu_accel_interval
#define OPEN_CFW_IMU_MOTION_THRESHOLD host_imu_motion_threshold
#define OPEN_CFW_IMU_MOTION_PERIOD host_imu_motion_period
#define OPEN_CFW_IMU_HEADING_PERIOD host_imu_heading_period
#define OPEN_CFW_IMU_HEADING host_imu_heading
#define OPEN_CFW_IMU_MAGNETIC ((volatile float *)host_imu_magnetic)
#define OPEN_CFW_IMU_ORIENTATION_VECTOR ((volatile float *)host_imu_orientation_vector)
#define OPEN_CFW_IMU_RAW_HANDLE host_imu_raw_handle
#define OPEN_CFW_IMU_RAW_COUNT host_imu_raw_count
#define OPEN_CFW_IMU_RAW_STARTED host_imu_raw_started
#define OPEN_CFW_IMU_RAW_ACTIVE host_imu_raw_active
#define OPEN_CFW_IMU_FORWARD_DIVISOR host_imu_forward_divisor
#define OPEN_CFW_IMU_LATEST_RESULT ((volatile float *)host_imu_latest_result)
#define OPEN_CFW_IMU_MODE host_imu_mode
#define OPEN_CFW_IMU_ODR_ACCEL host_imu_odr_accel
#define OPEN_CFW_IMU_ODR_GYRO host_imu_odr_gyro
#define OPEN_CFW_IMU_ODR_INDEX host_imu_odr_index
#define OPEN_CFW_IMU_FEATURE_ENABLE host_imu_feature_enable
#define OPEN_CFW_IMU_FIFO_WATERMARK host_imu_fifo_watermark
#define OPEN_CFW_IMU_INTERRUPT_PERIOD host_imu_interrupt_period
#define OPEN_CFW_IMU_AID_ENABLED host_imu_aid_enabled
#define OPEN_CFW_IMU_COMPASS_READY host_imu_compass_ready
#define OPEN_CFW_IMU_COMPASS_REPORTED host_imu_compass_reported
#define OPEN_CFW_IMU_HEAD_UP_ARMED host_imu_head_up_armed
#define OPEN_CFW_IMU_STATE_ZERO host_imu_state_zero
#define OPEN_CFW_IMU_STATE_ONE host_imu_state_one
#define OPEN_CFW_IMU_STATE_TWO host_imu_state_two
#define OPEN_CFW_IMU_STATE_THREE host_imu_state_three

void host_imu_reset(void);
void open_cfw_imu_data_parser_callback(const uint8_t *packet);

#endif
