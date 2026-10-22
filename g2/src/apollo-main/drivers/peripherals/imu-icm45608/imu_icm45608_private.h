/* Private layouts, RAM cells and callees of the stock IMU glue
 * (D:\01_workspace\s200_ap510b_iar_git\driver\sensor\imu\imu_icm45608.c,
 * native 0x4a35b0..0x4a656e), shared by imu_icm45608.c and imu_icm45608_fp.c.
 *
 * Upstream callees are the vendored TDK InvenSense driver
 * (third-party/upstream/invensense-icm45608, release 1.1.2, b79ae575) as
 * linked in the stock image; each keeps its upstream name plus the stock
 * address. Stock is an IAR build: TDK enums are one byte, so enum-typed
 * arguments and struct fields are uint8_t here. */
#ifndef G2_IMU_ICM45608_PRIVATE_H
#define G2_IMU_ICM45608_PRIVATE_H

#include <stdint.h>
#include <stddef.h>
#include "g2_imu.h"

#define IMU_I2C_BUS 4u
#define IMU_I2C_ADDR 0x69u
#define IMU_BUS_MAX_READ 16u   /* reads of more bytes take a second, identical path */
#define IMU_POWER_CHANNEL 1u   /* g2_codec_gpio_write channel 1 = GPIO 0x81 */
#define IMU_SAMPLE_SLOTS 20u
#define IMU_FIFO_MIRROR_SIZE 0x800u /* FIFO_MIRRORING_SIZE */

/* TDK register / SRAM addresses used directly by the glue. */
#define ICM_SW_PLL1_TRIM 0xa2a2u
#define ICM_SRAM_GAF_CONFIG_GYR_DT_US 0x4a0u /* read back after GAF setup, value unused */

/* ---- TDK driver objects (layouts of release 1.1.2, IAR one-byte enums) ---- */

typedef struct {
    int (*read_reg)(uint8_t reg, uint8_t *buf, uint32_t len);        /* +0x00 */
    int (*write_reg)(uint8_t reg, const uint8_t *buf, uint32_t len); /* +0x04 */
    uint32_t serif_type;                                              /* +0x08 0 = UI_I2C */
    void (*sleep_us)(uint32_t us);                                    /* +0x0c */
} g2_inv_imu_transport_t;

/* inv_imu_sensor_event_t handed to adv_var.sensor_event_cb. */
typedef struct {
    int32_t sensor_mask;      /* +0x00 bit0 accel, bit1 gyro, bit4 ES0, bit5 ES1 */
    uint16_t timestamp_fsync; /* +0x04 */
    int16_t accel[3];         /* +0x06 */
    int16_t gyro[3];          /* +0x0c */
    int16_t temperature;      /* +0x12 */
    int8_t accel_high_res[3]; /* +0x14 */
    int8_t gyro_high_res[3];  /* +0x17 */
    uint8_t es0[9];           /* +0x1a */
    uint8_t es1[6];           /* +0x23 */
} g2_inv_imu_sensor_event_t;

typedef struct {
    g2_inv_imu_transport_t transport; /* +0x00 */
    uint8_t fifo_frame_size;          /* +0x10 */
    uint8_t endianness_data;          /* +0x11 */
    uint8_t edmp_gaf_mode;            /* +0x12 */
    uint8_t pad13[5];
    void (*sensor_event_cb)(const g2_inv_imu_sensor_event_t *event); /* +0x18 adv_var[0] */
    uint8_t adv_var_rest[0x2c];       /* +0x1c */
} g2_inv_imu_device_t;
_Static_assert(sizeof(g2_inv_imu_device_t) == 0x48, "inv_imu_device_t");

typedef struct {
    int16_t accel[3]; /* +0x0 */
    int16_t gyro[3];  /* +0x6 */
    int16_t temp;     /* +0xc */
} g2_inv_imu_sensor_data_t;

/* inv_imu_int_state_t (15 bytes). */
typedef struct {
    uint8_t fifo_full, fifo_ths, ui_drdy, ois1, ui_fsync, agc_rdy, ois1_agc_rdy, reset_done;
    uint8_t pll_rdy, wom_x, wom_y, wom_z, i3c_prot_err, i2cm_done, edmp_event;
} g2_inv_imu_int_state_t;
_Static_assert(sizeof(g2_inv_imu_int_state_t) == 15, "inv_imu_int_state_t");

/* inv_imu_edmp_int_state_t (14 bytes). */
typedef struct {
    uint8_t tap, highg, lowg, sif, gaf_mrm_chg, gaf_mrm_run, ff, b2s;
    uint8_t b2s_rev, gaf_mrm_thr, self_test, sec_auth, aid_human, aid_device;
} g2_inv_imu_edmp_int_state_t;
_Static_assert(sizeof(g2_inv_imu_edmp_int_state_t) == 14, "inv_imu_edmp_int_state_t");

typedef struct {
    uint8_t int_polarity; /* 1 = active high */
    uint8_t int_mode;     /* 0 = pulse */
    uint8_t int_drive;    /* 0 = push-pull */
} g2_inv_imu_int_pin_config_t;

typedef struct {
    uint16_t tap_min_jerk;        /* +0x0 */
    uint16_t tap_tmax;            /* +0x2 */
    uint8_t tap_tmin;             /* +0x4 */
    uint8_t tap_max_peak_tol;     /* +0x5 */
    uint8_t tap_smudge_reject_th; /* +0x6 */
    uint8_t tap_tavg;             /* +0x7 */
    uint8_t tap_odr;              /* +0x8 */
    uint8_t tap_max;              /* +0x9 */
    uint8_t tap_min;              /* +0xa */
    uint8_t pad;
} g2_inv_imu_edmp_tap_parameters_t;
_Static_assert(sizeof(g2_inv_imu_edmp_tap_parameters_t) == 12, "tap parameters");

typedef struct {
    uint8_t num;       /* 1 single, 2 double, 3 triple */
    uint8_t axis;
    uint8_t direction;
    uint8_t pad;
    uint16_t double_tap_timing;
    uint16_t triple_tap_timing;
} g2_inv_imu_edmp_tap_data_t;

typedef struct {
    uint32_t power_save_time; /* +0x0 */
    uint8_t power_save_en;    /* +0x4 */
} g2_inv_imu_edmp_powersave_parameters_t;

/* struct aid_parameters_s; units are samples at the APEX rate. */
typedef struct {
    uint32_t aid_update_win;                /* +0x0 */
    uint32_t aid_alert_timer;               /* +0x4 */
    uint8_t aid_output_enable;              /* +0x8 bit0 activity, bit1 inactivity, bit2 alert */
    uint8_t aid_disable_multiple_interrupt; /* +0x9 */
} g2_inv_imu_aid_instance_t;

typedef struct {
    g2_inv_imu_aid_instance_t aid_human;  /* +0x00 */
    g2_inv_imu_aid_instance_t aid_device; /* +0x0c */
} g2_inv_imu_edmp_aid_parameters_t;
_Static_assert(sizeof(g2_inv_imu_edmp_aid_parameters_t) == 24, "AID parameters");

/* Parameters of the stock B2S ("TILT") image; not the 1.1.2 B2S API. */
typedef struct {
    uint32_t thr_cos_q30; /* SRAM 0x10ac */
    uint16_t mode;        /* SRAM 0x10aa */
} g2_imu_b2s_parameters_t;

/* inv_imu_edmp_gaf_parameters_t: only the head is set by the glue. */
typedef struct {
    uint8_t run_spherical;   /* +0x00 */
    int8_t clock_variation;  /* +0x01 SW_PLL1_TRIM */
    uint8_t pad2[2];
    uint32_t pdr_us;         /* +0x04 */
    uint32_t mag_dt_us;      /* +0x08 */
    int32_t tail[39];        /* +0x0c filled by get_gaf_parameters */
} g2_inv_imu_edmp_gaf_parameters_t;
_Static_assert(sizeof(g2_inv_imu_edmp_gaf_parameters_t) == 0xa8, "stock frame slot");

/* inv_imu_adv_fifo_config_t. */
typedef struct {
    uint8_t gyro_en;          /* +0x00 */
    uint8_t accel_en;         /* +0x01 */
    uint8_t hires_en;         /* +0x02 */
    uint8_t pad3;
    uint16_t fifo_wm_th;      /* +0x04 */
    uint8_t fifo_mode;        /* +0x06 */
    uint8_t fifo_depth;       /* +0x07 */
    uint8_t fifo_wr_wm_gt_th; /* +0x08 */
    uint8_t tmst_fsync_en;    /* +0x09 */
    uint8_t es1_en;           /* +0x0a */
    uint8_t es0_en;           /* +0x0b */
    uint8_t es0_6b_9b;        /* +0x0c */
    uint8_t comp_en;          /* +0x0d */
    uint8_t comp_nc_flow_cfg; /* +0x0e */
    uint8_t gyro_dec;         /* +0x0f */
    uint8_t accel_dec;        /* +0x10 */
} g2_inv_imu_adv_fifo_config_t;

/* inv_imu_edmp_gaf_outputs_t (0x4e bytes, cleared as 0x50). */
typedef struct {
    int16_t grv_quat_q14[4];  /* +0x00 */
    uint8_t grv_quat_valid;   /* +0x08 */
    uint8_t pad9;
    int16_t gmrv_quat_q14[4]; /* +0x0a */
    uint8_t gmrv_quat_valid;  /* +0x12 */
    uint8_t pad13;
    int16_t gmrv_heading_q11; /* +0x14 */
    uint8_t gmrv_heading_valid; /* +0x16 */
    uint8_t pad17;
    int16_t rv_quat_q14[4];   /* +0x18 */
    uint8_t rv_quat_valid;    /* +0x20 */
    uint8_t pad21;
    int16_t rv_heading_q11;   /* +0x22 */
    uint8_t rv_heading_valid; /* +0x24 */
    uint8_t pad25;
    int16_t gyr_bias_q12[3];  /* +0x26 */
    uint8_t gyr_bias_valid;   /* +0x2c */
    int8_t gyr_accuracy_flag; /* +0x2d */
    int8_t stationary_flag;   /* +0x2e */
    uint8_t gyr_flags_valid;  /* +0x2f */
    int16_t rmag[3];          /* +0x30 */
    uint8_t rmag_valid;       /* +0x36 */
    uint8_t pad37;
    int32_t mag_bias_q16[3];  /* +0x38 */
    int8_t mag_accuracy_flag; /* +0x44 */
    int8_t mag_anomalies;     /* +0x45 */
    uint8_t mag_bias_valid;   /* +0x46 */
    uint8_t hr_g[3];          /* +0x47 */
    uint8_t hr_g_valid;       /* +0x4a */
    uint8_t mrm_state;        /* +0x4b */
    uint8_t mrm_state_valid;  /* +0x4c */
    uint8_t frame_complete;   /* +0x4d */
    uint8_t pad4e[2];
} g2_inv_imu_edmp_gaf_outputs_t;
_Static_assert(offsetof(g2_inv_imu_edmp_gaf_outputs_t, frame_complete) == 0x4d, "GAF outputs");
_Static_assert(sizeof(g2_inv_imu_edmp_gaf_outputs_t) == 0x50, "GAF outputs");

/* ---- product records ---- */

/* Work-mode table row (RAM 0x20000db0, five initialised rows). */
typedef struct {
    uint8_t flags;           /* +0x0 bit1: gyro enabled */
    uint8_t pad1[3];
    uint32_t period_us;      /* +0x4 1000/2500/5000/10000/20000/40000 */
    uint32_t gaf_pdr_us;     /* +0x8 */
    uint32_t fifo_watermark; /* +0xc stored as uint16 */
} g2_imu_mode_row_t;
_Static_assert(sizeof(g2_imu_mode_row_t) == 16, "mode row");

/* Biquad low-pass on accel Z (RAM 0x20073170): y = b0 x + b1 x1 + b2 x2 - a1 y1 - a2 y2. */
typedef struct {
    double b0, b1, b2, a1, a2; /* +0x00 */
    float x1, x2, y1, y2;      /* +0x28 */
} g2_imu_biquad_t;
_Static_assert(sizeof(g2_imu_biquad_t) == 0x38, "biquad");

enum {
    IMU_SAMPLE_ACCEL = 0x01u,
    IMU_SAMPLE_GYRO = 0x02u,
    IMU_SAMPLE_MAG = 0x08u,
    IMU_SAMPLE_QUAT = 0x20u,
};

typedef struct {
    uint32_t tick;          /* +0x00 */
    uint8_t flags;          /* +0x04 IMU_SAMPLE_* */
    uint8_t pad5;
    int16_t accel_raw[3];   /* +0x06 */
    int16_t gyro_raw[3];    /* +0x0c */
    int16_t mag_raw[3];     /* +0x12 */
    int32_t quat_q30[4];    /* +0x18 */
    float accel[3];         /* +0x28 g */
    float gyro[3];          /* +0x34 dps */
    float mag[3];           /* +0x40 uT */
    float quat[4];          /* +0x4c */
    float euler[3];         /* +0x5c roll, pitch, yaw (degrees) */
    float heading;          /* +0x68 (yaw + 90) mod 360 */
    uint8_t mag_accuracy;   /* +0x6c */
    uint8_t mag_anomalies;  /* +0x6d */
    uint8_t pad6e[2];
} g2_imu_sample_t;
_Static_assert(sizeof(g2_imu_sample_t) == 0x70, "sample record");

typedef struct {
    uint32_t base_tick;   /* +0x0 DRV_IMUReadData argument */
    uint32_t frame_count; /* +0x4 FIFO frames of this batch */
    uint32_t count;       /* +0x8 parsed samples */
    g2_imu_sample_t sample[IMU_SAMPLE_SLOTS]; /* +0xc */
} g2_imu_samples_t;
_Static_assert(sizeof(g2_imu_samples_t) == 0x8cc, "sample buffer");

/* ---- RAM cells ---- */
extern g2_inv_imu_device_t g2_imu_device;              /* RAM 0x20073020 */
extern g2_imu_biquad_t g2_imu_headup_filter;           /* RAM 0x20073170 */
extern g2_imu_mode_row_t g2_imu_mode_table[G2_IMU_MODE_COUNT]; /* RAM 0x20000db0 */
extern uint8_t g2_imu_mode_index;                      /* RAM 0x20074fd1 */
extern uint8_t g2_imu_tilt_enabled;                    /* RAM 0x20074fd2, B2S */
extern uint8_t g2_imu_tap_enabled;                     /* RAM 0x20074fd3 */
extern uint8_t g2_imu_powersave_enabled;               /* RAM 0x20074fd4 */
extern uint8_t g2_imu_apex_odr;                        /* RAM 0x20074fd5 */
extern uint8_t g2_imu_accel_odr;                       /* RAM 0x20074fd6 */
extern uint8_t g2_imu_gyro_odr;                        /* RAM 0x20074fd7 */
extern volatile uint8_t g2_imu_aid_enabled_cell;       /* RAM 0x20074fd8, both AID in sedentary alert */
extern uint8_t g2_imu_mag_bias_valid;                  /* RAM 0x20074fd9 */
extern uint8_t g2_imu_mag_anomalies;                   /* RAM 0x20074fda */
extern uint8_t g2_imu_mag_accuracy;                    /* RAM 0x20074fdb */
extern uint8_t g2_imu_compass_calibrated;              /* RAM 0x20074fdc */
extern uint8_t g2_imu_csv_active;                      /* RAM 0x20074fdd */
extern uint8_t g2_imu_head_up_state;                   /* RAM 0x20074fde */
extern uint8_t g2_imu_compass_cal_reported;            /* RAM 0x20074fdf */
extern uint16_t g2_imu_fifo_watermark;                 /* RAM 0x20074f32 */
extern uint16_t g2_imu_tilt_angle;                     /* RAM 0x20074f34 */
extern uint8_t g2_imu_accel_enabled;                   /* RAM 0x20004549 */
extern uint8_t g2_imu_gyro_enabled;                    /* RAM 0x2000454a */
extern uint8_t g2_imu_gaf_enabled;                     /* RAM 0x2000454b */
extern uint8_t g2_imu_aid_feature_enabled;             /* RAM 0x2000454c */
extern uint8_t g2_imu_gyro_low_power;                  /* RAM 0x2000454d */
extern uint8_t g2_imu_aid_device_state;                /* RAM 0x2000454e */
extern uint8_t g2_imu_aid_human_state;                 /* RAM 0x2000454f */
extern uint8_t g2_imu_head_down_state;                 /* RAM 0x20004550 */
extern uint32_t g2_imu_gaf_pdr_us;                     /* RAM 0x20074670 */
extern uint32_t g2_imu_headup_open;                    /* RAM 0x20074674 */
extern uint32_t g2_imu_compass_open;                   /* RAM 0x20074678 */
extern uint32_t g2_imu_dis_open;                       /* RAM 0x2007467c */
extern uint32_t g2_imu_type5_open;                     /* RAM 0x20074680 */
extern void *g2_imu_csv_file;                          /* RAM 0x20074684 */
extern uint32_t g2_imu_csv_lines;                      /* RAM 0x20074688 */
extern uint32_t g2_imu_csv_start_tick;                 /* RAM 0x2007468c */
extern uint32_t g2_imu_compass_last_tick;              /* RAM 0x20074690 */
extern int32_t g2_imu_compass_last_angle;              /* RAM 0x20074694 */
extern uint32_t g2_imu_report_counter;                 /* RAM 0x20074698 */
extern float g2_imu_pitch;                             /* RAM 0x2007469c */
extern int32_t g2_imu_accel_bias_q16[3];               /* RAM 0x20074020 */
extern int32_t g2_imu_mag_bias_q16[3];                 /* RAM 0x2007402c */
extern int32_t g2_imu_gyro_bias_q16[3];                /* RAM 0x20074038 */
extern float g2_imu_euler[3];                          /* RAM 0x20074044 */
extern float g2_imu_orientation[3];                    /* RAM 0x20074050 */
extern int16_t g2_imu_mount_q14[9];                    /* RAM 0x20000e00 */
extern int32_t g2_imu_mount_q30[3][3];                 /* RAM 0x20000e14 */
extern float g2_imu_mount_matrix[3][3];                /* RAM 0x20000e38 */
extern uint32_t g2_imu_auto_mrm_enabled;               /* RAM 0x20000e5c */
extern g2_inv_imu_sensor_data_t g2_imu_register_data;  /* RAM 0x20073e84 */
extern uint8_t g2_imu_latest_sample[36];               /* RAM 0x20073894 */
extern g2_inv_imu_edmp_gaf_outputs_t g2_imu_gaf_outputs; /* RAM 0x20072bc8 */
extern g2_imu_samples_t g2_imu_samples;                /* RAM 0x200640a0 */
extern uint8_t g2_imu_fifo_mirror[IMU_FIFO_MIRROR_SIZE]; /* RAM 0x20067230 */

/* Sensor-hub parameter cells owned by hub-imu / hub-semantic units. */
extern uint32_t audio_hub_imu_report_interval_cell;    /* RAM 0x20000e60 */
extern uint32_t audio_hub_motion_threshold_cell;       /* RAM 0x20000e64, head-up pitch threshold (deg) */
extern float audio_hub_motion_threshold_sine_cell;     /* RAM 0x200731a8, filtered accel Z threshold */
extern uint32_t audio_hub_motion_period_cell;          /* RAM 0x20000e68, compass check period (ms) */
extern uint32_t audio_hub_motion_duration_cell;        /* RAM 0x20000e6c, compass report delta (deg) */

/* ---- logging ---- */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Stock log shape: extended text when flag bit1, compressed record when bit0
 * or bit2. The compressed mask is (level << 26) | (argument count << 22). */
#define IMU_LOG_ON() ((audio_log_flags() & 2u) != 0u)
#define IMU_CLOG_ON() ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)

/* ---- other callees ---- */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint32_t osKernelGetTickCount(void);  /* 0x4490cc */
extern int32_t osDelay(uint32_t ticks);       /* 0x449376 */

/* ---- functions split across the two units ---- */
void semantic_filter_init(g2_imu_biquad_t *f);
uint32_t DRV_IMUSetSensorParameters(const g2_imu_mode_row_t *row);
uint32_t semantic_emit_imu_event(uint32_t event, uint32_t value);
int32_t semantic_normalize_heading(int32_t yaw);
void semantic_noop_sample_callback(void);
void semantic_set_magnetic_vector(const float euler[3]);
void DRV_IMUDataParserCallback(const g2_inv_imu_sensor_event_t *event);
uint32_t semantic_postprocess_samples(void);
void DRV_IMUSaveRawDataToCSV(void);
int32_t DRV_IMUWriteCSVDataLine(uint32_t tick, const float accel[3], const float gyro[3],
                                const float mag[3], const float euler[3],
                                uint8_t accel_valid, uint8_t gyro_valid, uint8_t mag_valid);

#endif
