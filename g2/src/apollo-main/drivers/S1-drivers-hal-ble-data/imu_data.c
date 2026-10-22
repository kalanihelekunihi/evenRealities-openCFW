/* ICM-45608 product-driver storage (S1 storage-definition pass, 2.2.6.10).
 *
 * Stock owner: the product IMU driver (drv_imu_icm45608.c and its sensor-hub
 * glue). The TDK driver objects (inv_imu_device_t etc.) are allocated by this
 * product module; the TDK library's own statics (invn_mag.c mag_dev/self,
 * EDMP images) belong to the upstream units and are not defined here.
 * .data values are from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4); every other cell is in the zero-init range. Float initialisers
 * are data only, but this unit is built with the hard-float-capable profile
 * g2-apollo-main-3 as the brief asks for float objects. */
#include <stddef.h>
#include <stdint.h>
#include "../peripherals/imu-icm45608/imu_icm45608_private.h"

/* ---- .data (0x20000db0..0x20000e5f, 0x2000454a..0x20004550) ------------- */

/* RAM 0x20000db0: five work-mode rows {flags, period_us, gaf_pdr_us, fifo_wm}. */
g2_imu_mode_row_t g2_imu_mode_table[G2_IMU_MODE_COUNT] = {
    {0x0du, {0u, 0u, 0u}, 10000u, 20000u, 10u}, /* 0 head-up / type 5 */
    {0x0fu, {0u, 0u, 0u}, 10000u, 20000u, 3u},  /* 1 display */
    {0x0fu, {0u, 0u, 0u}, 10000u, 20000u, 10u}, /* 2 compass */
    {0x00u, {0u, 0u, 0u}, 0u, 0u, 0u},          /* 3 unused */
    {0x0fu, {0u, 0u, 0u}, 10000u, 20000u, 10u}, /* 4 */
};

/* RAM 0x20000e00: identity mount matrix in Q14 (18 bytes + 2 pad). */
int16_t g2_imu_mount_q14[9] = {
    0x4000, 0, 0,
    0, 0x4000, 0,
    0, 0, 0x4000,
};
/* RAM 0x20000e14: identity mount matrix in Q30. */
int32_t g2_imu_mount_q30[3][3] = {
    {0x40000000, 0, 0},
    {0, 0x40000000, 0},
    {0, 0, 0x40000000},
};
/* RAM 0x20000e38: identity mount matrix (1.0f = 0x3f800000). */
float g2_imu_mount_matrix[3][3] = {
    {1.0f, 0.0f, 0.0f},
    {0.0f, 1.0f, 0.0f},
    {0.0f, 0.0f, 1.0f},
};
uint32_t g2_imu_auto_mrm_enabled = 1u; /* RAM 0x20000e5c */

uint8_t g2_imu_gyro_enabled = 1u;        /* RAM 0x2000454a */
uint8_t g2_imu_gaf_enabled = 1u;         /* RAM 0x2000454b */
uint8_t g2_imu_aid_feature_enabled = 1u; /* RAM 0x2000454c */
uint8_t g2_imu_gyro_low_power = 1u;      /* RAM 0x2000454d */
uint8_t g2_imu_aid_device_state = 1u;    /* RAM 0x2000454e */
uint8_t g2_imu_aid_human_state = 1u;     /* RAM 0x2000454f */
uint8_t g2_imu_head_down_state = 1u;     /* RAM 0x20004550 */

/* ---- zero-init ---------------------------------------------------------- */

g2_inv_imu_device_t g2_imu_device;              /* RAM 0x20073020 */
g2_imu_biquad_t g2_imu_headup_filter;           /* RAM 0x20073170 */
uint8_t g2_imu_mode_index;                      /* RAM 0x20074fd1 */
uint8_t g2_imu_tilt_enabled;                    /* RAM 0x20074fd2 */
uint8_t g2_imu_tap_enabled;                     /* RAM 0x20074fd3 */
uint8_t g2_imu_powersave_enabled;               /* RAM 0x20074fd4 */
uint8_t g2_imu_apex_odr;                        /* RAM 0x20074fd5 */
uint8_t g2_imu_accel_odr;                       /* RAM 0x20074fd6 */
uint8_t g2_imu_gyro_odr;                        /* RAM 0x20074fd7 */
uint8_t g2_imu_mag_bias_valid;                  /* RAM 0x20074fd9 */
uint8_t g2_imu_mag_anomalies;                   /* RAM 0x20074fda */
uint8_t g2_imu_mag_accuracy;                    /* RAM 0x20074fdb */
uint8_t g2_imu_compass_calibrated;              /* RAM 0x20074fdc */
uint8_t g2_imu_csv_active;                      /* RAM 0x20074fdd */
uint8_t g2_imu_head_up_state;                   /* RAM 0x20074fde */
uint8_t g2_imu_compass_cal_reported;            /* RAM 0x20074fdf */
uint16_t g2_imu_fifo_watermark;                 /* RAM 0x20074f32 */
uint16_t g2_imu_tilt_angle;                     /* RAM 0x20074f34 */
uint32_t g2_imu_gaf_pdr_us;                     /* RAM 0x20074670 */
uint32_t g2_imu_headup_open;                    /* RAM 0x20074674 */
uint32_t g2_imu_compass_open;                   /* RAM 0x20074678 */
uint32_t g2_imu_dis_open;                       /* RAM 0x2007467c */
uint32_t g2_imu_type5_open;                     /* RAM 0x20074680 */
void *g2_imu_csv_file;                          /* RAM 0x20074684 */
uint32_t g2_imu_csv_lines;                      /* RAM 0x20074688 */
uint32_t g2_imu_csv_start_tick;                 /* RAM 0x2007468c */
uint32_t g2_imu_compass_last_tick;              /* RAM 0x20074690 */
int32_t g2_imu_compass_last_angle;              /* RAM 0x20074694 */
uint32_t g2_imu_report_counter;                 /* RAM 0x20074698 */
float g2_imu_pitch;                             /* RAM 0x2007469c */
int32_t g2_imu_accel_bias_q16[3];               /* RAM 0x20074020 */
int32_t g2_imu_mag_bias_q16[3];                 /* RAM 0x2007402c */
int32_t g2_imu_gyro_bias_q16[3];                /* RAM 0x20074038 */
float g2_imu_euler[3];                          /* RAM 0x20074044 */
float g2_imu_orientation[3];                    /* RAM 0x20074050 */
g2_inv_imu_sensor_data_t g2_imu_register_data;  /* RAM 0x20073e84 */
__attribute__((aligned(4))) uint8_t g2_imu_latest_sample[36]; /* RAM 0x20073894 */
g2_inv_imu_edmp_gaf_outputs_t g2_imu_gaf_outputs; /* RAM 0x20072bc8 */
g2_imu_samples_t g2_imu_samples;                /* RAM 0x200640a0 */
__attribute__((aligned(4))) uint8_t g2_imu_fifo_mirror[IMU_FIFO_MIRROR_SIZE]; /* RAM 0x20067230 */
