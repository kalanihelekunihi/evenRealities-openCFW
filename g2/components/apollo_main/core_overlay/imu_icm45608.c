/*
 * OpenCFW clean-room G2 ICM45608 policy and sample driver.
 *
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * The first-party policy in this file was reconstructed from authenticated
 * linked-object behavior.  The transport boundary follows TDK InvenSense's
 * public ICM456xx driver contract; no historical Even Realities source is
 * present here.  Each selector is compiled as an independent overlay leaf.
 */

#include <stddef.h>
#include <stdint.h>

#ifndef OPEN_CFW_IMU_SELECTOR
#define OPEN_CFW_IMU_SELECTOR 0
#endif

#define OPEN_CFW_IMU_UNUSED __attribute__((unused))

enum {
    OPEN_CFW_IMU_SLOT_COUNT = 20u,
    OPEN_CFW_IMU_SLOT_SIZE = 0x70u,
    OPEN_CFW_IMU_FLAG_ACCEL = 0x01u,
    OPEN_CFW_IMU_FLAG_GYRO = 0x02u,
    OPEN_CFW_IMU_FLAG_MAG = 0x08u,
    OPEN_CFW_IMU_FLAG_FUSION = 0x20u,
    OPEN_CFW_IMU_RAW_LIMIT_MS = 120000u,
    OPEN_CFW_IMU_EVENT_HEAD_UP = 6u,
    OPEN_CFW_IMU_EVENT_HEAD_DOWN = 7u,
    OPEN_CFW_IMU_EVENT_HEADING = 9u,
    OPEN_CFW_IMU_EVENT_COMPASS_READY = 16u,
};

struct open_cfw_imu_filter {
    double b0, b1, b2, a1, a2;
    float x1, x2, y1, y2;
};

struct open_cfw_imu_mode {
    uint8_t features;
    uint8_t reserved[3];
    uint32_t period_us;
    uint32_t fifo_watermark;
    uint32_t interrupt_period;
};

struct open_cfw_imu_device {
    int32_t (*read)(uint8_t, uint8_t *, uint32_t);
    int32_t (*write)(uint8_t, const uint8_t *, uint32_t);
    uint32_t interface_type;
    void (*sleep)(uint32_t);
    uint8_t fifo_frame_size;
    uint8_t endianness_data;
    uint8_t edmp_gaf_mode;
    uint8_t alignment_13[5];
    void (*fifo_callback)(const uint8_t *packet);
    uint8_t advanced_private[44];
};

struct open_cfw_imu_sample {
    uint32_t timestamp;
    uint8_t flags;
    uint8_t reserved_05;
    int16_t accel_raw[3];
    int16_t gyro_raw[3];
    int16_t mag_raw[3];
    int32_t quaternion_q30[4];
    float accel[3];
    float gyro[3];
    float magnetic[3];
    float quaternion[4];
    float euler[3];
    uint8_t reserved_68[4];
    uint8_t compass_valid;
    uint8_t compass_calibrated;
    uint8_t reserved_6e[2];
};

struct open_cfw_imu_ring {
    uint32_t start_timestamp;
    uint32_t first_index;
    uint32_t count;
    struct open_cfw_imu_sample sample[OPEN_CFW_IMU_SLOT_COUNT];
};

struct open_cfw_imu_packet {
    uint8_t header;
    uint8_t reserved_01[5];
    int16_t accel[3];
    int16_t gyro[3];
    uint8_t reserved_12[8];
    uint8_t external_sensor_0[9];
    uint8_t external_sensor_1[6];
};

struct open_cfw_imu_fusion_result {
    int16_t grv_quaternion_q14[4];
    uint8_t grv_quaternion_valid;
    uint8_t reserved_09;
    int16_t gmrv_quaternion_q14[4];
    uint8_t gmrv_quaternion_valid;
    uint8_t reserved_13;
    int16_t gmrv_heading_q11;
    uint8_t gmrv_heading_valid;
    uint8_t reserved_17;
    int16_t rv_quaternion_q14[4];
    uint8_t rv_quaternion_valid;
    uint8_t reserved_21;
    int16_t rv_heading_q11;
    uint8_t rv_heading_valid;
    uint8_t reserved_25;
    int16_t gyro_bias_q12[3];
    uint8_t gyro_bias_valid;
    int8_t gyro_accuracy;
    int8_t stationary;
    uint8_t gyro_flags_valid;
    int16_t raw_magnetic[3];
    uint8_t raw_magnetic_valid;
    uint8_t reserved_37;
    int32_t magnetic_bias_q16[3];
    int8_t magnetic_accuracy;
    int8_t magnetic_anomalies;
    uint8_t magnetic_bias_valid;
    uint8_t high_resolution_gyro[3];
    uint8_t high_resolution_gyro_valid;
    uint8_t reserved_4b;
    uint32_t mrm_state;
    uint8_t mrm_state_valid;
    uint8_t frame_complete;
    uint8_t reserved_52[2];
};

_Static_assert(sizeof(struct open_cfw_imu_sample) == OPEN_CFW_IMU_SLOT_SIZE,
               "IMU sample ABI changed");
_Static_assert(offsetof(struct open_cfw_imu_sample, accel) == 0x28u,
               "IMU acceleration ABI changed");
_Static_assert(offsetof(struct open_cfw_imu_sample, euler) == 0x5cu,
               "IMU Euler ABI changed");
_Static_assert(offsetof(struct open_cfw_imu_ring, sample) == 12u,
               "IMU ring header ABI changed");
_Static_assert(sizeof(struct open_cfw_imu_fusion_result) == 84u,
               "IMU fusion ABI changed");
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(struct open_cfw_imu_device, fifo_frame_size) == 0x10u,
               "ICM45608 FIFO-state ABI changed");
_Static_assert(offsetof(struct open_cfw_imu_device, fifo_callback) == 0x18u,
               "ICM45608 callback ABI changed");
_Static_assert(sizeof(struct open_cfw_imu_device) == 0x48u,
               "ICM45608 device ABI changed");
#endif

#ifndef OPEN_CFW_IMU_DEVICE
#define OPEN_CFW_IMU_DEVICE \
    (*(volatile struct open_cfw_imu_device *)(uintptr_t)0x20073020u)
#endif
#ifndef OPEN_CFW_IMU_RING
#define OPEN_CFW_IMU_RING \
    (*(volatile struct open_cfw_imu_ring *)(uintptr_t)0x200640a0u)
#endif
#ifndef OPEN_CFW_IMU_FIFO_MIRROR
#define OPEN_CFW_IMU_FIFO_MIRROR \
    ((uint8_t *)(uintptr_t)0x20073170u)
#endif
#ifndef OPEN_CFW_IMU_MODES
#define OPEN_CFW_IMU_MODES \
    ((const struct open_cfw_imu_mode *)(uintptr_t)0x20000db0u)
#endif
#ifndef OPEN_CFW_IMU_MODE
#define OPEN_CFW_IMU_MODE (*(volatile uint8_t *)(uintptr_t)0x20074fd1u)
#endif
#ifndef OPEN_CFW_IMU_ODR_ACCEL
#define OPEN_CFW_IMU_ODR_ACCEL (*(volatile uint8_t *)(uintptr_t)0x20074fd6u)
#endif
#ifndef OPEN_CFW_IMU_ODR_GYRO
#define OPEN_CFW_IMU_ODR_GYRO (*(volatile uint8_t *)(uintptr_t)0x20074fd7u)
#endif
#ifndef OPEN_CFW_IMU_ODR_INDEX
#define OPEN_CFW_IMU_ODR_INDEX (*(volatile uint8_t *)(uintptr_t)0x20074fd5u)
#endif
#ifndef OPEN_CFW_IMU_FEATURE_ENABLE
#define OPEN_CFW_IMU_FEATURE_ENABLE (*(volatile uint8_t *)(uintptr_t)0x2000454au)
#endif
#ifndef OPEN_CFW_IMU_FIFO_WATERMARK
#define OPEN_CFW_IMU_FIFO_WATERMARK (*(volatile uint32_t *)(uintptr_t)0x20074670u)
#endif
#ifndef OPEN_CFW_IMU_INTERRUPT_PERIOD
#define OPEN_CFW_IMU_INTERRUPT_PERIOD (*(volatile uint16_t *)(uintptr_t)0x20074f32u)
#endif
#ifndef OPEN_CFW_IMU_ACCEL_OFFSET
#define OPEN_CFW_IMU_ACCEL_OFFSET \
    ((volatile int32_t *)(uintptr_t)0x20072bc8u)
#endif
#ifndef OPEN_CFW_IMU_GYRO_OFFSET
#define OPEN_CFW_IMU_GYRO_OFFSET \
    ((volatile int32_t *)(uintptr_t)0x20074020u)
#endif
#ifndef OPEN_CFW_IMU_MAG_OFFSET
#define OPEN_CFW_IMU_MAG_OFFSET \
    ((volatile int32_t *)(uintptr_t)0x2007402cu)
#endif
#ifndef OPEN_CFW_IMU_ORIENTATION
#define OPEN_CFW_IMU_ORIENTATION \
    ((volatile float *)(uintptr_t)0x20000e00u)
#endif
#ifndef OPEN_CFW_IMU_ORIENTATION_Q14
#define OPEN_CFW_IMU_ORIENTATION_Q14 \
    ((volatile int16_t *)(uintptr_t)0x20000e14u)
#endif
#ifndef OPEN_CFW_IMU_ORIENTATION_Q30
#define OPEN_CFW_IMU_ORIENTATION_Q30 \
    ((volatile int32_t *)(uintptr_t)0x20000e38u)
#endif
#ifndef OPEN_CFW_IMU_ACCEL_INTERVAL
#define OPEN_CFW_IMU_ACCEL_INTERVAL \
    (*(volatile uint32_t *)(uintptr_t)0x20000e60u)
#endif
#ifndef OPEN_CFW_IMU_MOTION_THRESHOLD
#define OPEN_CFW_IMU_MOTION_THRESHOLD \
    (*(volatile int32_t *)(uintptr_t)0x20000e64u)
#endif
#ifndef OPEN_CFW_IMU_MOTION_PERIOD
#define OPEN_CFW_IMU_MOTION_PERIOD \
    (*(volatile uint32_t *)(uintptr_t)0x20000e68u)
#endif
#ifndef OPEN_CFW_IMU_HEADING_PERIOD
#define OPEN_CFW_IMU_HEADING_PERIOD \
    (*(volatile int32_t *)(uintptr_t)0x20000e6cu)
#endif
#ifndef OPEN_CFW_IMU_HEADING
#define OPEN_CFW_IMU_HEADING (*(volatile float *)(uintptr_t)0x2007469cu)
#endif
#ifndef OPEN_CFW_IMU_MAGNETIC
#define OPEN_CFW_IMU_MAGNETIC \
    ((volatile float *)(uintptr_t)0x20074044u)
#endif
#ifndef OPEN_CFW_IMU_ORIENTATION_VECTOR
#define OPEN_CFW_IMU_ORIENTATION_VECTOR \
    ((volatile float *)(uintptr_t)0x20074050u)
#endif
#ifndef OPEN_CFW_IMU_RAW_HANDLE
#define OPEN_CFW_IMU_RAW_HANDLE (*(volatile uint32_t *)(uintptr_t)0x20074684u)
#endif
#ifndef OPEN_CFW_IMU_RAW_COUNT
#define OPEN_CFW_IMU_RAW_COUNT (*(volatile uint32_t *)(uintptr_t)0x20074688u)
#endif
#ifndef OPEN_CFW_IMU_RAW_STARTED
#define OPEN_CFW_IMU_RAW_STARTED (*(volatile uint32_t *)(uintptr_t)0x2007468cu)
#endif
#ifndef OPEN_CFW_IMU_RAW_ACTIVE
#define OPEN_CFW_IMU_RAW_ACTIVE (*(volatile uint8_t *)(uintptr_t)0x20074fddu)
#endif
#ifndef OPEN_CFW_IMU_FORWARD_DIVISOR
#define OPEN_CFW_IMU_FORWARD_DIVISOR \
    (*(volatile uint32_t *)(uintptr_t)0x20074698u)
#endif
#ifndef OPEN_CFW_IMU_LATEST_RESULT
#define OPEN_CFW_IMU_LATEST_RESULT \
    ((volatile float *)(uintptr_t)0x20073894u)
#endif
#ifndef OPEN_CFW_IMU_AID_ENABLED
#define OPEN_CFW_IMU_AID_ENABLED (*(volatile uint8_t *)(uintptr_t)0x20074fd8u)
#endif
#ifndef OPEN_CFW_IMU_COMPASS_READY
#define OPEN_CFW_IMU_COMPASS_READY (*(volatile uint8_t *)(uintptr_t)0x20074fdcu)
#endif
#ifndef OPEN_CFW_IMU_COMPASS_REPORTED
#define OPEN_CFW_IMU_COMPASS_REPORTED (*(volatile uint8_t *)(uintptr_t)0x20074fdfu)
#endif
#ifndef OPEN_CFW_IMU_HEAD_UP_ARMED
#define OPEN_CFW_IMU_HEAD_UP_ARMED (*(volatile uint8_t *)(uintptr_t)0x20074fdeu)
#endif
#ifndef OPEN_CFW_IMU_STATE_ZERO
#define OPEN_CFW_IMU_STATE_ZERO (*(volatile uint32_t *)(uintptr_t)0x20074674u)
#endif
#ifndef OPEN_CFW_IMU_STATE_ONE
#define OPEN_CFW_IMU_STATE_ONE (*(volatile uint32_t *)(uintptr_t)0x20074678u)
#endif
#ifndef OPEN_CFW_IMU_STATE_TWO
#define OPEN_CFW_IMU_STATE_TWO (*(volatile uint32_t *)(uintptr_t)0x2007467cu)
#endif
#ifndef OPEN_CFW_IMU_STATE_THREE
#define OPEN_CFW_IMU_STATE_THREE (*(volatile uint32_t *)(uintptr_t)0x20074680u)
#endif

int32_t open_cfw_retained_imu_i2c_read(
    uint32_t bus, uint32_t address, const void *register_data,
    uint32_t register_size, void *data, uint32_t size);
int32_t open_cfw_retained_imu_i2c_write(
    uint32_t bus, uint32_t address, const void *register_data,
    uint32_t register_size, const void *data, uint32_t size);
void open_cfw_retained_imu_power(uint32_t sensor, uint32_t enabled);
void open_cfw_retained_imu_delay(uint32_t ticks);
uint32_t open_cfw_retained_imu_tick(void);
uint16_t open_cfw_retained_imu_event_source(void);
int32_t open_cfw_retained_imu_event_available(void);
void open_cfw_retained_imu_event_dispatch(
    uint16_t source, uint32_t event, int32_t value, uint32_t flags);
void open_cfw_retained_imu_forward(float x, float y, float z);
uint32_t open_cfw_retained_imu_raw_open(const char *path, const char *mode);
int32_t open_cfw_retained_imu_raw_write(const void *data, uint32_t item_size,
                                        uint32_t count, uint32_t handle);
int32_t open_cfw_retained_imu_raw_close(uint32_t handle);
void open_cfw_retained_imu_aid_changed(void);

int32_t open_cfw_icm45608_tdk_configure(
    void *, uint8_t, uint8_t, uint16_t, uint32_t, uint8_t, uint8_t,
    const int8_t[9]);
int32_t open_cfw_icm45608_tdk_read_fifo(
    void *, uint8_t *, uint32_t, uint16_t *);
int32_t open_cfw_icm45608_tdk_parse_fifo(
    void *, const uint8_t *, uint16_t);
int32_t open_cfw_icm45608_tdk_poll_registers(void *);
int32_t open_cfw_icm45608_tdk_read_extended_events(
    void *, uint8_t *, uint8_t *, uint8_t *);
int32_t open_cfw_icm45608_tdk_decode_gaf(
    void *, const uint8_t[9], const uint8_t[6],
    struct open_cfw_imu_fusion_result *);
int32_t open_cfw_icm45608_tdk_mag_who_am_i(void *, uint8_t *);

/* Cross-leaf ABI.  Production builds compile one selector per function. */
int32_t open_cfw_imu_bus_read(uint8_t, uint8_t *, uint32_t);
int32_t open_cfw_imu_bus_write(uint8_t, const uint8_t *, uint32_t);
void open_cfw_imu_filter_init(struct open_cfw_imu_filter *);
float open_cfw_imu_filter_update(float, struct open_cfw_imu_filter *);
int32_t open_cfw_imu_device_context_init(void);
int32_t open_cfw_imu_apply_odr_config(const struct open_cfw_imu_mode *);
int32_t open_cfw_imu_set_sensor_parameters(const struct open_cfw_imu_mode *);
void open_cfw_imu_sensor_power_cycle(void);
void open_cfw_imu_sensor_reset_line(void);
void open_cfw_imu_delay_callback(uint32_t);
int32_t open_cfw_imu_initialize(uint8_t);
int32_t open_cfw_imu_set_orientation_matrix(uint32_t, uint32_t, const float *);
void open_cfw_imu_aid_state_print(uint8_t, uint8_t);
uint8_t open_cfw_imu_get_aid_enabled(void);
int32_t open_cfw_imu_aid_state_update(uint8_t, uint8_t);
int32_t open_cfw_imu_read_data(uint32_t);
int32_t open_cfw_imu_set_motion_threshold(int32_t);
int32_t open_cfw_imu_set_motion_period(uint32_t, int32_t);
int32_t open_cfw_imu_emit_event(uint32_t, int32_t);
int32_t open_cfw_imu_check_head_up_event(void);
int32_t open_cfw_imu_normalize_heading(int32_t);
int32_t open_cfw_imu_check_compass_event(void);
void open_cfw_imu_noop_sample_callback(void);
int32_t open_cfw_imu_accel_config(uint32_t);
void open_cfw_imu_forward_periodic_sample(void);
int32_t open_cfw_imu_postprocess_samples(void);
void open_cfw_imu_transform_vector(float[3], const float[9]);
void open_cfw_imu_fixed_vector_to_float(const int32_t *, float *, uint8_t, uint8_t);
int32_t open_cfw_imu_quaternion_to_euler(const float[4], float[3]);
void open_cfw_imu_data_parser_callback(const uint8_t *);
const float *open_cfw_imu_get_latest_complete_sample(void);
void open_cfw_imu_set_heading(float);
void open_cfw_imu_set_magnetic_vector(const float[3]);
int32_t open_cfw_imu_get_heading_degrees(void);
float open_cfw_imu_get_heading_float(void);
const float *open_cfw_imu_get_magnetic_vector(void);
const float *open_cfw_imu_get_orientation_vector(void);
int32_t open_cfw_imu_build_raw_csv_path(char *, uint32_t);
int32_t open_cfw_imu_write_csv_header(void);
int32_t open_cfw_imu_write_csv_data_line(uint32_t, const float[3],
    const float[3], const float[3], const float[3], uint8_t, uint8_t, uint8_t);
int32_t open_cfw_imu_start_raw_data_collection(void);
int32_t open_cfw_imu_stop_raw_data_collection(void);
int32_t open_cfw_imu_save_raw_data_to_csv(void);
int32_t open_cfw_imu_read_who_am_i(uint32_t *);
int32_t open_cfw_mag_read_who_am_i(uint32_t *);
uint32_t open_cfw_imu_get_state_zero(void);
uint32_t open_cfw_imu_get_state_one(void);
uint32_t open_cfw_imu_get_state_two(void);
uint32_t open_cfw_imu_get_state_three(void);
void open_cfw_imu_set_state_zero(uint32_t);
void open_cfw_imu_set_state_one(uint32_t);
void open_cfw_imu_set_state_two(uint32_t);
uint8_t open_cfw_imu_get_compass_ready(void);
void open_cfw_imu_set_state_three(uint32_t);

static OPEN_CFW_IMU_UNUSED void open_cfw_imu_zero(void *destination,
                                                   uint32_t size)
{
    uint8_t *bytes = (uint8_t *)destination;
    while (size-- != 0u) {
        *bytes++ = 0u;
    }
}

static OPEN_CFW_IMU_UNUSED float open_cfw_imu_abs(float value)
{
    return value < 0.0f ? -value : value;
}

static OPEN_CFW_IMU_UNUSED float open_cfw_imu_sqrt(float value)
{
    float estimate;
    uint32_t index;
    if (value <= 0.0f) {
        return 0.0f;
    }
    estimate = value > 1.0f ? value : 1.0f;
    for (index = 0u; index < 8u; ++index) {
        estimate = 0.5f * (estimate + value / estimate);
    }
    return estimate;
}

static OPEN_CFW_IMU_UNUSED float open_cfw_imu_atan(float value)
{
    const float quarter_pi = 0.78539816339f;
    const float three_quarter_pi = 2.35619449019f;
    float absolute = open_cfw_imu_abs(value);
    if (absolute <= 1.0f) {
        return value * (quarter_pi + 0.273f * (1.0f - absolute));
    }
    return (value > 0.0f ? three_quarter_pi : -three_quarter_pi) -
           value / (value * value + 0.28f);
}

static OPEN_CFW_IMU_UNUSED float open_cfw_imu_atan2(float y, float x)
{
    const float pi = 3.14159265359f;
    if (x > 0.0f) {
        return open_cfw_imu_atan(y / x);
    }
    if (x < 0.0f) {
        return open_cfw_imu_atan(y / x) + (y >= 0.0f ? pi : -pi);
    }
    if (y > 0.0f) {
        return 0.5f * pi;
    }
    if (y < 0.0f) {
        return -0.5f * pi;
    }
    return 0.0f;
}

static OPEN_CFW_IMU_UNUSED int32_t open_cfw_imu_round(float value)
{
    return value >= 0.0f ? (int32_t)(value + 0.5f)
                         : (int32_t)(value - 0.5f);
}

static OPEN_CFW_IMU_UNUSED int16_t open_cfw_imu_read_i16(const uint8_t *data)
{
    return (int16_t)((uint16_t)data[0] | ((uint16_t)data[1] << 8));
}

static OPEN_CFW_IMU_UNUSED __attribute__((always_inline)) uint32_t
open_cfw_imu_append_char(char *data, uint32_t capacity, uint32_t offset, char value)
{
    if (offset < capacity) data[offset] = value;
    return offset + 1u;
}

static OPEN_CFW_IMU_UNUSED __attribute__((always_inline)) uint32_t
open_cfw_imu_append_u32(char *data, uint32_t capacity, uint32_t offset,
                        uint32_t value)
{
    char reverse[10]; uint32_t count = 0u;
    do { reverse[count++] = (char)('0' + value % 10u); value /= 10u; }
    while (value != 0u && count < sizeof(reverse));
    while (count != 0u) offset = open_cfw_imu_append_char(
        data, capacity, offset, reverse[--count]);
    return offset;
}

static OPEN_CFW_IMU_UNUSED __attribute__((always_inline)) uint32_t
open_cfw_imu_append_float(char *data, uint32_t capacity, uint32_t offset,
                          float value)
{
    int32_t scaled = open_cfw_imu_round(value * 1000.0f);
    uint32_t magnitude;
    if (scaled < 0) {
        offset = open_cfw_imu_append_char(data, capacity, offset, '-');
        magnitude = (uint32_t)(-(scaled + 1)) + 1u;
    } else {
        magnitude = (uint32_t)scaled;
    }
    offset = open_cfw_imu_append_u32(data, capacity, offset, magnitude / 1000u);
    offset = open_cfw_imu_append_char(data, capacity, offset, '.');
    offset = open_cfw_imu_append_char(data, capacity, offset,
                                      (char)('0' + (magnitude / 100u) % 10u));
    offset = open_cfw_imu_append_char(data, capacity, offset,
                                      (char)('0' + (magnitude / 10u) % 10u));
    return open_cfw_imu_append_char(data, capacity, offset,
                                    (char)('0' + magnitude % 10u));
}

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 1
__attribute__((noinline)) int32_t open_cfw_imu_bus_read(
    uint8_t register_address, uint8_t *data, uint32_t size)
{
    return open_cfw_retained_imu_i2c_read(
               4u, 0x69u, &register_address, 1u, data, size) == 0
               ? 0 : -1;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 2
__attribute__((noinline)) int32_t open_cfw_imu_bus_write(
    uint8_t register_address, const uint8_t *data, uint32_t size)
{
    return open_cfw_retained_imu_i2c_write(
               4u, 0x69u, &register_address, 1u, data, size) == 0
               ? 0 : -1;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 3
__attribute__((noinline)) void open_cfw_imu_filter_init(
    struct open_cfw_imu_filter *filter)
{
    if (filter == NULL) return;
    filter->b0 = 0.0001298499;
    filter->b1 = 0.0002596998;
    filter->b2 = 0.0001298499;
    filter->a1 = -1.967376;
    filter->a2 = 0.9678954;
    filter->x1 = filter->x2 = filter->y1 = filter->y2 = 0.0f;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 4
__attribute__((noinline)) float open_cfw_imu_filter_update(
    float value, struct open_cfw_imu_filter *filter)
{
    float result;
    if (filter == NULL) return value;
    result = (float)((double)value * filter->b0 +
                     (double)filter->x1 * filter->b1 +
                     (double)filter->x2 * filter->b2 -
                     (double)filter->y1 * filter->a1 -
                     (double)filter->y2 * filter->a2);
    filter->x2 = filter->x1; filter->x1 = value;
    filter->y2 = filter->y1; filter->y1 = result;
    return result;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 5
static int32_t open_cfw_imu_source_soft_reset(void)
{
    uint8_t interface_override;
    uint8_t drive_configuration;
    uint8_t reset = 0x02u;
    uint8_t interrupt_status;
    int32_t status = 0;

    status |= open_cfw_imu_bus_read(0x2du, &interface_override, 1u);
    status |= open_cfw_imu_bus_read(0x32u, &drive_configuration, 1u);
    status |= open_cfw_imu_bus_write(0x7fu, &reset, 1u);
    open_cfw_imu_delay_callback(1000u);
    status |= open_cfw_imu_bus_write(0x32u, &drive_configuration, 1u);
    status |= open_cfw_imu_bus_write(0x2du, &interface_override, 1u);
    status |= open_cfw_imu_bus_read(0x19u, &interrupt_status, 1u);
    if ((interrupt_status & 0x80u) == 0u)
        return -1;
    return status;
}

__attribute__((noinline)) int32_t open_cfw_imu_device_context_init(void)
{
    uint8_t who_am_i;
    uint8_t interrupt_pin;
    uint8_t fsync_configuration;
    uint32_t index;
    int32_t status = 0;

    OPEN_CFW_IMU_DEVICE.read = open_cfw_imu_bus_read;
    OPEN_CFW_IMU_DEVICE.write = open_cfw_imu_bus_write;
    OPEN_CFW_IMU_DEVICE.interface_type = 0u;
    OPEN_CFW_IMU_DEVICE.sleep = open_cfw_imu_delay_callback;
    OPEN_CFW_IMU_DEVICE.fifo_callback = open_cfw_imu_data_parser_callback;

    open_cfw_imu_delay_callback(3000u);
    status |= open_cfw_imu_bus_read(0x72u, &who_am_i, 1u);
    if (status != 0 || who_am_i != 0x81u)
        return -1;
    status |= open_cfw_imu_source_soft_reset();

    OPEN_CFW_IMU_DEVICE.fifo_frame_size = 0u;
    OPEN_CFW_IMU_DEVICE.endianness_data = 0u;
    OPEN_CFW_IMU_DEVICE.edmp_gaf_mode = 0u;
    OPEN_CFW_IMU_DEVICE.advanced_private[0] = 0u;
    OPEN_CFW_IMU_DEVICE.advanced_private[1] = 0u;
    for (index = 2u; index < 16u; index += 2u) {
        OPEN_CFW_IMU_DEVICE.advanced_private[index] = 0u;
        OPEN_CFW_IMU_DEVICE.advanced_private[index + 1u] = 0x80u;
    }
    OPEN_CFW_IMU_DEVICE.advanced_private[16] = 0u;
    OPEN_CFW_IMU_DEVICE.advanced_private[17] = 0u;
    OPEN_CFW_IMU_DEVICE.advanced_private[18] = 0u;
    status |= open_cfw_imu_bus_read(0x24u, &fsync_configuration, 1u);
    OPEN_CFW_IMU_DEVICE.advanced_private[19] =
        (uint8_t)(fsync_configuration & 0x07u);

    status |= open_cfw_imu_bus_read(0x18u, &interrupt_pin, 1u);
    interrupt_pin = (uint8_t)((interrupt_pin & 0xf8u) | 0x01u);
    status |= open_cfw_imu_bus_write(0x18u, &interrupt_pin, 1u);
    return status;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 6
__attribute__((noinline)) int32_t open_cfw_imu_apply_odr_config(
    const struct open_cfw_imu_mode *mode)
{
    uint8_t odr;
    if (mode == NULL) return -1;
    switch (mode->period_us) {
    case 1000u: odr = 6u; break;
    case 2500u: odr = 7u; break;
    case 5000u: odr = 8u; break;
    case 10000u: odr = 9u; break;
    case 20000u: odr = 10u; break;
    case 40000u: odr = 11u; break;
    default: return -1;
    }
    OPEN_CFW_IMU_ODR_ACCEL = odr;
    OPEN_CFW_IMU_ODR_GYRO = odr;
    OPEN_CFW_IMU_ODR_INDEX = (uint8_t)(11u - odr);
    OPEN_CFW_IMU_FEATURE_ENABLE = (uint8_t)((mode->features >> 1) & 1u);
    OPEN_CFW_IMU_FIFO_WATERMARK = mode->fifo_watermark;
    OPEN_CFW_IMU_INTERRUPT_PERIOD = (uint16_t)mode->interrupt_period;
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 7
__attribute__((noinline)) int32_t open_cfw_imu_set_sensor_parameters(
    const struct open_cfw_imu_mode *mode)
{
    int8_t mounting_matrix[9];
    uint8_t odr;
    uint32_t index;
    if (mode == NULL) return -1;
    switch (mode->period_us) {
    case 1000u: odr = 6u; break;
    case 2500u: odr = 7u; break;
    case 5000u: odr = 8u; break;
    case 10000u: odr = 9u; break;
    case 20000u: odr = 10u; break;
    case 40000u: odr = 11u; break;
    default: return -1;
    }
    if (mode->fifo_watermark == 0u || mode->fifo_watermark > 0xffffu)
        return -1;
    for (index = 0u; index < 9u; ++index) {
        int16_t value = OPEN_CFW_IMU_ORIENTATION_Q14[index];
        mounting_matrix[index] =
            value > 8192 ? 1 : value < -8192 ? -1 : 0;
    }
    return open_cfw_icm45608_tdk_configure(
        (void *)&OPEN_CFW_IMU_DEVICE, odr, odr,
        (uint16_t)mode->fifo_watermark, mode->period_us,
        (uint8_t)((mode->features >> 1) & 1u),
        (uint8_t)(mode->features & 1u), mounting_matrix);
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 8
__attribute__((noinline)) void open_cfw_imu_sensor_power_cycle(void)
{
    open_cfw_retained_imu_power(1u, 0u);
    open_cfw_retained_imu_delay(100u);
    open_cfw_retained_imu_power(1u, 1u);
    open_cfw_retained_imu_delay(5u);
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 9
__attribute__((noinline)) void open_cfw_imu_sensor_reset_line(void)
{
    open_cfw_retained_imu_power(1u, 0u);
}
#endif

/* Source-owned Thumb callback adapter for the vendor context function table. */
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 54
__attribute__((noinline)) void open_cfw_imu_delay_callback(uint32_t ticks)
{
    open_cfw_retained_imu_delay(ticks);
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 10
__attribute__((noinline)) int32_t open_cfw_imu_initialize(uint8_t mode)
{
    int32_t status;
    if (mode >= 5u) return -1;
    open_cfw_imu_sensor_power_cycle();
    status = open_cfw_imu_device_context_init();
    status |= open_cfw_imu_apply_odr_config(&OPEN_CFW_IMU_MODES[mode]);
    status |= open_cfw_imu_set_sensor_parameters(&OPEN_CFW_IMU_MODES[mode]);
    if (status == 0) OPEN_CFW_IMU_MODE = mode;
    return status;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 11
__attribute__((noinline)) int32_t open_cfw_imu_set_orientation_matrix(
    uint32_t first, uint32_t second, const float *matrix)
{
    uint32_t index;
    (void)first; (void)second;
    if (matrix == NULL) return -1;
    for (index = 0u; index < 9u; ++index) {
        float value = matrix[index];
        OPEN_CFW_IMU_ORIENTATION[index] = value;
        OPEN_CFW_IMU_ORIENTATION_Q14[index] =
            (int16_t)open_cfw_imu_round(value * 16384.0f);
        OPEN_CFW_IMU_ORIENTATION_Q30[index] = open_cfw_imu_round(
            ((index % 3u) == 2u ? value : -value) * 1073741824.0f);
    }
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 12
__attribute__((noinline)) void open_cfw_imu_aid_state_print(
    uint8_t state, uint8_t active)
{
    (void)state; (void)active;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 13
__attribute__((noinline)) uint8_t open_cfw_imu_get_aid_enabled(void)
{
    return OPEN_CFW_IMU_AID_ENABLED;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 14
__attribute__((noinline)) int32_t open_cfw_imu_aid_state_update(
    uint8_t first, uint8_t second)
{
    uint8_t enabled = (uint8_t)(first == 6u && second == 6u);
    if (OPEN_CFW_IMU_AID_ENABLED != enabled) {
        OPEN_CFW_IMU_AID_ENABLED = enabled;
        open_cfw_retained_imu_aid_changed();
    }
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 15
__attribute__((noinline)) int32_t open_cfw_imu_read_data(uint32_t tick)
{
    uint16_t frame_count = 0u;
    uint8_t extended_events = 0u;
    uint8_t aid_human = 0u;
    uint8_t aid_device = 0u;
    int32_t status;
    OPEN_CFW_IMU_RING.start_timestamp = tick;
    OPEN_CFW_IMU_RING.first_index = OPEN_CFW_IMU_RING.count;
    status = open_cfw_icm45608_tdk_read_fifo(
        (void *)&OPEN_CFW_IMU_DEVICE, OPEN_CFW_IMU_FIFO_MIRROR,
        2048u, &frame_count);
    if (status != 0)
        return status;
    if (frame_count != 0u)
        status = open_cfw_icm45608_tdk_parse_fifo(
            (void *)&OPEN_CFW_IMU_DEVICE, OPEN_CFW_IMU_FIFO_MIRROR,
            frame_count);
    else
        status = open_cfw_icm45608_tdk_poll_registers(
            (void *)&OPEN_CFW_IMU_DEVICE);
    if (status != 0)
        return status;
    status = open_cfw_icm45608_tdk_read_extended_events(
        (void *)&OPEN_CFW_IMU_DEVICE, &extended_events, &aid_human,
        &aid_device);
    if (status != 0)
        return status;
    if ((extended_events & 0x0cu) != 0u)
        status |= open_cfw_imu_aid_state_update(aid_human, aid_device);
    if ((extended_events & 0x01u) != 0u)
        status |= open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_HEAD_UP, 1);
    if ((extended_events & 0x02u) != 0u)
        status |= open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_HEAD_DOWN, 1);
    if (status != 0)
        return status;
    return open_cfw_imu_postprocess_samples();
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 16
__attribute__((noinline)) int32_t open_cfw_imu_set_motion_threshold(
    int32_t value)
{
    OPEN_CFW_IMU_MOTION_THRESHOLD = value;
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 17
__attribute__((noinline)) int32_t open_cfw_imu_set_motion_period(
    uint32_t period, int32_t heading_delta)
{
    OPEN_CFW_IMU_MOTION_PERIOD = period;
    OPEN_CFW_IMU_HEADING_PERIOD = heading_delta;
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 18
__attribute__((noinline)) int32_t open_cfw_imu_emit_event(
    uint32_t event, int32_t value)
{
    if (open_cfw_retained_imu_event_available() != 0)
        open_cfw_retained_imu_event_dispatch(
            open_cfw_retained_imu_event_source(), event, value, 0u);
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 19
__attribute__((noinline)) int32_t open_cfw_imu_check_head_up_event(void)
{
    uint32_t index;
    for (index = 0u; index < OPEN_CFW_IMU_RING.count; ++index) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[index];
        if ((sample->flags & OPEN_CFW_IMU_FLAG_FUSION) == 0u) continue;
        if (sample->euler[2] >= (float)OPEN_CFW_IMU_MOTION_THRESHOLD &&
            OPEN_CFW_IMU_HEAD_UP_ARMED != 0u) {
            OPEN_CFW_IMU_HEAD_UP_ARMED = 0u;
            return open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_HEAD_UP, 0);
        }
        if (sample->euler[2] < (float)(OPEN_CFW_IMU_MOTION_THRESHOLD - 20) &&
            OPEN_CFW_IMU_HEAD_UP_ARMED == 0u) {
            OPEN_CFW_IMU_HEAD_UP_ARMED = 1u;
            return open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_HEAD_DOWN, 0);
        }
    }
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 20
__attribute__((noinline)) int32_t open_cfw_imu_normalize_heading(int32_t value)
{
    value %= 360;
    return value < 0 ? value + 360 : value;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 21
__attribute__((noinline)) int32_t open_cfw_imu_check_compass_event(void)
{
    uint32_t index;
    int32_t heading = 0;
    if (OPEN_CFW_IMU_COMPASS_REPORTED == 0u && OPEN_CFW_IMU_COMPASS_READY != 0u) {
        OPEN_CFW_IMU_COMPASS_REPORTED = 1u;
        (void)open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_COMPASS_READY, 1);
    } else if (OPEN_CFW_IMU_COMPASS_READY == 0u) {
        OPEN_CFW_IMU_COMPASS_REPORTED = 0u;
    }
    for (index = OPEN_CFW_IMU_RING.count; index != 0u; --index) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[index - 1u];
        if ((sample->flags & OPEN_CFW_IMU_FLAG_FUSION) != 0u) {
            heading = open_cfw_imu_normalize_heading((int32_t)sample->euler[2]);
            break;
        }
    }
    if (open_cfw_imu_abs((float)heading - OPEN_CFW_IMU_HEADING) >
        (float)OPEN_CFW_IMU_HEADING_PERIOD) {
        OPEN_CFW_IMU_HEADING = (float)heading;
        return open_cfw_imu_emit_event(OPEN_CFW_IMU_EVENT_HEADING, heading);
    }
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 22
__attribute__((noinline)) void open_cfw_imu_noop_sample_callback(void) {}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 23
__attribute__((noinline)) int32_t open_cfw_imu_accel_config(uint32_t interval)
{
    if (interval < 100u || interval > 4999u) return -1;
    OPEN_CFW_IMU_ACCEL_INTERVAL = interval;
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 24
__attribute__((noinline)) void open_cfw_imu_forward_periodic_sample(void)
{
    uint32_t count = OPEN_CFW_IMU_RING.count;
    if (count == 0u) return;
    if (++OPEN_CFW_IMU_FORWARD_DIVISOR >= (OPEN_CFW_IMU_ACCEL_INTERVAL / 100u)) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[count - 1u];
        OPEN_CFW_IMU_FORWARD_DIVISOR = 0u;
        open_cfw_retained_imu_forward(sample->accel[0], sample->accel[1], sample->accel[2]);
    }
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 25
__attribute__((noinline)) int32_t open_cfw_imu_postprocess_samples(void)
{
    uint32_t index;
    if (OPEN_CFW_IMU_MODE == 4u) return 0;
    for (index = 0u; index < OPEN_CFW_IMU_RING.count; ++index) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[index];
        if ((sample->flags & OPEN_CFW_IMU_FLAG_FUSION) != 0u) {
            sample->euler[2] = (float)open_cfw_imu_normalize_heading(
                open_cfw_imu_round(sample->euler[2]));
            open_cfw_imu_set_heading(sample->euler[0]);
            open_cfw_imu_set_magnetic_vector((const float *)sample->euler);
        }
        if ((sample->flags & OPEN_CFW_IMU_FLAG_MAG) != 0u)
            open_cfw_imu_transform_vector((float *)sample->magnetic,
                                          (const float *)OPEN_CFW_IMU_ORIENTATION);
        open_cfw_imu_transform_vector((float *)sample->accel,
                                      (const float *)OPEN_CFW_IMU_ORIENTATION);
        open_cfw_imu_transform_vector((float *)sample->gyro,
                                      (const float *)OPEN_CFW_IMU_ORIENTATION);
    }
    (void)open_cfw_imu_save_raw_data_to_csv();
    if (OPEN_CFW_IMU_STATE_ZERO == 1u) (void)open_cfw_imu_check_head_up_event();
    if (OPEN_CFW_IMU_STATE_ONE == 1u) (void)open_cfw_imu_check_compass_event();
    if (OPEN_CFW_IMU_STATE_THREE == 1u) open_cfw_imu_forward_periodic_sample();
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 26
__attribute__((noinline)) void open_cfw_imu_transform_vector(
    float vector[3], const float matrix[9])
{
    float result[3]; uint32_t row;
    if (vector == NULL || matrix == NULL) return;
    for (row = 0u; row < 3u; ++row)
        result[row] = vector[0] * matrix[row * 3u] +
                      vector[1] * matrix[row * 3u + 1u] +
                      vector[2] * matrix[row * 3u + 2u];
    vector[0] = result[0]; vector[1] = result[1]; vector[2] = result[2];
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 27
__attribute__((noinline)) void open_cfw_imu_fixed_vector_to_float(
    const int32_t *input, float *output, uint8_t fractional_bits, uint8_t count)
{
    uint32_t index; float divisor = (float)(1u << (fractional_bits & 31u));
    if (input == NULL || output == NULL) return;
    for (index = 0u; index < count; ++index) output[index] = (float)input[index] / divisor;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 28
__attribute__((noinline)) int32_t open_cfw_imu_quaternion_to_euler(
    const float quaternion[4], float euler[3])
{
    const float degrees = 57.2957795131f;
    float w, x, y, z, sin_pitch;
    if (quaternion == NULL || euler == NULL) return -1;
    w = quaternion[0]; x = quaternion[1]; y = quaternion[2]; z = quaternion[3];
    euler[0] = open_cfw_imu_atan2(-2.0f * (y * x + z * w),
                                  1.0f - 2.0f * (y * y + z * z)) * degrees;
    euler[1] = open_cfw_imu_atan2(-2.0f * (z * y + x * w),
                                  1.0f - 2.0f * (x * x + y * y)) * degrees;
    sin_pitch = -2.0f * (z * x - y * w);
    if (sin_pitch > 1.0f) sin_pitch = 1.0f;
    if (sin_pitch < -1.0f) sin_pitch = -1.0f;
    euler[2] = open_cfw_imu_atan2(sin_pitch,
        open_cfw_imu_sqrt(1.0f - sin_pitch * sin_pitch)) * degrees;
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 29
__attribute__((noinline)) void open_cfw_imu_data_parser_callback(const uint8_t *packet_bytes)
{
    const struct open_cfw_imu_packet *packet =
        (const struct open_cfw_imu_packet *)packet_bytes;
    volatile struct open_cfw_imu_sample *sample;
    struct open_cfw_imu_fusion_result fusion;
    int32_t vector[4]; uint32_t index;
    if (packet == NULL || OPEN_CFW_IMU_RING.count >= OPEN_CFW_IMU_SLOT_COUNT) return;
    index = OPEN_CFW_IMU_RING.count;
    sample = &OPEN_CFW_IMU_RING.sample[index];
    open_cfw_imu_zero((void *)sample, sizeof(*sample));
    sample->timestamp = OPEN_CFW_IMU_RING.start_timestamp +
        (index - OPEN_CFW_IMU_RING.first_index) *
        (OPEN_CFW_IMU_MODES[OPEN_CFW_IMU_MODE].period_us / 1000u);
    if ((packet->header & 1u) != 0u) {
        for (index = 0u; index < 3u; ++index) {
            sample->accel_raw[index] = packet->accel[index];
            vector[index] = (int32_t)packet->accel[index] * 8 - OPEN_CFW_IMU_ACCEL_OFFSET[index];
        }
        open_cfw_imu_fixed_vector_to_float(vector, (float *)sample->accel, 16u, 3u);
        sample->flags |= OPEN_CFW_IMU_FLAG_ACCEL;
    }
    if ((packet->header & 2u) != 0u) {
        for (index = 0u; index < 3u; ++index) {
            sample->gyro_raw[index] = packet->gyro[index];
            vector[index] = (int32_t)packet->gyro[index] * 4000 - OPEN_CFW_IMU_GYRO_OFFSET[index];
        }
        open_cfw_imu_fixed_vector_to_float(vector, (float *)sample->gyro, 16u, 3u);
        sample->flags |= OPEN_CFW_IMU_FLAG_GYRO;
    }
    open_cfw_imu_zero(&fusion, sizeof(fusion));
    if ((packet->header & 0x30u) == 0x30u &&
        open_cfw_icm45608_tdk_decode_gaf((void *)&OPEN_CFW_IMU_DEVICE,
            packet->external_sensor_0, packet->external_sensor_1, &fusion) == 0 &&
        fusion.frame_complete != 0u) {
        if (fusion.raw_magnetic_valid != 0u) {
            for (index = 0u; index < 3u; ++index) {
                sample->mag_raw[index] = fusion.raw_magnetic[index];
                vector[index] = (int32_t)fusion.raw_magnetic[index] *
                                    0x1333 - OPEN_CFW_IMU_MAG_OFFSET[index];
            }
            open_cfw_imu_fixed_vector_to_float(vector, (float *)sample->magnetic, 16u, 3u);
            sample->flags |= OPEN_CFW_IMU_FLAG_MAG;
        }
        if (fusion.grv_quaternion_valid != 0u) {
            for (index = 0u; index < 4u; ++index)
                sample->quaternion_q30[index] =
                    (int32_t)fusion.grv_quaternion_q14[index] << 16;
            open_cfw_imu_fixed_vector_to_float((const int32_t *)sample->quaternion_q30,
                                               (float *)sample->quaternion, 30u, 4u);
            (void)open_cfw_imu_quaternion_to_euler((const float *)sample->quaternion,
                                                  (float *)sample->euler);
            { float first = sample->euler[0]; sample->euler[0] = sample->euler[1];
              sample->euler[1] = -sample->euler[2]; sample->euler[2] = first; }
            sample->flags |= OPEN_CFW_IMU_FLAG_FUSION;
        }
        sample->compass_valid = fusion.magnetic_bias_valid;
        sample->compass_calibrated =
            (uint8_t)(fusion.magnetic_accuracy >= 2);
        OPEN_CFW_IMU_COMPASS_READY = fusion.magnetic_bias_valid;
    }
    OPEN_CFW_IMU_RING.count = (OPEN_CFW_IMU_RING.count + 1u) % OPEN_CFW_IMU_SLOT_COUNT;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 30
__attribute__((noinline)) const float *open_cfw_imu_get_latest_complete_sample(void)
{
    uint32_t offset, index, axis;
    for (offset = 0u; offset < OPEN_CFW_IMU_SLOT_COUNT; ++offset) {
        volatile struct open_cfw_imu_sample *sample;
        index = (OPEN_CFW_IMU_RING.count + OPEN_CFW_IMU_SLOT_COUNT - 1u - offset) % OPEN_CFW_IMU_SLOT_COUNT;
        sample = &OPEN_CFW_IMU_RING.sample[index];
        if (sample->accel[0] == 0.0f && sample->accel[1] == 0.0f && sample->accel[2] == 0.0f) continue;
        if (sample->gyro[0] == 0.0f && sample->gyro[1] == 0.0f && sample->gyro[2] == 0.0f) continue;
        if (sample->magnetic[0] == 0.0f && sample->magnetic[1] == 0.0f && sample->magnetic[2] == 0.0f) continue;
        for (axis = 0u; axis < 3u; ++axis) {
            OPEN_CFW_IMU_LATEST_RESULT[axis] = sample->gyro[axis];
            OPEN_CFW_IMU_LATEST_RESULT[3u + axis] = sample->accel[axis];
            OPEN_CFW_IMU_LATEST_RESULT[6u + axis] = sample->magnetic[axis];
        }
        return (const float *)OPEN_CFW_IMU_LATEST_RESULT;
    }
    open_cfw_imu_zero((void *)OPEN_CFW_IMU_LATEST_RESULT, 9u * sizeof(float));
    return (const float *)OPEN_CFW_IMU_LATEST_RESULT;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 31
__attribute__((noinline)) void open_cfw_imu_set_heading(float value) { OPEN_CFW_IMU_HEADING = value; }
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 32
__attribute__((noinline)) void open_cfw_imu_set_magnetic_vector(const float value[3])
{
    if (value == NULL) return;
    OPEN_CFW_IMU_MAGNETIC[0] = value[0]; OPEN_CFW_IMU_MAGNETIC[1] = value[1]; OPEN_CFW_IMU_MAGNETIC[2] = value[2];
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 33
__attribute__((noinline)) int32_t open_cfw_imu_get_heading_degrees(void)
{ return open_cfw_imu_normalize_heading(open_cfw_imu_round(OPEN_CFW_IMU_HEADING)); }
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 34
__attribute__((noinline)) float open_cfw_imu_get_heading_float(void) { return OPEN_CFW_IMU_HEADING; }
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 35
__attribute__((noinline)) const float *open_cfw_imu_get_magnetic_vector(void)
{ return (const float *)OPEN_CFW_IMU_MAGNETIC; }
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 36
__attribute__((noinline)) const float *open_cfw_imu_get_orientation_vector(void)
{
    uint32_t count = OPEN_CFW_IMU_RING.count;
    if (count != 0u) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[(count - 1u) % OPEN_CFW_IMU_SLOT_COUNT];
        if ((sample->flags & OPEN_CFW_IMU_FLAG_ACCEL) != 0u) {
            float vector[3] = {sample->accel[0], sample->accel[1], sample->accel[2]};
            float horizontal = open_cfw_imu_sqrt(vector[1] * vector[1] + vector[2] * vector[2]);
            open_cfw_imu_transform_vector(vector, (const float *)OPEN_CFW_IMU_ORIENTATION);
            OPEN_CFW_IMU_ORIENTATION_VECTOR[0] = 0.0f;
            OPEN_CFW_IMU_ORIENTATION_VECTOR[1] = open_cfw_imu_atan2(-vector[0], horizontal) * 57.2957795131f;
            OPEN_CFW_IMU_ORIENTATION_VECTOR[2] = open_cfw_imu_atan2(vector[1], vector[2]) * 57.2957795131f;
        }
    }
    return (const float *)OPEN_CFW_IMU_ORIENTATION_VECTOR;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 37
__attribute__((noinline)) int32_t open_cfw_imu_build_raw_csv_path(char *path, uint32_t capacity)
{
    static const char prefix[] OPEN_CFW_IMU_UNUSED = "/log/imu_rawdata_";
    uint32_t offset = 0u, index, stamp;
    if (path == NULL || capacity < 28u) return -1;
    for (index = 0u; index < sizeof(prefix) - 1u; ++index)
        offset = open_cfw_imu_append_char(path, capacity, offset, prefix[index]);
    stamp = open_cfw_retained_imu_tick() % 1000000u;
    for (index = 0u; index < 6u; ++index) {
        uint32_t divisor = index == 0u ? 100000u : index == 1u ? 10000u :
                           index == 2u ? 1000u : index == 3u ? 100u :
                           index == 4u ? 10u : 1u;
        offset = open_cfw_imu_append_char(path, capacity, offset,
                                          (char)('0' + (stamp / divisor) % 10u));
    }
    offset = open_cfw_imu_append_char(path, capacity, offset, '.');
    offset = open_cfw_imu_append_char(path, capacity, offset, 'c');
    offset = open_cfw_imu_append_char(path, capacity, offset, 's');
    offset = open_cfw_imu_append_char(path, capacity, offset, 'v');
    path[offset] = '\0';
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 38
__attribute__((noinline)) int32_t open_cfw_imu_write_csv_header(void)
{
    char data[64];
    static const char header[] OPEN_CFW_IMU_UNUSED =
        "t,ax,ay,az,gx,gy,gz,mx,my,mz,roll,pitch,yaw\n";
    uint32_t size, index;
    for (index = 0u; index < sizeof(header) - 1u; ++index) data[index] = header[index];
    size = sizeof(header) - 1u;
    return open_cfw_retained_imu_raw_write(data, 1u, size,
                                           OPEN_CFW_IMU_RAW_HANDLE) == (int32_t)size ? 0 : -1;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 39
__attribute__((noinline)) int32_t open_cfw_imu_write_csv_data_line(
    uint32_t timestamp, const float accel[3], const float gyro[3],
    const float magnetic[3], const float euler[3], uint8_t accel_valid,
    uint8_t gyro_valid, uint8_t magnetic_valid)
{
    char data[256]; uint32_t size = 0u, group, axis;
    const float *groups[4] = {accel, gyro, magnetic, euler};
    uint8_t valid[4] = {accel_valid, gyro_valid, magnetic_valid, 1u};
    size = open_cfw_imu_append_u32(data, sizeof(data), size, timestamp);
    for (group = 0u; group < 4u; ++group) for (axis = 0u; axis < 3u; ++axis) {
        size = open_cfw_imu_append_char(data, sizeof(data), size, ',');
        size = open_cfw_imu_append_float(data, sizeof(data), size,
            valid[group] != 0u && groups[group] != NULL ? groups[group][axis] : 0.0f);
    }
    size = open_cfw_imu_append_char(data, sizeof(data), size, '\n');
    if (size >= sizeof(data)) return -1;
    if (open_cfw_retained_imu_raw_write(data, 1u, size,
                                        OPEN_CFW_IMU_RAW_HANDLE) != (int32_t)size) return -1;
    ++OPEN_CFW_IMU_RAW_COUNT; return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 40
__attribute__((noinline)) int32_t open_cfw_imu_start_raw_data_collection(void)
{
    char path[32]; char mode[3]; uint32_t handle;
    mode[0] = 'w'; mode[1] = '+'; mode[2] = '\0';
    if (OPEN_CFW_IMU_RAW_ACTIVE != 0u) (void)open_cfw_imu_stop_raw_data_collection();
    if (open_cfw_imu_build_raw_csv_path(path, sizeof(path)) != 0) return -1;
    handle = open_cfw_retained_imu_raw_open(path, mode);
    if (handle == 0u) return -1;
    OPEN_CFW_IMU_RAW_HANDLE = handle;
    if (open_cfw_imu_write_csv_header() != 0) { (void)open_cfw_retained_imu_raw_close(handle); OPEN_CFW_IMU_RAW_HANDLE = 0u; return -1; }
    OPEN_CFW_IMU_RAW_ACTIVE = 1u; OPEN_CFW_IMU_RAW_COUNT = 0u;
    OPEN_CFW_IMU_RAW_STARTED = open_cfw_retained_imu_tick(); return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 41
__attribute__((noinline)) int32_t open_cfw_imu_stop_raw_data_collection(void)
{
    int32_t status = 0;
    if (OPEN_CFW_IMU_RAW_ACTIVE == 0u) return 0;
    OPEN_CFW_IMU_RAW_ACTIVE = 0u;
    if (OPEN_CFW_IMU_RAW_HANDLE != 0u) status = open_cfw_retained_imu_raw_close(OPEN_CFW_IMU_RAW_HANDLE);
    OPEN_CFW_IMU_RAW_HANDLE = 0u; OPEN_CFW_IMU_RAW_STARTED = 0u; OPEN_CFW_IMU_RAW_COUNT = 0u;
    return status;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 42
__attribute__((noinline)) int32_t open_cfw_imu_save_raw_data_to_csv(void)
{
    uint32_t index;
    if (OPEN_CFW_IMU_RAW_ACTIVE == 0u) return 0;
    if (open_cfw_retained_imu_tick() - OPEN_CFW_IMU_RAW_STARTED >= OPEN_CFW_IMU_RAW_LIMIT_MS)
        return open_cfw_imu_stop_raw_data_collection();
    for (index = 0u; index < OPEN_CFW_IMU_RING.count; ++index) {
        volatile struct open_cfw_imu_sample *sample = &OPEN_CFW_IMU_RING.sample[index];
        int32_t status = open_cfw_imu_write_csv_data_line(sample->timestamp,
            (const float *)sample->accel, (const float *)sample->gyro,
            (const float *)sample->magnetic, (const float *)sample->euler,
            (uint8_t)(sample->flags & OPEN_CFW_IMU_FLAG_ACCEL),
            (uint8_t)(sample->flags & OPEN_CFW_IMU_FLAG_GYRO),
            (uint8_t)(sample->flags & OPEN_CFW_IMU_FLAG_MAG));
        if (status != 0) return status;
    }
    return 0;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 43
__attribute__((noinline)) int32_t open_cfw_imu_read_who_am_i(uint32_t *value)
{
    uint8_t byte = 0u; int32_t status;
    if (value == NULL) return -1;
    status = open_cfw_imu_bus_read(0x72u, &byte, 1u);
    if (status == 0) *value = byte; return status;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 44
__attribute__((noinline)) int32_t open_cfw_mag_read_who_am_i(uint32_t *value)
{
    uint8_t byte = 0u; int32_t status;
    if (value == NULL) return -1;
    status = open_cfw_icm45608_tdk_mag_who_am_i(
        (void *)&OPEN_CFW_IMU_DEVICE, &byte);
    if (status == 0) *value = byte; return status;
}
#endif

#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 45
__attribute__((noinline)) uint32_t open_cfw_imu_get_state_zero(void) { return OPEN_CFW_IMU_STATE_ZERO; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 46
__attribute__((noinline)) uint32_t open_cfw_imu_get_state_one(void) { return OPEN_CFW_IMU_STATE_ONE; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 47
__attribute__((noinline)) uint32_t open_cfw_imu_get_state_two(void) { return OPEN_CFW_IMU_STATE_TWO; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 48
__attribute__((noinline)) uint32_t open_cfw_imu_get_state_three(void) { return OPEN_CFW_IMU_STATE_THREE; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 49
__attribute__((noinline)) void open_cfw_imu_set_state_zero(uint32_t value) { OPEN_CFW_IMU_STATE_ZERO = value; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 50
__attribute__((noinline)) void open_cfw_imu_set_state_one(uint32_t value) { OPEN_CFW_IMU_STATE_ONE = value; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 51
__attribute__((noinline)) void open_cfw_imu_set_state_two(uint32_t value) { OPEN_CFW_IMU_STATE_TWO = value; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 52
__attribute__((noinline)) uint8_t open_cfw_imu_get_compass_ready(void) { return OPEN_CFW_IMU_COMPASS_READY; }
#endif
#if OPEN_CFW_IMU_SELECTOR == 0 || OPEN_CFW_IMU_SELECTOR == 53
__attribute__((noinline)) void open_cfw_imu_set_state_three(uint32_t value) { OPEN_CFW_IMU_STATE_THREE = value; }
#endif
