/*
 *
 * Copyright (c) [2024] by InvenSense, Inc.
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

#ifndef __INV_IMU_EDMP_APEX_MEMMAP_H__
#define __INV_IMU_EDMP_APEX_MEMMAP_H__

#ifdef __cplusplus
extern "C" {
#endif

/* use_case_bitmask
 *
 * ISR1 init request service ID depending on system usecase
 * Set bit 1 for usecase which does not require GAF
 * Set bit 3 for usecase which does not require Free-Fall
 * Set bit 4 for usecase which does not require TAP
 * Default: 0 (initialize all algo)
 */
#define EDMP_USE_CASE_BITMASK                                   0x5
#define EDMP_USE_CASE_BITMASK_SIZE                              1

/* ondemand_dynamic_service_request
 *
 * ISR1 on-demand service request ID
 * Set bit 1 to request set GAF parameters
 * Set bit 2 to request set GAF bias
 * Default: 0 (no ISR1 service requested)
 */
#define EDMP_ONDEMAND_DYNAMIC_SERVICE_REQUEST                   0x4
#define EDMP_ONDEMAND_DYNAMIC_SERVICE_REQUEST_SIZE              1

/* ondemand_static_service_request
 *
 * ISR2 on-demand service request ID
 * Set bit 0 to request memset service
 * Default: 0 (no ISR2 service requested)
 */
#define EDMP_ONDEMAND_STATIC_SERVICE_REQUEST                    0x118
#define EDMP_ONDEMAND_STATIC_SERVICE_REQUEST_SIZE               4

/* ondemand_memset_addr
 *
 * Start address of RAM area to be written by EDMP when requested by memset static service.
 */
#define EDMP_ONDEMAND_MEMSET_ADDR                               0x11c
#define EDMP_ONDEMAND_MEMSET_ADDR_SIZE                          2

/* ondemand_memset_size
 *
 * Length in bytes of RAM area to be written by EDMP when requested by memset static service.
 */
#define EDMP_ONDEMAND_MEMSET_SIZE                               0x120
#define EDMP_ONDEMAND_MEMSET_SIZE_SIZE                          2

/* ondemand_memset_value
 *
 * Value to be written by EDMP to RAM area when requested by memset static service.
 */
#define EDMP_ONDEMAND_MEMSET_VALUE                              0x11e
#define EDMP_ONDEMAND_MEMSET_VALUE_SIZE                         1

/* dmp_odr_last_init
 *
 * Encoded eDMP ODR value effective during last eDMP init request
 * 0x1 for eDMP ODR 25Hz
 * 0x2 for eDMP ODR 50Hz
 * 0x8 for eDMP ODR 100Hz
 * 0x80 for eDMP ODR 200Hz
 * 0x8000 for eDMP ODR 400Hz
 * 0x80000000 for eDMP ODR 800Hz
 */
#define EDMP_DMP_ODR_LAST_INIT                                  0x188
#define EDMP_DMP_ODR_LAST_INIT_SIZE                             4

/* global_mounting_matrix
 *
 * A q14 3x3 matrix applied to input accel and gyro data
 * Default:Identity matrix being
 * 0x4000   0      0  
 *   0    0x4000   0 
 *   0      0    0x4000
 */
#define EDMP_GLOBAL_MOUNTING_MATRIX                             0x1ac
#define EDMP_GLOBAL_MOUNTING_MATRIX_SIZE                        18

/* lowg_peak_th
 *
 * Threshold for accel values below which low-g state is detected.
 * Unit: g in q12
 * Range: [128 - 4096]
 * Default: 2048
 */
#define EDMP_LOWG_PEAK_TH                                       0x224
#define EDMP_LOWG_PEAK_TH_SIZE                                  2

/* lowg_peak_th_hyst
 *
 * Hysteresis value added to the low-g threshold after accel values get below threshold.
 * Unit: g in q12
 * Range: [128 - 1024]
 * Default: 128
 */
#define EDMP_LOWG_PEAK_TH_HYST                                  0x226
#define EDMP_LOWG_PEAK_TH_HYST_SIZE                             2

/* lowg_time_th
 *
 * Number of samples required to enter low-g state.
 * Unit: time in samples number
 * Range: [1 - 300]
 * Default: 13 (set for default ODR = 800 Hz, equivalent to 16 ms)
 */
#define EDMP_LOWG_TIME_TH                                       0x228
#define EDMP_LOWG_TIME_TH_SIZE                                  2

/* highg_peak_th
 *
 * Threshold for accel values above which high-g state is detected.
 * Unit: g in q12
 * Range: [1024 - 32768]
 * Default: 29696
 */
#define EDMP_HIGHG_PEAK_TH                                      0x218
#define EDMP_HIGHG_PEAK_TH_SIZE                                 2

/* highg_peak_th_hyst
 *
 * Hysteresis value subtracted from the high-g threshold after exceeding it.
 * Unit: g in q12
 * Range: [128 - 1024]
 * Default: 640
 */
#define EDMP_HIGHG_PEAK_TH_HYST                                 0x21a
#define EDMP_HIGHG_PEAK_TH_HYST_SIZE                            2

/* highg_time_th
 *
 * The number of samples device should stay above (highg_peak_th + highg_peak_th_hyst) before HighG state is triggered.
 * Unit: time in samples number
 * Range: [1-300]
 * Default: 1 (set for default ODR = 800 Hz, equivalent to 1.25 ms)
 */
#define EDMP_HIGHG_TIME_TH                                      0x21c
#define EDMP_HIGHG_TIME_TH_SIZE                                 2

/* ff_min_duration
 *
 * Minimum freefall duration. Shorter freefalls are ignored.
 * Unit: time in samples number
 * Range: [4 - 420]
 * Default: 57 (set for default ODR = 400 Hz, equivalent to 142 ms)
 */
#define EDMP_FF_MIN_DURATION                                    0x208
#define EDMP_FF_MIN_DURATION_SIZE                               4

/* ff_max_duration
 *
 * Maximum freefall duration. Longer freefalls are ignored.
 * Unit: time in samples number
 * Range: [12 - 1040]
 * Default: 285 (set for default ODR = 400 Hz, equivalent to 712 ms)
 */
#define EDMP_FF_MAX_DURATION                                    0x20c
#define EDMP_FF_MAX_DURATION_SIZE                               4

/* ff_debounce_duration
 *
 * Period after a freefall is signaled during which a new freefall will not be detected. Prevents false detection due to bounces.
 * Unit: time in samples number
 * Range: [75 - 3000]
 * Default: 800 (set for default ODR = 800 Hz, equivalent to 1 s)
 */
#define EDMP_FF_DEBOUNCE_DURATION                               0x210
#define EDMP_FF_DEBOUNCE_DURATION_SIZE                          4

/* ff_duration
 *
 * Duration of the freefall.
 * Unit: number of samples. Freefall duration in seconds / ACCEL_ODR_Hz
 */
#define EDMP_FF_DURATION                                        0x202
#define EDMP_FF_DURATION_SIZE                                   2

/* gaf_pdr_partition
 *
 * GAF partition reconfiguration in case GAF PDR is not 50 Hz and mag ODR is not 50 Hz.
 */
#define EDMP_GAF_PDR_PARTITION                                  0x154
#define EDMP_GAF_PDR_PARTITION_SIZE                             4

/* gaf_init_status
 *
 * GAF initialization status. Set to 1 by eDMP once GAF initialization is done.
 * Default: 0 (GAF initialization not performed)
 */
#define EDMP_GAF_INIT_STATUS                                    0x924
#define EDMP_GAF_INIT_STATUS_SIZE                               1

/* gaf_mode
 *
 * GAF configuration of eDMP system architecture.
 * bit 0:
 * - 0 if there is no mag (AG only)
 * - 1 if there is ICT-1531x (calib mag will be run)
 * bit 1:
 * - 0 if there is no calib gyro expected (AM only)
 * - 1 if there is calib gyro expected (calib gyro will be run)
 * bit 2:
 * - 0 if automatic MRM sequence is disabled
 * - 1 if automatic MRM is run depending on mag data value
 * bit 3
 * - 0 if push in FIFO is to be made at GAF PDR (default)
 * - 1 if no push in FIFO is to be done by DMP 
 * Default: 0x03 (calibration mag, calibration gyro, no auto MRM, push in FIFO)
 */
#define EDMP_GAF_MODE                                           0x1be
#define EDMP_GAF_MODE_SIZE                                      1

/* gaf_ondemand_mrm_request
 *
 * Request MRM to be run during next eDMP execution. Set to not null value to request MRM.
 * Default: 0x0
 */
#define EDMP_GAF_ONDEMAND_MRM_REQUEST                           0x1c1
#define EDMP_GAF_ONDEMAND_MRM_REQUEST_SIZE                      1

/* gaf_config_acc_odr_us
 *
 * GAF accelerometer input sensor data rate.
 * Range: {1250;2500;5000;10000;20000}
 * Unit: us
 * Default: 10000
 */
#define EDMP_GAF_CONFIG_ACC_ODR_US                              0x288
#define EDMP_GAF_CONFIG_ACC_ODR_US_SIZE                         4

/* gaf_config_gyr_odr_us
 *
 * GAF gyroscope input sensor data rate.
 * Range: {1250;2500;5000;10000;20000}
 * Unit: us
 * Default: 10000
 */
#define EDMP_GAF_CONFIG_GYR_ODR_US                              0x28c
#define EDMP_GAF_CONFIG_GYR_ODR_US_SIZE                         4

/* gaf_config_acc_pdr_us
 *
 * GAF accelerometer processing data rate, sensor data are averaged if sensor is faster than GAF accelerometer PDR.
 * Range: {1250;2500;5000;10000;20000}
 * Unit: us
 * Default: 10000
 */
#define EDMP_GAF_CONFIG_ACC_PDR_US                              0x290
#define EDMP_GAF_CONFIG_ACC_PDR_US_SIZE                         4

/* gaf_config_gyr_pdr_us
 *
 * GAF gyroscope processing data rate, sensor data are averaged if sensor is faster than GAF gyroscope PDR. Corresponds to GAF output data rate.
 * Range: {1250;2500;5000;10000;20000}
 * Unit: us
 * Default: 10000
 */
#define EDMP_GAF_CONFIG_GYR_PDR_US                              0x294
#define EDMP_GAF_CONFIG_GYR_PDR_US_SIZE                         4

/* gaf_config_stationary_angle_duration_us
 *
 * Duration of stationary detection.
 * Unit: us
 * Default: 500000 (0.5seconds)
 */
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_DURATION_US            0x298
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_DURATION_US_SIZE       4

/* gaf_config_stationary_angle_threshold_deg_q16
 *
 * Threshold on angular deviation for stationary detection.
 * Unit: degree s32q16
 * Default: 65536 (1 degree)
 */
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_THRESHOLD_DEG_Q16      0x29c
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_THRESHOLD_DEG_Q16_SIZE 4

/* gaf_config_fus_low_speed_drift_roll_pitch
 *
 * Gyroscope integration error related to bias precision. Higher value increases accel roll/pitch correction in steady state.
 * Unit: LSB
 * Default : 20
 */
#define EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_ROLL_PITCH          0x2a0
#define EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_ROLL_PITCH_SIZE     4

/* gaf_config_pll_clock_variation
 *
 * Error on the clock in same format as reg SW_PLL1_TRIM. Calculated as (actual_clk - target_clk) / target_clk * (2^7 - 1) / 5 * 100.
 * Default : 0
 */
#define EDMP_GAF_CONFIG_PLL_CLOCK_VARIATION                     0x2ac
#define EDMP_GAF_CONFIG_PLL_CLOCK_VARIATION_SIZE                1

/* gaf_config_stationary_angle_enable
 *
 * Enable/disable stop integration of stationary angle.
 * Default : 0
 */
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_ENABLE                 0x2ad
#define EDMP_GAF_CONFIG_STATIONARY_ANGLE_ENABLE_SIZE            1

/* gaf_config_run_spherical
 *
 * Enable fusion or only calibration : 0 to run only calibration steps, 1 to run also fusion/spherical steps.
 * Default : 1
 */
#define EDMP_GAF_CONFIG_RUN_SPHERICAL                           0x2ae
#define EDMP_GAF_CONFIG_RUN_SPHERICAL_SIZE                      1

/* gaf_config_loose_gyr_cal_sample_num_log2
 *
 * Gyroscope calibration number of samples used to estimate metric1 and metric2, and minimum gyroscope calibration duration.
 * Unit: number of samples in log2
 * Range: [6 - 8]
 * Default: 7 (so 2^7 = 128 samples)
 */
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_SAMPLE_NUM_LOG2           0x6c8
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_SAMPLE_NUM_LOG2_SIZE      4

/* gaf_config_golden_bias_timer
 *
 * Validity timer of the strict bias in sample number.
 * Default: 1440000 (so 8 hours at 50Hz)
 */
#define EDMP_GAF_CONFIG_GOLDEN_BIAS_TIMER                       0x6c0
#define EDMP_GAF_CONFIG_GOLDEN_BIAS_TIMER_SIZE                  4

/* gaf_config_gyr_dt_us
 *
 * Gyro ODR corrected with PLL clock correction.
 * Unit: us
 * Default: 20000
 */
#define EDMP_GAF_CONFIG_GYR_DT_US                               0x4a0
#define EDMP_GAF_CONFIG_GYR_DT_US_SIZE                          4

/* gaf_config_mag_dt_us
 *
 * Mag ODR as configured for magnetometer-based fusion.
 * Unit: us
 * Default: 20000
 */
#define EDMP_GAF_CONFIG_MAG_DT_US                               0x4a8
#define EDMP_GAF_CONFIG_MAG_DT_US_SIZE                          4

/* gaf_config_magcal_dt_us
 *
 * Mag ODR as configured for magnetometer calibration. Must match gaf_config_mag_dt_us value at any time.
 * Unit: us
 * Default: 20000
 */
#define EDMP_GAF_CONFIG_MAGCAL_DT_US                            0x818
#define EDMP_GAF_CONFIG_MAGCAL_DT_US_SIZE                       4

/* gaf_config_mag_softiron_matrix
 *
 * A q30 3x3 matrix applied to input mag data
 * Important: Because the default value is all zero's, it is expected to set it at least to Identity matrix in order to get magnetometer data:
 * 0x40000000      0           0
 *     0       0x40000000      0
 *     0           0       0x40000000
 * Soft-iron will be estimated on the final platform and the computed value (often different from Identity matrix) will need to be applied.
 */
#define EDMP_GAF_CONFIG_MAG_SOFTIRON_MATRIX                     0x264
#define EDMP_GAF_CONFIG_MAG_SOFTIRON_MATRIX_SIZE                36

/* gaf_config_fus_high_speed_drift
 *
 * Percentage of error (covering gyroscope sensitivity, timestamp and quantization) on gyroscope integration.
 * Unit: LSB with 2^15 LSB = 1% error
 * Default : 262144 (so 8% error)
 */
#define EDMP_GAF_CONFIG_FUS_HIGH_SPEED_DRIFT                    0x4f8
#define EDMP_GAF_CONFIG_FUS_HIGH_SPEED_DRIFT_SIZE               4

/* gaf_config_fus_low_speed_drift_yaw
 *
 * Gyroscope integration error related to bias precision. Higher value increases compass yaw correction in steady state.
 * Unit: LSB
 * Default : 20
 */
#define EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_YAW                 0x2a4
#define EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_YAW_SIZE            4

/* gaf_config_loose_gyr_cal_stationary_duration_us
 *
 * Duration for no motion gyroscope bias calibration.
 * Unit: us
 * Default value: 500000
 */
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_STATIONARY_DURATION_US    0x5cc
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_STATIONARY_DURATION_US_SIZE 4

/* gaf_config_loose_gyr_cal_threshold_metric1
 *
 * Stationary detection threshold of 1st metric for the loose bias calibration. Threshold is compare against absolute value of delta between current gyro value and last gyro value in an analysis window.
 * Unit: 2000dps = 2^20
 * Default value: 1200 (so 2.28dps)
 */
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC1         0x5ec
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC1_SIZE    4

/* gaf_config_loose_gyr_cal_threshold_metric2
 *
 * Stationary detection threshold of 2st metric for the loose bias calibration.
 * Default value: 60000 (no unit).
 */
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC2         0x5dc
#define EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC2_SIZE    4

/* gaf_config_strict_gyr_cal_threshold_metric1
 *
 * Stationary detection threshold of 1st metric for the strict bias calibration. Threshold is compare against absolute value of delta between current gyro value and last gyro value in an analysis window.
 * Unit: 2000dps = 2^20
 * Default value: 300 (so 0.57dps)
 */
#define EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC1        0x6b8
#define EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC1_SIZE   4

/* gaf_config_strict_gyr_cal_threshold_metric2
 *
 * Stationary detection threshold of 2st metric for the strict bias calibration.
 * Default value: 400 (no unit)
 */
#define EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC2        0x6bc
#define EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC2_SIZE   4

/* gaf_config_gyr_bias_reject_th
 *
 * Gyro bias rejection threshold above which device is considered as moving. Threshold is compare against absolute value of delta between current estimated gyro bias and last estimated gyro bias in an analysis window.
 * Unit: 2000dps = 2^30.
 * Default value: 3650722 (so 6.8dps)
 */
#define EDMP_GAF_CONFIG_GYR_BIAS_REJECT_TH                      0x5e0
#define EDMP_GAF_CONFIG_GYR_BIAS_REJECT_TH_SIZE                 4

/* gaf_config_acc_filtering_Npoints_log2
 *
 * Accelerometer filtering mean value.
 * Unit: sample number in log2
 * Default: 5 (so 32 samples)
 */
#define EDMP_GAF_CONFIG_ACC_FILTERING_NPOINTS_LOG2              0x6b4
#define EDMP_GAF_CONFIG_ACC_FILTERING_NPOINTS_LOG2_SIZE         4

/* gaf_config_acc_square_sin_angle_motion_detect_th
 *
 * Square of sinus on angle threshold to reject gyroscope calibration.
 * Unit: (sin(theta)2)*225
 * Default: 4318 (so 0.65 degree)
 */
#define EDMP_GAF_CONFIG_ACC_SQUARE_SIN_ANGLE_MOTION_DETECT_TH   0x6b0
#define EDMP_GAF_CONFIG_ACC_SQUARE_SIN_ANGLE_MOTION_DETECT_TH_SIZE 4

/* gaf_config_golden_bias_temperature_validity
 *
 * Validity temperature variation of the strict bias.
 * Unit: degree C s32q16
 * Default: 983040 (so 15 degree C)
 */
#define EDMP_GAF_CONFIG_GOLDEN_BIAS_TEMPERATURE_VALIDITY        0x6c4
#define EDMP_GAF_CONFIG_GOLDEN_BIAS_TEMPERATURE_VALIDITY_SIZE   4

/* gaf_config_fus_measurement_covariance_acc
 *
 * Accelerometer measurement covariance.
 * Unit: g^2 s32q15
 * Default: 32768 (so 0.5g^2)
 */
#define EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_ACC          0x4d8
#define EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_ACC_SIZE     4

/* gaf_config_fus_acceleration_rejection
 *
 * Linear acceleration rejection.
 * Unit: m/s^2 s32q30
 * Range: [0 - 1073741824]
 * Default: 1073741824 (so 1.0, being maximum rejection)
 */
#define EDMP_GAF_CONFIG_FUS_ACCELERATION_REJECTION              0x4f4
#define EDMP_GAF_CONFIG_FUS_ACCELERATION_REJECTION_SIZE         4

/* gaf_saved_acc_bias_1g_q16
 *
 * Accelerometer bias to start algorithm with (one value per axis).
 * Unit: g in s32q16
 * Default: 0;0;0
 */
#define EDMP_GAF_SAVED_ACC_BIAS_1G_Q16                          0x8c8
#define EDMP_GAF_SAVED_ACC_BIAS_1G_Q16_SIZE                     12

/* gaf_saved_acc_accuracy
 *
 * Accelerometer accuracy from 0 (non calibrated) to 3 (well calibrated) to start algorithm with.
 * Range : [0 - 3]
 * Default: 0
 */
#define EDMP_GAF_SAVED_ACC_ACCURACY                             0x923
#define EDMP_GAF_SAVED_ACC_ACCURACY_SIZE                        1

/* gaf_gyr_bias_dps_q12
 *
 * Gyroscope bias to start algorithm with (one value per axis), also acts as latest gyroscope bias computed value to be saved.
 * Unit: dps in s32q12
 * Default: 0;0;0
 */
#define EDMP_GAF_GYR_BIAS_DPS_Q12                               0x6cc
#define EDMP_GAF_GYR_BIAS_DPS_Q12_SIZE                          12

/* gaf_read_gyr_accuracy
 *
 * Latest gyroscope accuracy computed to be saved.
 * Range : [0 - 3]
 * Default: 0
 */
#define EDMP_GAF_READ_GYR_ACCURACY                              0x6e4
#define EDMP_GAF_READ_GYR_ACCURACY_SIZE                         4

/* gaf_saved_gyr_accuracy
 *
 * Gyroscope accuracy from 0 (non calibrated) to 3 (well calibrated) to start algorithm with.
 * Range : [0 - 3]
 * Default: 0
 */
#define EDMP_GAF_SAVED_GYR_ACCURACY                             0x5bc
#define EDMP_GAF_SAVED_GYR_ACCURACY_SIZE                        4

/* gaf_gyr_bias_temperature_deg_q16
 *
 * Temperature to start algorithm with, also acts as latest temperature associated with computed gyro bias.
 * Unit: degree C in s32q16
 * Default: 0
 */
#define EDMP_GAF_GYR_BIAS_TEMPERATURE_DEG_Q16                   0x6a0
#define EDMP_GAF_GYR_BIAS_TEMPERATURE_DEG_Q16_SIZE              4

/* gaf_saved_mag_bias_ut_q16
 *
 * Magnetometer bias to start algorithm with (one value per axis).
 * Unit: uT in s32q16
 * Default: 0;0;0
 */
#define EDMP_GAF_SAVED_MAG_BIAS_UT_Q16                          0x774
#define EDMP_GAF_SAVED_MAG_BIAS_UT_Q16_SIZE                     12

/* gaf_mag_bias_scaled_ut_q11
 *
 * Magnetometer bias to start algorithm with (one value per axis).
 * Unit: uT in s32q11
 * Default: 0;0;0
 */
#define EDMP_GAF_MAG_BIAS_SCALED_UT_Q11                         0x780
#define EDMP_GAF_MAG_BIAS_SCALED_UT_Q11_SIZE                    12

/* gaf_mag_bias_selected_scaled_ut_q11
 *
 * Magnetometer bias to start algorithm with (one value per axis).
 * Unit: uT in s32q11
 * Default: 0;0;0
 */
#define EDMP_GAF_MAG_BIAS_SELECTED_SCALED_UT_Q11                0x78c
#define EDMP_GAF_MAG_BIAS_SELECTED_SCALED_UT_Q11_SIZE           12

/* gaf_read_mag_bias_ut_q16
 *
 * Latest magnetometer bias computed to be saved (one value per axis), any new mag bias must also be applied in this RAM area.
 * Unit: uT in s32q16
 * Default: 0;0;0
 */
#define EDMP_GAF_READ_MAG_BIAS_UT_Q16                           0x974
#define EDMP_GAF_READ_MAG_BIAS_UT_Q16_SIZE                      12

/* gaf_read_mag_accuracy
 *
 * Latest magnetometer accuracy from 0 (non calibrated) to 3 (well calibrated) to be saved.
 * Range : [0 - 3]
 * Default: 0
 */
#define EDMP_GAF_READ_MAG_ACCURACY                              0x981
#define EDMP_GAF_READ_MAG_ACCURACY_SIZE                         1

/* gaf_saved_mag_accuracy
 *
 * Magnetometer accuracy from 0 (non calibrated) to 3 (well calibrated) to start algorithm with.
 * Range : [0 - 3]
 * Default: 0
 */
#define EDMP_GAF_SAVED_MAG_ACCURACY                             0x770
#define EDMP_GAF_SAVED_MAG_ACCURACY_SIZE                        4

/* gaf_saved_mag_accuracy_covariance
 *
 * Magnetometer maximum covariance inherited from new mag accuracy to be applied.
 * Range : {2499 for accuracy 3, 4999 for accuracy 2, 9999 for accuracy 1, 500000 for accuracy 0}
 * Default: 500000
 */
#define EDMP_GAF_SAVED_MAG_ACCURACY_COVARIANCE                  0x76c
#define EDMP_GAF_SAVED_MAG_ACCURACY_COVARIANCE_SIZE             4

/* gaf_config_fus_measurement_covariance_mag
 *
 * Magnetometer measurement covariance.
 * Unit: uT^2 s32q16
 * Default: 65536 (so 1.0uT^2)
 */
#define EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_MAG          0x4b8
#define EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_MAG_SIZE     4

/* gaf_config_fus_mag_anomaly_rejection
 *
 * Magnetometer anomalies rejection.
 * Unit: uT^2 s32q30
 * Default: 1073741824 (so 1.0uT^2)
 */
#define EDMP_GAF_CONFIG_FUS_MAG_ANOMALY_REJECTION               0x4bc
#define EDMP_GAF_CONFIG_FUS_MAG_ANOMALY_REJECTION_SIZE          4

/* gaf_config_thresh_yaw_stop_convergence
 *
 * Parameter to stop yaw error correction when value to correct is lower than threshold.
 * Unit: rad s32q30
 * Default: -1 (deactivated feature)
 */
#define EDMP_GAF_CONFIG_THRESH_YAW_STOP_CONVERGENCE             0x4d0
#define EDMP_GAF_CONFIG_THRESH_YAW_STOP_CONVERGENCE_SIZE        4

/* gaf_config_thresh_yaw_smooth_convergence
 *
 * Parameter to control yaw error correction speed as a percentage of the gyro speed.
 * Unit: percentage in s32q15
 * Default: -1 (deactivated feature)
 */
#define EDMP_GAF_CONFIG_THRESH_YAW_SMOOTH_CONVERGENCE           0x4d4
#define EDMP_GAF_CONFIG_THRESH_YAW_SMOOTH_CONVERGENCE_SIZE      4

/* gaf_config_mag_thr_huge_disturbance
 *
 * Huge disturbance threshold to reset the algorithm.
 * Unit: uT in s32q11
 * Default: 409600 (200 uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_HUGE_DISTURBANCE                0x820
#define EDMP_GAF_CONFIG_MAG_THR_HUGE_DISTURBANCE_SIZE           4

/* gaf_config_mag_thr_anomaly_radius
 *
 * Difference between current radius and measurement to switch to disturbed state.
 * Unit: uT in s32q11
 * Default: 30720 (15 uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_ANOMALY_RADIUS                  0x824
#define EDMP_GAF_CONFIG_MAG_THR_ANOMALY_RADIUS_SIZE             4

/* gaf_config_mag_thr_select_angle
 *
 * Minimum angular variation between 2 consecutive measurements (using gyro).
 * Unit: s32q30
 * Default: 1050277989 (cos(12deg))
 */
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_ANGLE                    0x828
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_ANGLE_SIZE               4

/* gaf_config_mag_thr_select_distance_gyro
 *
 * Minimum distance variation between 2 consecutive measurements (using gyro).
 * Unit: uT in s32q11
 * Default: 10240 (5uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_GYRO            0x82c
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_GYRO_SIZE       4

/* gaf_config_mag_thr_select_distance_nogyro
 *
 * Minimum distance variation between 2 consecutive measurements (not using gyro).
 * Unit: uT in s32q11
 * Default: 30720 (15uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_NOGYRO          0x830
#define EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_NOGYRO_SIZE     4

/* gaf_config_mag_q0_standalone
 *
 * Magnetometer calibration model covariance.
 * Default: 3
 */
#define EDMP_GAF_CONFIG_MAG_Q0_STANDALONE                       0x834
#define EDMP_GAF_CONFIG_MAG_Q0_STANDALONE_SIZE                  4

/* gaf_config_mag_r0_standalone
 *
 * Magnetometer calibration measurement covariance.
 * Default: 400000
 */
#define EDMP_GAF_CONFIG_MAG_R0_STANDALONE                       0x838
#define EDMP_GAF_CONFIG_MAG_R0_STANDALONE_SIZE                  4

/* gaf_config_mag_q0_assisted
 *
 * Magnetometer calibration model covariance for gyro assisted model.
 * Default: 1
 */
#define EDMP_GAF_CONFIG_MAG_Q0_ASSISTED                         0x83c
#define EDMP_GAF_CONFIG_MAG_Q0_ASSISTED_SIZE                    4

/* gaf_config_mag_r0_assisted
 *
 * Magnetometer calibration measurement covariance for gyro assisted model.
 * Default: 5000
 */
#define EDMP_GAF_CONFIG_MAG_R0_ASSISTED                         0x840
#define EDMP_GAF_CONFIG_MAG_R0_ASSISTED_SIZE                    4

/* gaf_config_mag_thr_max_radius_jump
 *
 * Maximum radius jump between 2 solutions.
 * Unit: uT in s32q11
 * Default: 40960 (20uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS_JUMP                 0x844
#define EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS_JUMP_SIZE            4

/* gaf_config_mag_thr_max_radius
 *
 * Maximum field radius.
 * Unit: uT in s32q11
 * Default: 256000 (125uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS                      0x848
#define EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS_SIZE                 4

/* gaf_config_mag_thr_min_radius
 *
 * Minimum field radius.
 * Unit: uT in s32q11
 * Default: 36864 (18uT)
 */
#define EDMP_GAF_CONFIG_MAG_THR_MIN_RADIUS                      0x84c
#define EDMP_GAF_CONFIG_MAG_THR_MIN_RADIUS_SIZE                 4

/* gaf_config_mag_thr_lock_acc
 *
 * Threshold of steady accelerometer.
 * Default: -1 (Disable the Lock mode feature)
 */
#define EDMP_GAF_CONFIG_MAG_THR_LOCK_ACC                        0x4c4
#define EDMP_GAF_CONFIG_MAG_THR_LOCK_ACC_SIZE                   4

/* gaf_config_mag_calibration_condition
 *
 * Control if we check additional condition on covariance in magnetometer calibration.
 * Default: 1
 */
#define EDMP_GAF_CONFIG_MAG_CALIBRATION_CONDITION               0x850
#define EDMP_GAF_CONFIG_MAG_CALIBRATION_CONDITION_SIZE          2

/* sif_time_feas_config
 *
 * Structure member of the SIF configuration generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TIME_FEAS_CONFIG                               0x9dc
#define EDMP_SIF_TIME_FEAS_CONFIG_SIZE                          2

/* sif_filter
 *
 * Structure member of the SIF filter configuration generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_FILTER                                         0xa5c
#define EDMP_SIF_FILTER_SIZE                                    76

/* sif_cconfig
 *
 * Structure member of the SIF filter configuration generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_CCONFIG                                        0xa34
#define EDMP_SIF_CCONFIG_SIZE                                   12

/* sif_tconfig
 *
 * Structure member of the SIF filter configuration generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TCONFIG                                        0xa40
#define EDMP_SIF_TCONFIG_SIZE                                   24

/* sif_tree_thresholds
 *
 * Structure member of the SIF model Decision Tree generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TREE_THRESHOLDS                                0x138c
#define EDMP_SIF_TREE_THRESHOLDS_SIZE                           2

/* sif_tree_featureids
 *
 * Structure member of the SIF model Decision Tree generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TREE_FEATUREIDS                                0x158a
#define EDMP_SIF_TREE_FEATUREIDS_SIZE                           1

/* sif_tree_nextnoderight
 *
 * Structure member of the SIF model Decision Tree generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TREE_NEXTNODERIGHT                             0x1689
#define EDMP_SIF_TREE_NEXTNODERIGHT_SIZE                        1

/* sif_tree_thresholdsshift
 *
 * Structure member of the SIF model Decision Tree generated with TDK SIF software tools. It shall be loaded as-is based on TDK recommendation.
 */
#define EDMP_SIF_TREE_THRESHOLDSSHIFT                           0x1788
#define EDMP_SIF_TREE_THRESHOLDSSHIFT_SIZE                      1

/* sif_pdr_partition
 *
 * SIF partition reconfiguration in case SIF PDR is not 50 Hz.
 */
#define EDMP_SIF_PDR_PARTITION                                  0x138
#define EDMP_SIF_PDR_PARTITION_SIZE                             4

/* sif_interrupt_control
 *
 * SIF interrupt control: repeated interrupt even if sif_class_index has not changed (0) or only trigger interrupt if sif_class_index has changed (1).
 * Default: 0
 */
#define EDMP_SIF_INTERRUPT_CONTROL                              0x1c3
#define EDMP_SIF_INTERRUPT_CONTROL_SIZE                         1

/* sif_class_index
 *
 * Index of SIF predicted gesture class.
 */
#define EDMP_SIF_CLASS_INDEX                                    0x9f4
#define EDMP_SIF_CLASS_INDEX_SIZE                               2

/* tap_min_jerk
 *
 * The minimal value of jerk to be considered as a tap candidate.
 * Unit: LSB with 1 LSB = 1g / 2^12 (of the jerk value)
 * Range: [0 - 16384]
 * Default: 4608 (equivalent to 1.125 g) 
 */
#define EDMP_TAP_MIN_JERK                                       0x230
#define EDMP_TAP_MIN_JERK_SIZE                                  2

/* tap_tmax
 *
 * Size of the analysis window to detect tap events (single, double or triple tap)
 * Unit: time in sample number
 * Range: [49 - 496]
 * Default : 248 (set for default ODR = 400 Hz, equivalent to 0.620 s)
 */
#define EDMP_TAP_TMAX                                           0x232
#define EDMP_TAP_TMAX_SIZE                                      2

/* tap_tmin
 *
 * Single tap window, sub-windows within Tmax to detect single-tap event.
 * Unit: time in sample number
 * Range: [24 - 184]
 * Default: 66 (set for default ODR = 400 Hz, equivalent to 0.165 s)
 */
#define EDMP_TAP_TMIN                                           0x234
#define EDMP_TAP_TMIN_SIZE                                      1

/* tap_max_peak_tol
 *
 * Maximum peak tolerance is the percentage of pulse amplitude to get the smudge threshold for rejection.
 * Unit: N/A
 * Range: [1 (12.5%) 2 (25.0%) 3 (37.5%) 4 (50.0 %)]
 * Default: 2
 */
#define EDMP_TAP_MAX_PEAK_TOL                                   0x236
#define EDMP_TAP_MAX_PEAK_TOL_SIZE                              1

/* tap_smudge_reject_thr
 *
 * Max acceptable number of samples (jerk value) over tap_max_peak_tol during the Tmin window. Over this value, Tap event is rejected
 * unit: time in number of samples
 * range: [13 - 92]
 * Default: 34 (set for default ODR = 400 Hz, equivalent to 0.085 s)
 */
#define EDMP_TAP_SMUDGE_REJECT_THR                              0x235
#define EDMP_TAP_SMUDGE_REJECT_THR_SIZE                         1

/* tap_tavg
 *
 * Energy measurement window size to determine the tap axis associated with the 1st tap.
 * Unit: time in sample number
 * Range: [1 ; 2 ; 4 ; 8]
 * Default: 8
 * 
 */
#define EDMP_TAP_TAVG                                           0x237
#define EDMP_TAP_TAVG_SIZE                                      1

/* tap_odr
 *
 * TAP execution ODR:
 * 0: 200Hz, 1: 400Hz, 2: 800Hz.
 * Unit: N/A
 * Range: [0 ; 1 ; 2]
 * Default: 1 (400Hz)
 * 
 */
#define EDMP_TAP_ODR                                            0x238
#define EDMP_TAP_ODR_SIZE                                       1

/* tap_max
 *
 * Maximal number of tap quantity detected to be valid.
 * Unit: N/A
 * Range: [1 (single) ; 2 (double) ; 3 (triple)]
 * Default: 2 (double tap)
 * 
 */
#define EDMP_TAP_MAX                                            0x239
#define EDMP_TAP_MAX_SIZE                                       1

/* tap_min
 *
 * Minimal number of tap quantity detected to be valid.
 * Unit: N/A
 * Range: [1 (single) ; 2 (double) ; 3 (triple)]
 * Default: 2 (double tap)
 * 
 */
#define EDMP_TAP_MIN                                            0x23a
#define EDMP_TAP_MIN_SIZE                                       1

/* tap_num
 *
 * type of the last reported TAP event:
 * 0: no tap, 1: single tap, 2: double tap, 3:triple tap
 */
#define EDMP_TAP_NUM                                            0x7
#define EDMP_TAP_NUM_SIZE                                       1

/* tap_axis
 *
 * Indicate the axis of the tap in the device frame
 * 0: ax, 1: ay, 2: az
 */
#define EDMP_TAP_AXIS                                           0x8
#define EDMP_TAP_AXIS_SIZE                                      1

/* tap_dir
 *
 * Indicate the direction of the tap in the device frame
 * 0: positive, 1: negative
 */
#define EDMP_TAP_DIR                                            0x9
#define EDMP_TAP_DIR_SIZE                                       1

/* double_tap_timing
 *
 * In case of double tap, indicate the sample count between the two detected pulses. Double tap timing in seconds is double_tap_timing / TAP_ODR in Hz.
 */
#define EDMP_DOUBLE_TAP_TIMING                                  0x260
#define EDMP_DOUBLE_TAP_TIMING_SIZE                             2

/* triple_tap_timing
 *
 * In case of triple tap, indicate the sample count between the first and third detected pulses. Triple tap timing in seconds is triple_tap_timing / TAP_ODR in Hz.
 */
#define EDMP_TRIPLE_TAP_TIMING                                  0x262
#define EDMP_TRIPLE_TAP_TIMING_SIZE                             2

/* power_save_time
 *
 * Time of inactivity after which eDMP goes in power save mode.
 * Unit: time in sample number
 * Range: [0 - 4294967295] 
 * Default value: 6400
 */
#define EDMP_POWER_SAVE_TIME                                    0x40
#define EDMP_POWER_SAVE_TIME_SIZE                               4

#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMP_APEX_MEMMAP_H__
