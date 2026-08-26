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

#include "imu/inv_imu_edmp.h"
#include "imu/inv_imu_edmp_defs.h"
#include "imu/inv_imu_edmp_algo_defs.h"
#include "imu/inv_imu_edmp_patches_defs.h"
#include "imu/inv_imu_edmp_patch_key_offsets.h"
#include "imu/inv_imu_edmp_calmag_defs.h"

/* FIFO frame type definition */
typedef struct {
	uint8_t frame_id : 1;
	uint8_t accuracy : 2;
	uint8_t stationary : 3;
	uint8_t rmag_valid : 1;
	uint8_t hrc_nfusion : 1;
} status_byte_frameA_t;

typedef struct {
	uint8_t frame_id : 1;
	uint8_t accuracy : 2;
	uint8_t mag_anom : 2;
	uint8_t mrm_state : 2;
	uint8_t hrc_nfusion : 1;
} status_byte_frameB_t;

typedef struct {
	int16_t quat[4];
	union {
		int16_t bias_g[3];
		int16_t raw_m[3];
	};
	status_byte_frameA_t status_byte;
} frameA_t;

typedef struct {
	int32_t              bias_m[3];
	int16_t              heading_accuracy;
	status_byte_frameB_t status_byte;
} frameB_t;

typedef struct {
	uint8_t gx : 4;
	uint8_t gy : 4;
} hr_gxy_t;

typedef struct {
	uint8_t reserved : 4;
	uint8_t gz : 4;
} hr_gz_t;

typedef struct {
	int16_t              bias_g[3];
	int16_t              raw_m[3];
	hr_gxy_t             hr_gxy;
	hr_gz_t              hr_gz;
	status_byte_frameA_t status_byte;
} frameA_HRC_t;

typedef struct {
	int32_t              bias_m[3];
	hr_gxy_t             hr_gxy;
	hr_gz_t              hr_gz;
	status_byte_frameB_t status_byte;
} frameB_HRC_t;

#define EDMP_ROM_START_ADDR_IRQ0 EDMP_ROM_BASE
#define EDMP_ROM_START_ADDR_IRQ1 (EDMP_ROM_BASE + 0x04)
#define EDMP_ROM_START_ADDR_IRQ2 (EDMP_ROM_BASE + 0x08)

#define FRAME_ID_FRAME_A 0x1
#define FRAME_ID_FRAME_B 0x0

#define GAF_MODE_BITMASK_MAG       0x1
#define GAF_MODE_BITMASK_GYRO      0x2
#define GAF_MODE_BITMASK_FIFO_PUSH 0x8

static int dynamic_service_request(inv_imu_device_t *s, uint8_t service_id);

int inv_imu_edmp_set_frequency(inv_imu_device_t *s, const dmp_ext_sen_odr_cfg_apex_odr_t frequency)
{
	int                   status = INV_IMU_OK;
	dmp_ext_sen_odr_cfg_t dmp_ext_sen_odr_cfg;

	status |= inv_imu_read_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);
	dmp_ext_sen_odr_cfg.apex_odr = frequency;
	status |= inv_imu_write_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);

	return status;
}

int inv_imu_edmp_init(inv_imu_device_t *s)
{
	int               status = INV_IMU_OK;
	fifo_sram_sleep_t fifo_sram_sleep;

	/* Configure DMP address registers */
	status |= inv_imu_edmp_configure(s);

	/* Same impl as inv_imu_adv_power_up_sram, duplicated here to prevent dependency */
	status |= inv_imu_read_reg(s, FIFO_SRAM_SLEEP, 1, (uint8_t *)&fifo_sram_sleep);
	fifo_sram_sleep.fifo_gsleep_shared_sram = 0x03;
	status |= inv_imu_write_reg(s, FIFO_SRAM_SLEEP, 1, (uint8_t *)&fifo_sram_sleep);

	/* Clear SRAM, take advantage of internal memset EDMP service which is faster
	 * than writing each RAM byte through serial interface transaction
	 */
	status |= inv_imu_edmp_write_ram_area(s, EDMP_RAM_BASE, EDMP_ROM_DATA_SIZE, 0);

	/* Init will eventually depend on the usecase, it can now proceed */
	status |= inv_imu_edmp_recompute_decimation(s);

	return status;
}

int inv_imu_edmp_recompute_decimation(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	uint8_t         value;
	edmp_apex_en0_t save_edmp_apex_en0;
	edmp_apex_en1_t save_edmp_apex_en1;
	edmp_apex_en0_t edmp_apex_en0 = { 0 };
	edmp_apex_en1_t edmp_apex_en1 = { 0 };
	reg_host_msg_t  reg_host_msg;

	/*
	 * Check that DMP is turned OFF before requesting init APEX and save DMP enabled bits before
	 * requesting init procedure
	 */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&save_edmp_apex_en0);
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&save_edmp_apex_en1);
	if (save_edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	/*
	 * Make sure that all DMP interrupts are masked by default, to not trigger unexpected algorithm
	 *  execution when initialization is done if any sensor is running
	 */
	value = 0x3F;
	status |= inv_imu_write_reg(s, STATUS_MASK_PIN_0_7, 1, &value);
	status |= inv_imu_write_reg(s, STATUS_MASK_PIN_8_15, 1, &value);
	status |= inv_imu_write_reg(s, STATUS_MASK_PIN_16_23, 1, &value);

	/* Trigger EDMP with on-demand mode */
	status |= inv_imu_edmp_unmask_int_src(s, INV_IMU_EDMP_INT1, EDMP_INT_SRC_ON_DEMAND_MASK);

	/*
	 * Request to execute init procedure, make sure init is the only feature enabled
	 * (overwrite previously saved config)
	 */
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en1.init_en     = INV_IMU_ENABLE;
	edmp_apex_en1.edmp_enable = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	status |= inv_imu_read_reg(s, REG_HOST_MSG, 1, (uint8_t *)&reg_host_msg);
	reg_host_msg.edmp_on_demand_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, REG_HOST_MSG, 1, (uint8_t *)&reg_host_msg);

	/* Wait 200 us to give enough time for EMDP to start running */
	inv_imu_sleep_us(s, 200);

	/* Wait for DMP execution to complete */
	status |= inv_imu_edmp_wait_for_idle(s);

	/* Reset states */
	status |= inv_imu_edmp_mask_int_src(s, INV_IMU_EDMP_INT1, EDMP_INT_SRC_ON_DEMAND_MASK);

	/* Restore original DMP state, with DMP necessarily disabled as it was checked at the beginning of this function */
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&save_edmp_apex_en0);
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&save_edmp_apex_en1);

	status |= inv_imu_edmp_unmask_int_src(
	    s, INV_IMU_EDMP_INT0, EDMP_INT_SRC_ACCEL_DRDY_MASK | EDMP_INT_SRC_GYRO_DRDY_MASK);

	/* By default DMP init procedure initializes GAF mode with gyro and mag ON */
	s->edmp_gaf_mode = GAF_MODE_BITMASK_GYRO | GAF_MODE_BITMASK_MAG;

	return status;
}

static int dynamic_service_request(inv_imu_device_t *s, uint8_t service_id)
{
	int status = INV_IMU_OK;

	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_ONDEMAND_DYNAMIC_SERVICE_REQUEST, (uint8_t *)&service_id);

	/* Trigger EDMP with on-demand mode */
	status |= inv_imu_edmp_run_ondemand(s, INV_IMU_EDMP_INT1);

	/* Wait 200 us to give enough time for EMDP to start running */
	inv_imu_sleep_us(s, 200);

	/* Wait for DMP execution to complete */
	status |= inv_imu_edmp_wait_for_idle(s);

	return status;
}

int inv_imu_edmp_get_powersave_parameters(inv_imu_device_t *                   s,
                                          inv_imu_edmp_powersave_parameters_t *p)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_POWER_SAVE_TIME, (uint8_t *)&p->power_save_time);
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	p->power_save_en = edmp_apex_en1.power_save_en ? INV_IMU_ENABLE : INV_IMU_DISABLE;

	return status;
}

int inv_imu_edmp_get_tap_parameters(inv_imu_device_t *s, inv_imu_edmp_tap_parameters_t *p)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_MIN_JERK, (uint8_t *)&p->tap_min_jerk);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_TMAX, (uint8_t *)&p->tap_tmax);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_TMIN, (uint8_t *)&p->tap_tmin);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_MAX, (uint8_t *)&p->tap_max);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_MIN, (uint8_t *)&p->tap_min);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_MAX_PEAK_TOL, (uint8_t *)&p->tap_max_peak_tol);
	status |=
	    INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_SMUDGE_REJECT_THR, (uint8_t *)&p->tap_smudge_reject_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_TAVG, (uint8_t *)&p->tap_tavg);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_ODR, (uint8_t *)&p->tap_odr);

	return status;
}

int inv_imu_edmp_get_ff_parameters(inv_imu_device_t *s, inv_imu_edmp_ff_parameters_t *p)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_LOWG_PEAK_TH, (uint8_t *)&p->lowg_peak_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_LOWG_PEAK_TH_HYST, (uint8_t *)&p->lowg_peak_th_hyst);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_LOWG_TIME_TH, (uint8_t *)&p->lowg_time_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_HIGHG_PEAK_TH, (uint8_t *)&p->highg_peak_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_HIGHG_PEAK_TH_HYST, (uint8_t *)&p->highg_peak_th_hyst);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_HIGHG_TIME_TH, (uint8_t *)&p->highg_time_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_FF_MIN_DURATION, (uint8_t *)&p->ff_min_duration);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_FF_MAX_DURATION, (uint8_t *)&p->ff_max_duration);
	status |=
	    INV_IMU_READ_EDMP_SRAM(s, EDMP_FF_DEBOUNCE_DURATION, (uint8_t *)&p->ff_debounce_duration);

	return status;
}

int inv_imu_edmp_set_powersave_parameters(inv_imu_device_t *                         s,
                                          const inv_imu_edmp_powersave_parameters_t *p)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	/* Allow DMP power save reconfiguration if DMP is not running or if we want to disable DMP power save mode */
	if ((edmp_apex_en1.edmp_enable == 0) || (p->power_save_en == 0)) {
		edmp_apex_en1.power_save_en = p->power_save_en;
		status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
		status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_POWER_SAVE_TIME, (uint8_t *)&p->power_save_time);
	} else {
		/* Allow DMP power save reconfiguration if DMP is running with power save mode disabled
		 * and we want to enable DMP power save mode */
		if (edmp_apex_en1.power_save_en == 0) {
			status |=
			    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_POWER_SAVE_TIME, (uint8_t *)&p->power_save_time);
			edmp_apex_en1.power_save_en = p->power_save_en;
			status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
		} else {
			/* Forbid DMP power save reconfiguration if DMP is running with power save mode enabled
			 * and we want to reconfigure DMP power save time on the fly */
			return INV_IMU_ERROR;
		}
	}

	return status;
}

int inv_imu_edmp_set_tap_parameters(inv_imu_device_t *s, const inv_imu_edmp_tap_parameters_t *p)
{
	int             status = INV_IMU_OK;
	edmp_apex_enx_t cfg;

	/* DMP cannot be configured if it is running, hence make sure TAP APEX algorithm is off */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 2, (uint8_t *)&cfg);
	if (cfg.edmp_apex_en0.tap_en && cfg.edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_MIN_JERK, (uint8_t *)&p->tap_min_jerk);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_TMAX, (uint8_t *)&p->tap_tmax);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_TMIN, (uint8_t *)&p->tap_tmin);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_MAX, (uint8_t *)&p->tap_max);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_MIN, (uint8_t *)&p->tap_min);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_MAX_PEAK_TOL, (uint8_t *)&p->tap_max_peak_tol);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_SMUDGE_REJECT_THR, (uint8_t *)&p->tap_smudge_reject_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_TAVG, (uint8_t *)&p->tap_tavg);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_TAP_ODR, (uint8_t *)&p->tap_odr);

	return status;
}

int inv_imu_edmp_set_ff_parameters(inv_imu_device_t *s, const inv_imu_edmp_ff_parameters_t *p)
{
	int             status = INV_IMU_OK;
	edmp_apex_enx_t cfg;

	/* DMP cannot be configured if it is running, hence make sure FF APEX algorithms is off */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 2, (uint8_t *)&cfg);
	if (cfg.edmp_apex_en0.ff_en && cfg.edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_LOWG_PEAK_TH, (uint8_t *)&p->lowg_peak_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_LOWG_PEAK_TH_HYST, (uint8_t *)&p->lowg_peak_th_hyst);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_LOWG_TIME_TH, (uint8_t *)&p->lowg_time_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_HIGHG_PEAK_TH, (uint8_t *)&p->highg_peak_th);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_HIGHG_PEAK_TH_HYST, (uint8_t *)&p->highg_peak_th_hyst);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_HIGHG_TIME_TH, (uint8_t *)&p->highg_time_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_FF_MIN_DURATION, (uint8_t *)&p->ff_min_duration);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_FF_MAX_DURATION, (uint8_t *)&p->ff_max_duration);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_FF_DEBOUNCE_DURATION, (uint8_t *)&p->ff_debounce_duration);

	return status;
}

int inv_imu_edmp_get_gaf_parameters(inv_imu_device_t *s, inv_imu_edmp_gaf_parameters_t *gaf_params)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_RUN_SPHERICAL,
	                                 (uint8_t *)&gaf_params->run_spherical);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_PLL_CLOCK_VARIATION,
	                                 (uint8_t *)&gaf_params->clock_variation);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_GYR_PDR_US, (uint8_t *)&gaf_params->pdr_us);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_ENABLE,
	                                 (uint8_t *)&gaf_params->stationary_angle_enable);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_DURATION_US,
	                                 (uint8_t *)&gaf_params->stationary_angle_duration_us);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_THRESHOLD_DEG_Q16,
	                                 (uint8_t *)&gaf_params->stationary_angle_threshold_deg_q16);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_ROLL_PITCH,
	                                 (uint8_t *)&gaf_params->fus_low_speed_drift_roll_pitch);

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_STATIONARY_DURATION_US,
	                                 (uint8_t *)&gaf_params->gyr_cal_stationary_duration_us);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC1,
	                                 (uint8_t *)&gaf_params->gyr_cal_threshold_metric1);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC2,
	                                 (uint8_t *)&gaf_params->gyr_cal_threshold_metric2);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC1,
	                                 (uint8_t *)&gaf_params->strict_gyr_cal_threshold_metric1);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC2,
	                                 (uint8_t *)&gaf_params->strict_gyr_cal_threshold_metric2);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_SAMPLE_NUM_LOG2,
	                                 (uint8_t *)&gaf_params->gyr_cal_sample_num_log2);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_GYR_BIAS_REJECT_TH,
	                                 (uint8_t *)&gaf_params->gyr_bias_reject_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_FILTERING_NPOINTS_LOG2,
	                                 (uint8_t *)&gaf_params->acc_filtering_Npoints_log2);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_SQUARE_SIN_ANGLE_MOTION_DETECT_TH,
	                                 (uint8_t *)&gaf_params->acc_square_sin_angle_motion_detect_th);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_GOLDEN_BIAS_TIMER,
	                                 (uint8_t *)&gaf_params->golden_bias_timer);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_GOLDEN_BIAS_TEMPERATURE_VALIDITY,
	                                 (uint8_t *)&gaf_params->golden_bias_temperature_validity);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_HIGH_SPEED_DRIFT,
	                                 (uint8_t *)&gaf_params->fus_high_speed_drift);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_YAW,
	                                 (uint8_t *)&gaf_params->fus_low_speed_drift_yaw);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_ACC,
	                                 (uint8_t *)&gaf_params->fus_measurement_covariance_acc);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_ACCELERATION_REJECTION,
	                                 (uint8_t *)&gaf_params->fus_acceleration_rejection);

	status |=
	    INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_DT_US, (uint8_t *)&gaf_params->mag_dt_us);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_MAG,
	                                 (uint8_t *)&gaf_params->fus_measurement_covariance_mag);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MAG_ANOMALY_REJECTION,
	                                 (uint8_t *)&gaf_params->fus_mag_anomaly_rejection);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_THRESH_YAW_STOP_CONVERGENCE,
	                                 (uint8_t *)&gaf_params->thresh_yaw_stop_convergence_q30);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_THRESH_YAW_SMOOTH_CONVERGENCE,
	                                 (uint8_t *)&gaf_params->thresh_yaw_smooth_convergence_q15);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_HUGE_DISTURBANCE,
	                                 (uint8_t *)&gaf_params->mag_thr_huge_disturbance);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_ANOMALY_RADIUS,
	                                 (uint8_t *)&gaf_params->mag_thr_anomaly_radius);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_ANGLE,
	                                 (uint8_t *)&gaf_params->mag_thr_select_angle);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_GYRO,
	                                 (uint8_t *)&gaf_params->mag_thr_select_distance_gyro);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_NOGYRO,
	                                 (uint8_t *)&gaf_params->mag_thr_select_distance_nogyro);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_Q0_STANDALONE,
	                                 (uint8_t *)&gaf_params->mag_q0_standalone);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_R0_STANDALONE,
	                                 (uint8_t *)&gaf_params->mag_r0_standalone);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_Q0_ASSISTED,
	                                 (uint8_t *)&gaf_params->mag_q0_assisted);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_R0_ASSISTED,
	                                 (uint8_t *)&gaf_params->mag_r0_assisted);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS_JUMP,
	                                 (uint8_t *)&gaf_params->mag_thr_max_radius_jump);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS,
	                                 (uint8_t *)&gaf_params->mag_thr_max_radius);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MIN_RADIUS,
	                                 (uint8_t *)&gaf_params->mag_thr_min_radius);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_LOCK_ACC,
	                                 (uint8_t *)&gaf_params->mag_thr_lock_acc);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_CALIBRATION_CONDITION,
	                                 (uint8_t *)&gaf_params->mag_calibration_condition);
	/* These parameters come from the SRAM calmag image, which is
	 * loaded by the `inv_imu_edmp_set_gaf_parameters` API. There
	 * is no way to know if the image was already loaded when 
	 * this API is called. The decision is therefore to return
	 * the default values here, caller will update them before
	 * calling the `inv_imu_edmp_set_gaf_parameters` API.
	 */
	gaf_params->mag_fast_covariance_conv_thr  = EDMP_MAG_FAST_COVARIANCE_CONV_THR_DEFAULT;
	gaf_params->mag_stuck_covariance_conv_thr = EDMP_MAG_STUCK_COVARIANCE_CONV_THR_DEFAULT;

	return status;
}

int inv_imu_edmp_set_gaf_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_gaf_parameters_t *gaf_params)
{
	int                            status = INV_IMU_OK;
	accel_config0_t                accel_config0;
	gyro_config0_t                 gyro_config0;
	uint32_t                       acc_odr_us;
	uint32_t                       gyr_odr_us;
	dmp_ext_sen_odr_cfg_t          dmp_ext_sen_odr_cfg;
	dmp_ext_sen_odr_cfg_apex_odr_t dmp_odr;
	const void *                   gaf_pdr_array;
	uint32_t                       accuracy;
	uint32_t                       key;
	static const uint8_t           img[] = {
#include "imu/edmp_prgm_ram_patch_calmag.h"
	};

	status |= inv_imu_read_reg(s, ACCEL_CONFIG0, 1, (uint8_t *)&accel_config0);
	switch (accel_config0.accel_odr) {
	case ACCEL_CONFIG0_ACCEL_ODR_50_HZ:
		acc_odr_us = 20000;
		break;
	case ACCEL_CONFIG0_ACCEL_ODR_100_HZ:
		acc_odr_us = 10000;
		break;
	case ACCEL_CONFIG0_ACCEL_ODR_200_HZ:
		acc_odr_us = 5000;
		break;
	case ACCEL_CONFIG0_ACCEL_ODR_400_HZ:
		acc_odr_us = 2500;
		break;
	case ACCEL_CONFIG0_ACCEL_ODR_800_HZ:
		acc_odr_us = 1250;
		break;
	default:
		return INV_IMU_ERROR;
	}
	status |= inv_imu_read_reg(s, GYRO_CONFIG0, 1, (uint8_t *)&gyro_config0);
	switch (gyro_config0.gyro_odr) {
	case GYRO_CONFIG0_GYRO_ODR_50_HZ:
		gyr_odr_us = 20000;
		break;
	case GYRO_CONFIG0_GYRO_ODR_100_HZ:
		gyr_odr_us = 10000;
		break;
	case GYRO_CONFIG0_GYRO_ODR_200_HZ:
		gyr_odr_us = 5000;
		break;
	case GYRO_CONFIG0_GYRO_ODR_400_HZ:
		gyr_odr_us = 2500;
		break;
	case GYRO_CONFIG0_GYRO_ODR_800_HZ:
		gyr_odr_us = 1250;
		break;
	default:
		return INV_IMU_ERROR;
	}

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_RUN_SPHERICAL,
	                                  (uint8_t *)&gaf_params->run_spherical);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_PLL_CLOCK_VARIATION,
	                                  (uint8_t *)&gaf_params->clock_variation);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_ODR_US, (uint8_t *)&acc_odr_us);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_PDR_US, (uint8_t *)&gaf_params->pdr_us);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_GYR_ODR_US, (uint8_t *)&gyr_odr_us);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_GYR_PDR_US, (uint8_t *)&gaf_params->pdr_us);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_ENABLE,
	                                  (uint8_t *)&gaf_params->stationary_angle_enable);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_DURATION_US,
	                                  (uint8_t *)&gaf_params->stationary_angle_duration_us);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_STATIONARY_ANGLE_THRESHOLD_DEG_Q16,
	                                  (uint8_t *)&gaf_params->stationary_angle_threshold_deg_q16);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_ROLL_PITCH,
	                                  (uint8_t *)&gaf_params->fus_low_speed_drift_roll_pitch);

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_STATIONARY_DURATION_US,
	                                  (uint8_t *)&gaf_params->gyr_cal_stationary_duration_us);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC1,
	                                  (uint8_t *)&gaf_params->gyr_cal_threshold_metric1);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_THRESHOLD_METRIC2,
	                                  (uint8_t *)&gaf_params->gyr_cal_threshold_metric2);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC1,
	                                  (uint8_t *)&gaf_params->strict_gyr_cal_threshold_metric1);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_STRICT_GYR_CAL_THRESHOLD_METRIC2,
	                                  (uint8_t *)&gaf_params->strict_gyr_cal_threshold_metric2);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_LOOSE_GYR_CAL_SAMPLE_NUM_LOG2,
	                                  (uint8_t *)&gaf_params->gyr_cal_sample_num_log2);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_GYR_BIAS_REJECT_TH,
	                                  (uint8_t *)&gaf_params->gyr_bias_reject_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_FILTERING_NPOINTS_LOG2,
	                                  (uint8_t *)&gaf_params->acc_filtering_Npoints_log2);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_ACC_SQUARE_SIN_ANGLE_MOTION_DETECT_TH,
	                            (uint8_t *)&gaf_params->acc_square_sin_angle_motion_detect_th);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_GOLDEN_BIAS_TIMER,
	                                  (uint8_t *)&gaf_params->golden_bias_timer);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_GOLDEN_BIAS_TEMPERATURE_VALIDITY,
	                                  (uint8_t *)&gaf_params->golden_bias_temperature_validity);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_HIGH_SPEED_DRIFT,
	                                  (uint8_t *)&gaf_params->fus_high_speed_drift);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_LOW_SPEED_DRIFT_YAW,
	                                  (uint8_t *)&gaf_params->fus_low_speed_drift_yaw);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_ACC,
	                                  (uint8_t *)&gaf_params->fus_measurement_covariance_acc);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_ACCELERATION_REJECTION,
	                                  (uint8_t *)&gaf_params->fus_acceleration_rejection);

	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_DT_US, (uint8_t *)&gaf_params->mag_dt_us);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAGCAL_DT_US, (uint8_t *)&gaf_params->mag_dt_us);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MEASUREMENT_COVARIANCE_MAG,
	                                  (uint8_t *)&gaf_params->fus_measurement_covariance_mag);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_FUS_MAG_ANOMALY_REJECTION,
	                                  (uint8_t *)&gaf_params->fus_mag_anomaly_rejection);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_THRESH_YAW_STOP_CONVERGENCE,
	                                  (uint8_t *)&gaf_params->thresh_yaw_stop_convergence_q30);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_THRESH_YAW_SMOOTH_CONVERGENCE,
	                                  (uint8_t *)&gaf_params->thresh_yaw_smooth_convergence_q15);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_HUGE_DISTURBANCE,
	                                  (uint8_t *)&gaf_params->mag_thr_huge_disturbance);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_ANOMALY_RADIUS,
	                                  (uint8_t *)&gaf_params->mag_thr_anomaly_radius);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_ANGLE,
	                                  (uint8_t *)&gaf_params->mag_thr_select_angle);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_GYRO,
	                                  (uint8_t *)&gaf_params->mag_thr_select_distance_gyro);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_SELECT_DISTANCE_NOGYRO,
	                                  (uint8_t *)&gaf_params->mag_thr_select_distance_nogyro);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_Q0_STANDALONE,
	                                  (uint8_t *)&gaf_params->mag_q0_standalone);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_R0_STANDALONE,
	                                  (uint8_t *)&gaf_params->mag_r0_standalone);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_Q0_ASSISTED,
	                                  (uint8_t *)&gaf_params->mag_q0_assisted);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_R0_ASSISTED,
	                                  (uint8_t *)&gaf_params->mag_r0_assisted);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS_JUMP,
	                                  (uint8_t *)&gaf_params->mag_thr_max_radius_jump);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MAX_RADIUS,
	                                  (uint8_t *)&gaf_params->mag_thr_max_radius);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_MIN_RADIUS,
	                                  (uint8_t *)&gaf_params->mag_thr_min_radius);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_THR_LOCK_ACC,
	                                  (uint8_t *)&gaf_params->mag_thr_lock_acc);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_CONFIG_MAG_CALIBRATION_CONDITION,
	                                  (uint8_t *)&gaf_params->mag_calibration_condition);

	/* Run on-demand service to compute complex parameters based on customer simplified parameters */
	/* Complex parameters first */
	status |= dynamic_service_request(s, EDMP_ONDEMAND_ENABLE_GAF_PARAM);
	/* Then bias */
	status |= dynamic_service_request(s, EDMP_ONDEMAND_ENABLE_GAF_BIAS);
	/* Reset states */
	status |= inv_imu_edmp_mask_int_src(s, INV_IMU_EDMP_INT1, EDMP_INT_SRC_ON_DEMAND_MASK);
	status |= inv_imu_edmp_disable(s);

	/* Preload patch image and enable covariance patch since it will always be required */
	status |= inv_imu_write_sram(s, RAM_CALMAG_IMG_PRGM_BASE, sizeof(img), img);
	(void)memcpy(&key, img + RAM_CALMAG_IMG_PART4_ACCEPTANCE_PATCH_KEY_OFFSET, sizeof(key));
	status |= inv_imu_write_sram(s, EDMP_INVN_ALGO_GAF_PATCH_POINT_RLS_MAG_PART4_ACCEPTANCE,
	                             sizeof(key), (uint8_t *)&key);
	/* Adjust calmag SRAM image parameters */
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_MAG_FAST_COVARIANCE_CONV_THR,
	                                  (uint8_t *)&gaf_params->mag_fast_covariance_conv_thr);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_MAG_STUCK_COVARIANCE_CONV_THR,
	                                  (uint8_t *)&gaf_params->mag_stuck_covariance_conv_thr);

	/* Init gyro biases temperature to -273 C if accuracy level is low (0) */
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_SAVED_GYR_ACCURACY, (uint8_t *)&accuracy);
	if (accuracy == 0) {
		int32_t temperature_q16 = GAF_DEFAULT_TEMPERATURE_INIT_Q16;
		status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_GYR_BIAS_TEMPERATURE_DEG_Q16,
		                                  (uint8_t *)&temperature_q16);
	}

	status |= inv_imu_read_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);
	dmp_odr = (dmp_ext_sen_odr_cfg_apex_odr_t)dmp_ext_sen_odr_cfg.apex_odr;

	/* Reconfigure system scheduling in case GAF PDR is not default one */

	/*
	 * Warning : Full flexibility is allowed below by not restraining system scheduling reconfiguration but
	 * feature concurrency is reduced depending on following values
	 * - gaf_params->pdr_us
	 * - gaf_params->mag_dt_us
	 * - gaf_params->run_spherical
	 * - dmp_odr
	 * Please refer to inv_imu_edmp_algo_defs.h for concurrency capability when all features are enabled together
	 */
	switch (gaf_params->pdr_us) {
	case 20000 /* 50 Hz */: {
		static EDMP_GAF_PDR_50HZ_MAGODR_50HZ_DECLARE_ARRAY(gaf_pdr_50hz_magodr_50hz_array);
		static EDMP_GAF_PDR_50HZ_MAGODR_25HZ_DECLARE_ARRAY(gaf_pdr_50hz_magodr_25hz_array);
		static EDMP_GAF_PDR_50HZ_NOMAG_DECLARE_ARRAY(gaf_pdr_50hz_nomag_array);
		switch (gaf_params->mag_dt_us) {
		case 20000 /* 50 Hz */:
			gaf_pdr_array = gaf_pdr_50hz_magodr_50hz_array[dmp_odr];
			break;
		case 40000 /* 25 Hz */:
			gaf_pdr_array = gaf_pdr_50hz_magodr_25hz_array[dmp_odr];
			break;
		case 0 /* no mag */:
			gaf_pdr_array = gaf_pdr_50hz_nomag_array[dmp_odr];
			break;
		default:
			status = INV_IMU_ERROR;
			break;
		}
		break;
	}

	case 10000 /* 100 Hz */: {
		static EDMP_GAF_PDR_100HZ_MAGODR_100HZ_DECLARE_ARRAY(gaf_pdr_100hz_magodr_100hz_array);
		static EDMP_GAF_PDR_100HZ_MAGODR_50HZ_DECLARE_ARRAY(gaf_pdr_100hz_magodr_50hz_array);
		static EDMP_GAF_PDR_100HZ_NOMAG_DECLARE_ARRAY(gaf_pdr_100hz_nomag_array);
		switch (gaf_params->mag_dt_us) {
		case 10000 /* 100 Hz */:
			if ((gaf_params->run_spherical == 1) &&
			    ((dmp_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ) ||
			     (dmp_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_800_HZ)))
				status = INV_IMU_ERROR;
			else
				gaf_pdr_array = gaf_pdr_100hz_magodr_100hz_array[dmp_odr];
			break;
		case 20000 /* 50 Hz */:
			if ((gaf_params->run_spherical == 1) &&
			    (dmp_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_800_HZ))
				status = INV_IMU_ERROR;
			else
				gaf_pdr_array = gaf_pdr_100hz_magodr_50hz_array[dmp_odr];
			break;
		case 0 /* no mag */:
			gaf_pdr_array = gaf_pdr_100hz_nomag_array[dmp_odr];
			break;
		default:
			status = INV_IMU_ERROR;
			break;
		}
		break;
	}

	case 5000 /* 200 Hz */: {
		static EDMP_GAF_PDR_200HZ_MAGODR_100HZ_DECLARE_ARRAY(gaf_pdr_200hz_magodr_100hz_array);
		static EDMP_GAF_PDR_200HZ_MAGODR_50HZ_DECLARE_ARRAY(gaf_pdr_200hz_magodr_50hz_array);
		static EDMP_GAF_PDR_200HZ_NOMAG_DECLARE_ARRAY(gaf_pdr_200hz_nomag_array);
		switch (gaf_params->mag_dt_us) {
		case 10000 /* 100 Hz */:
			if ((gaf_params->run_spherical == 1) ||
			    (dmp_odr != DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ))
				status = INV_IMU_ERROR;
			else
				gaf_pdr_array = gaf_pdr_200hz_magodr_100hz_array[dmp_odr];
			break;
		case 20000 /* 50 Hz */:
			if (dmp_odr != DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ)
				status = INV_IMU_ERROR;
			else
				gaf_pdr_array = gaf_pdr_200hz_magodr_50hz_array[dmp_odr];
			break;
		case 0 /* no mag */:
			gaf_pdr_array = gaf_pdr_200hz_nomag_array[dmp_odr];
			break;
		default:
			status = INV_IMU_ERROR;
			break;
		}

		/* All cases with GAF PDR 200Hz and mag is ON request a specific RAM image to achieve such PDR */
		if ((status == INV_IMU_OK) && (gaf_params->mag_dt_us != 0)) {
			(void)memcpy(&key, img + RAM_CALMAG_IMG_CHUNK6_PATCH_KEY_OFFSET, sizeof(key));
			status |= inv_imu_write_sram(s, EDMP_INVN_ALGO_GAF_PATCH_POINT_BEFORE_MAG_CHUNK6,
			                             sizeof(key), (uint8_t *)&key);
			(void)memcpy(&key, img + RAM_CALMAG_IMG_CHUNK7_PATCH_KEY_OFFSET, sizeof(key));
			status |= inv_imu_write_sram(s, EDMP_INVN_ALGO_GAF_PATCH_POINT_BEFORE_MAG_CHUNK7,
			                             sizeof(key), (uint8_t *)&key);
		}

		break;
	}

	case 2500 /* 400 Hz */: {
		static EDMP_GAF_PDR_400HZ_NOMAG_DECLARE_ARRAY(gaf_pdr_400hz_nomag_array);
		switch (gaf_params->mag_dt_us) {
		case 0 /* no mag */:
			gaf_pdr_array = gaf_pdr_400hz_nomag_array[dmp_odr];
			break;
		default:
			status = INV_IMU_ERROR;
			break;
		}
		break;
	}

	default:
		status = INV_IMU_ERROR;
		break;
	}

	if (status == INV_IMU_OK)
		status |= inv_imu_write_sram(s, EDMP_GAF_PDR_PARTITION, 4 * EDMP_GAF_PARTITION_CNT,
		                             gaf_pdr_array);

	return status;
}

int inv_imu_edmp_set_gaf_soft_iron_cor_matrix(inv_imu_device_t *s, const int32_t matrix[3][3])
{
	int status = INV_IMU_OK;

	for (uint8_t i = 0; i < 3; i++) {
		for (uint8_t j = 0; j < 3; j++) {
			status |= inv_imu_write_sram(s, EDMP_GAF_CONFIG_MAG_SOFTIRON_MATRIX + i * 4 * 3 + j * 4,
			                             4, (uint8_t *)&matrix[i][j]);
		}
	}

	return status;
}

int inv_imu_edmp_stop_gaf_fifo_push(inv_imu_device_t *s)
{
	int status = INV_IMU_OK;

	s->edmp_gaf_mode |= GAF_MODE_BITMASK_FIFO_PUSH;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_MODE, &s->edmp_gaf_mode);

	return status;
}

int inv_imu_edmp_start_gaf_fifo_push(inv_imu_device_t *s)
{
	int status = INV_IMU_OK;

	s->edmp_gaf_mode &= ~GAF_MODE_BITMASK_FIFO_PUSH;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_MODE, &s->edmp_gaf_mode);

	return status;
}

int inv_imu_edmp_get_gaf_gyr_bias(inv_imu_device_t *s, int16_t gyr_bias_q12[3],
                                  int32_t *gyr_bias_temperature, uint8_t *accuracy)
{
	const int64_t gyr_2000dps_q30_to_1dps_q12 = 8192000; /* 2000 << 12 */
	int32_t       gyr_bias[3];
	uint32_t      accuracy32;
	int           status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_GYR_BIAS_DPS_Q12, (uint8_t *)gyr_bias);
	/* Convert from internal format to FIFO format, so it can be reapplied afterwards with inv_imu_edmp_set_gaf_gyr_bias() */
	for (uint8_t i = 0; i < 3; i++) {
		int64_t tmp     = (((int64_t)gyr_bias[i] * gyr_2000dps_q30_to_1dps_q12) + (1 << 29)) >> 30;
		gyr_bias_q12[i] = (int16_t)tmp;
	}

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_READ_GYR_ACCURACY, (uint8_t *)&accuracy32);
	*accuracy = (uint8_t)accuracy32;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_GYR_BIAS_TEMPERATURE_DEG_Q16,
	                                 (uint8_t *)gyr_bias_temperature);

	return status;
}

int inv_imu_edmp_set_gaf_gyr_bias(inv_imu_device_t *s, const int16_t gyr_bias_q12[3],
                                  const int32_t gyr_bias_temperature, const uint8_t accuracy)
{
	int      status = INV_IMU_OK;
	uint32_t accuracy32;
	/* convert 16bits gyro bias value to 32bits */
	int32_t gyr_bias[3] = { gyr_bias_q12[0], gyr_bias_q12[1], gyr_bias_q12[2] };
	/* Default temperature (-273 C) to be used with low accuracy level (0) */
	int32_t temperature_q16 = GAF_DEFAULT_TEMPERATURE_INIT_Q16;

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_GYR_BIAS_DPS_Q12, (const uint8_t *)gyr_bias);
	accuracy32 = (uint32_t)accuracy;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_GYR_ACCURACY, (const uint8_t *)&accuracy32);

	if (accuracy != 0)
		temperature_q16 = gyr_bias_temperature;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_GYR_BIAS_TEMPERATURE_DEG_Q16,
	                                  (uint8_t *)&temperature_q16);

	return status;
}

int inv_imu_edmp_get_gaf_mag_bias(inv_imu_device_t *s, int32_t mag_bias_q16[3], uint8_t *accuracy)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_READ_MAG_BIAS_UT_Q16, (uint8_t *)mag_bias_q16);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_GAF_READ_MAG_ACCURACY, (uint8_t *)accuracy);

	return status;
}

int inv_imu_edmp_set_gaf_mag_bias(inv_imu_device_t *s, const int32_t mag_bias_q16[3],
                                  const uint8_t accuracy)
{
	int      status           = INV_IMU_OK;
	uint32_t cov_max_selected = EDMP_COV_MAX_SELECTED_ACCURACY_0;
	uint32_t accuracy32;
	int32_t  scaled_bias_mag[3];

	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_MAG_BIAS_UT_Q16, (const uint8_t *)mag_bias_q16);
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_READ_MAG_BIAS_UT_Q16, (const uint8_t *)mag_bias_q16);
	accuracy32 = (uint32_t)accuracy;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_MAG_ACCURACY, (const uint8_t *)&accuracy32);
	if (accuracy == 3)
		cov_max_selected = EDMP_COV_MAX_SELECTED_ACCURACY_3;
	else if (accuracy == 2)
		cov_max_selected = EDMP_COV_MAX_SELECTED_ACCURACY_2;
	else if (accuracy == 1)
		cov_max_selected = EDMP_COV_MAX_SELECTED_ACCURACY_1;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_MAG_ACCURACY_COVARIANCE,
	                                  (const uint8_t *)&cov_max_selected);

	/* Set internal biases as well to avoid accuracy reset when large biases are to be loaded */
	scaled_bias_mag[0] = mag_bias_q16[0] >> EDMP_MAG_BIAS_SHIFT;
	scaled_bias_mag[1] = mag_bias_q16[1] >> EDMP_MAG_BIAS_SHIFT;
	scaled_bias_mag[2] = mag_bias_q16[2] >> EDMP_MAG_BIAS_SHIFT;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_MAG_BIAS_SCALED_UT_Q11,
	                                  (const uint8_t *)scaled_bias_mag);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_MAG_BIAS_SELECTED_SCALED_UT_Q11,
	                                  (const uint8_t *)scaled_bias_mag);

	return status;
}

int inv_imu_edmp_set_gaf_acc_bias(inv_imu_device_t *s, const int32_t acc_bias_q16[3])
{
	const uint8_t accuracy = 3;
	int           status   = INV_IMU_OK;

	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_ACC_BIAS_1G_Q16, (const uint8_t *)acc_bias_q16);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_SAVED_ACC_ACCURACY, (const uint8_t *)&accuracy);

	return status;
}

int inv_imu_edmp_set_gaf_mode(inv_imu_device_t *s, uint8_t gyro_is_on, uint8_t mag_is_on)
{
	int status = INV_IMU_OK;

	/* Default is gyr is ON */
	if (!gyro_is_on)
		s->edmp_gaf_mode &= ~GAF_MODE_BITMASK_GYRO;
	else
		s->edmp_gaf_mode |= GAF_MODE_BITMASK_GYRO;

	/* Default is mag is ON */
	if (!mag_is_on)
		s->edmp_gaf_mode &= ~GAF_MODE_BITMASK_MAG;
	else
		s->edmp_gaf_mode |= GAF_MODE_BITMASK_MAG;

	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_MODE, &s->edmp_gaf_mode);

	return status;
}

int inv_imu_edmp_set_sif_model(inv_imu_device_t *s, const inv_imu_edmp_sif_user_config_t *cfg)
{
	int                   status      = INV_IMU_OK;
	uint32_t              nb_features = 0;
	config_common_t       cconfig;
	config_time_t         tconfig;
	dmp_ext_sen_odr_cfg_t dmp_ext_sen_odr_cfg;

	status |= inv_imu_read_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);

	/* Clear SRAM, take advantage of internal memset EDMP service which is faster
	 * than writing each RAM byte through serial interface transaction
	 */
	status |= inv_imu_edmp_write_ram_area(s, EDMP_SIF_TIME_FEAS_CONFIG,
	                                      EDMP_ROM_DATA_SIZE - EDMP_SIF_TIME_FEAS_CONFIG, 0);

	/* Initialize the SIF time domain feature configuration matrix */
	for (uint8_t k = 0; k < cfg->acc_t_config_num; k++) {
		uint16_t time_feas_config = cfg->acc_temporal_feas_config[k * ACC_T_CONFIG_NUM_MAX + 1];
		for (uint8_t i = 2; i < ACC_T_CONFIG_NUM_MAX; i++) {
			if (cfg->acc_temporal_feas_config[k * ACC_T_CONFIG_NUM_MAX + i])
				time_feas_config |= 1 << i;
		}
		/* Load SIF data memory to EDMP RAM */
		status |=
		    inv_imu_write_sram(s, EDMP_SIF_TIME_FEAS_CONFIG + k * EDMP_SIF_TIME_FEAS_CONFIG_SIZE,
		                       EDMP_SIF_TIME_FEAS_CONFIG_SIZE, (uint8_t *)&time_feas_config);
	}

	/* Initialize the SIF feature extraction filter */
	for (int32_t k = 0; k < cfg->acc_t_config_num; k++) {
		filter_state_t sif_filter = { 0 };
		uint32_t       idx = MAX_FLT_COEF * cfg->acc_temporal_feas_config[k * ACC_T_CONFIG_NUM_MAX];
		SIF_Filter_Init(&sif_filter, MAX_FLT_COEF, (const int32_t *)&cfg->acc_t_filtbna_q28[idx]);
		/* Load SIF data memory to EDMP RAM */
		status |= inv_imu_write_sram(s, EDMP_SIF_FILTER + k * EDMP_SIF_FILTER_SIZE,
		                             EDMP_SIF_FILTER_SIZE, (uint8_t *)&sif_filter);
	}

	/* Initialize the SIF feature extraction configurations */
	SIF_CommonConfig_Init(&cconfig, (int32_t)cfg->wind_size_sample, (int32_t)cfg->acc_t_config_num);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_SIF_CCONFIG, (uint8_t *)&cconfig);
	SIF_TemporalConfig_Init(&tconfig, (int32_t)cfg->inv_data_wind, (int32_t)cfg->acc_hyst_thr_q16,
	                        (int32_t)cfg->acc_min_peak_distance,
	                        (int32_t)cfg->acc_min_peak_height_q16);
	switch ((dmp_ext_sen_odr_cfg_apex_odr_t)dmp_ext_sen_odr_cfg.apex_odr) {
	case DMP_EXT_SEN_ODR_CFG_APEX_ODR_50_HZ:
		tconfig.acc_odr_us = 20000;
		break;
	case DMP_EXT_SEN_ODR_CFG_APEX_ODR_100_HZ:
		tconfig.acc_odr_us = 10000;
		break;
	case DMP_EXT_SEN_ODR_CFG_APEX_ODR_200_HZ:
		tconfig.acc_odr_us = 5000;
		break;
	case DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ:
		tconfig.acc_odr_us = 2500;
		break;
	case DMP_EXT_SEN_ODR_CFG_APEX_ODR_800_HZ:
		tconfig.acc_odr_us = 1250;
		break;
	default:
		/* Set a value for acc_odr_us not to have random, but it does not matter since it is an error case (25 Hz not supported) */
		tconfig.acc_odr_us = 1000000 / cfg->sif_odr;
		status |= INV_IMU_ERROR_EDMP_ODR;
		break;
	}
	tconfig.sif_pdr_us = 1000000 / cfg->sif_odr;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_SIF_TCONFIG, (uint8_t *)&tconfig);

	/* Initialize the SIF tree structure */
	for (int32_t i = 0; i < cfg->node_size; i++) {
		/* Load SIF data memory to EDMP RAM */
		status |=
		    inv_imu_write_sram(s, EDMP_SIF_TREE_THRESHOLDS + i * EDMP_SIF_TREE_THRESHOLDS_SIZE,
		                       EDMP_SIF_TREE_THRESHOLDS_SIZE,
		                       (uint8_t *)&cfg->tree.decisionTreeThresholds[i]);
		status |=
		    inv_imu_write_sram(s, EDMP_SIF_TREE_FEATUREIDS + i * EDMP_SIF_TREE_FEATUREIDS_SIZE,
		                       EDMP_SIF_TREE_FEATUREIDS_SIZE,
		                       (uint8_t *)&cfg->tree.decisionTreeFeatureIDs[i]);
		status |= inv_imu_write_sram(
		    s, EDMP_SIF_TREE_NEXTNODERIGHT + i * EDMP_SIF_TREE_NEXTNODERIGHT_SIZE,
		    EDMP_SIF_TREE_NEXTNODERIGHT_SIZE, (uint8_t *)&cfg->tree.decisionTreeNextNodeRight[i]);
		if (cfg->tree.decisionTreeFeatureIDs[i] > nb_features)
			nb_features = cfg->tree.decisionTreeFeatureIDs[i];
	}
	for (uint32_t i = 0; i < (nb_features + 1); i++) {
		status |= inv_imu_write_sram(
		    s, EDMP_SIF_TREE_THRESHOLDSSHIFT + i * EDMP_SIF_TREE_THRESHOLDSSHIFT_SIZE,
		    EDMP_SIF_TREE_THRESHOLDSSHIFT_SIZE,
		    (uint8_t *)&cfg->tree.decisionTreeThresholdsShift[i]);
	}

	return status;
}

int inv_imu_edmp_set_sif_pdr(inv_imu_device_t *s, uint32_t pdr)
{
	int                   status = INV_IMU_OK;
	edmp_apex_en1_t       edmp_apex_en1;
	dmp_ext_sen_odr_cfg_t dmp_ext_sen_odr_cfg;
	EDMP_SIF_PDR_100HZ_DECLARE_ARRAY(sif_pdr100hz_array);

	/*
	 * Check that DMP is turned OFF before requesting set SIF PDR service
	 */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	if (edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	/* ROM configures system to run for SIF PDR 50Hz by default with init EDMP service */
	if (pdr == 50 /* Hz */)
		return status;

	/* Set of values for EDMP_SIF_PDR_PARTITION are only available for SIF PDR 100 Hz */
	if (pdr != 100 /* Hz */)
		return INV_IMU_ERROR;

	status |= inv_imu_read_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);

	if ((dmp_ext_sen_odr_cfg_apex_odr_t)dmp_ext_sen_odr_cfg.apex_odr <=
	    DMP_EXT_SEN_ODR_CFG_APEX_ODR_50_HZ)
		/* It is an error case in case of PDR 100Hz for DMP ODR <= 50 Hz */
		status |= INV_IMU_ERROR_EDMP_ODR;

	status |= inv_imu_write_sram(s, EDMP_SIF_PDR_PARTITION, 4 * EDMP_SIF_PARTITION_CNT,
	                             (uint8_t *)sif_pdr100hz_array[dmp_ext_sen_odr_cfg.apex_odr]);

	return status;
}

int inv_imu_edmp_set_sif_int_control(inv_imu_device_t *                s,
                                     const inv_imu_edmp_sif_int_mode_t int_mode)
{
	int status = INV_IMU_OK;
	status |= inv_imu_write_sram(s, EDMP_SIF_INTERRUPT_CONTROL, EDMP_SIF_INTERRUPT_CONTROL_SIZE,
	                             (uint8_t *)&int_mode);
	return status;
}

int inv_imu_edmp_set_mounting_matrix(inv_imu_device_t *s, const int8_t mounting_matrix[9])
{
	int           status                  = INV_IMU_OK;
	const int16_t edmp_mounting_matrix[9] = {
		(int16_t)mounting_matrix[0] << 14, (int16_t)mounting_matrix[1] << 14,
		(int16_t)mounting_matrix[2] << 14, (int16_t)mounting_matrix[3] << 14,
		(int16_t)mounting_matrix[4] << 14, (int16_t)mounting_matrix[5] << 14,
		(int16_t)mounting_matrix[6] << 14, (int16_t)mounting_matrix[7] << 14,
		(int16_t)mounting_matrix[8] << 14,
	};
	status |=
	    INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GLOBAL_MOUNTING_MATRIX, (uint8_t *)&edmp_mounting_matrix);

	return status;
}

int inv_imu_edmp_get_config_int_apex(inv_imu_device_t *s, inv_imu_edmp_int_state_t *it)
{
	int                status = INV_IMU_OK;
	int_apex_configx_t cfg;

	status |= inv_imu_read_reg(s, INT_APEX_CONFIG0, 2, (uint8_t *)&cfg);
	/* INT_APEX_CONFIG0 */
	it->INV_TAP         = !cfg.int_apex_config0.int_status_mask_pin_tap_detect;
	it->INV_HIGHG       = !cfg.int_apex_config0.int_status_mask_pin_high_g_det;
	it->INV_LOWG        = !cfg.int_apex_config0.int_status_mask_pin_low_g_det;
	it->INV_SIF         = !cfg.int_apex_config0.int_status_mask_pin_sif_det;
	it->INV_GAF_MRM_CHG = !cfg.int_apex_config0.int_status_mask_pin_ext0_det;
	it->INV_GAF_MRM_RUN = !cfg.int_apex_config0.int_status_mask_pin_ext1_det;
	it->INV_FF          = !cfg.int_apex_config0.int_status_mask_pin_ff_det;
	it->INV_B2S         = !cfg.int_apex_config0.int_status_mask_pin_ext2_det;

	/* INT_APEX_CONFIG1 */
	it->INV_B2S_REV     = !cfg.int_apex_config1.int_status_mask_pin_ext3_det;
	it->INV_GAF_MRM_THR = !cfg.int_apex_config1.int_status_mask_pin_ext4_det;
	it->INV_SELF_TEST   = !cfg.int_apex_config1.int_status_mask_pin_selftest_done;
	it->INV_SEC_AUTH    = !cfg.int_apex_config1.int_status_mask_pin_sa_done;
	it->INV_AID_HUMAN   = !cfg.int_apex_config1.int_status_mask_pin_ext5_det;
	it->INV_AID_DEVICE  = !cfg.int_apex_config1.int_status_mask_pin_ext6_det;

	return status;
}

int inv_imu_edmp_set_config_int_apex(inv_imu_device_t *s, const inv_imu_edmp_int_state_t *it)
{
	int                status = INV_IMU_OK;
	int_apex_configx_t cfg    = { 0 };

	/* INT_APEX_CONFIG0 */
	cfg.int_apex_config0.int_status_mask_pin_tap_detect = !it->INV_TAP;
	cfg.int_apex_config0.int_status_mask_pin_high_g_det = !it->INV_HIGHG;
	cfg.int_apex_config0.int_status_mask_pin_low_g_det  = !it->INV_LOWG;
	cfg.int_apex_config0.int_status_mask_pin_sif_det    = !it->INV_SIF;
	cfg.int_apex_config0.int_status_mask_pin_ext0_det   = !it->INV_GAF_MRM_CHG;
	cfg.int_apex_config0.int_status_mask_pin_ext1_det   = !it->INV_GAF_MRM_RUN;
	cfg.int_apex_config0.int_status_mask_pin_ff_det     = !it->INV_FF;
	cfg.int_apex_config0.int_status_mask_pin_ext2_det   = !it->INV_B2S;

	/* INT_APEX_CONFIG1 */
	cfg.int_apex_config1.int_status_mask_pin_ext3_det      = !it->INV_B2S_REV;
	cfg.int_apex_config1.int_status_mask_pin_ext4_det      = !it->INV_GAF_MRM_THR;
	cfg.int_apex_config1.int_status_mask_pin_selftest_done = !it->INV_SELF_TEST;
	cfg.int_apex_config1.int_status_mask_pin_sa_done       = !it->INV_SEC_AUTH;
	cfg.int_apex_config1.int_status_mask_pin_ext5_det      = !it->INV_AID_HUMAN;
	cfg.int_apex_config1.int_status_mask_pin_ext6_det      = !it->INV_AID_DEVICE;

	status |= inv_imu_write_reg(s, INT_APEX_CONFIG0, 2, (uint8_t *)&cfg);

	return status;
}

int inv_imu_edmp_enable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.edmp_enable = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_disable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.edmp_enable = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	/* eDMP will be disabled once current processing is done, wait for idle then */
	status |= inv_imu_edmp_wait_for_idle(s);

	return status;
}

int inv_imu_edmp_check_odr_decimation(inv_imu_device_t *s)
{
	int                            status = INV_IMU_OK;
	uint32_t                       dmp_decim_rate_from_sram;
	dmp_ext_sen_odr_cfg_t          dmp_ext_sen_odr_cfg;
	dmp_ext_sen_odr_cfg_apex_odr_t apex_odr;

	/* This function will compare edmp decimation rate in IMU SRAM as computed at APEX init step vs the
	 * DMP ODR currently written in IMU register.
	 */
	status |=
	    INV_IMU_READ_EDMP_SRAM(s, EDMP_DMP_ODR_LAST_INIT, (uint8_t *)&dmp_decim_rate_from_sram);
	status |= inv_imu_read_reg(s, DMP_EXT_SEN_ODR_CFG, 1, (uint8_t *)&dmp_ext_sen_odr_cfg);
	apex_odr = (dmp_ext_sen_odr_cfg_apex_odr_t)dmp_ext_sen_odr_cfg.apex_odr;
	switch (dmp_decim_rate_from_sram) {
	case 0x80000000:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_800_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	case 0x8000:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	case 0x80:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_200_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	case 0x8:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_100_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	case 0x2:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_50_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	case 0x1:
		if (apex_odr == DMP_EXT_SEN_ODR_CFG_APEX_ODR_25_HZ)
			return status;
		else
			return INV_IMU_ERROR_EDMP_ODR;
	default:
		return INV_IMU_ERROR;
	}
}

int inv_imu_edmp_enable_tap(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.tap_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_disable_tap(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.tap_en = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_enable_ff(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	/* Make sure freefall is not already enabled to prevent messing up pointers */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	if (edmp_apex_en0.ff_en)
		return status;

	/* Enable freefall */
	edmp_apex_en0.ff_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_disable_ff(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.ff_en = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_enable_gaf(inv_imu_device_t *s)
{
	int             status   = INV_IMU_OK;
	uint8_t         gaf_init = 0;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	/* Make sure GAF is not already enabled to prevent messing up pointers */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	if (edmp_apex_en1.gaf_en)
		return status;

	/*
	 * Force reinitialization of algorithm because user might have changed GAF parameters between
	 * call	to `inv_imu_init_gaf()` and call to `inv_imu_edmp_enable_gaf()`.
	 * If this is not done, new user parameters won't be applied.
	 */
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_GAF_INIT_STATUS, (uint8_t *)&gaf_init);

	/* Enable GAF */
	edmp_apex_en1.gaf_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_disable_gaf(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.gaf_en = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_enable_gaf_soft_iron_cor(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.soft_hard_iron_corr_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_disable_gaf_soft_iron_cor(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.soft_hard_iron_corr_en = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_enable_sif(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	/* Make sure SIF is not already enabled to prevent messing up pointers */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	if (edmp_apex_en0.sif_en)
		return status;

	edmp_apex_en0.sif_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_disable_sif(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.sif_en = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	return status;
}

int inv_imu_edmp_get_int_apex_status(inv_imu_device_t *s, inv_imu_edmp_int_state_t *it)
{
	int                status = INV_IMU_OK;
	int_apex_statusx_t st;

	/* Read APEX interrupt status */
	status |= inv_imu_read_reg(s, INT_APEX_STATUS0, 2, (uint8_t *)&st);

	it->INV_TAP         = st.int_apex_status0.int_status_tap_det;
	it->INV_HIGHG       = st.int_apex_status0.int_status_high_g_det;
	it->INV_LOWG        = st.int_apex_status0.int_status_low_g_det;
	it->INV_SIF         = st.int_apex_status0.int_status_sif_det;
	it->INV_GAF_MRM_CHG = st.int_apex_status0.int_status_ext0_det;
	it->INV_GAF_MRM_RUN = st.int_apex_status0.int_status_ext1_det;
	it->INV_FF          = st.int_apex_status0.int_status_ff_det;
	it->INV_B2S         = st.int_apex_status0.int_status_ext2_det;
	it->INV_B2S_REV     = st.int_apex_status1.int_status_ext3_det;
	it->INV_GAF_MRM_THR = st.int_apex_status1.int_status_ext4_det;
	it->INV_SELF_TEST   = st.int_apex_status1.int_status_selftest_done;
	it->INV_SEC_AUTH    = st.int_apex_status1.int_status_sa_done;
	it->INV_AID_HUMAN   = st.int_apex_status1.int_status_ext5_det;
	it->INV_AID_DEVICE  = st.int_apex_status1.int_status_ext6_det;

	return status;
}

int inv_imu_edmp_get_ff_data(inv_imu_device_t *s, uint16_t *freefall_duration)
{
	int     status = INV_IMU_OK;
	uint8_t data1[2];
	uint8_t data2[2];

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_FF_DURATION, data1);
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_FF_DURATION, data2);
	if ((data1[0] == data2[0]) && (data1[1] == data2[1])) {
		*freefall_duration = (data1[1] << 8) | data1[0];
		return status;
	} else {
		*freefall_duration = 0;
		return INV_IMU_ERROR_EDMP_RAM_KO;
	}
}

int inv_imu_edmp_get_tap_data(inv_imu_device_t *s, inv_imu_edmp_tap_data_t *data)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_NUM, (uint8_t *)&(data->num));
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_AXIS, (uint8_t *)&(data->axis));
	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TAP_DIR, (uint8_t *)&(data->direction));
	if (data->num == INV_IMU_EDMP_TAP_DOUBLE)
		status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_DOUBLE_TAP_TIMING,
		                                 (uint8_t *)&(data->double_tap_timing));
	else
		data->double_tap_timing = 0;

	if (data->num == INV_IMU_EDMP_TAP_TRIPLE)
		status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_TRIPLE_TAP_TIMING,
		                                 (uint8_t *)&(data->triple_tap_timing));
	else
		data->triple_tap_timing = 0;

	return status;
}

int inv_imu_edmp_get_gaf_frame_type(inv_imu_device_t *s, const uint8_t es1[6],
                                    inv_imu_edmp_gaf_frame_type_t *frame_type)
{
	int                   status = INV_IMU_OK;
	status_byte_frameA_t *st     = (status_byte_frameA_t *)&es1[5];

	if (st->frame_id == FRAME_ID_FRAME_A) {
		if (st->hrc_nfusion == 0) {
			switch (s->edmp_gaf_mode & (GAF_MODE_BITMASK_GYRO | GAF_MODE_BITMASK_MAG)) {
			case GAF_MODE_BITMASK_GYRO:
				*frame_type = INV_IMU_EDMP_GAF_QUAT_BIAS_GYR;
				break;
			case GAF_MODE_BITMASK_MAG:
				*frame_type = INV_IMU_EDMP_GAF_QUAT_RAW_MAG;
				break;
			case GAF_MODE_BITMASK_GYRO | GAF_MODE_BITMASK_MAG:
				*frame_type = INV_IMU_EDMP_GAF_QUAT_RAW_MAG_GYR_FLAGS;
				break;
			default:
				status = INV_IMU_ERROR;
				break;
			}
		} else {
			switch (s->edmp_gaf_mode & (GAF_MODE_BITMASK_GYRO | GAF_MODE_BITMASK_MAG)) {
			case GAF_MODE_BITMASK_GYRO:
				*frame_type = INV_IMU_EDMP_GAF_HRC_BIAS_GYR;
				break;
			case GAF_MODE_BITMASK_MAG:
				*frame_type = INV_IMU_EDMP_GAF_HRC_RAW_MAG;
				break;
			case GAF_MODE_BITMASK_GYRO | GAF_MODE_BITMASK_MAG:
				*frame_type = INV_IMU_EDMP_GAF_HRC_BIAS_GYR_RAW_MAG;
				break;
			default:
				status = INV_IMU_ERROR;
				break;
			}
		}
	} else {
		if (st->hrc_nfusion == 0)
			*frame_type = INV_IMU_EDMP_GAF_BIAS_MAG_HEADING;
		else
			*frame_type = INV_IMU_EDMP_GAF_HRC_BIAS_MAG;
	}

	return status;
}

static void undo_fifo_rounding(inv_imu_device_t *s, const uint8_t hr_g[3],
                               const gyro_config0_gyro_ui_fs_sel_t gyro_fsr, int16_t prev_rgyr[3])
{
	uint8_t loc_hr_gx;
	uint8_t loc_hr_gy;
	uint8_t loc_hr_gz;
	uint8_t rounding_thr;
	uint8_t hr_bits_mask;

	/*
	 * Depending on current FSR setting, a portion of hr_gx/y/z bits might already be part 
	 * of stdRes value. So we need to:
	 *  - adapt the rounding threshold used to undo the FIFO rounding
	 */
	rounding_thr = 8 >> gyro_fsr;
	hr_bits_mask = 0xF >> gyro_fsr;

	/*
	 *  - locally cap hr_gx/y/z to remove the bits that are already parts of prev_rgyr to have a
	 *    fair comparison to threshold. But keep original hr_gx/y/z untouched for later use.
	 */
	loc_hr_gx = hr_g[0] & hr_bits_mask;
	loc_hr_gy = hr_g[1] & hr_bits_mask;
	loc_hr_gz = hr_g[2] & hr_bits_mask;

	/* 
	 * - undo FIFO rounding on prev_rgyr:
	 *    FIFO stdRes value is rounded by HW. Rounding function is as follows:
	 *    if ( (hi_res > rounding_thr) ||
	 *        ((hi_res == rounding_thr) && (std_res_val >= 0)))
	 *        std_res_val += 1
	 *    Let's do the opposite operation.
	 */
	if ((loc_hr_gx > rounding_thr) || ((loc_hr_gx == rounding_thr) && (prev_rgyr[0] >= 0)))
		prev_rgyr[0] = prev_rgyr[0] - 1;
	if ((loc_hr_gy > rounding_thr) || ((loc_hr_gy == rounding_thr) && (prev_rgyr[1] >= 0)))
		prev_rgyr[1] = prev_rgyr[1] - 1;
	if ((loc_hr_gz > rounding_thr) || ((loc_hr_gz == rounding_thr) && (prev_rgyr[2] >= 0)))
		prev_rgyr[2] = prev_rgyr[2] - 1;
}

int inv_imu_edmp_decode_gaf_rgyr_highres(inv_imu_device_t *s, const uint8_t hr_g[3],
                                         const gyro_config0_gyro_ui_fs_sel_t gyro_fsr,
                                         const int16_t prev_rgyr[3], int32_t rgyr_highres[3])
{
	int status = INV_IMU_OK;

	/* 
	 * If gyro FSR is smaller than 250 dps then prev_rgyr already contains all significant bits. No
	 * need to add any high-res bits. Just return prev_rgyr for the highres rgyr value scaled to 
	 * 4000 dps over 20 bits.
	 * note: '>=' comparison is due to enum reversed order.
	 */
	if (gyro_fsr >= GYRO_CONFIG0_GYRO_UI_FS_SEL_250_DPS) {
		rgyr_highres[0] = (int32_t)prev_rgyr[0] >> (gyro_fsr - 4);
		rgyr_highres[1] = (int32_t)prev_rgyr[1] >> (gyro_fsr - 4);
		rgyr_highres[2] = (int32_t)prev_rgyr[2] >> (gyro_fsr - 4);
	} else {
		int16_t loc_prev_rgyr[3];

		loc_prev_rgyr[0] = prev_rgyr[0];
		loc_prev_rgyr[1] = prev_rgyr[1];
		loc_prev_rgyr[2] = prev_rgyr[2];

		/* 
		 * Raw gyr data must be converted to full FSR 4000 dps before building full raw gyro value in
		 * high resolution.
		 * But, depending on current FSR setting, a portion of hr_gx/y/z bits might already be part 
		 * of stdRes value. So we need to:
		 *  - undo FIFO rounding on loc_prev_rgyr 
		 */
		undo_fifo_rounding(s, hr_g, gyro_fsr, loc_prev_rgyr);

		/*
		 *  - r-shift loc_prev_rgyr according to FSR to remove the bits that are already in hx_gx/y/z
		 *  - l-shift loc_prev_rgyr by 4 and concatenate the 4 HR bits
		 */
		rgyr_highres[0] = ((int32_t)loc_prev_rgyr[0] << (4 - gyro_fsr)) | hr_g[0];
		rgyr_highres[1] = ((int32_t)loc_prev_rgyr[1] << (4 - gyro_fsr)) | hr_g[1];
		rgyr_highres[2] = ((int32_t)loc_prev_rgyr[2] << (4 - gyro_fsr)) | hr_g[2];
	}

	return status;
}

int inv_imu_edmp_gaf_decode_fifo(inv_imu_device_t *s, const uint8_t es0[9], const uint8_t es1[6],
                                 inv_imu_edmp_gaf_outputs_t *const out)
{
	int                           status = INV_IMU_OK;
	inv_imu_edmp_gaf_frame_type_t frame_type;
	status_byte_frameA_t *        stA    = (status_byte_frameA_t *)&es1[5];
	status_byte_frameB_t *        stB    = (status_byte_frameB_t *)&es1[5];
	hr_gxy_t *                    hr_gxy = (hr_gxy_t *)&es1[3];
	hr_gz_t *                     hr_gz  = (hr_gz_t *)&es1[4];

	status |= inv_imu_edmp_get_gaf_frame_type(s, es1, &frame_type);
	if (status)
		return status;

	switch (frame_type) {
	case INV_IMU_EDMP_GAF_QUAT_BIAS_GYR:
		out->grv_quat_q14[0] = es0[0] + ((int32_t)es0[1] << 8);
		out->grv_quat_q14[1] = es0[2] + ((int32_t)es0[3] << 8);
		out->grv_quat_q14[2] = es0[4] + ((int32_t)es0[5] << 8);
		out->grv_quat_q14[3] = es0[6] + ((int32_t)es0[7] << 8);
		out->grv_quat_valid  = 1;

		/* Gyro calibration output */
		out->gyr_bias_q12[0] = es0[8] + ((int32_t)es1[0] << 8);
		out->gyr_bias_q12[1] = es1[1] + ((int32_t)es1[2] << 8);
		out->gyr_bias_q12[2] = es1[3] + ((int32_t)es1[4] << 8);
		out->gyr_bias_valid  = 1;

		out->gyr_accuracy_flag = stA->accuracy;
		out->stationary_flag   = stA->stationary - 1;
		out->gyr_flags_valid   = 1;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_QUAT_RAW_MAG:
		out->gmrv_quat_q14[0] = es0[0] + ((int32_t)es0[1] << 8);
		out->gmrv_quat_q14[1] = es0[2] + ((int32_t)es0[3] << 8);
		out->gmrv_quat_q14[2] = es0[4] + ((int32_t)es0[5] << 8);
		out->gmrv_quat_q14[3] = es0[6] + ((int32_t)es0[7] << 8);
		out->gmrv_quat_valid  = 1;

		out->rmag[0]    = es0[8] + ((int32_t)es1[0] << 8);
		out->rmag[1]    = es1[1] + ((int32_t)es1[2] << 8);
		out->rmag[2]    = es1[3] + ((int32_t)es1[4] << 8);
		out->rmag_valid = stA->rmag_valid;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_QUAT_RAW_MAG_GYR_FLAGS:
		out->rv_quat_q14[0] = es0[0] + ((int32_t)es0[1] << 8);
		out->rv_quat_q14[1] = es0[2] + ((int32_t)es0[3] << 8);
		out->rv_quat_q14[2] = es0[4] + ((int32_t)es0[5] << 8);
		out->rv_quat_q14[3] = es0[6] + ((int32_t)es0[7] << 8);
		out->rv_quat_valid  = 1;

		out->rmag[0]    = es0[8] + ((int32_t)es1[0] << 8);
		out->rmag[1]    = es1[1] + ((int32_t)es1[2] << 8);
		out->rmag[2]    = es1[3] + ((int32_t)es1[4] << 8);
		out->rmag_valid = stA->rmag_valid;

		out->gyr_accuracy_flag = stA->accuracy;
		out->stationary_flag   = stA->stationary - 1;
		out->gyr_flags_valid   = 1;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_BIAS_MAG_HEADING:
		if ((s->edmp_gaf_mode & GAF_MODE_BITMASK_GYRO) == 0) { // no gyr
			out->gmrv_heading_q11   = es1[3] + ((int32_t)es1[4] << 8);
			out->gmrv_heading_valid = 1;
		} else {
			out->rv_heading_q11   = es1[3] + ((int32_t)es1[4] << 8);
			out->rv_heading_valid = 1;
		}

		out->mrm_state       = (inv_imu_auto_mrm_state_t)stB->mrm_state;
		out->mrm_state_valid = 1;

		/* Mag calibration output */
		out->mag_bias_q16[0] =
		    es0[0] + ((int32_t)es0[1] << 8) + ((int32_t)es0[2] << 16) + ((int32_t)es0[3] << 24);
		out->mag_bias_q16[1] =
		    es0[4] + ((int32_t)es0[5] << 8) + ((int32_t)es0[6] << 16) + ((int32_t)es0[7] << 24);
		out->mag_bias_q16[2] =
		    es0[8] + ((int32_t)es1[0] << 8) + ((int32_t)es1[1] << 16) + ((int32_t)es1[2] << 24);
		out->mag_accuracy_flag = stB->accuracy;
		out->mag_anomalies     = stB->mag_anom;
		out->mag_bias_valid    = 1;

		out->frame_complete = 0;
		break;

	case INV_IMU_EDMP_GAF_HRC_BIAS_GYR_RAW_MAG:
		out->rmag[0]    = es0[6] + ((int32_t)es0[7] << 8);
		out->rmag[1]    = es0[8] + ((int32_t)es1[0] << 8);
		out->rmag[2]    = es1[1] + ((int32_t)es1[2] << 8);
		out->rmag_valid = stA->rmag_valid;

		/* Gyro calibration output */
		out->gyr_bias_q12[0] = es0[0] + ((int32_t)es0[1] << 8);
		out->gyr_bias_q12[1] = es0[2] + ((int32_t)es0[3] << 8);
		out->gyr_bias_q12[2] = es0[4] + ((int32_t)es0[5] << 8);
		out->gyr_bias_valid  = 1;

		out->gyr_accuracy_flag = stA->accuracy;
		out->stationary_flag   = stA->stationary - 1;
		out->gyr_flags_valid   = 1;

		out->hr_g[0]    = hr_gxy->gx;
		out->hr_g[1]    = hr_gxy->gy;
		out->hr_g[2]    = hr_gz->gz;
		out->hr_g_valid = 1;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_HRC_BIAS_GYR:
		/* Gyro calibration output */
		out->gyr_bias_q12[0] = es0[0] + ((int32_t)es0[1] << 8);
		out->gyr_bias_q12[1] = es0[2] + ((int32_t)es0[3] << 8);
		out->gyr_bias_q12[2] = es0[4] + ((int32_t)es0[5] << 8);
		out->gyr_bias_valid  = 1;

		out->gyr_accuracy_flag = stA->accuracy;
		out->stationary_flag   = stA->stationary - 1;
		out->gyr_flags_valid   = 1;

		out->hr_g[0]    = hr_gxy->gx;
		out->hr_g[1]    = hr_gxy->gy;
		out->hr_g[2]    = hr_gz->gz;
		out->hr_g_valid = 1;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_HRC_RAW_MAG:
		out->rmag[0]    = es0[6] + ((int32_t)es0[7] << 8);
		out->rmag[1]    = es0[8] + ((int32_t)es1[0] << 8);
		out->rmag[2]    = es1[1] + ((int32_t)es1[2] << 8);
		out->rmag_valid = stA->rmag_valid;

		out->frame_complete = 1;
		break;

	case INV_IMU_EDMP_GAF_HRC_BIAS_MAG:
		/* Mag calibration output */
		out->mag_bias_q16[0] =
		    es0[0] + ((int32_t)es0[1] << 8) + ((int32_t)es0[2] << 16) + ((int32_t)es0[3] << 24);
		out->mag_bias_q16[1] =
		    es0[4] + ((int32_t)es0[5] << 8) + ((int32_t)es0[6] << 16) + ((int32_t)es0[7] << 24);
		out->mag_bias_q16[2] =
		    es0[8] + ((int32_t)es1[0] << 8) + ((int32_t)es1[1] << 16) + ((int32_t)es1[2] << 24);
		out->mag_accuracy_flag = stB->accuracy;
		out->mag_anomalies     = stB->mag_anom;
		out->mag_bias_valid    = 1;

		out->mrm_state       = (inv_imu_auto_mrm_state_t)stB->mrm_state;
		out->mrm_state_valid = 1;

		out->frame_complete = 0;
		break;

	default:
		return INV_IMU_ERROR;
	}

	return status;
}

int inv_imu_edmp_get_sif_class_index(inv_imu_device_t *s, int16_t *class_index)
{
	int status = INV_IMU_OK;

	status |= INV_IMU_READ_EDMP_SRAM(s, EDMP_SIF_CLASS_INDEX, (uint8_t *)class_index);
	return status;
}

int inv_imu_edmp_mask_int_src(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb, uint8_t int_mask)
{
	int      status = INV_IMU_OK;
	uint32_t reg_addr;
	uint8_t  reg;

	/*
	 * Interrupt mask register for EDMP interrupts are located in 3 consecutive
	 * registers starting with STATUS_MASK_PIN_0_7 for interrupt0.
	 */
	reg_addr = STATUS_MASK_PIN_0_7 + edmp_int_nb;

	/* Set bits passed in param to mask corresponding interrupts */
	status |= inv_imu_read_reg(s, reg_addr, 1, &reg);
	reg |= int_mask;
	status |= inv_imu_write_reg(s, reg_addr, 1, &reg);

	return status;
}

int inv_imu_edmp_unmask_int_src(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb,
                                uint8_t int_mask)
{
	int      status = INV_IMU_OK;
	uint32_t reg_addr;
	uint8_t  reg;

	/*
	 * Interrupt mask register for EDMP interrupts are located in 3 consecutive
	 * registers starting with STATUS_MASK_PIN_0_7 for interrupt0.
	 */
	reg_addr = STATUS_MASK_PIN_0_7 + edmp_int_nb;

	/* Clear bits passed in param to unmask corresponding interrupts */
	status |= inv_imu_read_reg(s, reg_addr, 1, &reg);
	reg &= ~(int_mask);
	status |= inv_imu_write_reg(s, reg_addr, 1, &reg);

	return status;
}

int inv_imu_edmp_configure(inv_imu_device_t *s)
{
	int      status       = INV_IMU_OK;
	uint16_t start_addr[] = { EDMP_ROM_START_ADDR_IRQ0, EDMP_ROM_START_ADDR_IRQ1,
		                      EDMP_ROM_START_ADDR_IRQ2 };
	/* Only 8 MSB of SP address is written to register */
	uint8_t stack_addr = (uint8_t)(EDMP_APEX_FEATURE_STACK_END >> 8);

	/* Set Start address for 3 edmp IRQ handlers */
	status |=
	    inv_imu_write_reg(s, EDMP_PRGRM_IRQ0_0, sizeof(start_addr), (uint8_t *)&start_addr[0]);

	/* Set Stack pointer start address */
	status |= inv_imu_write_reg(s, EDMP_SP_START_ADDR, sizeof(stack_addr), (uint8_t *)&stack_addr);

	return status;
}

int inv_imu_edmp_run_ondemand(inv_imu_device_t *s, inv_imu_edmp_int_t edmp_int_nb)
{
	int            status = INV_IMU_OK;
	reg_host_msg_t reg_host_msg;

	status |= inv_imu_edmp_unmask_int_src(s, edmp_int_nb, EDMP_INT_SRC_ON_DEMAND_MASK);

	status |= inv_imu_edmp_enable(s);

	status |= inv_imu_read_reg(s, REG_HOST_MSG, 1, (uint8_t *)&reg_host_msg);
	reg_host_msg.edmp_on_demand_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, REG_HOST_MSG, 1, (uint8_t *)&reg_host_msg);

	return status;
}

int inv_imu_edmp_write_ram_area(inv_imu_device_t *s, uint16_t start_addr, uint16_t size,
                                uint8_t value)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t save_edmp_apex_en0;
	edmp_apex_en1_t save_edmp_apex_en1;
	uint32_t        edmp_service_id;

	/*
	 * Check that DMP is turned OFF before requesting memset service
	 */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&save_edmp_apex_en0);
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&save_edmp_apex_en1);
	if (save_edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	/* Request memset(start_addr, val, size) */
	edmp_service_id = EDMP_ONDEMAND_ENABLE_MEMSET;
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_ONDEMAND_STATIC_SERVICE_REQUEST,
	                                  (uint8_t *)&edmp_service_id);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_ONDEMAND_MEMSET_ADDR, (uint8_t *)&start_addr);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_ONDEMAND_MEMSET_SIZE, (uint8_t *)&size);
	status |= INV_IMU_WRITE_EDMP_SRAM(s, EDMP_ONDEMAND_MEMSET_VALUE, (uint8_t *)&value);
	status |= inv_imu_edmp_run_ondemand(s, INV_IMU_EDMP_INT2);

	/* Wait 200 us to give enough time for EMDP to start running */
	inv_imu_sleep_us(s, 200);

	/* Wait for DMP execution to complete */
	status |= inv_imu_edmp_wait_for_idle(s);

	/* Reset states */
	status |= inv_imu_edmp_mask_int_src(s, INV_IMU_EDMP_INT2, EDMP_INT_SRC_ON_DEMAND_MASK);

	/* Restore original DMP state, with DMP necessarily disabled as it was checked at the beginning of this function */
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&save_edmp_apex_en0);
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&save_edmp_apex_en1);

	return status;
}

int inv_imu_edmp_wait_for_idle(inv_imu_device_t *s)
{
	int          status = INV_IMU_OK;
	ipreg_misc_t ipreg_misc;
	int          timeout_us = 1000000; /* 1 sec */

	/* Wait for idle == 1 (indicates EDMP is not running, e.g execution is completed) */
	while (status == INV_IMU_OK) {
		status |= inv_imu_read_reg(s, IPREG_MISC, 1, (uint8_t *)&ipreg_misc);
		if (ipreg_misc.edmp_idle != 0)
			break;

		inv_imu_sleep_us(s, 5);
		timeout_us -= 5;

		if (timeout_us <= 0)
			return INV_IMU_ERROR_TIMEOUT;
	}

	return status;
}
