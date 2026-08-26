/*
 * G2 integration for the pristine TDK InvenSense ICM45608 1.1.2 driver.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * The driver sources remain immutable under third_party/invensense-icm45608.
 * This adapter supplies freestanding memory primitives, a stateless ICT1531x
 * I2C-master bring-up, the official MRM image loader, bounded FIFO access, and
 * the complete public GAF configuration/decode path used by the G2 wrapper.
 */

#include <stddef.h>
#include <stdint.h>

#include "imu/inv_imu_driver.h"
#include "imu/inv_imu_driver_advanced.h"
#include "imu/inv_imu_edmp.h"
#include "imu/inv_imu_edmp_defs.h"
#include "imu/inv_imu_edmp_ext_features_memmap.h"
#include "imu/inv_imu_edmp_patches_defs.h"
#include "imu/inv_imu_edmp_ram_mrm_memmap.h"
#include "imu/inv_imu_i2cm.h"

enum {
    OPEN_CFW_TDK_MAG_ADDRESS = 0x1eu,
    OPEN_CFW_TDK_MAG_CHIP_ID_REGISTER = 0x01u,
    OPEN_CFW_TDK_MAG_CHIP_ID = 0x45u,
    OPEN_CFW_TDK_MAG_MODE_CONTROL_REGISTER = 0x04u,
    OPEN_CFW_TDK_MAG_STATUS_REGISTER = 0x06u,
    OPEN_CFW_TDK_MAG_SEQUENCER_CONTROL_REGISTER = 0x7cu,
    OPEN_CFW_TDK_MAG_GLOBAL_LOCK_REGISTER = 0x7fu,
    OPEN_CFW_TDK_MAG_SINGLE_SHOT = 0x02u,
    OPEN_CFW_TDK_MAG_STANDBY = 0x00u,
    OPEN_CFW_TDK_I2CM_POLL_LIMIT = 10000u,
};

static void *open_cfw_tdk_copy_bytes(void *destination, const void *source,
                                     size_t length)
{
    volatile uint8_t *out = (volatile uint8_t *)destination;
    const volatile uint8_t *in = (const volatile uint8_t *)source;
    size_t index;
    for (index = 0u; index < length; ++index)
        out[index] = in[index];
    return destination;
}

static void *open_cfw_tdk_fill_bytes(void *destination, int value,
                                     size_t length)
{
    volatile uint8_t *out = (volatile uint8_t *)destination;
    size_t index;
    for (index = 0u; index < length; ++index)
        out[index] = (uint8_t)value;
    return destination;
}

void *open_cfw_tdk_memset(void *destination, int value, size_t length)
{
    return open_cfw_tdk_fill_bytes(destination, value, length);
}

/* The pristine SIF sources use memset without including a hosted header. */
#define memset open_cfw_tdk_memset

void __aeabi_memcpy4(void *destination, const void *source, size_t length)
{
    (void)open_cfw_tdk_copy_bytes(destination, source, length);
}

void __aeabi_memclr4(void *destination, size_t length)
{
    (void)open_cfw_tdk_fill_bytes(destination, 0, length);
}

static int open_cfw_tdk_wait_i2cm(inv_imu_device_t *device)
{
    inv_imu_int_state_t state;
    i2cm_status_t status_register;
    uint32_t attempt;
    int status = INV_IMU_OK;

    (void)open_cfw_tdk_fill_bytes(&state, 0, sizeof(state));
    for (attempt = 0u; attempt < OPEN_CFW_TDK_I2CM_POLL_LIMIT; ++attempt) {
        status = inv_imu_get_int_status(device, INV_IMU_INT1, &state);
        if (status != INV_IMU_OK || state.INV_I2CM_DONE != 0u)
            break;
    }
    if (status != INV_IMU_OK || state.INV_I2CM_DONE == 0u)
        return status != INV_IMU_OK ? status : INV_IMU_ERROR_TIMEOUT;
    status = inv_imu_read_reg(device, I2CM_STATUS, 1u,
                              (uint8_t *)&status_register);
    if (status != INV_IMU_OK)
        return status;
    if (status_register.i2cm_busy || status_register.i2cm_timeout_err ||
        status_register.i2cm_srst_err || status_register.i2cm_scl_err ||
        status_register.i2cm_sda_err)
        return INV_IMU_ERROR_TRANSPORT;
    return INV_IMU_OK;
}

static int open_cfw_tdk_mag_read(inv_imu_device_t *device, uint8_t reg,
                                 uint8_t *data, uint8_t length)
{
    inv_imu_i2c_master_cfg_t configuration;
    int status;
    if (device == NULL || data == NULL || length == 0u)
        return INV_IMU_ERROR_BAD_ARG;
    (void)open_cfw_tdk_fill_bytes(&configuration, 0, sizeof(configuration));
    configuration.i2c_addr = OPEN_CFW_TDK_MAG_ADDRESS;
    configuration.op_cnt = 1u;
    configuration.op[0].r_n_w = 1u;
    configuration.op[0].reg_addr = reg;
    configuration.op[0].len = length;
    status = inv_imu_configure_i2cm(device, &configuration, NULL);
    status |= inv_imu_start_i2cm_ops(device, 1u);
    status |= open_cfw_tdk_wait_i2cm(device);
    status |= inv_imu_get_i2cm_data(device, data, length);
    return status;
}

static int open_cfw_tdk_mag_write(inv_imu_device_t *device, uint8_t reg,
                                  const uint8_t *data, uint8_t length)
{
    inv_imu_i2c_master_cfg_t configuration;
    int status;
    if (device == NULL || data == NULL || length == 0u)
        return INV_IMU_ERROR_BAD_ARG;
    (void)open_cfw_tdk_fill_bytes(&configuration, 0, sizeof(configuration));
    configuration.i2c_addr = OPEN_CFW_TDK_MAG_ADDRESS;
    configuration.op_cnt = 1u;
    configuration.op[0].r_n_w = 0u;
    configuration.op[0].reg_addr = reg;
    configuration.op[0].len = length;
    configuration.op[0].wdata = data;
    status = inv_imu_configure_i2cm(device, &configuration, NULL);
    status |= inv_imu_start_i2cm_ops(device, 1u);
    status |= open_cfw_tdk_wait_i2cm(device);
    return status;
}

int open_cfw_icm45608_tdk_mag_who_am_i(inv_imu_device_t *device,
                                        uint8_t *identity)
{
    inv_imu_int_state_t interrupt_configuration;
    int status;
    if (device == NULL || identity == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    status = inv_imu_init_i2cm(device);
    (void)open_cfw_tdk_fill_bytes(&interrupt_configuration, 0,
                                  sizeof(interrupt_configuration));
    status |= inv_imu_get_config_int(device, INV_IMU_INT1,
                                     &interrupt_configuration);
    interrupt_configuration.INV_I2CM_DONE = INV_IMU_ENABLE;
    status |= inv_imu_set_config_int(device, INV_IMU_INT1,
                                     &interrupt_configuration);
    status |= open_cfw_tdk_mag_read(device,
                                    OPEN_CFW_TDK_MAG_CHIP_ID_REGISTER,
                                    identity, 1u);
    return status;
}

static int open_cfw_tdk_mag_initialize(inv_imu_device_t *device)
{
    inv_imu_int_state_t interrupt_configuration;
    uint8_t value;
    const uint8_t profile[2] = {
        OPEN_CFW_TDK_MAG_STATUS_REGISTER, OPEN_CFW_TDK_MAG_ADDRESS,
    };
    const uint8_t write_buffer[4] = {
        OPEN_CFW_TDK_MAG_MODE_CONTROL_REGISTER,
        OPEN_CFW_TDK_MAG_SINGLE_SHOT,
        OPEN_CFW_TDK_MAG_MODE_CONTROL_REGISTER,
        OPEN_CFW_TDK_MAG_STANDBY,
    };
    const uint8_t command = 0x82u;
    int status;

    status = open_cfw_icm45608_tdk_mag_who_am_i(device, &value);
    if (status != INV_IMU_OK)
        return status;

    value = 0xcau;
    status |= open_cfw_tdk_mag_write(device,
                                     OPEN_CFW_TDK_MAG_GLOBAL_LOCK_REGISTER,
                                     &value, 1u);
    status |= open_cfw_tdk_mag_read(
        device, OPEN_CFW_TDK_MAG_SEQUENCER_CONTROL_REGISTER, &value, 1u);
    value |= 0x80u;
    status |= open_cfw_tdk_mag_write(
        device, OPEN_CFW_TDK_MAG_SEQUENCER_CONTROL_REGISTER, &value, 1u);
    inv_imu_sleep_us(device, 1000u);
    value = 0u;
    status |= open_cfw_tdk_mag_write(device,
                                     OPEN_CFW_TDK_MAG_GLOBAL_LOCK_REGISTER,
                                     &value, 1u);
    status |= open_cfw_tdk_mag_read(device,
                                    OPEN_CFW_TDK_MAG_CHIP_ID_REGISTER,
                                    &value, 1u);
    if (status != INV_IMU_OK || value != OPEN_CFW_TDK_MAG_CHIP_ID)
        return status != INV_IMU_OK ? status : INV_IMU_ERROR;
    status |= open_cfw_tdk_mag_read(device, OPEN_CFW_TDK_MAG_STATUS_REGISTER,
                                    &value, 1u);

    (void)open_cfw_tdk_fill_bytes(&interrupt_configuration, 0,
                                  sizeof(interrupt_configuration));
    status |= inv_imu_get_config_int(device, INV_IMU_INT1,
                                     &interrupt_configuration);
    interrupt_configuration.INV_I2CM_DONE = INV_IMU_DISABLE;
    status |= inv_imu_set_config_int(device, INV_IMU_INT1,
                                     &interrupt_configuration);
    status |= inv_imu_write_reg(device, I2CM_DEV_PROFILE0, sizeof(profile),
                                profile);
    status |= inv_imu_write_reg(device, I2CM_WR_DATA0, sizeof(write_buffer),
                                write_buffer);
    status |= inv_imu_write_reg(device, I2CM_COMMAND_1, sizeof(command),
                                &command);
    return status;
}

static int open_cfw_tdk_load_mrm_image(inv_imu_device_t *device)
{
    static const uint8_t image[] = {
#include "imu/edmp_ram_mrm_image.h"
    };
    uint32_t program_start;
    int status;
    (void)open_cfw_tdk_copy_bytes(
        &program_start,
        &image[RAM_MRM_IMG_PRGM_BASE - RAM_MRM_IMG_DATA_BASE],
        sizeof(program_start));
    status = inv_imu_write_sram(device, RAM_MRM_IMG_DATA_BASE,
                                sizeof(image), image);
    status |= inv_imu_write_sram(
        device, EDMP_INVN_ALGO_MRM_PATCH_POINT_DISPATCH,
        sizeof(program_start), (const uint8_t *)&program_start);
    return status;
}

/*
 * The upstream extended-feature implementation declares its embedded images
 * as writable arrays.  Keep the exact vendor bytes in read-only storage and
 * load them explicitly so the firmware overlay has no startup-copy .data
 * dependency.
 */
static const uint8_t open_cfw_tdk_extended_dispatch[] = {
#include "imu/edmp_prgm_ram_dispatch.h"
};

static const uint8_t open_cfw_tdk_b2s_image[] = {
#include "imu/edmp_ram_b2s_image.h"
};

static const uint8_t open_cfw_tdk_aid_image[] = {
#include "imu/edmp_ram_aid_image.h"
};

static int open_cfw_tdk_b2s_mounting_code(
    const int8_t mounting_matrix[9], uint8_t *code)
{
    uint8_t candidate;
    if (mounting_matrix == NULL || code == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    for (candidate = 0u; candidate < 8u; ++candidate) {
        uint8_t axis[3] = {0u, 1u, 2u};
        int8_t sign[3] = {1, 1, 1};
        uint8_t row;
        uint8_t column;
        uint8_t matches = 1u;
        if ((candidate & 4u) != 0u) {
            uint8_t saved_axis = axis[0];
            int8_t saved_sign = sign[0];
            axis[0] = axis[1];
            sign[0] = sign[1];
            axis[1] = saved_axis;
            sign[1] = saved_sign;
            sign[2] = (int8_t)-sign[2];
        }
        if ((candidate & 2u) != 0u) {
            sign[0] = (int8_t)-sign[0];
            sign[2] = (int8_t)-sign[2];
        }
        if ((candidate & 1u) != 0u) {
            sign[1] = (int8_t)-sign[1];
            sign[2] = (int8_t)-sign[2];
        }
        for (row = 0u; row < 3u; ++row) {
            for (column = 0u; column < 3u; ++column) {
                const int8_t expected =
                    column == axis[row] ? sign[row] : 0;
                if (mounting_matrix[(uint32_t)row * 3u + column] !=
                    expected)
                    matches = 0u;
            }
        }
        if (matches != 0u) {
            *code = candidate;
            return INV_IMU_OK;
        }
    }
    return INV_IMU_ERROR_BAD_ARG;
}

static int open_cfw_tdk_load_extended_images(
    inv_imu_device_t *device, const int8_t mounting_matrix[9])
{
    const uint32_t patch_key =
        (uint32_t)0x000070f1u |
        ((uint32_t)(RAM_DISPATCH_PRGM_BASE & 0xff00u) << 8) |
        ((uint32_t)(RAM_DISPATCH_PRGM_BASE & 0x00ffu) << 24);
    uint32_t installed_key = 0u;
    uint8_t b2s_mounting = 0u;
    int status;

    status = open_cfw_tdk_b2s_mounting_code(mounting_matrix, &b2s_mounting);
    if (status != INV_IMU_OK)
        return status;
    status = inv_imu_read_sram(device, EDMP_RAM_FEATURE_PRGM_RAM_BASE,
                               sizeof(installed_key),
                               (uint8_t *)&installed_key);
    if (status != INV_IMU_OK)
        return status;
    if (installed_key == 0u) {
        status |= inv_imu_write_sram(device, RAM_DISPATCH_PRGM_BASE,
                                     sizeof(open_cfw_tdk_extended_dispatch),
                                     open_cfw_tdk_extended_dispatch);
        status |= inv_imu_write_sram(device, EDMP_RAM_FEATURE_PRGM_RAM_BASE,
                                     sizeof(patch_key),
                                     (const uint8_t *)&patch_key);
    } else if (installed_key != patch_key) {
        return INV_IMU_ERROR;
    }
    status |= inv_imu_write_sram(device, RAM_B2S_IMG_DATA_BASE,
                                 sizeof(open_cfw_tdk_b2s_image),
                                 open_cfw_tdk_b2s_image);
    status |= inv_imu_write_sram(device, RAM_AID_IMG_DATA_BASE,
                                 sizeof(open_cfw_tdk_aid_image),
                                 open_cfw_tdk_aid_image);
    status |= inv_imu_write_sram(device, EDMP_B2S_MOUNTING_MATRIX,
                                 EDMP_B2S_MOUNTING_MATRIX_SIZE,
                                 &b2s_mounting);
    return status;
}

int open_cfw_icm45608_tdk_set_extended_features(
    inv_imu_device_t *device, uint8_t aid_enabled, uint8_t b2s_enabled)
{
    edmp_apex_en0_t enable0;
    edmp_apex_en1_t enable1;
    int status;
    if (device == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    status = inv_imu_read_reg(device, EDMP_APEX_EN0, 1u,
                              (uint8_t *)&enable0);
    status |= inv_imu_read_reg(device, EDMP_APEX_EN1, 1u,
                               (uint8_t *)&enable1);
    enable0.reserved0 = b2s_enabled != 0u;
    enable0.reserved1 = aid_enabled != 0u;
    enable1.feature3_en = aid_enabled != 0u || b2s_enabled != 0u;
    status |= inv_imu_write_reg(device, EDMP_APEX_EN0, 1u,
                                (const uint8_t *)&enable0);
    status |= inv_imu_write_reg(device, EDMP_APEX_EN1, 1u,
                                (const uint8_t *)&enable1);
    return status;
}

int open_cfw_icm45608_tdk_read_extended_events(
    inv_imu_device_t *device, uint8_t *events, uint8_t *aid_human,
    uint8_t *aid_device)
{
    inv_imu_edmp_int_state_t state;
    int status;
    if (device == NULL || events == NULL || aid_human == NULL ||
        aid_device == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    (void)open_cfw_tdk_fill_bytes(&state, 0, sizeof(state));
    *events = 0u;
    *aid_human = 0u;
    *aid_device = 0u;
    status = inv_imu_edmp_get_int_apex_status(device, &state);
    if (status != INV_IMU_OK)
        return status;
    *events = (uint8_t)((state.INV_B2S != 0u ? 1u : 0u) |
                        (state.INV_B2S_REV != 0u ? 2u : 0u) |
                        (state.INV_AID_HUMAN != 0u ? 4u : 0u) |
                        (state.INV_AID_DEVICE != 0u ? 8u : 0u));
    if (state.INV_AID_HUMAN != 0u)
        status |= inv_imu_read_sram(device, EDMP_AID_HUMAN_OUTPUT_STATE,
                                    EDMP_AID_HUMAN_OUTPUT_STATE_SIZE,
                                    aid_human);
    if (state.INV_AID_DEVICE != 0u)
        status |= inv_imu_read_sram(device, EDMP_AID_DEVICE_OUTPUT_STATE,
                                    EDMP_AID_DEVICE_OUTPUT_STATE_SIZE,
                                    aid_device);
    return status;
}

static dmp_ext_sen_odr_cfg_apex_odr_t open_cfw_tdk_edmp_odr(uint8_t odr)
{
    switch (odr) {
    case ACCEL_CONFIG0_ACCEL_ODR_800_HZ:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_800_HZ;
    case ACCEL_CONFIG0_ACCEL_ODR_400_HZ:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_400_HZ;
    case ACCEL_CONFIG0_ACCEL_ODR_200_HZ:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_200_HZ;
    case ACCEL_CONFIG0_ACCEL_ODR_100_HZ:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_100_HZ;
    case ACCEL_CONFIG0_ACCEL_ODR_50_HZ:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_50_HZ;
    default:
        return DMP_EXT_SEN_ODR_CFG_APEX_ODR_25_HZ;
    }
}

int open_cfw_icm45608_tdk_configure(inv_imu_device_t *device,
                                     uint8_t accel_odr, uint8_t gyro_odr,
                                     uint16_t watermark, uint32_t period_us,
                                     uint8_t fusion_enabled,
                                     uint8_t extended_enabled,
                                     const int8_t mounting_matrix[9])
{
    inv_imu_adv_fifo_config_t fifo_configuration;
    inv_imu_int_state_t interrupt_configuration;
    inv_imu_edmp_gaf_parameters_t gaf_parameters;
    const int32_t zero_accel_bias[3] = {0, 0, 0};
    const int16_t zero_gyro_bias[3] = {0, 0, 0};
    const int32_t zero_mag_bias[3] = {0, 0, 0};
    const int32_t identity_soft_iron[3][3] = {
        {1L << 30, 0, 0}, {0, 1L << 30, 0}, {0, 0, 1L << 30},
    };
    int status = INV_IMU_OK;

    if (device == NULL || mounting_matrix == NULL || watermark == 0u ||
        period_us == 0u)
        return INV_IMU_ERROR_BAD_ARG;

    status |= inv_imu_edmp_disable(device);
    status |= inv_imu_set_accel_mode(device, PWR_MGMT0_ACCEL_MODE_OFF);
    status |= inv_imu_set_gyro_mode(device, PWR_MGMT0_GYRO_MODE_OFF);
    status |= inv_imu_set_accel_frequency(
        device, (accel_config0_accel_odr_t)accel_odr);
    status |= inv_imu_set_gyro_frequency(
        device, (gyro_config0_gyro_odr_t)gyro_odr);
    status |= inv_imu_set_accel_fsr(
        device, ACCEL_CONFIG0_ACCEL_UI_FS_SEL_16_G);
    status |= inv_imu_set_gyro_fsr(
        device, GYRO_CONFIG0_GYRO_UI_FS_SEL_2000_DPS);
    status |= inv_imu_set_accel_ln_bw(
        device, IPREG_SYS2_REG_131_ACCEL_UI_LPFBW_DIV_4);
    status |= inv_imu_set_gyro_ln_bw(
        device, IPREG_SYS1_REG_172_GYRO_UI_LPFBW_DIV_4);

    (void)open_cfw_tdk_fill_bytes(&fifo_configuration, 0,
                                  sizeof(fifo_configuration));
    fifo_configuration.base_conf.gyro_en = INV_IMU_ENABLE;
    fifo_configuration.base_conf.accel_en = INV_IMU_ENABLE;
    fifo_configuration.base_conf.hires_en = INV_IMU_DISABLE;
    fifo_configuration.base_conf.fifo_wm_th = watermark;
    fifo_configuration.base_conf.fifo_mode = FIFO_CONFIG0_FIFO_MODE_SNAPSHOT;
    fifo_configuration.base_conf.fifo_depth = FIFO_CONFIG0_FIFO_DEPTH_APEX;
    fifo_configuration.fifo_wr_wm_gt_th =
        FIFO_CONFIG2_FIFO_WR_WM_EQ_OR_GT_TH;
    fifo_configuration.tmst_fsync_en = INV_IMU_ENABLE;
    fifo_configuration.es0_6b_9b = FIFO_CONFIG4_FIFO_ES0_9B;
    fifo_configuration.comp_en = INV_IMU_DISABLE;
    fifo_configuration.comp_nc_flow_cfg =
        FIFO_CONFIG4_FIFO_COMP_NC_FLOW_CFG_DIS;
    fifo_configuration.gyro_dec = ODR_DECIMATE_CONFIG_GYRO_FIFO_ODR_DEC_1;
    fifo_configuration.accel_dec = ODR_DECIMATE_CONFIG_ACCEL_FIFO_ODR_DEC_1;

    if (fusion_enabled != 0u || extended_enabled != 0u) {
        status |= inv_imu_edmp_set_frequency(device,
                                              open_cfw_tdk_edmp_odr(accel_odr));
        status |= inv_imu_edmp_init(device);
    }
    if (extended_enabled != 0u) {
        inv_imu_edmp_int_state_t apex_interrupts;
        status |= open_cfw_tdk_load_extended_images(device,
                                                     mounting_matrix);
        status |= open_cfw_icm45608_tdk_set_extended_features(device, 1u,
                                                               1u);
        (void)open_cfw_tdk_fill_bytes(&apex_interrupts, 0,
                                      sizeof(apex_interrupts));
        apex_interrupts.INV_B2S = INV_IMU_ENABLE;
        apex_interrupts.INV_B2S_REV = INV_IMU_ENABLE;
        apex_interrupts.INV_AID_HUMAN = INV_IMU_ENABLE;
        apex_interrupts.INV_AID_DEVICE = INV_IMU_ENABLE;
        status |= inv_imu_edmp_set_config_int_apex(device,
                                                   &apex_interrupts);
    } else if (fusion_enabled != 0u) {
        status |= open_cfw_icm45608_tdk_set_extended_features(device, 0u,
                                                               0u);
    }
    if (fusion_enabled != 0u) {
        status |= open_cfw_tdk_mag_initialize(device);
        status |= inv_imu_edmp_get_gaf_parameters(device, &gaf_parameters);
        gaf_parameters.pdr_us = period_us;
        gaf_parameters.run_spherical = 1u;
        gaf_parameters.mag_dt_us = 20000u;
        status |= inv_imu_edmp_set_gaf_acc_bias(device, zero_accel_bias);
        status |= inv_imu_edmp_set_gaf_gyr_bias(device, zero_gyro_bias, 0u, 0u);
        status |= inv_imu_edmp_set_gaf_mag_bias(device, zero_mag_bias, 0u);
        status |= inv_imu_edmp_set_gaf_parameters(device, &gaf_parameters);
        status |= inv_imu_edmp_set_gaf_mode(device, 1u, 1u);
        status |= inv_imu_edmp_set_gaf_soft_iron_cor_matrix(
            device, identity_soft_iron);
        status |= inv_imu_edmp_enable_gaf_soft_iron_cor(device);
        status |= inv_imu_edmp_set_mounting_matrix(device, mounting_matrix);
        status |= open_cfw_tdk_load_mrm_image(device);
        status |= inv_imu_edmp_start_gaf_fifo_push(device);
        fifo_configuration.es0_en = INV_IMU_ENABLE;
        fifo_configuration.es1_en = INV_IMU_ENABLE;
    }

    status |= inv_imu_adv_disable_wom(device);
    status |= inv_imu_adv_reset_fifo(device);
    status |= inv_imu_set_accel_mode(device, PWR_MGMT0_ACCEL_MODE_LN);
    status |= inv_imu_set_gyro_mode(device, PWR_MGMT0_GYRO_MODE_LN);
    inv_imu_sleep_us(device, GYR_STARTUP_TIME_US);
    status |= inv_imu_adv_set_fifo_config(device, &fifo_configuration);

    (void)open_cfw_tdk_fill_bytes(&interrupt_configuration, 0,
                                  sizeof(interrupt_configuration));
    interrupt_configuration.INV_FIFO_THS = INV_IMU_ENABLE;
    interrupt_configuration.INV_UI_DRDY = INV_IMU_ENABLE;
    interrupt_configuration.INV_EDMP_EVENT =
        fusion_enabled != 0u || extended_enabled != 0u;
    status |= inv_imu_set_config_int(device, INV_IMU_INT1,
                                     &interrupt_configuration);
    if (fusion_enabled != 0u)
        status |= inv_imu_edmp_enable_gaf(device);
    if (fusion_enabled != 0u || extended_enabled != 0u)
        status |= inv_imu_edmp_enable(device);
    return status;
}

int open_cfw_icm45608_tdk_read_fifo(inv_imu_device_t *device,
                                     uint8_t *buffer, uint32_t capacity,
                                     uint16_t *frame_count)
{
    uint32_t required;
    int status;
    if (device == NULL || buffer == NULL || frame_count == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    status = inv_imu_get_frame_count(device, frame_count);
    required = (uint32_t)(*frame_count) * device->fifo_frame_size;
    if (status != INV_IMU_OK)
        return status;
    if (device->fifo_frame_size == 0u || required > capacity)
        return INV_IMU_ERROR_BAD_ARG;
    return inv_imu_read_reg(device, FIFO_DATA, required, buffer);
}

int open_cfw_icm45608_tdk_parse_fifo(inv_imu_device_t *device,
                                      const uint8_t *buffer,
                                      uint16_t frame_count)
{
    if (device == NULL || buffer == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    return inv_imu_adv_parse_fifo_data(device, buffer, frame_count);
}

int open_cfw_icm45608_tdk_poll_registers(inv_imu_device_t *device)
{
    if (device == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    return inv_imu_adv_get_data_from_registers(device);
}

int open_cfw_icm45608_tdk_decode_gaf(
    inv_imu_device_t *device, const uint8_t es0[9], const uint8_t es1[6],
    inv_imu_edmp_gaf_outputs_t *output)
{
    if (device == NULL || es0 == NULL || es1 == NULL || output == NULL)
        return INV_IMU_ERROR_BAD_ARG;
    return inv_imu_edmp_gaf_decode_fifo(device, es0, es1, output);
}
