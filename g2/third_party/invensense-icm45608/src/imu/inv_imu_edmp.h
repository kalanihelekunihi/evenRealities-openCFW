/*
 *
 * Copyright (c) [2020] by InvenSense, Inc.
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 * WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
 * SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 * WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION
 * OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

/** @defgroup EDMP EDMP
 *  @brief API to drive eDMP features.
 *  @{
 */

/** @file inv_imu_edmp.h */

#ifndef _INV_IMU_EDMP_H_
#define _INV_IMU_EDMP_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "imu/inv_imu_driver.h"
#include "imu/inv_imu_edmp_memmap.h"

#include "sif_feature_extract_ir.h"
#include "sif_classifier_ir.h"

#include <stdint.h>
#include <string.h>

/** @brief Writes in EDMP SRAM
 *  @param[in] s     Pointer to device.
 *  @param[in] name  Name of the parameter.
 *  @param[in] val   Value to be written.
 *  @return          0 on success, negative value on error.
 */
#define INV_IMU_WRITE_EDMP_SRAM(s, name, val)                                                      \
	inv_imu_write_sram(s, (uint32_t)name, name##_SIZE, val)

/** @brief Reads in EDMP SRAM
 *  @param[in] s     Pointer to device.
 *  @param[in] name  Name of the parameter.
 *  @param[in] val   Value to be read.
 *  @return          0 on success, negative value on error.
 */
#define INV_IMU_READ_EDMP_SRAM(s, name, val) inv_imu_read_sram(s, (uint32_t)name, name##_SIZE, val)

/** @brief Default GAF temperature (-273 C) to be used with low accuracy level (0) */
#define GAF_DEFAULT_TEMPERATURE_INIT_Q16 0xFEEF0000;

/** @brief EDMP input interrupt lines definition */
typedef enum { INV_IMU_EDMP_INT0 = 0, INV_IMU_EDMP_INT1, INV_IMU_EDMP_INT2 } inv_imu_edmp_int_t;

/** @brief APEX interrupts definition */
typedef struct {
	uint8_t INV_TAP;
	uint8_t INV_HIGHG;
	uint8_t INV_LOWG;
	uint8_t INV_SIF;
	uint8_t INV_GAF_MRM_CHG;
	uint8_t INV_GAF_MRM_RUN;
	uint8_t INV_FF;
	uint8_t INV_B2S;

	uint8_t INV_B2S_REV;
	uint8_t INV_GAF_MRM_THR;
	uint8_t INV_SELF_TEST;
	uint8_t INV_SEC_AUTH;
	uint8_t INV_AID_HUMAN;
	uint8_t INV_AID_DEVICE;
} inv_imu_edmp_int_state_t;

/** Registers to retrieve interrupts status for APEX. */
typedef struct {
	int_apex_status0_t int_apex_status0;
	int_apex_status1_t int_apex_status1;
} int_apex_statusx_t;

/** Registers to configure interrupts for APEX. */
typedef struct {
	int_apex_config0_t int_apex_config0;
	int_apex_config1_t int_apex_config1;
} int_apex_configx_t;

/** Registers to enable APEX features. */
typedef struct {
	edmp_apex_en0_t edmp_apex_en0;
	edmp_apex_en1_t edmp_apex_en1;
} edmp_apex_enx_t;

/** @brief IMU TAP inputs parameters definition
 *  @note Refer to the datasheet for details on how to configure these parameters.
 */
typedef struct {
	uint16_t tap_min_jerk;
	uint16_t tap_tmax;
	uint8_t  tap_tmin;
	uint8_t  tap_max_peak_tol;
	uint8_t  tap_smudge_reject_th;
	uint8_t  tap_tavg;
	uint8_t  tap_odr;
	uint8_t  tap_max;
	uint8_t  tap_min;
} inv_imu_edmp_tap_parameters_t;

/** @brief IMU Freefall inputs parameters definition
 *  @note Refer to the datasheet for details on how to configure these parameters.
 */
typedef struct {
	uint16_t lowg_peak_th;
	uint16_t lowg_peak_th_hyst;
	uint16_t lowg_time_th;
	uint16_t highg_peak_th;
	uint16_t highg_peak_th_hyst;
	uint16_t highg_time_th;
	uint32_t ff_min_duration;
	uint32_t ff_max_duration;
	uint32_t ff_debounce_duration;
} inv_imu_edmp_ff_parameters_t;

/** @brief IMU EDMP power save mode inputs parameters definition
 *  @note Refer to the datasheet for details on how to configure these parameters.
 */
typedef struct {
	uint32_t power_save_time;
	uint8_t  power_save_en;
} inv_imu_edmp_powersave_parameters_t;

/** @brief Tap number definition */
typedef enum {
	INV_IMU_EDMP_TAP_TRIPLE = 0x03,
	INV_IMU_EDMP_TAP_DOUBLE = 0x02,
	INV_IMU_EDMP_TAP_SINGLE = 0x01,
} inv_imu_edmp_tap_num_t;

/** @brief Tap axis definition */
typedef enum {
	INV_IMU_EDMP_TAP_AXIS_Z = 0x02,
	INV_IMU_EDMP_TAP_AXIS_Y = 0x01,
	INV_IMU_EDMP_TAP_AXIS_X = 0x00,
} inv_imu_edmp_tap_axis_t;

/** @brief Tap direction definition */
typedef enum {
	INV_IMU_EDMP_TAP_DIR_POSITIVE = 0x01,
	INV_IMU_EDMP_TAP_DIR_NEGATIVE = 0x00,
} inv_imu_edmp_tap_dir_t;

/** @brief Tap outputs */
typedef struct {
	inv_imu_edmp_tap_num_t  num;
	inv_imu_edmp_tap_axis_t axis;
	inv_imu_edmp_tap_dir_t  direction;
	uint16_t                double_tap_timing;
	uint16_t                triple_tap_timing;
} inv_imu_edmp_tap_data_t;

/** @brief EDMP GAF frame type definition */
typedef enum {
	INV_IMU_EDMP_GAF_QUAT_BIAS_GYR = 0,
	INV_IMU_EDMP_GAF_QUAT_RAW_MAG,
	INV_IMU_EDMP_GAF_QUAT_RAW_MAG_GYR_FLAGS,
	INV_IMU_EDMP_GAF_BIAS_MAG_HEADING,
	INV_IMU_EDMP_GAF_HRC_BIAS_GYR_RAW_MAG,
	INV_IMU_EDMP_GAF_HRC_BIAS_GYR,
	INV_IMU_EDMP_GAF_HRC_RAW_MAG,
	INV_IMU_EDMP_GAF_HRC_BIAS_MAG
} inv_imu_edmp_gaf_frame_type_t;

/** @brief IMU GAF inputs parameters definition
 *  @note Refer to the datasheet and appnote for details on how to configure these parameters.
 */
typedef struct {
	uint8_t  run_spherical;
	int8_t   clock_variation;
	uint32_t pdr_us;
	uint32_t mag_dt_us;
	int32_t  stationary_angle_enable;
	int32_t  stationary_angle_duration_us;
	int32_t  stationary_angle_threshold_deg_q16;
	int32_t  gyr_cal_stationary_duration_us;
	int32_t  gyr_cal_threshold_metric1;
	int32_t  strict_gyr_cal_threshold_metric1;
	int32_t  gyr_cal_threshold_metric2;
	int32_t  strict_gyr_cal_threshold_metric2;
	int32_t  gyr_cal_sample_num_log2;
	int32_t  gyr_bias_reject_th;
	int32_t  acc_filtering_Npoints_log2;
	int32_t  acc_square_sin_angle_motion_detect_th;
	int32_t  golden_bias_timer;
	int32_t  golden_bias_temperature_validity;
	int32_t  fus_high_speed_drift;
	int32_t  fus_low_speed_drift_roll_pitch;
	int32_t  fus_measurement_covariance_acc;
	int32_t  fus_acceleration_rejection;
	int32_t  fus_low_speed_drift_yaw;
	int32_t  fus_measurement_covariance_mag;
	int32_t  fus_mag_anomaly_rejection;
	int32_t  thresh_yaw_stop_convergence_q30;
	int32_t  thresh_yaw_smooth_convergence_q15;
	int32_t  mag_thr_huge_disturbance;
	int32_t  mag_thr_anomaly_radius;
	int32_t  mag_thr_select_angle;
	int32_t  mag_thr_select_distance_gyro;
	int32_t  mag_thr_select_distance_nogyro;
	int32_t  mag_q0_standalone;
	int32_t  mag_r0_standalone;
	int32_t  mag_q0_assisted;
	int32_t  mag_r0_assisted;
	int32_t  mag_thr_max_radius_jump;
	int32_t  mag_thr_max_radius;
	int32_t  mag_thr_min_radius;
	int32_t  mag_thr_lock_acc;
	int16_t  mag_calibration_condition;

	/* Parameters below are used only if edmp_prgm_ram_patch_calmag RAM image is used by current driver */
	int32_t  mag_fast_covariance_conv_thr;
	int32_t  mag_stuck_covariance_conv_thr;
} inv_imu_edmp_gaf_parameters_t;

/** @brief Auto MRM states. 
 *  Mag data are considered as valid only in `INV_IMU_AUTO_MRM_STATE_RUN` mode.
 */
typedef enum {
	INV_IMU_AUTO_MRM_STATE_CHECK_NORM = 0,
	INV_IMU_AUTO_MRM_STATE_CHECK_OFFSETS,
	INV_IMU_AUTO_MRM_STATE_RUN,
	INV_IMU_AUTO_MRM_STATE_WAIT_STAB,
} inv_imu_auto_mrm_state_t;

/** @brief IMU GAF outputs definition
 */
typedef struct {
	/** 6-axis (accel and gyro fusion) {w, x, y, z} quaternion in Q14 */
	int16_t grv_quat_q14[4];
	/** Valid bit set to 1 when `grv_quat_q14` contains relevant data */
	uint8_t grv_quat_valid;

	/** 6-axis (accel and mag fusion) {w, x, y, z} quaternion in Q14 */
	int16_t gmrv_quat_q14[4];
	/** Valid bit set to 1 when `gmrv_quat_q14` contains relevant data */
	uint8_t gmrv_quat_valid;
	/** Heading accuracy of 6-axis (accel and mag fusion) (1 rad = 1<<11) */
	int16_t gmrv_heading_q11;
	/** Valid bit set to 1 when `gmrv_heading_q11` contains relevant data */
	uint8_t gmrv_heading_valid;

	/** 9-axis (accel, gyro and mag fusion) {w, x, y, z} quaternion in Q14 */
	int16_t rv_quat_q14[4];
	/** Valid bit set to 1 when `rv_quat_q14` contains relevant data */
	uint8_t rv_quat_valid;
	/** Heading accuracy of 9-axis (accel, gyro and mag fusion) (1 rad = 1<<11) */
	int16_t rv_heading_q11;
	/** Valid bit set to 1 when `rv_heading_valid` contains relevant data */
	uint8_t rv_heading_valid;

	/** Gyro bias {x, y, z} (1 dps = 1<<12)*/
	int16_t gyr_bias_q12[3];
	/** Valid bit set to 1 when `gyr_bias_q12` contains relevant data */
	uint8_t gyr_bias_valid;
	/** Gyro accuracy, from 0 (non calibrated) to 3 (well calibrated) */
	int8_t gyr_accuracy_flag;
	/** Stationary detection based on gyro data: 0 is for motion detected, 1 and 2 are for no motion, -1 is for not estimated flag */
	int8_t stationary_flag;
	/** Valid bit set to 1 when `gyr_accuracy_flag` and `stationary_flag` contain relevant data */
	uint8_t gyr_flags_valid;

	/** Raw mag data as read from magnetometer register */
	int16_t rmag[3];
	/** Valid bit set to 1 when `rmag` contains relevant data */
	uint8_t rmag_valid;

	/** Mag bias {x, y, z} (1 uT = 1<<16)*/
	int32_t mag_bias_q16[3];
	/** Mag accuracy, from 0 (non calibrated) to 3 (well calibrated) */
	int8_t mag_accuracy_flag;
	/** Mag anomalies flag : 0 is for no anomalies, 1 is for small anomalies or temperature variation detected, 2 is for huges anomalies detected */
	int8_t mag_anomalies;
	/** Valid bit set to 1 when `mag_anomalies`, `mag_accuracy_flag` and `mag_anomalies` contain relevant data */
	uint8_t mag_bias_valid;

	/** 4 bits high resolution gyro {x, y, z} */
	uint8_t hr_g[3];
	/** Valid bit set to 1 when `hr_g` contains relevant data */
	uint8_t hr_g_valid;

	/** Current state of MRM state machine, `INV_IMU_AUTO_MRM_STATE_RUN` if no MRM image is loaded */
	inv_imu_auto_mrm_state_t mrm_state;
	/** Valid bit set to 1 when `mrm_state` contains relevant data */
	uint8_t mrm_state_valid;

	/** Set to 1 when all FIFO frames to rebuild one GAF output were received, 0 if more FIFO frame is still needed */
	uint8_t frame_complete;
} inv_imu_edmp_gaf_outputs_t;

/** @brief SIF decision tree
 */
typedef struct {
	/* Pointer to array of [MAX_NODE_SIZE] */
	int16_t *decisionTreeThresholds;
	/* Pointer to array of [MAX_NODE_SIZE] */
	uint8_t *decisionTreeFeatureIDs;
	/* Pointer to array of [MAX_NODE_SIZE] */
	uint8_t *decisionTreeNextNodeRight;
	/* Pointer to array of [MAX_FEATURE_IDS] */
	uint8_t *decisionTreeThresholdsShift;
} inv_imu_edmp_decision_tree_t;

/** @brief SIF configurations from user.
 */
typedef struct {
	/*======================== Common Settings ========================*/
	int32_t wind_size_sample;
	int32_t inv_data_wind;

	/*======================== Time domain Features ========================*/
	int32_t acc_hyst_thr_q16;
	int32_t acc_min_peak_distance;
	int32_t acc_min_peak_height_q16;

	int32_t acc_t_config_num;

	/* Pointer to array of [ACC_T_FILTERS_NUM_MAX][MAX_FLT_COEF] */
	int32_t *acc_t_filtbna_q28;
	/* Pointer to array of [ACC_T_CONFIG_NUM_MAX][ACC_T_CONFIG_NUM_MAX] */
	uint8_t *acc_temporal_feas_config;

	/*======================== Decision Tree Params ========================*/
	int32_t                      node_size;
	inv_imu_edmp_decision_tree_t tree;

	/*======================== Algo ODR ========================*/
	uint32_t sif_odr;
} inv_imu_edmp_sif_user_config_t;

typedef enum {
	SIF_INTERRUPT_ASSERTED_ALWAYS =
	    0, /**< SIF interrupt is always asserted at the end of the window */
	SIF_INTERRUPT_ASSERTED_ON_CHANGE =
	    1, /**< SIF interrupt is only asserted if the classification result changed at the end of the window */
} inv_imu_edmp_sif_int_mode_t;

/** @brief Configure EDMP Output Data Rate.
 *  @warning Accel frequency must be higher or equal to EDMP frequency.
 *  @warning If inv_imu_edmp_init() was already called, application should call
 *          `inv_imu_edmp_recompute_decimation()` afterwards if EDMP algorithms are to be run.
 *  @param[in] s         Pointer to device.
 *  @param[in] frequency The requested frequency.
 *  @return              0 on success, negative value on error.
 */
int inv_imu_edmp_set_frequency(inv_imu_device_t *s, const dmp_ext_sen_odr_cfg_apex_odr_t frequency);

/** @brief Initialize EDMP algorithms. This function should be called before
 *         calling any other function (except for `inv_imu_edmp_set_frequency`).
 *  @warning This function will reset all interrupt masks previously set with
 *           `inv_imu_edmp_unmask_int_src` and exit with `EDMP_INT_SRC_ACCEL_DRDY_MASK|EDMP_INT_SRC_GYRO_DRDY_MASK` unmasked on
 *           `INV_IMU_EDMP_INT0`.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error or if EDMP is enabled.
 */
int inv_imu_edmp_init(inv_imu_device_t *s);

/** @brief Recompute EDMP algorithms internal decimator based on new EDMP output Data Rate
           configured with `inv_imu_edmp_set_frequency`.
 *  @warning It is up to application level to save/restore previously configured APEX parameters,
 *           if any, with `inv_imu_edmp_set_tap_parameters`, `inv_imu_edmp_set_ff_parameters` or `inv_imu_edmp_set_gaf_parameters`.
 *  @warning EDMP must be disabled before calling this function.
 *  @warning This function will reset all interrupt masks previously set with
 *           `inv_imu_edmp_unmask_int_src` and exit with `EDMP_INT_SRC_ACCEL_DRDY_MASK|EDMP_INT_SRC_GYRO_DRDY_MASK` unmasked on
 *           `INV_IMU_EDMP_INT0`.
 *  @param[in] s Pointer to device.
 *  @return      0 on success, negative value on error or if EDMP is enabled.
 */
int inv_imu_edmp_recompute_decimation(inv_imu_device_t *s);

/** @brief Returns current EDMP parameters for EDMP power save mode.
 *  @param[in] s   Pointer to device.
 *  @param[out] p  The current parameters read from registers.
 *  @return        0 on success, negative value on error.
 */
int inv_imu_edmp_get_powersave_parameters(inv_imu_device_t *                   s,
                                          inv_imu_edmp_powersave_parameters_t *p);

/** @brief Returns current EDMP parameters for TAP APEX algorithm.
 *  @param[in] s   Pointer to device.
 *  @param[out] p  The current parameters read from registers.
 *  @return        0 on success, negative value on error.
 */
int inv_imu_edmp_get_tap_parameters(inv_imu_device_t *s, inv_imu_edmp_tap_parameters_t *p);

/** @brief Returns current EDMP parameters for FreeFall APEX algorithm.
 *  @param[in] s   Pointer to device.
 *  @param[out] p  The current parameters read from registers.
 *  @return        0 on success, negative value on error.
 */
int inv_imu_edmp_get_ff_parameters(inv_imu_device_t *s, inv_imu_edmp_ff_parameters_t *p);

/** @brief Configures EDMP parameters for EDMP power save mode.
 *  @warning This function should not be called to reconfigure DMP power save time
 *           if DMP is running with already enabled DMP power save mode.
 *  @param[in] s  Pointer to device.
 *  @param[in] p  The requested input parameters.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_set_powersave_parameters(inv_imu_device_t *                         s,
                                          const inv_imu_edmp_powersave_parameters_t *p);

/** @brief Configures EDMP parameters for TAP APEX algorithm.
 *  @warning This function should be called only when TAP algorithm is disabled.
 *  @param[in] s  Pointer to device.
 *  @param[in] p  The requested input parameters.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_set_tap_parameters(inv_imu_device_t *s, const inv_imu_edmp_tap_parameters_t *p);

/** @brief Configures EDMP parameters for FreeFall APEX algorithm.
 *  @warning This function should be called only when FreeFall algorithm is disabled.
 *  @param[in] s  Pointer to device.
 *  @param[in] p  The requested input parameters.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_set_ff_parameters(inv_imu_device_t *s, const inv_imu_edmp_ff_parameters_t *p);

/** @brief  Get current APEX GAF configuration settings.
 *  @param[in]  s           Pointer to device.
 *  @param[out] gaf_params  GAF parameters.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_get_gaf_parameters(inv_imu_device_t *s, inv_imu_edmp_gaf_parameters_t *gaf_params);

/** @brief  Set current APEX GAF configuration settings.
 *  @param[in]  s           Pointer to device.
 *  @param[in]  gaf_params  GAF parameters.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_set_gaf_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_gaf_parameters_t *gaf_params);

/** @brief  Set APEX GAF algorithm soft iron correlation matrix.
 *  @param[in] s      Pointer to device.
 *  @param[in] matrix 3*3 q30 matrix to apply to raw data.
 *  @return           0 on success, negative value on error.
 *  @warning          This must be called after inv_imu_edmp_gaf_init() and before enabling EDMP.
 */
int inv_imu_edmp_set_gaf_soft_iron_cor_matrix(inv_imu_device_t *s, const int32_t matrix[3][3]);

/** @brief  Stop any FIFO push from EDMP APEX GAF.
 *  @param[in] s      Pointer to device.
 *  @return           0 on success, negative value on error.
 */
int inv_imu_edmp_stop_gaf_fifo_push(inv_imu_device_t *s);

/** @brief  Allows FIFO push from EDMP APEX GAF, this is default behavior.
 *  @param[in] s      Pointer to device.
 *  @return           0 on success, negative value on error.
 */
int inv_imu_edmp_start_gaf_fifo_push(inv_imu_device_t *s);

/** @brief  Get previously computed APEX GAF gyro bias so it can start from non-zero
 *  @param[in] s        Pointer to device.
 *  @param[out] gyr_bias_q12 Gyroscope biases in Q12 read from RAM in EDMP (FIFO output format)
 *  @param[out] gyr_bias_temperature Chip temperature at which gyroscope bias have been computed in Q16
 *  @param[out] accuracy Gyroscope calibration accuracy read from calibration algorithm in EDMP
 *  @return             0 on success, negative value on error.
 *  @warning            This should be called after disabling EDMP to be sure of array consistency.
 */
int inv_imu_edmp_get_gaf_gyr_bias(inv_imu_device_t *s, int16_t gyr_bias_q12[3],
                                  int32_t *gyr_bias_temperature, uint8_t *accuracy);

/** @brief  Set previously computed APEX GAF gyro bias so it can start from non-zero
 *  @param[in] s        Pointer to device.
 *  @param[in] gyr_bias_q12 Gyroscope biases to be applied in Q12 (FIFO format)
 *  @param[in] gyr_bias_temperature Chip temperature at which gyroscope bias have been computed in Q16
 *  @param[in] accuracy Gyroscope accuracy to be applied
 *  @return             0 on success, negative value on error.
 *  @warning            This must be called before inv_imu_edmp_set_gaf_parameters().
 */
int inv_imu_edmp_set_gaf_gyr_bias(inv_imu_device_t *s, const int16_t gyr_bias_q12[3],
                                  const int32_t gyr_bias_temperature, const uint8_t accuracy);

/** @brief  Get previously computed APEX GAF mag bias so it can start from non-zero
 *  @param[in] s             Pointer to device.
 *  @param[out] mag_bias_q16 Magnetometer biases in Q16 read from RAM in EDMP (FIFO output format)
 *  @param[out] accuracy     Magnetometer calibration accuracy read from calibration algorithm in EDMP
 *  @return                  0 on success, negative value on error.
 *  @warning                 This should be called after disabling EDMP to be sure of array consistency.
 */
int inv_imu_edmp_get_gaf_mag_bias(inv_imu_device_t *s, int32_t mag_bias_q16[3], uint8_t *accuracy);

/** @brief  Set previously computed APEX GAF mag bias so it can start from non-zero
 *  @param[in] s            Pointer to device.
 *  @param[in] mag_bias_q16 Magnetometer biases to be applied in Q16 (FIFO format)
 *  @param[in] accuracy     Magnetometer accuracy to be applied
 *  @return                 0 on success, negative value on error.
 *  @warning                This must be called after inv_imu_edmp_gaf_init() and before enabling EDMP.
 */
int inv_imu_edmp_set_gaf_mag_bias(inv_imu_device_t *s, const int32_t mag_bias_q16[3],
                                  const uint8_t accuracy);

/** @brief Set previously computed APEX GAF accel bias so it can start from non-zero
 *  @param[in] s            Pointer to device.
 *  @param[in] acc_bias_q16 Accelerometer biases to be applied in Q16
 *  @return                 0 on success, negative value on error.
 *  @warning                This must be called before inv_imu_edmp_set_gaf_parameters().
 */
int inv_imu_edmp_set_gaf_acc_bias(inv_imu_device_t *s, const int32_t acc_bias_q16[3]);

/** @brief Configure set of EDMP APEX GAF algorithm to be run.
 *  @param[in] s          Pointer to device.
 *  @param[in] gyro_is_on Gyro calibration is run in EDMP if set to 1.
 *  @param[in] mag_is_on  Mag calibration is run in EDMP if set to 1.
 *  @return               0 on success, negative value on error.
 *  @warning              This must be called after inv_imu_edmp_gaf_init() and before enabling EDMP.
 */
int inv_imu_edmp_set_gaf_mode(inv_imu_device_t *s, uint8_t gyro_is_on, uint8_t mag_is_on);

/** @brief  Initialize APEX SIF configuration with user settings.
 *  @param[in]  s    Pointer to device.
 *  @param[out] cfg  SIF parameters.
 *  @return          0 on success, negative value on error.
 */
int inv_imu_edmp_set_sif_model(inv_imu_device_t *s, const inv_imu_edmp_sif_user_config_t *cfg);

/** @brief  Request APEX SIF PDR update (50 Hz is default).
 *  @param[in]  s     Pointer to device.
 *  @param[in]  pdr   SIF PDR requested in Hz.
 *  @return           0 on success, negative value on error.
 */
int inv_imu_edmp_set_sif_pdr(inv_imu_device_t *s, uint32_t pdr);

/** @brief  Configure APEX SIF interrupt behavior at the end of the observation window.
 *  @param[in] s        Pointer to device.
 *  @param[in] int_mode Control condition for asserting interrupt at the end of SIF classification window (@sa inv_imu_edmp_sif_int_mode_t)
 *  @return             0 on success, negative value on error.
 */
int inv_imu_edmp_set_sif_int_control(inv_imu_device_t *                s,
                                     const inv_imu_edmp_sif_int_mode_t int_mode);

/** @brief  Apply a mounting-matrix at EDMP level, on all input data (axis remapping)
 *  @param[in] s                Pointer to device.
 *  @param[in] mounting_matrix  Mounting-matrix composed of -1/0/1 values.
 *  @return                     0 on success, negative value on error.
 */
int inv_imu_edmp_set_mounting_matrix(inv_imu_device_t *s, const int8_t mounting_matrix[9]);

/** @brief Retrieve interrupts configuration.
 *  @param[in] s    Pointer to device.
 *  @param[out] it  Configuration of each APEX interrupt.
 *  @return         0 on success, negative value on error.
 */
int inv_imu_edmp_get_config_int_apex(inv_imu_device_t *s, inv_imu_edmp_int_state_t *it);

/** @brief Configure APEX interrupt.
 *  @param[in] s   Pointer to device.
 *  @param[in] it  State of each APEX interrupt to configure.
 *  @return        0 on success, negative value on error.
 */
int inv_imu_edmp_set_config_int_apex(inv_imu_device_t *s, const inv_imu_edmp_int_state_t *it);

/** @brief  Enable EDMP.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_enable(inv_imu_device_t *s);

/** @brief  Disable EDMP.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable(inv_imu_device_t *s);

/** @brief  Check if inv_imu_edmp_set_frequency() was called without recomputing EDMP decimation
 *          thanks to inv_imu_edmp_recompute_decimation().
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, INV_IMU_ERROR_EDMP_ODR if inv_imu_edmp_recompute_decimation()
 *                should have been called.
 */
int inv_imu_edmp_check_odr_decimation(inv_imu_device_t *s);

/** @brief  Enable APEX algorithm Tap.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success
 *                INV_IMU_ERROR_EDMP_ODR if user should have called
 *                                       `inv_imu_edmp_recompute_decimation()`
 *                other negative value on error.
 */
int inv_imu_edmp_enable_tap(inv_imu_device_t *s);

/** @brief  Disable APEX algorithm Tap.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable_tap(inv_imu_device_t *s);

/** @brief  Enable APEX algorithm Free Fall.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success
 *                INV_IMU_ERROR_EDMP_ODR if user should have called
 *                                       `inv_imu_edmp_recompute_decimation()`
 *                other negative value on error.
 */
int inv_imu_edmp_enable_ff(inv_imu_device_t *s);

/** @brief  Disable APEX algorithm Free Fall.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable_ff(inv_imu_device_t *s);

/** @brief  Enable APEX algorithm GAF.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_enable_gaf(inv_imu_device_t *s);

/** @brief  Disable APEX algorithm GAF.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable_gaf(inv_imu_device_t *s);

/** @brief  Enable APEX GAF algorithm soft iron correlation.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_enable_gaf_soft_iron_cor(inv_imu_device_t *s);

/** @brief  Disable APEX GAF algorithm soft iron correlation.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable_gaf_soft_iron_cor(inv_imu_device_t *s);

/** @brief  Enable APEX algorithm SIF.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_enable_sif(inv_imu_device_t *s);

/** @brief  Disable APEX algorithm SIF.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_disable_sif(inv_imu_device_t *s);

/** @brief Read APEX interrupt status.
 *  @param[in] s    Pointer to device.
 *  @param[out] it  Status of each APEX interrupt.
 *  @return         0 on success, negative value on error.
 */
int inv_imu_edmp_get_int_apex_status(inv_imu_device_t *s, inv_imu_edmp_int_state_t *it);

/** @brief Retrieve APEX free fall outputs and format them.
 *  @param[in] s                   Pointer to device.
 *  @param[out] freefall_duration  Duration in number of sample.
 *  @return                        0 on success, negative value on error.
 */
int inv_imu_edmp_get_ff_data(inv_imu_device_t *s, uint16_t *freefall_duration);

/** @brief Retrieve APEX tap outputs.
 *  @param[in] s      Pointer to device.
 *  @param[out] data  Tap number and direction.
 *  @return           0 on success, negative value on error.
 */
int inv_imu_edmp_get_tap_data(inv_imu_device_t *s, inv_imu_edmp_tap_data_t *data);

/** @brief Decode APEX GAF FIFO frame type.
 *  @param[in] s             Pointer to device.
 *  @param[in] es1           Pointer to ES1 field of input FIFO frame.
 *  @param[out] frame_type   Decoded frame type.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_get_gaf_frame_type(inv_imu_device_t *s, const uint8_t es1[6],
                                    inv_imu_edmp_gaf_frame_type_t *frame_type);

/** @brief  Build APEX GAF output value based on FIFO frame(s). 
 *  @param[in]  s            Pointer to device.
 *  @param[in]  es0          FIFO frame field of ES data, typically es0 field of @sa inv_imu_sensor_event_t.
 *  @param[in]  es1          FIFO frame field of ES data, typically es1 field of @sa inv_imu_sensor_event_t.
 *  @param[out] out          Pointer to GAF output structure, which will hold GAF latest values computed.
 *  @return                  0 on success, negative value on error.

 */
int inv_imu_edmp_gaf_decode_fifo(inv_imu_device_t *s, const uint8_t es0[9], const uint8_t es1[6],
                                 inv_imu_edmp_gaf_outputs_t *const out);

/** @brief Decode APEX GAF FIFO frame for gyro high resolution value.
 *  @param[in] s             Pointer to device.
 *  @param[in] hr_g          Array of 4 bits high res gyro as decoded by inv_imu_edmp_gaf_decode_fifo().
 *  @param[in] gyro_fsr      Gyro FSR currently applied to raw gyro data read from FIFO.
 *  @param[in] prev_rgyr     Last raw gyr data received in previous FIFO frame.
 *  @param[out] rgyr_highres Decoded 20 bits high resolution gyro value.
 *  @return                  0 on success, negative value on error.
 */
int inv_imu_edmp_decode_gaf_rgyr_highres(inv_imu_device_t *s, const uint8_t hr_g[3],
                                         const gyro_config0_gyro_ui_fs_sel_t gyro_fsr,
                                         const int16_t prev_rgyr[3], int32_t rgyr_highres[3]);

/** @brief  Get APEX SIF output value - class index. 
 *  @param[in]  s            Pointer to device.
 *  @param[out] class_index  predicted class index.
 *  @return                  0 on success, negative value on error.
 */
int inv_imu_edmp_get_sif_class_index(inv_imu_device_t *s, int16_t *class_index);

/** @brief  Mask requested interrupt sources for edmp interrupt line passed in parameter.
 *  @param[in] s            Pointer to device.
 *  @param[in] edmp_int_nb  EDMP input interrupt line number that should be configured.
 *  @param[in] int_mask     Interrupt sources to mask.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_mask_int_src(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb,
                              uint8_t int_mask);

/** @brief  Unmask requested interrupt sources for edmp interrupt line passed in parameter.
 *  @param[in] s            Pointer to device.
 *  @param[in] edmp_int_nb  EDMP input interrupt line number that should be configured.
 *  @param[in] int_mask     Interrupt sources to unmask. 
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_unmask_int_src(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb,
                                uint8_t int_mask);

/** @brief  Setup EDMP to execute code in ROM.
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_configure(inv_imu_device_t *s);

/** @brief Run EDMP using the on-demand mechanism.
 *  @param[in] s            Pointer to device.
 *  @param[in] edmp_int_nb  EDMP input interrupt line.
 *  @return                 0 on success, negative value on error.
 */
int inv_imu_edmp_run_ondemand(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb);

/** @brief  Run EDMP using the on-demand mechanism to execute memset value in RAM range [start_addr, start_addr+size-1].
 *  @param[in] s           Pointer to device.
 *  @param[in] start_addr  RAM start address for which memset is to be done.
 *  @param[in] size        Size in bytes of RAM area to be set.
 *  @param[in] value       Value to be written to RAM area.
 *  @return                0 on success, negative value on error.
 */
int inv_imu_edmp_write_ram_area(inv_imu_device_t *s, uint16_t start_addr, uint16_t size,
                                uint8_t value);

/** @brief Wait until EDMP idle bit is set (means EDMP execution is completed).
 *  @param[in] s  Pointer to device.
 *  @return       0 on success, negative value on error.
 */
int inv_imu_edmp_wait_for_idle(inv_imu_device_t *s);

#ifdef __cplusplus
}
#endif

#endif /* _INV_IMU_EDMP_H_ */

/** @} */
