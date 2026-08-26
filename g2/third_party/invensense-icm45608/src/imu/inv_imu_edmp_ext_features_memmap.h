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

#ifndef __INV_IMU_EDMP_EXT_FEATURES_MEMMAP_H__
#define __INV_IMU_EDMP_EXT_FEATURES_MEMMAP_H__

#ifdef __cplusplus
extern "C" {
#endif

/* b2s_mounting_matrix
 *
 * Mounting matrix to apply the accelerometer data before bring-to-see computation, as a bit-mask combination of operations.
 * bit0: flip Y, flip Z
 * bit1: flip X, flip Z
 * bit2: swap X/Y, flip Z
 * Range: [0 - 7]
 * Default: 0 being identity matrix
 */
#define EDMP_B2S_MOUNTING_MATRIX                                0x100c
#define EDMP_B2S_MOUNTING_MATRIX_SIZE                           1

/* b2s_one_g_value
 *
 * One gee value to be used as reference to trigger Bring-To-See.
 * Unit: 1gee = 2^12
 * Default: 4096
 */
#define EDMP_B2S_ONE_G_VALUE                                    0x1010
#define EDMP_B2S_ONE_G_VALUE_SIZE                               4

/* b2s_settings_dev_norm_max
 *
 * Hysteresis added or removed to norm estimate and Y axis constrains value for RevB2S.
 * Unit: LSB, with 1 LBS = 1g / 2^12
 * Range: [1 - 2048]
 * Default: 700 (corresponding to 0.1709g)
 */
#define EDMP_B2S_SETTINGS_DEV_NORM_MAX                          0x1014
#define EDMP_B2S_SETTINGS_DEV_NORM_MAX_SIZE                     4

/* b2s_settings_sin_limit
 *
 * Maximum threshold on absolute value of X axis in b2s position. Link to the sinus value of inclination angle on X axis.
 * Unit: LSB, with 1 LBS = 1g / 2^12
 * Range: [300 - 3000]
 * Default: 2048 (corresponding to 30deg)
 */
#define EDMP_B2S_SETTINGS_SIN_LIMIT                             0x1018
#define EDMP_B2S_SETTINGS_SIN_LIMIT_SIZE                        4

/* b2s_settings_fast_limit
 *
 * Threshold of minimal motion to be detected as "Fast motion".
 * Unit: No unit, filtered data
 * Range: [300 - 3000]
 * Default: 200
 */
#define EDMP_B2S_SETTINGS_FAST_LIMIT                            0x101c
#define EDMP_B2S_SETTINGS_FAST_LIMIT_SIZE                       4

/* b2s_settings_static_limit
 *
 * Threshold to determine static phase required after the gesture B2S to validate it.
 * Unit: No unit, filtered data
 * Default: 1400
 */
#define EDMP_B2S_SETTINGS_STATIC_LIMIT                          0x1028
#define EDMP_B2S_SETTINGS_STATIC_LIMIT_SIZE                     4

/* b2s_settings_thr_cos_ang
 *
 * RevB2S threshold, condition satisfied when moving away from bring2see orientation position by more than threshold angle corresponding to the cosine angle.
 * Unit: cosine value of angle in q30
 * Default: 1057429273 (so 10deg)
 */
#define EDMP_B2S_SETTINGS_THR_COS_ANG                           0x102c
#define EDMP_B2S_SETTINGS_THR_COS_ANG_SIZE                      4

/* b2s_settings_limit_inf
 *
 * Lower bound limit of the last sample's norm considered for b2s detection, in s32q24. Value corresponding to the squared norm value of 0.687g2 is: 11532816
 * Unit: s32q24
 */
#define EDMP_B2S_SETTINGS_LIMIT_INF                             0x1034
#define EDMP_B2S_SETTINGS_LIMIT_INF_SIZE                        4

/* b2s_settings_limit_sup
 *
 * Higher bound limit of the last sample's norm considered for b2s detection, in s32q24. Value corresponding to the squared norm value of 1.371g2 is: 23001616
 * Unit: s32q24
 */
#define EDMP_B2S_SETTINGS_LIMIT_SUP                             0x1038
#define EDMP_B2S_SETTINGS_LIMIT_SUP_SIZE                        4

/* b2s_settings_rev_x_limit
 *
 * Condition of reverse bring2see on X axis value to ensure Rev-B2S when arm points down.
 * Unit: LSB, with 1 LBS = 1g / 2^12
 * Default: 3680 (corresponding to 0.8984g)
 */
#define EDMP_B2S_SETTINGS_REV_X_LIMIT                           0x1030
#define EDMP_B2S_SETTINGS_REV_X_LIMIT_SIZE                      4

/* b2s_settings_sin_flat_angle
 *
 * Condition to detect the flat position and reject B2S interrupt at return to rest position.
 * Unit: LSB, with 1 LBS = 1g / 2^12
 * Default: 2048 (corresponding to 30Â°)
 */
#define EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE                        0x103c
#define EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE_SIZE                   4

/* b2s_settings_timer_flat_reject
 *
 * A timer to disable flat rejection when age of the last no-flat B2S detection is over the timer.
 * Unit: sample number - ODR dependent
 * Default: 350 (corresponding to 7s at 50Hz)
 */
#define EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT                     0x1040
#define EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT_SIZE                4

/* b2s_settings_fast_motion_age_limit
 *
 * Time limit between last "Fast motion" and b2s position.
 * Unit: sample number - ODR dependent
 * Default: 20 (corresponding to 400ms at 50Hz)
 */
#define EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT                 0x1020
#define EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT_SIZE            2

/* b2s_settings_fast_motion_time_limit
 *
 * Minimum time where the criterion is above the threshold  to be classified as "Fast motion".
 * Unit: sample number - ODR dependent
 * Default: 4 (corresponding to 80ms at 50Hz)
 */
#define EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT                0x1022
#define EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT_SIZE           2

/* b2s_settings_age_limit
 *
 * Minimum time between 2 event b2s.
 * Unit: sample number - ODR dependent
 * Default: 50 (corresponding to 1s at 50Hz)
 */
#define EDMP_B2S_SETTINGS_AGE_LIMIT                             0x1024
#define EDMP_B2S_SETTINGS_AGE_LIMIT_SIZE                        2

/* b2s_settings_rev_latency_th
 *
 * Condition of RevB2S should be maintained at least during RevB2sLatencyTh.
 * Unit: sample number - ODR dependent
 * Default: 25 (corresponding to 0.5s at 50Hz)
 */
#define EDMP_B2S_SETTINGS_REV_LATENCY_TH                        0x1026
#define EDMP_B2S_SETTINGS_REV_LATENCY_TH_SIZE                   2

/* aid_win_human
 *
 * The window time in number of samples to wait for continuous WOM before triggering AID
 * Unit: time in sample number
 * Range: [25 - 500] 
 * Default: 150 (3sec at 50Hz)
 * Recommended value at 50Hz = 150
 * Recommended value at 25Hz = 75
 */
#define EDMP_AID_WIN_HUMAN                                      0x1618
#define EDMP_AID_WIN_HUMAN_SIZE                                 4

/* aid_alert_human
 *
 * The window time in number of samples before AID alert trigger after WOM stop reported motion
 * Unit: time in sample number
 * Range: [150 - 2147483648] 
 * Default: 90000 (30min at 50Hz)
 * Recommended value at 50Hz = 90000
 * Recommended value at 25Hz = 45000
 */
#define EDMP_AID_ALERT_HUMAN                                    0x161c
#define EDMP_AID_ALERT_HUMAN_SIZE                               4

/* aid_en_output_human
 *
 * Bitmask controlling which output are enabled from AID
 * No Unit: bit 0 for enable activity detection, bit 1 for inactivity detection, bit 2 for alert
 * Default: 7 (all output enabled)
 */
#define EDMP_AID_EN_OUTPUT_HUMAN                                0x1614
#define EDMP_AID_EN_OUTPUT_HUMAN_SIZE                           1

/* aid_dis_multi_output_human
 *
 * Option to disable output after each internal decision of the algorithm
 * No Unit: 1 to disable repetition of same state, 0 to enable repetition of same state after aid_win_human
 * Default: 0 (repetition enabled)
 */
#define EDMP_AID_DIS_MULTI_OUTPUT_HUMAN                         0x1615
#define EDMP_AID_DIS_MULTI_OUTPUT_HUMAN_SIZE                    1

/* aid_win_device
 *
 * The window time in number of samples to wait for continuous WOM before triggering AID
 * Unit: time in sample number
 * Range: [25 - 500] 
 * Default: 150 (3sec at 50Hz)
 * Recommended value at 50Hz = 150
 * Recommended value at 25Hz = 75
 */
#define EDMP_AID_WIN_DEVICE                                     0x163c
#define EDMP_AID_WIN_DEVICE_SIZE                                4

/* aid_alert_device
 *
 * The window time in number of samples before AID alert trigger after WOM stop reported motion
 * Unit: time in sample number
 * Range: [150 - 2147483648] 
 * Default: 90000 (30min at 50Hz)
 * Recommended value at 50Hz = 90000
 * Recommended value at 25Hz = 45000
 */
#define EDMP_AID_ALERT_DEVICE                                   0x1640
#define EDMP_AID_ALERT_DEVICE_SIZE                              4

/* aid_en_output_device
 *
 * Bitmask controlling which output are enabled from AID
 * No Unit: bit 0 for enable activity detection, bit 1 for inactivity detection, bit 2 for alert
 * Default: 7 (all output enabled)
 */
#define EDMP_AID_EN_OUTPUT_DEVICE                               0x1638
#define EDMP_AID_EN_OUTPUT_DEVICE_SIZE                          1

/* aid_dis_multi_output_device
 *
 * Option to disable output after each internal decision of the algorithm
 * No Unit: 1 to disable repetition of same state, 0 to enable repetition of same state after aid_win_device
 * Default: 0 (repetition enabled)
 */
#define EDMP_AID_DIS_MULTI_OUTPUT_DEVICE                        0x1639
#define EDMP_AID_DIS_MULTI_OUTPUT_DEVICE_SIZE                   1

/* aid_human_output_state
 *
 * Decision taken by the AID algorithm for human instance
 * No unit: 1 when activity is detected, 2 when inactivity is detected, 6 when inactivity and sedentary alert are detected
 */
#define EDMP_AID_HUMAN_OUTPUT_STATE                             0x1621
#define EDMP_AID_HUMAN_OUTPUT_STATE_SIZE                        1

/* aid_device_output_state
 *
 * Decision taken by the AID algorithm for device instance
 * No unit: 1 when activity is detected, 2 when inactivity is detected, 6 when inactivity and sedentary alert are detected
 */
#define EDMP_AID_DEVICE_OUTPUT_STATE                            0x1645
#define EDMP_AID_DEVICE_OUTPUT_STATE_SIZE                       1

#ifdef __cplusplus
}
#endif

#endif // __INV_IMU_EDMP_EXT_FEATURES_MEMMAP_H__
