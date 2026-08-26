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
#include "imu/inv_imu_edmp_extended_features.h"
#include "imu/inv_imu_edmp_defs.h"
#include "imu/inv_imu_edmp_ext_features_memmap.h"
#include "imu/inv_imu_edmp_patches_defs.h"

/** Value to be written in RAM in EDMP_RAM_FEATURE_PRGM_RAM_BASE to jump to
 *  edmp_prgm_ram_dispatch.h entry point when this patch point is hit by EDMP */
#define PATCH_KEY_OVER_SIF ( (uint32_t)0x000070f1 | \
	                        ((uint32_t)(RAM_DISPATCH_PRGM_BASE & 0xFF00) << 8) | \
	                        ((uint32_t)(RAM_DISPATCH_PRGM_BASE & 0x00FF) \
	                        << 24) )

/** Value to be written in RAM in EDMP_RAM_FEATURE_PRGM_RAM_BASE to jump to
 *  edmp_prgm_ram_dispatch_over_gaf.h entry point when this patch point is hit by EDMP */
#define PATCH_KEY_OVER_GAF ( (uint32_t)0x000070f1 | \
	                        ((uint32_t)(RAM_DISPATCH_OVER_GAF_PRGM_BASE & 0xFF00) << 8) | \
	                        ((uint32_t)(RAM_DISPATCH_OVER_GAF_PRGM_BASE & 0x00FF) \
	                        << 24) )

int inv_imu_edmp_b2s_init_over_sif(inv_imu_device_t *s, inv_imu_edmp_b2s_init_t *usecase)
{
	int status = INV_IMU_OK;

	/* Load B2S RAM image over SIF data area, part of APEX set of default features */
	const uint32_t patch_key = PATCH_KEY_OVER_SIF;
	uint32_t       read_patch_key;
	static uint8_t ram_loader_img[] = {
#include "imu/edmp_prgm_ram_dispatch.h"
	};
	static uint8_t ram_img[] = {
#include "imu/edmp_ram_b2s_image.h"
	};

	/* Check if RAM loader image was already loaded in RAM */
	status |= inv_imu_read_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&read_patch_key);
	if (read_patch_key == 0) {
		/* If it was not already loaded, load it to RAM and update patch entry point value */
		status |=
		    inv_imu_write_sram(s, RAM_DISPATCH_PRGM_BASE, sizeof(ram_loader_img), ram_loader_img);
		status |= inv_imu_write_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&patch_key);
	} else if (read_patch_key != patch_key) {
		/* If an image was already loaded but it is not the expected RAM image, return an error */
		status = INV_IMU_ERROR;
	}

	status |= inv_imu_write_sram(s, RAM_B2S_IMG_DATA_BASE, sizeof(ram_img), ram_img);
	*usecase = INV_IMU_EDMP_B2S_INIT_OVER_SIF;

	return status;
}

int inv_imu_edmp_b2s_init_over_gaf(inv_imu_device_t *s, inv_imu_edmp_b2s_init_t *usecase)
{
	int status = INV_IMU_OK;

	/* Load B2S RAM image over GAF data area, part of APEX set of default features */
	const uint32_t patch_key = PATCH_KEY_OVER_GAF;
	uint32_t       read_patch_key;
	static uint8_t ram_loader_img[] = {
#include "imu/edmp_prgm_ram_dispatch_over_gaf.h"
	};
	static uint8_t ram_img[] = {
#include "imu/edmp_ram_b2s_over_gaf_image.h"
	};

	/* Check if RAM loader image was already loaded in RAM */
	status |= inv_imu_read_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&read_patch_key);
	if (read_patch_key == 0) {
		/* If it was not already loaded, load it to RAM and update patch entry point value */
		status |= inv_imu_write_sram(s, RAM_DISPATCH_OVER_GAF_PRGM_BASE, sizeof(ram_loader_img),
		                             ram_loader_img);
		status |= inv_imu_write_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&patch_key);
	} else if (read_patch_key != patch_key) {
		/* If an image was already loaded but it is not the expected RAM image, return an error */
		status = INV_IMU_ERROR;
	}

	status |= inv_imu_write_sram(s, RAM_B2S_OVER_GAF_IMG_DATA_BASE, sizeof(ram_img), ram_img);
	*usecase = INV_IMU_EDMP_B2S_INIT_OVER_GAF;

	return status;
}

int inv_imu_edmp_b2s_get_parameters(inv_imu_device_t *s, inv_imu_edmp_b2s_parameters_t *b2s_params,
                                    inv_imu_edmp_b2s_init_t usecase)
{
	int     status = INV_IMU_OK;
	int16_t ram_offset;

	if (usecase == INV_IMU_EDMP_B2S_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_B2S_OVER_GAF_IMG_DATA_BASE - RAM_B2S_IMG_DATA_BASE;

	status |=
	    inv_imu_read_sram(s, EDMP_B2S_MOUNTING_MATRIX + ram_offset, EDMP_B2S_MOUNTING_MATRIX_SIZE,
	                      (uint8_t *)&b2s_params->b2s_mounting_matrix);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_DEV_NORM_MAX + ram_offset,
	                            EDMP_B2S_SETTINGS_DEV_NORM_MAX_SIZE,
	                            (uint8_t *)&b2s_params->dev_norm_max);
	status |=
	    inv_imu_read_sram(s, EDMP_B2S_SETTINGS_SIN_LIMIT + ram_offset,
	                      EDMP_B2S_SETTINGS_SIN_LIMIT_SIZE, (uint8_t *)&b2s_params->sin_limit);
	status |=
	    inv_imu_read_sram(s, EDMP_B2S_SETTINGS_FAST_LIMIT + ram_offset,
	                      EDMP_B2S_SETTINGS_FAST_LIMIT_SIZE, (uint8_t *)&b2s_params->fast_limit);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_STATIC_LIMIT + ram_offset,
	                            EDMP_B2S_SETTINGS_STATIC_LIMIT_SIZE,
	                            (uint8_t *)&b2s_params->static_limit);
	status |=
	    inv_imu_read_sram(s, EDMP_B2S_SETTINGS_THR_COS_ANG + ram_offset,
	                      EDMP_B2S_SETTINGS_THR_COS_ANG_SIZE, (uint8_t *)&b2s_params->thr_cos_ang);
	status |=
	    inv_imu_read_sram(s, EDMP_B2S_SETTINGS_REV_X_LIMIT + ram_offset,
	                      EDMP_B2S_SETTINGS_REV_X_LIMIT_SIZE, (uint8_t *)&b2s_params->rev_x_limit);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE + ram_offset,
	                            EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE_SIZE,
	                            (uint8_t *)&b2s_params->sin_flat_angle);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT + ram_offset,
	                            EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT_SIZE,
	                            (uint8_t *)&b2s_params->timer_flat_reject);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT + ram_offset,
	                            EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT_SIZE,
	                            (uint8_t *)&b2s_params->fast_motion_age_limit);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT + ram_offset,
	                            EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT_SIZE,
	                            (uint8_t *)&b2s_params->fast_motion_time_limit);
	status |=
	    inv_imu_read_sram(s, EDMP_B2S_SETTINGS_AGE_LIMIT + ram_offset,
	                      EDMP_B2S_SETTINGS_AGE_LIMIT_SIZE, (uint8_t *)&b2s_params->age_limit);
	status |= inv_imu_read_sram(s, EDMP_B2S_SETTINGS_REV_LATENCY_TH + ram_offset,
	                            EDMP_B2S_SETTINGS_REV_LATENCY_TH_SIZE,
	                            (uint8_t *)&b2s_params->rev_latency_th);

	return status;
}

int inv_imu_edmp_b2s_set_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_b2s_parameters_t *b2s_params,
                                    inv_imu_edmp_b2s_init_t              usecase)
{
	int             status = INV_IMU_OK;
	int16_t         ram_offset;
	int32_t         one_g_value;
	int32_t         b2s_limit_inf;
	int32_t         b2s_limit_sup;
	edmp_apex_en0_t edmp_apex_en0;
	edmp_apex_en1_t edmp_apex_en1;

	/* DMP cannot be configured if it is running, hence make sure B2S algorithm is off */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	if (edmp_apex_en0.reserved0 && edmp_apex_en1.feature3_en && edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	if (usecase == INV_IMU_EDMP_B2S_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_B2S_OVER_GAF_IMG_DATA_BASE - RAM_B2S_IMG_DATA_BASE;

	status |=
	    inv_imu_write_sram(s, EDMP_B2S_MOUNTING_MATRIX + ram_offset, EDMP_B2S_MOUNTING_MATRIX_SIZE,
	                       (uint8_t *)&b2s_params->b2s_mounting_matrix);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_DEV_NORM_MAX + ram_offset,
	                             EDMP_B2S_SETTINGS_DEV_NORM_MAX_SIZE,
	                             (uint8_t *)&b2s_params->dev_norm_max);
	status |=
	    inv_imu_write_sram(s, EDMP_B2S_SETTINGS_SIN_LIMIT + ram_offset,
	                       EDMP_B2S_SETTINGS_SIN_LIMIT_SIZE, (uint8_t *)&b2s_params->sin_limit);
	status |=
	    inv_imu_write_sram(s, EDMP_B2S_SETTINGS_FAST_LIMIT + ram_offset,
	                       EDMP_B2S_SETTINGS_FAST_LIMIT_SIZE, (uint8_t *)&b2s_params->fast_limit);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_STATIC_LIMIT + ram_offset,
	                             EDMP_B2S_SETTINGS_STATIC_LIMIT_SIZE,
	                             (uint8_t *)&b2s_params->static_limit);
	status |=
	    inv_imu_write_sram(s, EDMP_B2S_SETTINGS_THR_COS_ANG + ram_offset,
	                       EDMP_B2S_SETTINGS_THR_COS_ANG_SIZE, (uint8_t *)&b2s_params->thr_cos_ang);
	status |=
	    inv_imu_write_sram(s, EDMP_B2S_SETTINGS_REV_X_LIMIT + ram_offset,
	                       EDMP_B2S_SETTINGS_REV_X_LIMIT_SIZE, (uint8_t *)&b2s_params->rev_x_limit);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE + ram_offset,
	                             EDMP_B2S_SETTINGS_SIN_FLAT_ANGLE_SIZE,
	                             (uint8_t *)&b2s_params->sin_flat_angle);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT + ram_offset,
	                             EDMP_B2S_SETTINGS_TIMER_FLAT_REJECT_SIZE,
	                             (uint8_t *)&b2s_params->timer_flat_reject);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT + ram_offset,
	                             EDMP_B2S_SETTINGS_FAST_MOTION_AGE_LIMIT_SIZE,
	                             (uint8_t *)&b2s_params->fast_motion_age_limit);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT + ram_offset,
	                             EDMP_B2S_SETTINGS_FAST_MOTION_TIME_LIMIT_SIZE,
	                             (uint8_t *)&b2s_params->fast_motion_time_limit);
	status |=
	    inv_imu_write_sram(s, EDMP_B2S_SETTINGS_AGE_LIMIT + ram_offset,
	                       EDMP_B2S_SETTINGS_AGE_LIMIT_SIZE, (uint8_t *)&b2s_params->age_limit);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_REV_LATENCY_TH + ram_offset,
	                             EDMP_B2S_SETTINGS_REV_LATENCY_TH_SIZE,
	                             (uint8_t *)&b2s_params->rev_latency_th);

	/* Get internal parameter from edmp */
	status |= inv_imu_read_sram(s, EDMP_B2S_ONE_G_VALUE + ram_offset, EDMP_B2S_ONE_G_VALUE_SIZE,
	                            (uint8_t *)&one_g_value);

	/* Derive internal parameters */
	b2s_limit_inf =
	    (one_g_value - b2s_params->dev_norm_max) * (one_g_value - b2s_params->dev_norm_max);
	b2s_limit_sup =
	    (one_g_value + b2s_params->dev_norm_max) * (one_g_value + b2s_params->dev_norm_max);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_LIMIT_INF + ram_offset,
	                             EDMP_B2S_SETTINGS_LIMIT_INF_SIZE, (uint8_t *)&b2s_limit_inf);
	status |= inv_imu_write_sram(s, EDMP_B2S_SETTINGS_LIMIT_SUP + ram_offset,
	                             EDMP_B2S_SETTINGS_LIMIT_SUP_SIZE, (uint8_t *)&b2s_limit_sup);

	return status;
}

int inv_imu_edmp_b2s_enable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.reserved0 = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.feature3_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_b2s_disable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.reserved0 = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	/* All extended custom algorithms from RAM image are now disabled, can now disable EDMP to run any algorithm from RAM image */
	if (edmp_apex_en0.reserved1 == INV_IMU_DISABLE) {
		edmp_apex_en1_t edmp_apex_en1;
		status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
		edmp_apex_en1.feature3_en = INV_IMU_DISABLE;
		status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	}

	return status;
}

int inv_imu_edmp_aid_init_over_sif(inv_imu_device_t *s, inv_imu_edmp_aid_init_t *usecase)
{
	int status = INV_IMU_OK;

	/* Load AID RAM image over SIF data area, part of APEX set of default features */
	const uint32_t patch_key = PATCH_KEY_OVER_SIF;
	uint32_t       read_patch_key;
	static uint8_t ram_loader_img[] = {
#include "imu/edmp_prgm_ram_dispatch.h"
	};
	static uint8_t ram_img[] = {
#include "imu/edmp_ram_aid_image.h"
	};

	/* Check if RAM loader image was already loaded in RAM */
	status |= inv_imu_read_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&read_patch_key);
	if (read_patch_key == 0) {
		/* If it was not already loaded, load it to RAM and update patch entry point value */
		status |=
		    inv_imu_write_sram(s, RAM_DISPATCH_PRGM_BASE, sizeof(ram_loader_img), ram_loader_img);
		status |= inv_imu_write_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&patch_key);
	} else if (read_patch_key != patch_key) {
		/* If an image was already loaded but it is not the expected RAM image, return an error */
		status = INV_IMU_ERROR;
	}

	status |= inv_imu_write_sram(s, RAM_AID_IMG_DATA_BASE, sizeof(ram_img), ram_img);
	*usecase = INV_IMU_EDMP_AID_INIT_OVER_SIF;

	return status;
}

int inv_imu_edmp_aid_init_over_gaf(inv_imu_device_t *s, inv_imu_edmp_aid_init_t *usecase)
{
	int status = INV_IMU_OK;

	/* Load AID RAM image over GAF data area, part of APEX set of default features */
	const uint32_t patch_key = PATCH_KEY_OVER_GAF;
	uint32_t       read_patch_key;
	static uint8_t ram_loader_img[] = {
#include "imu/edmp_prgm_ram_dispatch_over_gaf.h"
	};
	static uint8_t ram_img[] = {
#include "imu/edmp_ram_aid_over_gaf_image.h"
	};

	/* Check if RAM loader image was already loaded in RAM */
	status |= inv_imu_read_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&read_patch_key);
	if (read_patch_key == 0) {
		/* If it was not already loaded, load it to RAM and update patch entry point value */
		status |= inv_imu_write_sram(s, RAM_DISPATCH_OVER_GAF_PRGM_BASE, sizeof(ram_loader_img),
		                             ram_loader_img);
		status |= inv_imu_write_sram(s, EDMP_RAM_FEATURE_PRGM_RAM_BASE, 4, (uint8_t *)&patch_key);
	} else if (read_patch_key != patch_key) {
		/* If an image was already loaded but it is not the expected RAM image, return an error */
		status = INV_IMU_ERROR;
	}

	status |= inv_imu_write_sram(s, RAM_AID_OVER_GAF_IMG_DATA_BASE, sizeof(ram_img), ram_img);
	*usecase = INV_IMU_EDMP_AID_INIT_OVER_GAF;

	return status;
}

int inv_imu_edmp_aid_get_parameters(inv_imu_device_t *s, inv_imu_edmp_aid_parameters_t *aid_params,
                                    inv_imu_edmp_aid_init_t usecase)
{
	int     status = INV_IMU_OK;
	int16_t ram_offset;

	if (usecase == INV_IMU_EDMP_AID_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_AID_OVER_GAF_IMG_DATA_BASE - RAM_AID_IMG_DATA_BASE;

	/* -- human instance -- */
	status |= inv_imu_read_sram(s, EDMP_AID_WIN_HUMAN + ram_offset, EDMP_AID_WIN_HUMAN_SIZE,
	                            (uint8_t *)&aid_params->aid_human.aid_update_win);
	status |= inv_imu_read_sram(s, EDMP_AID_ALERT_HUMAN + ram_offset, EDMP_AID_ALERT_HUMAN_SIZE,
	                            (uint8_t *)&aid_params->aid_human.aid_alert_timer);
	status |=
	    inv_imu_read_sram(s, EDMP_AID_EN_OUTPUT_HUMAN + ram_offset, EDMP_AID_EN_OUTPUT_HUMAN_SIZE,
	                      (uint8_t *)&aid_params->aid_human.aid_output_enable);
	status |= inv_imu_read_sram(s, EDMP_AID_DIS_MULTI_OUTPUT_HUMAN + ram_offset,
	                            EDMP_AID_DIS_MULTI_OUTPUT_HUMAN_SIZE,
	                            (uint8_t *)&aid_params->aid_human.aid_disable_multiple_interrupt);
	/* -- device instance -- */
	status |= inv_imu_read_sram(s, EDMP_AID_WIN_DEVICE + ram_offset, EDMP_AID_WIN_DEVICE_SIZE,
	                            (uint8_t *)&aid_params->aid_device.aid_update_win);
	status |= inv_imu_read_sram(s, EDMP_AID_ALERT_DEVICE + ram_offset, EDMP_AID_ALERT_DEVICE_SIZE,
	                            (uint8_t *)&aid_params->aid_device.aid_alert_timer);
	status |=
	    inv_imu_read_sram(s, EDMP_AID_EN_OUTPUT_DEVICE + ram_offset, EDMP_AID_EN_OUTPUT_DEVICE_SIZE,
	                      (uint8_t *)&aid_params->aid_device.aid_output_enable);
	status |= inv_imu_read_sram(s, EDMP_AID_DIS_MULTI_OUTPUT_DEVICE + ram_offset,
	                            EDMP_AID_DIS_MULTI_OUTPUT_DEVICE_SIZE,
	                            (uint8_t *)&aid_params->aid_device.aid_disable_multiple_interrupt);

	return status;
}

int inv_imu_edmp_aid_set_parameters(inv_imu_device_t *                   s,
                                    const inv_imu_edmp_aid_parameters_t *aid_params,
                                    inv_imu_edmp_aid_init_t              usecase)
{
	int             status = INV_IMU_OK;
	int16_t         ram_offset;
	edmp_apex_en0_t edmp_apex_en0;
	edmp_apex_en1_t edmp_apex_en1;

	/* DMP cannot be configured if it is running, hence make sure AID algorithm is off */
	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	if (edmp_apex_en0.reserved1 && edmp_apex_en1.feature3_en && edmp_apex_en1.edmp_enable)
		return INV_IMU_ERROR;

	if (usecase == INV_IMU_EDMP_AID_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_AID_OVER_GAF_IMG_DATA_BASE - RAM_AID_IMG_DATA_BASE;

	/* -- human instance -- */
	status |= inv_imu_write_sram(s, EDMP_AID_WIN_HUMAN + ram_offset, EDMP_AID_WIN_HUMAN_SIZE,
	                             (uint8_t *)&aid_params->aid_human.aid_update_win);
	status |= inv_imu_write_sram(s, EDMP_AID_ALERT_HUMAN + ram_offset, EDMP_AID_ALERT_HUMAN_SIZE,
	                             (uint8_t *)&aid_params->aid_human.aid_alert_timer);
	status |=
	    inv_imu_write_sram(s, EDMP_AID_EN_OUTPUT_HUMAN + ram_offset, EDMP_AID_EN_OUTPUT_HUMAN_SIZE,
	                       (uint8_t *)&aid_params->aid_human.aid_output_enable);
	status |= inv_imu_write_sram(s, EDMP_AID_DIS_MULTI_OUTPUT_HUMAN + ram_offset,
	                             EDMP_AID_DIS_MULTI_OUTPUT_HUMAN_SIZE,
	                             (uint8_t *)&aid_params->aid_human.aid_disable_multiple_interrupt);
	/* -- device instance -- */
	status |= inv_imu_write_sram(s, EDMP_AID_WIN_DEVICE + ram_offset, EDMP_AID_WIN_DEVICE_SIZE,
	                             (uint8_t *)&aid_params->aid_device.aid_update_win);
	status |= inv_imu_write_sram(s, EDMP_AID_ALERT_DEVICE + ram_offset, EDMP_AID_ALERT_DEVICE_SIZE,
	                             (uint8_t *)&aid_params->aid_device.aid_alert_timer);
	status |= inv_imu_write_sram(s, EDMP_AID_EN_OUTPUT_DEVICE + ram_offset,
	                             EDMP_AID_EN_OUTPUT_DEVICE_SIZE,
	                             (uint8_t *)&aid_params->aid_device.aid_output_enable);
	status |= inv_imu_write_sram(s, EDMP_AID_DIS_MULTI_OUTPUT_DEVICE + ram_offset,
	                             EDMP_AID_DIS_MULTI_OUTPUT_DEVICE_SIZE,
	                             (uint8_t *)&aid_params->aid_device.aid_disable_multiple_interrupt);

	return status;
}

int inv_imu_edmp_aid_enable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;
	edmp_apex_en1_t edmp_apex_en1;

	status |= inv_imu_edmp_check_odr_decimation(s);
	if (status)
		return status;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.reserved1 = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	edmp_apex_en1.feature3_en = INV_IMU_ENABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);

	return status;
}

int inv_imu_edmp_aid_disable(inv_imu_device_t *s)
{
	int             status = INV_IMU_OK;
	edmp_apex_en0_t edmp_apex_en0;

	status |= inv_imu_read_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);
	edmp_apex_en0.reserved1 = INV_IMU_DISABLE;
	status |= inv_imu_write_reg(s, EDMP_APEX_EN0, 1, (uint8_t *)&edmp_apex_en0);

	/* All extended custom algorithms from RAM image are now disabled, can now disable EDMP to run any algorithm from RAM image */
	if (edmp_apex_en0.reserved0 == INV_IMU_DISABLE) {
		edmp_apex_en1_t edmp_apex_en1;
		status |= inv_imu_read_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
		edmp_apex_en1.feature3_en = INV_IMU_DISABLE;
		status |= inv_imu_write_reg(s, EDMP_APEX_EN1, 1, (uint8_t *)&edmp_apex_en1);
	}

	return status;
}

int inv_imu_edmp_aid_get_data_human(inv_imu_device_t *s, inv_imu_edmp_aid_init_t usecase,
                                    uint8_t *output_state)
{
	int     status = INV_IMU_OK;
	int16_t ram_offset;

	if (usecase == INV_IMU_EDMP_AID_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_AID_OVER_GAF_IMG_DATA_BASE - RAM_AID_IMG_DATA_BASE;

	status |= inv_imu_read_sram(s, EDMP_AID_HUMAN_OUTPUT_STATE + ram_offset,
	                            EDMP_AID_HUMAN_OUTPUT_STATE_SIZE, output_state);

	return status;
}

int inv_imu_edmp_aid_get_data_device(inv_imu_device_t *s, inv_imu_edmp_aid_init_t usecase,
                                     uint8_t *output_state)
{
	int     status = INV_IMU_OK;
	int16_t ram_offset;

	if (usecase == INV_IMU_EDMP_AID_INIT_OVER_SIF)
		ram_offset = 0;
	else
		ram_offset = RAM_AID_OVER_GAF_IMG_DATA_BASE - RAM_AID_IMG_DATA_BASE;

	status |= inv_imu_read_sram(s, EDMP_AID_DEVICE_OUTPUT_STATE + ram_offset,
	                            EDMP_AID_DEVICE_OUTPUT_STATE_SIZE, output_state);

	return status;
}